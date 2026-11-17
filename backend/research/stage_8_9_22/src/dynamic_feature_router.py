"""
Stage 8.9.22 - Part 6: Signal-Driven Dynamic Feature Router (SDDFR)

Dynamically routes, scales, and masks acoustic features based on:
1. Signal-to-Noise Ratio (SNR) and SNR confidence.
2. Signal RMS energy and vocal activity probability.
3. Feature-specific measurement confidences (SHR, HNR, Pitch, Formants).

Implements smooth continuous sigmoid transitions without hard discontinuities at 5 dB and 10 dB.
Produces auditable feature weights and telemetry logs.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Tuple
import numpy as np

logger = logging.getLogger("dynamic_feature_router")

class DynamicFeatureRouter:
    def __init__(
        self,
        low_snr_cutoff: float = 5.0,
        high_snr_cutoff: float = 10.0,
        transition_slope: float = 0.8
    ):
        self.low_snr = low_snr_cutoff
        self.high_snr = high_snr_cutoff
        self.k = transition_slope

    def compute_routing_weights(
        self,
        snr_info: Dict[str, Any],
        acoustic_confidences: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Computes continuous reliability weights in [0.0, 1.0] for each feature family.
        """
        snr_db = float(snr_info.get("estimated_snr_db", 10.0))
        snr_conf = float(snr_info.get("snr_confidence", 0.8))

        # Sigmoidal SNR transition factors
        # s_high -> 1.0 when SNR > 10 dB, -> 0.0 when SNR < 10 dB
        s_high = 1.0 / (1.0 + np.exp(-self.k * (snr_db - self.high_snr)))
        # s_low -> 1.0 when SNR < 5 dB, -> 0.0 when SNR > 5 dB
        s_low = 1.0 / (1.0 + np.exp(self.k * (snr_db - self.low_snr)))

        c_pitch = acoustic_confidences.get("pitch_confidence", 0.5)
        c_shr = acoustic_confidences.get("shr_confidence", 0.5)
        c_hnr = acoustic_confidences.get("hnr_confidence", 0.5)
        c_formant = acoustic_confidences.get("formant_confidence", 0.5)
        c_temporal = acoustic_confidences.get("temporal_confidence", 0.8)

        # 1. HNR Reliability Weight:
        # At low SNR, background noise artificially depresses HNR, so HNR reliability must drop.
        w_hnr = float(np.clip(s_high * c_hnr * snr_conf + (1.0 - s_low) * 0.3 * c_hnr, 0.05, 1.0))

        # 2. SHR Reliability Weight:
        # Low SNR introduces inter-harmonic noise peaks resembling subharmonics.
        # Under low SNR, SHR reliability is sharply suppressed.
        w_shr = float(np.clip(s_high * c_shr * snr_conf, 0.02, 1.0))

        # 3. Formant Reliability Weight:
        # Formants require distinct resonant peaks above the noise floor.
        w_formant = float(np.clip(s_high * c_formant * snr_conf, 0.0, 1.0))

        # 4. Pitch Tracking & Chaos Reliability Weight:
        # High-energy pitch failure is informative even at moderate noise if vocal energy is strong.
        w_pitch = float(np.clip(c_pitch * (1.0 - 0.5 * s_low), 0.15, 1.0))

        # 5. YAMNet Reliability Weight:
        # Pretrained AudioSet representations are robust across noise. Always heavily trusted.
        w_yamnet = float(np.clip(0.70 + 0.30 * (1.0 - s_low), 0.70, 1.0))

        # 6. Temporal & Energy Crest Reliability Weight:
        # Attack crest factor and log attack time are transient-based and remain informative across SNR.
        w_temporal = float(np.clip(c_temporal * (0.60 + 0.40 * snr_conf), 0.30, 1.0))

        # Overall Signal Quality Index
        signal_quality = float(np.clip(0.35 * snr_conf + 0.25 * c_pitch + 0.25 * w_hnr + 0.15 * (snr_db / 25.0), 0.0, 1.0))

        return {
            "w_hnr": round(w_hnr, 4),
            "w_shr": round(w_shr, 4),
            "w_pitch": round(w_pitch, 4),
            "w_formant": round(w_formant, 4),
            "w_yamnet": round(w_yamnet, 4),
            "w_temporal": round(w_temporal, 4),
            "signal_quality": round(signal_quality, 4),
            "snr_db": round(snr_db, 2),
            "snr_confidence": round(snr_conf, 4)
        }

    def apply_routing(
        self,
        feature_vector: np.ndarray,
        feature_names: List[str],
        weights: Dict[str, float]
    ) -> np.ndarray:
        """
        Applies smooth continuous scaling to the feature vector based on family reliability weights.
        """
        scaled = feature_vector.copy()

        for idx, name in enumerate(feature_names):
            if "shr" in name or "biphonic" in name:
                scaled[idx] *= weights["w_shr"]
            elif "hnr" in name:
                scaled[idx] *= weights["w_hnr"]
            elif "pitch" in name or "f0" in name or "discontinuity" in name:
                scaled[idx] *= weights["w_pitch"]
            elif "formant" in name:
                scaled[idx] *= weights["w_formant"]
            elif "attack" in name or "crest" in name or "flutter" in name:
                scaled[idx] *= weights["w_temporal"]
            # Quality metrics remain unscaled

        return scaled
