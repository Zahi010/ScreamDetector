"""Integrated Multi-Stage Scream Detection Pipeline (Stage 8.9.26).

Architecture:
  Stage 1: Acoustic Pre-Screening (Inexpensive energy, flux, centroid, noise-floor)
  Stage 2: Fast Temporal Candidate Detection (Model C: Dilated 1D CNN, 300 ms receptive field)
  Stage 3: Temporal & Acoustic Verification (Candidate G TMSCV + Model E Horn Resonance + Spectral Peak Prominence)
  Stage 4: Confidence-Aware Multi-Stage Fusion & 3-Class Decision Layer
           (POSSIBLE_SCREAM, NON_SCREAM, AMBIGUOUS_VOCALIZATION)

Fusion Variants Evaluated:
  - Fusion A: Model C alone
  - Fusion B: Model C + Candidate G
  - Fusion C: Model C + Model E
  - Fusion D: Model C + Candidate G + Model E (Linear / Logistic validation-trained)
  - Fusion E: Confidence-Aware Asymmetric Fusion with Explicit Feature-Reliability Handling
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler

from pre_screener import AcousticPreScreener, PreScreeningResult
from spectral_peak_prominence import analyze_resonance_profile, ResonanceAnalysisResult


@dataclass
class DetectionResult:
    file_id: str
    ground_truth: int
    duration_sec: float
    canonical_category: str
    split: str
    
    # Stage 1: Pre-screening
    passed_prescreen: bool
    prescreen_latency_ms: float
    prescreen_reason: str
    
    # Stage 2: Fast Temporal Detection (Model C)
    fast_score: float
    fast_latency_ms: float
    is_fast_candidate: bool
    
    # Stage 3: Verification
    cand_g_score: float
    model_e_score: float
    horn_resonance_ratio: float
    horn_peak_prominence_db: float
    lpc_formant_dispersion: float
    lpc_success: bool
    f0_hz: float
    is_high_pitch: bool
    verification_latency_ms: float
    
    # Stage 4: Fusion Scores
    score_fusion_a: float
    score_fusion_b: float
    score_fusion_c: float
    score_fusion_d: float
    score_fusion_e: float
    
    # Decisions @ 0.35 threshold
    decision_fusion_a: int
    decision_fusion_b: int
    decision_fusion_c: int
    decision_fusion_d: int
    decision_fusion_e: int
    classification_category_e: str  # POSSIBLE_SCREAM, NON_SCREAM, AMBIGUOUS_VOCALIZATION
    total_compute_latency_ms: float


class IntegratedMultiStageDetector:
    """Four-stage detection engine integrating pre-screening, fast detection, verification, and fusion."""

    def __init__(self, backend_dir: Path):
        self.backend_dir = backend_dir
        self.stage25_models_dir = backend_dir / "research" / "stage_8_9_25" / "models"
        self.stage24_dir = backend_dir / "research" / "stage_8_9_24"
        
        # Load Pre-screener
        self.pre_screener = AcousticPreScreener(sample_rate=16000)
        
        # Load Model C
        import keras
        model_c_path = self.stage25_models_dir / "model_c_temporal_1d_cnn.keras"
        self.model_c = keras.models.load_model(model_c_path)
        
        # Load Model E
        model_e_path = self.stage25_models_dir / "model_e_hybrid_multimodal.joblib"
        self.model_e = joblib.load(model_e_path)
        
        # Load Candidate G reference predictions map
        cand_g_csv = self.stage24_dir / "temporal_candidate_prediction_comparison.csv"
        self.cand_g_preds = {}
        if cand_g_csv.exists():
            with open(cand_g_csv, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.cand_g_preds[row["recording_id"]] = float(row["final_research_prediction"])

    def evaluate_asymmetric_fusion_e(
        self,
        fast_score: float,
        cand_g_score: float,
        model_e_score: float,
        horn_ratio: float,
        horn_prom_db: float,
        duration: float,
        lpc_success: bool,
        is_high_pitch: bool,
    ) -> Tuple[float, str]:
        """Asymmetric confidence-aware fusion logic (Fusion E).
        
        Principles:
        1. Short-Event Protection: If duration < 0.8s, fast_score carries primary weight (0.65).
           Cadence suppression is INHIBITED because syllabic cadence requires multiple syllables.
        2. Speech Cadence Suppression: If duration >= 1.2s and Cand G score is low (< 0.20)
           WITH low horn resonance (< 0.35), reduce combined score to suppress speech shouting.
        3. Resonance Confirmation: If horn resonance ratio > 0.45 or horn peak prominence > 6 dB,
           boost confidence (+0.12), overcoming glottal fry in screamed vocalizations.
        4. Ambiguity Quarantine: Flag vocalizations where fast pathway triggers (> 0.40)
           but acoustic verifier shows borderline confidence (0.25 - 0.45) and no speech cadence evidence.
        """
        # Base weighted fusion
        if duration < 0.8:
            # Fast pathway dominates for short events
            base_score = 0.65 * fast_score + 0.35 * model_e_score
        else:
            # Multi-scale integration for longer events
            base_score = 0.35 * fast_score + 0.35 * model_e_score + 0.30 * cand_g_score

        # Asymmetric Evidence Adjustments
        adjusted_score = base_score

        # Positive Evidence: Strong vocal-tract horn resonance
        if horn_ratio >= 0.45 or horn_prom_db >= 6.0:
            adjusted_score = min(1.0, adjusted_score + 0.12)

        # Negative Evidence: Validated multi-syllabic speech shouting
        # Only suppress if duration is long enough for cadence to be verified reliably
        if duration >= 1.2 and cand_g_score <= 0.15 and horn_ratio < 0.35:
            adjusted_score = max(0.0, adjusted_score - 0.22)

        # 3-Class Categorization
        # Threshold: 0.3500 (Production threshold preserved)
        if adjusted_score >= 0.45:
            category = "POSSIBLE_SCREAM"
        elif adjusted_score < 0.25:
            category = "NON_SCREAM"
        else:
            # Ambiguity zone: 0.25 <= adjusted_score < 0.45
            # If fast pathway triggered strongly or it's a short burst, keep in possible scream,
            # otherwise quarantine as ambiguous
            if fast_score >= 0.50 and duration < 0.8:
                category = "POSSIBLE_SCREAM"
            else:
                category = "AMBIGUOUS_VOCALIZATION"

        return float(adjusted_score), category
