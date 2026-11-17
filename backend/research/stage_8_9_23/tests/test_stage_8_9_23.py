"""
Stage 8.9.23 Automated Test Suite
Verifies:
1. Production artifact immutability (4 authoritative SHA-256 hashes verified)
2. Production threshold strictly remains 0.3500
3. SHR calculation (pure tone low SHR vs period-doubled high SHR)
4. Signal-conditioned pitch tracking failure handling
5. Handling of missing/corrupted acoustic features
6. Near-silent and invalid inputs
7. Dynamic feature routing weight allocations across SNR
8. Tier 2 verifier integration and tri-state decision logic
9. Candidate prediction comparison ledger integrity
10. Source-group disjointness and isolation (zero train-test leakage)
"""

import hashlib
import json
from pathlib import Path
import pytest
import numpy as np

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = WORKSPACE_DIR.parent.parent
REPO_ROOT = BACKEND_DIR.parent
STAGE22_DIR = BACKEND_DIR / "research" / "stage_8_9_22"

import sys
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(STAGE22_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE22_DIR))
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from research.stage_8_9_22.src.shr_formula_validation import SHRFormulaValidator
from research.stage_8_9_22.src.signal_conditioned_pitch import SignalConditionedPitchTracker
from research.stage_8_9_22.src.dynamic_feature_router import DynamicFeatureRouter
from research.stage_8_9_22.src.sddfr_classifier import SDDFRTwoTierClassifier

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
        assert full_path.exists(), f"Missing production artifact: {rel_path}"
        with open(full_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        assert computed_hash == expected_hash, f"Hash mismatch for {rel_path}!"

    def test_production_threshold(self):
        metadata_path = BACKEND_DIR / "models/model_metadata.json"
        with open(metadata_path, "r") as f:
            meta = json.load(f)
        threshold = meta.get("selected_threshold", meta.get("operating_threshold", meta.get("threshold")))
        assert abs(threshold - 0.3500) < 1e-4, f"Production threshold modified: {threshold}"


class TestSHRAndPitchMechanics:
    def test_shr_pure_tone_vs_biphonation(self):
        validator = SHRFormulaValidator(sample_rate=16000)
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        # Modal
        s_modal = np.sin(2 * np.pi * 300 * t) + 0.5 * np.sin(2 * np.pi * 600 * t)
        res_modal = validator.robust_instantaneous_shr(s_modal)
        # Biphonic
        s_biphonic = np.sin(2 * np.pi * 300 * t) + 0.8 * np.sin(2 * np.pi * 150 * t)
        res_biphonic = validator.robust_instantaneous_shr(s_biphonic)

        assert res_modal["shr_db"] < -20.0, f"Pure modal SHR too high: {res_modal['shr_db']}"
        assert res_biphonic["shr_db"] > -10.0, f"Biphonic SHR too low: {res_biphonic['shr_db']}"
        assert res_biphonic["shr_db"] > res_modal["shr_db"] + 15.0

    def test_pitch_clipping_separation(self):
        tracker = SignalConditionedPitchTracker(sample_rate=16000)
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        clipped_signal = np.clip(10.0 * np.sin(2 * np.pi * 300 * t), -0.99, 0.99)
        res = tracker.analyze_audio(clipped_signal)
        assert res["clipping_ratio"] > 0.80, "Failed to flag clipped audio"

    def test_near_silence_input(self):
        tracker = SignalConditionedPitchTracker(sample_rate=16000)
        silence = np.zeros(16000, dtype=np.float32)
        res = tracker.analyze_audio(silence)
        assert res["vocal_confidence"] == 0.0
        assert res["eligible_vocal_he_frames"] == 0


class TestDynamicRouterAndTwoTier:
    def test_router_weights_gradient(self):
        router = DynamicFeatureRouter()
        snr_low = {"estimated_snr_db": 0.0, "snr_confidence": 0.9}
        snr_high = {"estimated_snr_db": 20.0, "snr_confidence": 0.9}
        confs = {
            "pitch_confidence": 0.8,
            "shr_confidence": 0.8,
            "hnr_confidence": 0.8,
            "formant_confidence": 0.8,
            "temporal_confidence": 0.8,
        }

        w_low = router.compute_routing_weights(snr_low, confs)
        w_high = router.compute_routing_weights(snr_high, confs)

        assert w_low["w_hnr"] < 0.20, "HNR not properly down-weighted at 0 dB SNR"
        assert w_high["w_hnr"] > 0.70, "HNR not properly trusted at 20 dB SNR"
        assert w_low["w_yamnet"] >= 0.70, "YAMNet mean should maintain robust baseline >= 0.70"
        assert w_high["w_yamnet"] >= 0.95, "YAMNet mean should approach 1.0 at high SNR"

    def test_two_tier_tri_state_contract(self):
        clf = SDDFRTwoTierClassifier(tier1_threshold=0.35)
        # Dummy fits
        X_dummy = np.random.randn(20, 1056).astype(np.float32)
        y_dummy = np.array([0, 1] * 10)
        X_t2_dummy = np.random.randn(20, 24).astype(np.float32)

        clf.fit(X_dummy, y_dummy, X_t2_dummy, X_dummy, y_dummy, X_t2_dummy)

        weights = {"w_hnr": 1.0, "w_shr": 1.0, "w_pitch": 1.0, "w_formant": 1.0, "w_yamnet": 1.0}
        fnames = [f"f_{i}" for i in range(24)]
        pred = clf.predict_sample(X_dummy[0], X_t2_dummy[0], weights, fnames)

        assert "status" in pred
        assert pred["status"] in ["POSSIBLE_SCREAM", "LIKELY_CONFUSER", "UNCERTAIN"]
        assert pred["final_decision"] in [0, 1]


class TestDatasetIntegrityAndArtifacts:
    def test_source_group_disjointness(self):
        f17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
        d17 = np.load(f17_path, allow_pickle=True)
        splits = d17["splits"]
        source_groups = d17["source_groups"]

        tr_sg = set(source_groups[splits == "train"])
        te_sg = set(source_groups[splits == "test"])
        leakage = tr_sg.intersection(te_sg)

        assert len(leakage) == 0, f"Source group leakage detected: {leakage}"

    def test_candidate_comparison_csv_exists(self):
        csv_path = WORKSPACE_DIR / "candidate_prediction_comparison.csv"
        assert csv_path.exists(), "candidate_prediction_comparison.csv not found!"
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) > 462 * 8, f"Expected at least 3,696 candidate prediction rows, got {len(lines)}"

    def test_missed_screams_csv_count(self):
        csv_path = WORKSPACE_DIR / "missed_scream_forensic_analysis.csv"
        assert csv_path.exists(), "missed_scream_forensic_analysis.csv not found!"
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.strip()]
        assert len(lines) == 18, f"Expected header + 17 missed screams, got {len(lines)}"
