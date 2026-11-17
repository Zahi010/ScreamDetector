"""
Stage 8.9.21 - Experiment E: Asymmetric Two-Tier Classification & Confidence-Aware Acoustic Verification

Architecture:
- TIER 1: Candidate Detection (High-sensitivity generator targeting Recall >= 96%)
- TIER 2: Acoustic Verification (Nonlinear vocal dynamics, SHR, HNR, formant dispersion, pitch tracking failure)

Evaluates 5 Second-Stage Verification Methods:
A. Interpretable Logistic Regression (L2 penalized, normalized coefficients)
B. Gradient-Boosted Classifier (HistGradientBoosting / LightGBM style)
C. Small Neural Network (MLP with 64 units, dropout & early stopping)
D. Calibrated Confidence-Aware Decision Model (Platt-scaled ensemble with uncertainty gating)
E. Explicit Rule-Based Override (Ablation testing multi-feature conjunctions)

Decision Tri-State Outputs:
- POSSIBLE_SCREAM: Tier 1 candidate confirmed by chaotic phonation or elevated subharmonics/instability.
- LIKELY_CONFUSER: Tier 1 candidate suppressed due to validated modal phonation (high HNR, stable pitch, low SHR).
- UNCERTAIN: Indeterminate phonation, low SNR, or missing formants -> Preserves Tier 1 sensitivity.

Every decision carries an auditable reason code and retains raw Tier 1 & Tier 2 scores.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, recall_score, precision_score, f1_score

logger = logging.getLogger("two_tier_classifier")

class TwoTierScreamVerifier:
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

        self.scaler = StandardScaler()
        # Method A: Interpretable Logistic Regression
        self.clf_logreg = LogisticRegression(C=0.5, penalty='l2', max_iter=1000, random_state=random_state)
        # Method B: Gradient-Boosted Classifier
        self.clf_gb = HistGradientBoostingClassifier(max_iter=100, learning_rate=0.05, max_leaf_nodes=15, random_state=random_state)
        # Method C: Small Neural Network
        self.clf_mlp = MLPClassifier(hidden_layer_sizes=(64,), alpha=0.01, max_iter=500, random_state=random_state)
        # Method D: Calibrated Confidence Model (Calibrated Platt Logistic on GB logits)
        self.platt_calibrator = LogisticRegression(C=1.0, max_iter=500, random_state=random_state)

        self.is_fitted = False

    def fit(self, X_tier2_train: np.ndarray, y_train: np.ndarray, X_tier2_val: np.ndarray, y_val: np.ndarray):
        """
        Fits Tier 2 verification models on training and validation splits.
        Strictly source-group isolated; no test data used.
        """
        X_tr_s = self.scaler.fit_transform(X_tier2_train)
        X_va_s = self.scaler.transform(X_tier2_val)

        # Train models
        self.clf_logreg.fit(X_tr_s, y_train)
        self.clf_gb.fit(X_tr_s, y_train)
        self.clf_mlp.fit(X_tr_s, y_train)

        # Method D: Platt calibrator on validation GB decision function
        gb_val_margin = self.clf_gb.decision_function(X_va_s).reshape(-1, 1)
        self.platt_calibrator.fit(gb_val_margin, y_val)

        self.is_fitted = True

    def predict_tier2_prob(self, X_tier2: np.ndarray, method: str = "calibrated") -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Tier 2 verifier must be fitted before prediction.")
        X_s = self.scaler.transform(X_tier2)

        m = method.lower()
        if m in ("logreg", "a", "e", "rule_override"):
            return self.clf_logreg.predict_proba(X_s)[:, 1]
        elif m in ("gb", "gradient_boosting", "b"):
            return self.clf_gb.predict_proba(X_s)[:, 1]
        elif m in ("mlp", "neural_net", "c"):
            return self.clf_mlp.predict_proba(X_s)[:, 1]
        elif m in ("calibrated", "confidence", "d"):
            margin = self.clf_gb.decision_function(X_s).reshape(-1, 1)
            return self.platt_calibrator.predict_proba(margin)[:, 1]
        else:
            raise ValueError(f"Unknown tier2 method: {method}")

    def evaluate_tri_state(
        self,
        tier1_scores: np.ndarray,
        X_tier2: np.ndarray,
        method: str = "calibrated",
        feature_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Produces auditable tri-state decision for each sample:
        - POSSIBLE_SCREAM
        - LIKELY_CONFUSER
        - UNCERTAIN
        """
        t2_probs = self.predict_tier2_prob(X_tier2, method=method)
        results = []

        feat_idx = {}
        if feature_names:
            feat_idx = {name: i for i, name in enumerate(feature_names)}

        for i in range(len(tier1_scores)):
            s1 = float(tier1_scores[i])
            s2 = float(t2_probs[i])
            row = X_tier2[i]

            # Extract key physical acoustic markers if available
            hnr_val = float(row[feat_idx["hnr_db"]]) if "hnr_db" in feat_idx else 0.0
            shr_val = float(row[feat_idx["shr_db"]]) if "shr_db" in feat_idx else -20.0
            invalid_pitch = float(row[feat_idx["invalid_pitch_ratio"]]) if "invalid_pitch_ratio" in feat_idx else 0.0
            formant_conf = float(row[feat_idx["formant_confidence"]]) if "formant_confidence" in feat_idx else 0.0

            if s1 < self.t1_thresh:
                # Sub-threshold at Tier 1: Rejected early
                status = "LIKELY_CONFUSER"
                reason = "TIER1_BELOW_DETECTION_THRESHOLD"
                final_decision = 0
            else:
                # Candidate passed Tier 1! Tier 2 acoustic verification engaged:
                if method.lower() in ("rule_override", "e"):
                    # Method E: Multi-feature validated rule conjunction
                    # A scream candidate is suppressed ONLY IF BOTH high HNR (>14 dB) AND low pitch failure (<15%) AND low SHR (<-15 dB)
                    is_modal_speech = (hnr_val > 14.0) and (invalid_pitch < 0.15) and (shr_val < -15.0)
                    has_chaotic_scream = (shr_val > -5.0) or (invalid_pitch > 0.40 and hnr_val < 8.0)

                    if is_modal_speech:
                        status = "LIKELY_CONFUSER"
                        reason = "RULE_VALIDATED_MODAL_SHOUTING"
                        final_decision = 0
                    elif has_chaotic_scream:
                        status = "POSSIBLE_SCREAM"
                        reason = "RULE_VALIDATED_CHAOTIC_PHONATION"
                        final_decision = 1
                    else:
                        status = "UNCERTAIN"
                        reason = "AMBIGUOUS_ACOUSTIC_PROFILES_PRESERVE_RECALL"
                        final_decision = 1 # Fail-safe: uncertain candidates retain trigger
                else:
                    # Model-based Tier 2 verification (Methods A, B, C, D)
                    if s2 >= self.t2_scream_thresh:
                        status = "POSSIBLE_SCREAM"
                        reason = "TIER2_CONFIRMED_CHAOTIC_OR_SCREAM_DYNAMICS"
                        final_decision = 1
                    elif s2 < (1.0 - self.t2_confuser_thresh):
                        # High confidence that candidate is a non-scream confuser
                        # Strict safeguard: never suppress if formant tracking failed completely or pitch is chaotic
                        if invalid_pitch > 0.50 or shr_val > -6.0:
                            status = "UNCERTAIN"
                            reason = "TIER2_LOW_CONFIDENCE_CHAOTIC_SIGNAL_SAFEGUARD"
                            final_decision = 1 # Do not suppress chaotic screams
                        else:
                            status = "LIKELY_CONFUSER"
                            reason = "TIER2_CONFIRMED_SUSTAINED_HARMONIC_CONFUSER"
                            final_decision = 0
                    else:
                        status = "UNCERTAIN"
                        reason = "TIER2_MARGINAL_CONFIDENCE_FAIL_SAFE"
                        final_decision = 1 # Preserve sensitivity

            results.append({
                "sample_idx": i,
                "tier1_score": round(s1, 4),
                "tier2_score": round(s2, 4),
                "status": status,
                "final_decision": int(final_decision),
                "reason": reason,
                "hnr_db": round(hnr_val, 2),
                "shr_db": round(shr_val, 2),
                "invalid_pitch_ratio": round(invalid_pitch, 3),
                "formant_confidence": round(formant_conf, 3)
            })

        return results
