"""
Stage 8.9.22 - Part 7: Dual-Stream Audio Fusion Module

Integrates independent original and enhanced streams:
1. Stream A: Raw unprocessed waveform (Always preserved).
2. Stream B: Enhanced waveform (Spectral gating / Wiener filtered).

Evaluates:
- Mode A: Original-only stream.
- Mode B: Enhanced-only stream.
- Mode C: Normalized late probability fusion.
- Mode D: Dynamic confidence-aware stream gating (w_orig >= 0.90 at low SNR or high turbulence).
- Mode E: Learned feature concatenation fusion with z-score standardization.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Tuple
import numpy as np

logger = logging.getLogger("dual_stream_fusion")

class DualStreamFusionController:
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate

    def calculate_stream_weights(
        self,
        snr_db: float,
        is_explosive_onset: bool,
        enhancement_distortion_index: float
    ) -> Dict[str, float]:
        """
        Calculates dynamic stream weights (w_orig, w_enh) where w_orig + w_enh = 1.0.
        Safeguards:
        - If SNR < 5 dB or explosive onset detected -> w_orig >= 0.90 (prevent scream suppression).
        - If high enhancement distortion -> w_orig increases.
        - If SNR > 12 dB and stationary background -> w_orig ~ 0.65, w_enh ~ 0.35.
        """
        if snr_db < 5.0 or is_explosive_onset:
            w_orig = 0.92
        elif snr_db < 10.0:
            w_orig = 0.80
        elif enhancement_distortion_index > 0.30:
            w_orig = 0.85
        else:
            w_orig = 0.65

        w_enh = float(1.0 - w_orig)
        return {
            "w_orig": round(float(w_orig), 4),
            "w_enh": round(float(w_enh), 4),
            "reason": (
                "LOW_SNR_OR_EXPLOSIVE_ATTACK_PRESERVE_RAW" if w_orig >= 0.90
                else "BALANCED_DUAL_STREAM_ENHANCEMENT"
            )
        }

    def fuse_probabilities(
        self,
        prob_orig: float,
        prob_enh: float,
        weights: Dict[str, float]
    ) -> float:
        """Normalized late fusion of model probability outputs."""
        w_orig = weights["w_orig"]
        w_enh = weights["w_enh"]
        fused = w_orig * prob_orig + w_enh * prob_enh
        return float(np.clip(fused, 0.0, 1.0))

    def fuse_features_normalized(
        self,
        feat_orig: np.ndarray,
        feat_enh: np.ndarray,
        mean_orig: np.ndarray,
        std_orig: np.ndarray,
        mean_enh: np.ndarray,
        std_enh: np.ndarray
    ) -> np.ndarray:
        """
        Early feature-level concatenation with independent z-score normalization
        to prevent feature distribution and scale mismatch.
        """
        norm_orig = (feat_orig - mean_orig) / (std_orig + 1e-6)
        norm_enh = (feat_enh - mean_enh) / (std_enh + 1e-6)
        return np.concatenate([norm_orig, norm_enh], axis=-1)
