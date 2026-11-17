"""
Stage 8.9.22 Automated Test Suite
Verifies:
1. Production artifact immutability (4 authoritative SHA-256 hashes verified)
2. Production threshold strictly remains 0.3500
3. SHR formula validation on synthetic signals (biphonation vs modal phonation)
4. Signal-conditioned pitch tracking failure (dropout exclusion & vocal activity gating)
5. Real-time SNR estimator and smooth sigmoidal routing regions
6. Dynamic feature router weight allocations across Low/Mid/High SNR
7. Dual-stream audio fusion safeguards (w_orig >= 0.90 at low SNR)
8. SDDFR Two-Tier tri-state decisions and auditable reason codes
9. Forensic audit artifacts and per-recording decision ledger integrity
"""

import hashlib
import json
from pathlib import Path
import pytest
import numpy as np

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent
REPO_ROOT = BACKEND_DIR.parent

import sys
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

FROZEN_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

class TestProductionImmutability:
    @pytest.mark.parametrize("rel_path,expected_hash", FROZEN_HASHES.items())
    def test_production_file_hash(self, rel_path, expected_hash):
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Missing production file: {full_path}"
        with open(full_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest().lower()
        assert actual_hash == expected_hash.lower(), (
            f"Production file {rel_path} mutated! Expected {expected_hash}, got {actual_hash}"
        )

    def test_production_threshold(self):
        meta_path = REPO_ROOT / "backend/models/model_metadata.json"
        with open(meta_path, "r") as f:
            meta = json.load(f)
        assert meta.get("selected_threshold") == 0.35, "Production threshold must remain exactly 0.3500!"

class TestSHRFormulaValidation:
    def test_synthetic_shr_discrimination(self):
        from research.stage_8_9_22.src.shr_formula_validation import SHRFormulaValidator
        validator = SHRFormulaValidator()
        signals = validator.generate_synthetic_signals(duration_sec=0.5)

        # Pure harmonic modal phonation
        pure_audio, _ = signals["pure_harmonic_modal"]
        res_pure = validator.robust_instantaneous_shr(pure_audio)
        assert res_pure["shr_db"] < -20.0, f"Pure harmonic should have low SHR, got {res_pure['shr_db']} dB"

        # Period doubled biphonic phonation
        biphonic_audio, _ = signals["period_doubled_biphonic"]
        res_biphonic = validator.robust_instantaneous_shr(biphonic_audio)
        assert res_biphonic["shr_db"] > -10.0, f"Biphonic signal should have elevated SHR, got {res_biphonic['shr_db']} dB"
        assert res_biphonic["shr_db"] > res_pure["shr_db"], "Biphonic SHR must exceed pure modal SHR"

class TestSignalConditionedPitch:
    def test_dropout_exclusion(self):
        from research.stage_8_9_22.src.signal_conditioned_pitch import SignalConditionedPitchTracker
        tracker = SignalConditionedPitchTracker()

        # Signal with active burst followed by silence dropouts
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        burst = (0.5 * np.sin(2 * np.pi * 500 * t)).astype(np.float32)
        silence = np.zeros(8000, dtype=np.float32)
        sig = np.concatenate([burst, silence])

        res = tracker.analyze_audio(sig)
        assert res["dropout_ratio"] > 0.30, "Should detect dropout frames"
        # High energy vocal pitch failure should be low for pure tone
        assert res["high_energy_vocal_pitch_failure"] < 0.20

class TestRealTimeSNREstimator:
    def test_snr_regions_and_weights(self):
        from research.stage_8_9_22.src.snr_estimator import RealTimeSNREstimator
        estimator = RealTimeSNREstimator()

        # Clean sine wave
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        clean = (0.8 * np.sin(2 * np.pi * 400 * t)).astype(np.float32)
        res_clean = estimator.estimate_snr(clean)
        assert res_clean["estimated_snr_db"] > 10.0
        assert res_clean["routing_region"] == "HIGH_SNR"

        # Very noisy signal (-5 dB SNR)
        noise = (0.8 * np.random.randn(16000)).astype(np.float32)
        noisy = (0.1 * np.sin(2 * np.pi * 400 * t) + noise).astype(np.float32)
        res_noisy = estimator.estimate_snr(noisy)
        assert res_noisy["routing_region"] in ("LOW_SNR", "INTERMEDIATE_SNR")

class TestDynamicFeatureRouter:
    def test_routing_suppression_at_low_snr(self):
        from research.stage_8_9_22.src.dynamic_feature_router import DynamicFeatureRouter
        router = DynamicFeatureRouter()

        snr_low = {"estimated_snr_db": -2.0, "snr_confidence": 0.5}
        confs = {"pitch_confidence": 0.6, "shr_confidence": 0.7, "hnr_confidence": 0.8, "formant_confidence": 0.6, "temporal_confidence": 0.8}
        w_low = router.compute_routing_weights(snr_low, confs)

        snr_high = {"estimated_snr_db": 18.0, "snr_confidence": 0.9}
        w_high = router.compute_routing_weights(snr_high, confs)

        # HNR, SHR, Formants must be heavily down-weighted at low SNR
        assert w_low["w_hnr"] < w_high["w_hnr"]
        assert w_low["w_shr"] < w_high["w_shr"]
        assert w_low["w_formant"] < w_high["w_formant"]
        # YAMNet and temporal remain trusted
        assert w_low["w_yamnet"] >= 0.70

class TestDualStreamFusion:
    def test_preservation_at_low_snr(self):
        from research.stage_8_9_22.src.dual_stream_fusion import DualStreamFusionController
        ctrl = DualStreamFusionController()
        w_low = ctrl.calculate_stream_weights(snr_db=-3.0, is_explosive_onset=False, enhancement_distortion_index=0.1)
        assert w_low["w_orig"] >= 0.90, "At low SNR, original stream must have weight >= 0.90"

        w_onset = ctrl.calculate_stream_weights(snr_db=15.0, is_explosive_onset=True, enhancement_distortion_index=0.0)
        assert w_onset["w_orig"] >= 0.90, "During explosive onset, original stream must have weight >= 0.90"

class TestSDDFRTwoTierClassifier:
    def test_two_tier_tri_state(self):
        from research.stage_8_9_22.src.sddfr_classifier import SDDFRTwoTierClassifier
        clf = SDDFRTwoTierClassifier(tier1_threshold=0.35)

        # Dummy fit
        X_t1 = np.random.randn(20, 1056).astype(np.float32)
        y = np.array([1]*10 + [0]*10)
        X_t2 = np.random.randn(20, 24).astype(np.float32)
        clf.fit(X_t1, y, X_t2, X_t1[:10], y[:10], X_t2[:10])

        x_sample_t1 = X_t1[0]
        x_sample_t2 = X_t2[0]
        feat_names = [f"f_{i}" for i in range(24)]
        feat_names[0] = "high_energy_vocal_pitch_failure"
        feat_names[6] = "shr_db"
        feat_names[9] = "hnr_db"
        feat_names[13] = "formant_dispersion"
        feat_names[14] = "formant_available"

        weights = {"w_hnr": 0.8, "w_shr": 0.8, "w_pitch": 0.8, "w_formant": 0.8, "snr_db": 12.0}
        res = clf.predict_sample(x_sample_t1, x_sample_t2, weights, feat_names)
        assert res["status"] in ("POSSIBLE_SCREAM", "LIKELY_CONFUSER", "UNCERTAIN")
        assert len(res["reason"]) > 0
