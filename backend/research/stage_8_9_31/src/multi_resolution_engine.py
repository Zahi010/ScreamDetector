"""
Stage 8.9.31 - Dual-Resolution Multi-Scale Streaming Inference Architecture.

Implements:
1. Micro-Resolution Branch: 375 ms window / 100 ms hop.
2. Macro-Resolution Branch: 975 ms window / 250 ms hop.
3. End-of-stream flush with right-padding and sample tracking.
4. Experimental fusion candidates (A through F).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

# Research paths
BACKEND_DIR = Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation" / "src"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_24"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_26" / "src"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_29"))

from research_ring_buffer import ResearchAudioRingBuffer, WindowFrame
from pre_screener import AcousticPreScreener
from temporal_feature_extractor import TemporalPhonationExtractor
from temporal_feature_extraction import TemporalModulationExtractor
from spectral_peak_prominence import analyze_resonance_profile
from multi_stage_detector import IntegratedMultiStageDetector


@dataclass
class MicroBranchResult:
    window_idx: int
    start_sec: float
    end_sec: float
    score_cand_g: float
    passed_prescreen: bool
    horn_ratio: float
    horn_prom_db: float
    valid_samples: int
    padded_samples: int
    padding_fraction: float
    compute_ms: float


@dataclass
class MacroBranchResult:
    window_idx: int
    start_sec: float
    end_sec: float
    score_model_c: float
    score_cand_g: float
    score_model_e: float
    passed_prescreen: bool
    horn_ratio: float
    horn_prom_db: float
    lpc_success: bool
    is_high_pitch: bool
    valid_samples: int
    padded_samples: int
    padding_fraction: float
    compute_ms: float


@dataclass
class MultiResolutionWindowDecision:
    window_idx: int
    start_sec: float
    end_sec: float
    micro_result: Optional[MicroBranchResult]
    macro_result: Optional[MacroBranchResult]
    fusion_candidate_scores: Dict[str, float]
    primary_score: float
    primary_classification: str
    is_alert: bool
    compute_ms: float


class MultiResolutionInferenceEngine:
    """Coordinates dual-resolution streaming branches and multi-scale fusion."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

        # 1. Dual-Resolution Ring Buffers
        # Micro Branch: 375 ms window (6,000 samples), 100 ms hop (1,600 samples)
        self.micro_buffer = ResearchAudioRingBuffer(
            sample_rate=sample_rate,
            window_sec=0.375,
            hop_sec=0.100,
            capacity_sec=6.0,
            min_valid_sec=0.200,
        )

        # Macro Branch: 975 ms window (15,600 samples), 250 ms hop (4,000 samples)
        self.macro_buffer = ResearchAudioRingBuffer(
            sample_rate=sample_rate,
            window_sec=0.975,
            hop_sec=0.250,
            capacity_sec=6.0,
            min_valid_sec=0.200,
        )

        # 2. Extractors & Shared Pre-screener
        self.detector = IntegratedMultiStageDetector(BACKEND_DIR)
        self.pre_screener = self.detector.pre_screener
        self.phon_ext = TemporalPhonationExtractor(sr=sample_rate)
        self.mod_ext_micro = TemporalModulationExtractor(sr=sample_rate)
        self.mod_ext_macro = TemporalModulationExtractor(sr=sample_rate)

        # 3. Model Weights & Scalers
        stage24_models_dir = BACKEND_DIR / "research" / "stage_8_9_24" / "models"
        self.cand_e_model = joblib.load(stage24_models_dir / "candidate_e_short_pathway.joblib")
        self.scaler_short = joblib.load(stage24_models_dir / "scaler_short.joblib")

        # Scalers for Model C and Model E
        d18_path = BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation" / "data" / "features_stage8_9_18_temporal.npz"
        d18 = np.load(d18_path, allow_pickle=True)
        tr_mask = d18["splits"] == "train"
        seq16_tr = d18["features_seq_16"][tr_mask].astype(np.float32)
        scaler_seq = StandardScaler().fit(seq16_tr.reshape(-1, 16))
        self.scaler_seq = scaler_seq
        self.scale_seq = np.maximum(1e-6, np.sqrt(scaler_seq.var_))
        temp32_tr = d18["features_temporal"][tr_mask].astype(np.float32)
        self.scaler_temp32 = StandardScaler().fit(temp32_tr)

        # Model C (compiled TensorFlow)
        import tensorflow as tf
        model_c = self.detector.model_c
        @tf.function
        def compiled_model_c(x):
            return model_c(x, training=False)
        self._tf_model_c = compiled_model_c

    def reset(self) -> None:
        """Reset internal buffers and stream state."""
        self.micro_buffer.reset()
        self.macro_buffer.reset()

    def process_micro_window(self, win: WindowFrame) -> MicroBranchResult:
        """Process a single 375 ms window through the micro-resolution branch."""
        t0 = time.perf_counter()
        pcm = win.pcm
        passed_ps = self.pre_screener.process_waveform(pcm)

        score_cand_g = 0.0
        res_prof = analyze_resonance_profile(pcm, sr=self.sample_rate)

        valid_sec = win.valid_duration_sec
        # Candidate G modulation features
        f_ms = self.mod_ext_micro.extract_feature_vector(pcm, context_sec=min(0.375, valid_sec))
        f_ms_scaled = self.scaler_short.transform(f_ms[np.newaxis, :])
        score_cand_g = float(self.cand_e_model.predict_proba(f_ms_scaled)[0, 1])

        compute_ms = (time.perf_counter() - t0) * 1000.0

        return MicroBranchResult(
            window_idx=win.window_idx,
            start_sec=win.start_sec,
            end_sec=win.end_sec,
            score_cand_g=score_cand_g,
            passed_prescreen=passed_ps,
            horn_ratio=float(res_prof.horn_energy_ratio),
            horn_prom_db=float(res_prof.horn_peak_prominence_db),
            valid_samples=win.valid_samples,
            padded_samples=win.padded_samples,
            padding_fraction=win.padding_fraction,
            compute_ms=compute_ms,
        )

    def process_macro_window(self, win: WindowFrame) -> MacroBranchResult:
        """Process a single 975 ms window through the macro-resolution branch."""
        t0 = time.perf_counter()
        pcm = win.pcm
        passed_ps = self.pre_screener.process_waveform(pcm)

        # Model C temporal sequence features
        seq_16 = self.phon_ext.extract_short_time_feature_sequence(pcm, max_frames=70)
        seq_norm = ((seq_16 - self.scaler_seq.mean_) / self.scale_seq).astype(np.float32)
        score_model_c = float(self._tf_model_c(seq_norm[np.newaxis, ...]).numpy()[0, 0])

        # Candidate G modulation features
        f_ms = self.mod_ext_macro.extract_feature_vector(pcm, context_sec=0.5)
        f_ms_scaled = self.scaler_short.transform(f_ms[np.newaxis, :])
        score_cand_g = float(self.cand_e_model.predict_proba(f_ms_scaled)[0, 1])

        # Model E multimodal features
        t_vec32 = self.phon_ext.extract_temporal_features(pcm)
        t_vec32_n = self.scaler_temp32.transform(t_vec32[np.newaxis, :])
        xe_in = np.concatenate([
            np.zeros(1024, dtype=np.float32),
            [score_model_c * 0.9 + 0.05],
            [score_model_c],
            t_vec32_n[0],
        ])
        score_model_e = float(self.detector.model_e.predict_proba(xe_in[np.newaxis, :])[0, 1])

        # Resonance profile
        res_prof = analyze_resonance_profile(pcm, sr=self.sample_rate)

        compute_ms = (time.perf_counter() - t0) * 1000.0

        return MacroBranchResult(
            window_idx=win.window_idx,
            start_sec=win.start_sec,
            end_sec=win.end_sec,
            score_model_c=score_model_c,
            score_cand_g=score_cand_g,
            score_model_e=score_model_e,
            passed_prescreen=passed_ps,
            horn_ratio=float(res_prof.horn_energy_ratio),
            horn_prom_db=float(res_prof.horn_peak_prominence_db),
            lpc_success=bool(res_prof.lpc_success),
            is_high_pitch=bool(res_prof.is_high_pitch),
            valid_samples=win.valid_samples,
            padded_samples=win.padded_samples,
            padding_fraction=win.padding_fraction,
            compute_ms=compute_ms,
        )

    def evaluate_fusion_candidates(
        self,
        micro: Optional[MicroBranchResult],
        macro: Optional[MacroBranchResult],
    ) -> Dict[str, float]:
        """Compute scores for all 6 experimental fusion candidates (A through F)."""
        scores = {}

        # -------------------------------------------------------------
        # Candidate A: Baseline Fusion E (Macro-Only)
        # -------------------------------------------------------------
        if macro is not None:
            score_a, _ = self.detector.evaluate_asymmetric_fusion_e(
                fast_score=macro.score_model_c,
                cand_g_score=macro.score_cand_g,
                model_e_score=macro.score_model_e,
                horn_ratio=macro.horn_ratio,
                horn_prom_db=macro.horn_prom_db,
                duration=0.975,
                lpc_success=macro.lpc_success,
                is_high_pitch=macro.is_high_pitch,
            )
            scores["cand_a_baseline_macro"] = float(score_a)
        else:
            scores["cand_a_baseline_macro"] = 0.0

        # -------------------------------------------------------------
        # Candidate B: Candidate G Dominant Fusion
        # -------------------------------------------------------------
        cg_score = 0.0
        if micro is not None and macro is not None:
            cg_score = max(micro.score_cand_g, macro.score_cand_g)
        elif micro is not None:
            cg_score = micro.score_cand_g
        elif macro is not None:
            cg_score = macro.score_cand_g

        if macro is not None:
            # Overrides Model C if Candidate G is strong (>= 0.35)
            if cg_score >= 0.35:
                score_b = 0.70 * cg_score + 0.30 * max(macro.score_model_c, macro.score_model_e)
            else:
                score_b = scores["cand_a_baseline_macro"]
            scores["cand_b_cand_g_dominant"] = float(score_b)
        else:
            scores["cand_b_cand_g_dominant"] = float(cg_score)

        # -------------------------------------------------------------
        # Candidate C: Duration-Aware Asymmetric Fusion
        # -------------------------------------------------------------
        # If event is short (< 0.8s) or heavily padded, boost Candidate G & horn ratio
        if macro is not None:
            is_short = (macro.valid_samples < 12800) or (macro.padding_fraction > 0.20)
            if is_short:
                # Short event pathway: balance micro modulation and horn resonance
                effective_cg = max(cg_score, macro.score_cand_g)
                horn_boost = 0.10 if macro.horn_ratio > 0.30 else 0.0
                score_c = 0.65 * effective_cg + 0.25 * macro.score_model_c + 0.10 * macro.score_model_e + horn_boost
                scores["cand_c_duration_aware"] = float(min(1.0, score_c))
            else:
                scores["cand_c_duration_aware"] = scores["cand_a_baseline_macro"]
        else:
            scores["cand_c_duration_aware"] = float(cg_score)

        # -------------------------------------------------------------
        # Candidate D: Dual-Resolution Micro/Macro Confidence Fusion
        # -------------------------------------------------------------
        if micro is not None and macro is not None:
            # Micro captures fast onset modulation; macro captures contextual resonance
            score_d = (
                0.40 * micro.score_cand_g +
                0.30 * macro.score_model_c * (1.0 - macro.padding_fraction) +
                0.30 * macro.score_model_e
            )
            # If both branches support event, boost confidence
            if micro.score_cand_g >= 0.35 and macro.score_model_e >= 0.35:
                score_d = min(1.0, score_d * 1.25)
            scores["cand_d_dual_resolution"] = float(score_d)
        elif macro is not None:
            scores["cand_d_dual_resolution"] = scores["cand_a_baseline_macro"]
        elif micro is not None:
            scores["cand_d_dual_resolution"] = float(micro.score_cand_g)
        else:
            scores["cand_d_dual_resolution"] = 0.0

        # -------------------------------------------------------------
        # Candidate E: Padding-Aware Confidence Adjusted Fusion
        # -------------------------------------------------------------
        if macro is not None:
            # De-weight Model C proportional to padding fraction
            pad_factor = max(0.2, 1.0 - macro.padding_fraction)
            adj_model_c = macro.score_model_c * pad_factor
            score_e, _ = self.detector.evaluate_asymmetric_fusion_e(
                fast_score=adj_model_c,
                cand_g_score=max(cg_score, macro.score_cand_g),
                model_e_score=macro.score_model_e,
                horn_ratio=macro.horn_ratio,
                horn_prom_db=macro.horn_prom_db,
                duration=0.975,
                lpc_success=macro.lpc_success,
                is_high_pitch=macro.is_high_pitch,
            )
            # If Candidate G is high and Model C was downweighted by padding, restore score
            if cg_score >= 0.35 and macro.padding_fraction > 0.30:
                score_e = max(score_e, cg_score * 0.90)
            scores["cand_e_padding_aware"] = float(score_e)
        else:
            scores["cand_e_padding_aware"] = float(cg_score)

        # -------------------------------------------------------------
        # Candidate F: Conservative Branch Agreement (Hard-Negative Protected)
        # -------------------------------------------------------------
        if micro is not None and macro is not None:
            # Requires agreement or strong resonance confirmation
            both_agree = (micro.score_cand_g >= 0.35) and (macro.score_model_c >= 0.30 or macro.score_model_e >= 0.30)
            strong_horn = (macro.horn_ratio >= 0.40 and macro.horn_prom_db >= 8.0)
            if both_agree or strong_horn:
                score_f = max(scores["cand_c_duration_aware"], scores["cand_d_dual_resolution"])
            else:
                # Suppress stadium cheering/laughter by penalizing disagreement
                score_f = min(scores["cand_a_baseline_macro"], micro.score_cand_g * 0.70)
            scores["cand_f_conservative_agreement"] = float(score_f)
        else:
            scores["cand_f_conservative_agreement"] = scores.get("cand_a_baseline_macro", 0.0)

        return scores
