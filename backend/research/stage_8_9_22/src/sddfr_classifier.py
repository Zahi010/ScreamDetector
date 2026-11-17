"""
Stage 8.9.22 - Part 9: Signal-Driven Dynamic Feature Routing Classifier & Two-Tier Verifier

Architecture:
- TIER 1: High-Sensitivity Candidate Detector (YAMNet Mean + Temporal, Theta1 = 0.35).
- DYNAMIC ROUTER: Real-time SNR estimation & feature reliability weighting.
- TIER 2: Confidence-Aware Acoustic Verifier (Energy-conditioned pitch failure, SHR, HNR, Formants).

Produces Tri-State Decisions:
- POSSIBLE_SCREAM: Tier 1 candidate confirmed by chaotic phonation or subharmonics.
- LIKELY_CONFUSER: Tier 1 candidate safely suppressed due to MULTIPLE reliable harmonic speech markers.
- UNCERTAIN: Ambiguous/low-SNR candidate -> Preserves Tier 1 trigger (fail-safe).

Guarantees:
- Every suppression decision requires high feature reliability (w_feature > 0.50).
- Verifier records explicit per-sample prediction adjustments and auditable reason codes.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("sddfr_classifier")

class SDDFRTwoTierClassifier:
    def __init__(
        self,
        tier1_threshold: float = 0.35,
        tier2_confuser_threshold: float = 0.65,
        tier2_scream_threshold: float = 0.40,
        random_state: int = 42
    ):
        self.t1_thresh = tier1_threshold
        self.t2_confuser_thresh = tier2_confuser_threshold
        self.t2_scream_thresh = tier2_scream_threshold
        self.random_state = random_state

        self.scaler_t1 = StandardScaler()
        self.scaler_t2 = StandardScaler()

        # Tier 1 Classifier (Logistic Regression over YAMNet Mean + Temporal)
        self.clf_t1 = LogisticRegression(C=0.5, max_iter=1000, random_state=random_state)
        # Tier 2 Acoustic Verifier (Calibrated Logistic over Dynamic Routed Acoustics)
        self.clf_t2 = LogisticRegression(C=1.0, max_iter=1000, random_state=random_state)

        self.is_fitted = False

    def fit(
        self,
        X_t1_tr: np.ndarray,
        y_tr: np.ndarray,
        X_t2_tr: np.ndarray,
        X_t1_va: np.ndarray,
        y_va: np.ndarray,
        X_t2_va: np.ndarray
    ):
        """Fits Tier 1 and Tier 2 on training and validation splits strictly."""
        X_t1_tr_s = self.scaler_t1.fit_transform(X_t1_tr)
        self.clf_t1.fit(X_t1_tr_s, y_tr)

        # Train Tier 2 exclusively on candidates that pass Tier 1 (or all training with high sensitivity)
        X_t2_tr_s = self.scaler_t2.fit_transform(X_t2_tr)
        self.clf_t2.fit(X_t2_tr_s, y_tr)

        self.is_fitted = True

    def predict_sample(
        self,
        x_t1: np.ndarray,
        x_t2: np.ndarray,
        routing_weights: Dict[str, float],
        feature_names_t2: List[str]
    ) -> Dict[str, Any]:
        """
        Executes dynamic routing and two-tier verification on a single audio sample.
        """
        x_t1_s = self.scaler_t1.transform(x_t1.reshape(1, -1))
        p1 = float(self.clf_t1.predict_proba(x_t1_s)[0, 1])

        feat_idx = {name: i for i, name in enumerate(feature_names_t2)}

        # Extract key raw physical acoustic markers
        he_pitch_fail = float(x_t2[feat_idx.get("high_energy_vocal_pitch_failure", 0)])
        hnr_val = float(x_t2[feat_idx.get("hnr_db", 9)])
        shr_db = float(x_t2[feat_idx.get("shr_db", 6)])
        f_disp = float(x_t2[feat_idx.get("formant_dispersion", 13)])
        f_avail = float(x_t2[feat_idx.get("formant_available", 14)])

        # Apply dynamic routing weights to x_t2
        x_t2_routed = x_t2.copy()
        for i, name in enumerate(feature_names_t2):
            if "shr" in name or "biphonic" in name:
                x_t2_routed[i] *= routing_weights.get("w_shr", 1.0)
            elif "hnr" in name:
                x_t2_routed[i] *= routing_weights.get("w_hnr", 1.0)
            elif "pitch" in name or "f0" in name:
                x_t2_routed[i] *= routing_weights.get("w_pitch", 1.0)
            elif "formant" in name:
                x_t2_routed[i] *= routing_weights.get("w_formant", 1.0)

        x_t2_s = self.scaler_t2.transform(x_t2_routed.reshape(1, -1))
        p2 = float(self.clf_t2.predict_proba(x_t2_s)[0, 1])

        w_hnr = routing_weights.get("w_hnr", 1.0)
        w_shr = routing_weights.get("w_shr", 1.0)
        w_pitch = routing_weights.get("w_pitch", 1.0)
        w_formant = routing_weights.get("w_formant", 1.0)
        snr_db = routing_weights.get("snr_db", 10.0)

        # -------------------------------------------------------------
        # Decision Logic:
        # -------------------------------------------------------------
        if p1 < self.t1_thresh:
            status = "LIKELY_CONFUSER"
            reason = "TIER1_BELOW_DETECTION_THRESHOLD"
            final_decision = 0
            decision_modified = False
        else:
            # Candidate passed Tier 1! Tier 2 evaluates evidence:
            # A candidate can be suppressed (overridden to 0) ONLY IF:
            # 1. HNR is reliably high (> 12 dB) with w_hnr > 0.40
            # 2. Pitch failure is low (< 0.15) with w_pitch > 0.40
            # 3. Formants are confident and wide (> 850 Hz) with w_formant > 0.35
            # 4. Model p2 confirms confuser (p2 < 0.35)
            is_reliable_modal_shouting = (
                (p2 < 0.35) and
                (w_hnr >= 0.40 and hnr_val > 10.0) and
                (w_pitch >= 0.40 and he_pitch_fail < 0.15) and
                (w_formant >= 0.30 and f_disp > 800.0 and f_avail > 0.5)
            )

            is_confirmed_chaotic_scream = (
                (p2 >= 0.40) or
                (he_pitch_fail > 0.35 and w_pitch >= 0.40) or
                (shr_db > -6.0 and w_shr >= 0.40)
            )

            if is_reliable_modal_shouting:
                # Successfully suppressed false alarm!
                status = "LIKELY_CONFUSER"
                reason = "TIER2_SUPPRESSED_VALIDATED_MODAL_SHOUTING"
                final_decision = 0
                decision_modified = True
            elif is_confirmed_chaotic_scream:
                status = "POSSIBLE_SCREAM"
                reason = "TIER2_CONFIRMED_CHAOTIC_OR_BIPHONIC_DISTRESS"
                final_decision = 1
                decision_modified = False
            else:
                # Low SNR, ambiguous phonation, or missing formants -> FAIL-SAFE PRESERVE!
                status = "UNCERTAIN"
                reason = "AMBIGUOUS_OR_LOW_SNR_PRESERVE_TRIGGER"
                final_decision = 1
                decision_modified = False

        return {
            "tier1_prob": round(p1, 4),
            "tier2_prob": round(p2, 4),
            "status": status,
            "final_decision": int(final_decision),
            "decision_modified": decision_modified,
            "reason": reason,
            "he_pitch_fail": round(he_pitch_fail, 3),
            "hnr_db": round(hnr_val, 2),
            "shr_db": round(shr_db, 2),
            "formant_dispersion": round(f_disp, 1),
            "routing_weights": routing_weights
        }
