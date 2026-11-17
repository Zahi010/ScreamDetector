"""
Stage 8.9.41: Comprehensive Automated Verification Test Suite
Validates 16 core architectural, cryptographic, and statistical invariants.
"""
import unittest
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"
STAGE39_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
STAGE40_DIR = BACKEND_DIR / "research" / "stage_8_9_40"
STAGE41_DIR = BACKEND_DIR / "research" / "stage_8_9_41"

def get_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class TestStage8941Verification(unittest.TestCase):

    def test_01_production_model_immutability(self):
        """1. Production scream classifier joblib SHA-256 immutability."""
        expected = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
        actual = get_sha256(BACKEND_DIR / "models" / "scream_classifier.joblib")
        self.assertEqual(actual, expected, "Production model joblib hash has changed!")

    def test_02_production_metadata_immutability(self):
        """2. Production metadata JSON SHA-256 immutability."""
        expected = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
        actual = get_sha256(BACKEND_DIR / "models" / "model_metadata.json")
        self.assertEqual(actual, expected, "Production model metadata JSON hash has changed!")

    def test_03_production_historical_predictions_immutability(self):
        """3. Production test predictions CSV SHA-256 immutability."""
        expected = "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"
        actual = get_sha256(BACKEND_DIR / "reports" / "test_predictions.csv")
        self.assertEqual(actual, expected, "Production historical test predictions CSV has changed!")

    def test_04_production_historical_evaluation_immutability(self):
        """4. Production Stage 5 test evaluation MD SHA-256 immutability."""
        expected = "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
        actual = get_sha256(BACKEND_DIR / "reports" / "stage5_test_evaluation.md")
        self.assertEqual(actual, expected, "Production Stage 5 evaluation report has changed!")

    def test_05_frozen_config_b_checkpoint_hash(self):
        """5. Candidate B PyTorch checkpoint SHA-256 preservation."""
        expected = "037be323c73202b2fb2f95415796ba147ff506bb47f2d66df27d99be41cfe527"
        actual = get_sha256(STAGE39_DIR / "checkpoints" / "config_b" / "best_model.pt")
        self.assertEqual(actual, expected, "Config B checkpoint weights have changed!")

    def test_06_frozen_config_b_calibrator_hash(self):
        """6. Candidate B Platt calibrator SHA-256 preservation."""
        expected = "1818271467d198610e6ca1a68f75b66a99bd02860c02c4c649a1383016267ecd"
        actual = get_sha256(STAGE39_DIR / "checkpoints" / "config_b" / "platt_calibrator.joblib")
        self.assertEqual(actual, expected, "Config B Platt calibrator has changed!")

    def test_07_frozen_threshold_preservation(self):
        """7. Frozen threshold 0.24 preserved in config and evaluation."""
        with open(STAGE41_DIR / "configs" / "frozen_config_b.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertEqual(cfg["decision_threshold"], 0.24)
        with open(STAGE41_DIR / "results" / "metrics" / "evaluation_results.json", "r", encoding="utf-8") as f:
            res = json.load(f)
        self.assertEqual(res["frozen_threshold"], 0.24)

    def test_08_expansion_benchmark_snapshot_immutability(self):
        """8. Expansion benchmark snapshot (N=102) SHA-256 verification."""
        expected = "d9b5ab556d5ef286bcf1097ae46f70c0965fff1b54af1deac8be065920f01ee4"
        actual = get_sha256(STAGE40_DIR / "manifests" / "expansion_benchmark_snapshot.csv")
        self.assertEqual(actual, expected, "Expansion benchmark snapshot has been modified!")

    def test_09_positive_cohort_physical_audio_existence(self):
        """9. Positive evaluation cohort (N=57) physical audio files existence and format."""
        manifest_path = STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv"
        df = pd.read_csv(manifest_path)
        self.assertEqual(len(df), 57, "Positive cohort manifest must contain exactly 57 records")
        for _, r in df.iterrows():
            audio_path = REPO_ROOT / r["workspace_audio_path"]
            self.assertTrue(audio_path.exists(), f"Audio file missing: {audio_path}")

    def test_10_cross_partition_source_group_isolation(self):
        """10. Zero source-group leakage across dataset v4, stage 8.9.40, and stage 8.9.41."""
        df_new = pd.read_csv(STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv")
        df_v4 = pd.read_csv(STAGE38_DIR / "manifests" / "dataset_manifest_v4.csv")
        df_s40 = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")

        new_sgs = set(df_new["source_group_id"])
        v4_sgs = set(df_v4["source_group_id"])
        s40_sgs = set(df_s40["source_group_id"])

        self.assertEqual(len(new_sgs.intersection(v4_sgs)), 0, "Source group collision with Dataset v4!")
        self.assertEqual(len(new_sgs.intersection(s40_sgs)), 0, "Source group collision with Stage 8.9.40!")

    def test_11_quarantine_manifest_isolation(self):
        """11. Absolute isolation between active positive manifest and quarantine manifest."""
        df_active = pd.read_csv(STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv")
        df_quar = pd.read_csv(STAGE41_DIR / "manifests" / "quarantine_manifest.csv")
        self.assertEqual(len(df_quar), 8, "Quarantine manifest must contain exactly 8 records")
        overlap = set(df_active["file_id"]).intersection(set(df_quar["file_id"]))
        self.assertEqual(len(overlap), 0, "Quarantined recording found in active manifest!")

    def test_12_no_hash_collisions(self):
        """12. Zero SHA-256 and PCM collisions within new positive cohort."""
        df = pd.read_csv(STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv")
        self.assertEqual(len(df["sha256_hash"].unique()), 57, "Duplicate SHA-256 in positive cohort!")
        self.assertEqual(len(df["pcm_sha256"].unique()), 57, "Duplicate PCM hash in positive cohort!")

    def test_13_license_eligibility_commercial(self):
        """13. All active positive recordings are commercially eligible (no CC BY-NC)."""
        df = pd.read_csv(STAGE41_DIR / "manifests" / "stage_8_9_41_positive_manifest.csv")
        for _, r in df.iterrows():
            lic = str(r["license"]).upper()
            self.assertNotIn("NC", lic, f"Non-commercial license in active cohort: {r['file_id']}")
            self.assertTrue(r["is_commercially_eligible"])

    def test_14_prediction_accounting_integrity(self):
        """14. Prediction accounting exactly matches manifest records."""
        df_pred = pd.read_csv(STAGE41_DIR / "predictions" / "config_b_positive_predictions.csv")
        self.assertEqual(len(df_pred), 57)
        tp = int(df_pred["prediction"].sum())
        fn = int(len(df_pred) - tp)
        self.assertEqual(tp + fn, 57)
        self.assertEqual(tp, 20)
        self.assertEqual(fn, 37)

    def test_15_wilson_confidence_interval_bounds(self):
        """15. Wilson score confidence interval mathematical soundness."""
        from backend.research.stage_8_9_41.scripts.evaluate_frozen_config_b import wilson_score_interval
        p, low, high = wilson_score_interval(20, 57)
        self.assertEqual(p, 20/57)
        self.assertAlmostEqual(low, 0.2400, places=3)
        self.assertAlmostEqual(high, 0.4806, places=3)
        self.assertTrue(0.0 <= low <= p <= high <= 1.0)

    def test_16_latency_and_gate_5(self):
        """16. Computational P95 latency is <= 25 ms."""
        with open(STAGE41_DIR / "results" / "metrics" / "evaluation_results.json", "r", encoding="utf-8") as f:
            res = json.load(f)
        g5 = res["acceptance_gates_audit"]["gate_5_p95_inference_latency"]
        self.assertEqual(g5["status"], "PASS")
        self.assertLessEqual(g5["value_ms"], 25.0)

if __name__ == "__main__":
    unittest.main()

