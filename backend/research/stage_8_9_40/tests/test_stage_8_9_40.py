"""
Stage 8.9.40: Comprehensive Verification & Regression Test Suite
Validates 15 core architectural, cryptographic, and statistical invariants.
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

def get_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class TestStage8940Verification(unittest.TestCase):

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

    def test_05_config_b_checkpoint_immutability(self):
        """5. Candidate B PyTorch checkpoint SHA-256 preservation."""
        expected = "037be323c73202b2fb2f95415796ba147ff506bb47f2d66df27d99be41cfe527"
        actual = get_sha256(STAGE39_DIR / "checkpoints" / "config_b" / "best_model.pt")
        self.assertEqual(actual, expected, "Config B checkpoint weights have changed!")

    def test_06_config_d_checkpoint_immutability(self):
        """6. Candidate D PyTorch checkpoint SHA-256 preservation."""
        expected = "be0b160df7f92d250720d880f8f876d3a599b92b5c9960f8eb4a8d7fae171d1b"
        actual = get_sha256(STAGE39_DIR / "checkpoints" / "config_d" / "best_model.pt")
        self.assertEqual(actual, expected, "Config D checkpoint weights have changed!")

    def test_07_frozen_thresholds_preservation(self):
        """7. Frozen thresholds (0.24 for Config B, 0.34 for Config D) preservation."""
        results_path = STAGE40_DIR / "results" / "metrics" / "frozen_model_evaluation_results.json"
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["candidate_b"]["frozen_threshold"], 0.24)
        self.assertEqual(data["candidate_d"]["frozen_threshold"], 0.34)

    def test_08_expansion_benchmark_snapshot_immutability(self):
        """8. Expansion benchmark snapshot (N=102) SHA-256 verification."""
        expected = "d9b5ab556d5ef286bcf1097ae46f70c0965fff1b54af1deac8be065920f01ee4"
        actual = get_sha256(STAGE40_DIR / "manifests" / "expansion_benchmark_snapshot.csv")
        self.assertEqual(actual, expected, "Expansion benchmark snapshot has been modified!")

    def test_09_new_cohort_physical_audio_existence(self):
        """9. New independent cohort (N=145) manifest and physical audio file integrity."""
        manifest_path = STAGE40_DIR / "manifests" / "new_cohort_manifest.csv"
        df = pd.read_csv(manifest_path)
        self.assertEqual(len(df), 145, "New cohort manifest must contain exactly 145 records")
        for _, r in df.iterrows():
            audio_path = REPO_ROOT / r["workspace_audio_path"]
            self.assertTrue(audio_path.exists(), f"Audio file missing: {audio_path}")

    def test_10_new_cohort_cross_partition_isolation(self):
        """10. Complete source-group and file isolation from train, val, hist_test, exp_test."""
        df_new = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")
        df_v4 = pd.read_csv(STAGE38_DIR / "manifests" / "dataset_manifest_v4.csv")
        new_fids = set(df_new["file_id"])
        v4_fids = set(df_v4["file_id"])
        self.assertEqual(len(new_fids.intersection(v4_fids)), 0, "File ID collision with dataset v4!")
        new_sgs = set(df_new["source_group_id"])
        v4_sgs = set(df_v4["source_group_id"])
        self.assertEqual(len(new_sgs.intersection(v4_sgs)), 0, "Source group leakage with dataset v4!")

    def test_11_new_cohort_quarantine_isolation(self):
        """11. Absolute isolation between new active cohort and quarantine manifests."""
        df_new = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")
        df_quar = pd.read_csv(STAGE40_DIR / "manifests" / "quarantine_manifest.csv")
        self.assertEqual(len(df_quar), 19, "Quarantine manifest must contain exactly 19 records")
        overlap = set(df_new["file_id"]).intersection(set(df_quar["file_id"]))
        self.assertEqual(len(overlap), 0, "Quarantined file present in active evaluation cohort!")

    def test_12_no_hash_collisions(self):
        """12. Zero SHA-256 duplicate collisions within new cohort."""
        df_new = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")
        self.assertEqual(len(df_new["sha256_hash"].unique()), 145, "Duplicate audio files in new cohort!")

    def test_13_license_compliance_commercial_eligibility(self):
        """13. Strict license compliance: zero CC BY-NC licenses in active cohort."""
        df_new = pd.read_csv(STAGE40_DIR / "manifests" / "new_cohort_manifest.csv")
        for _, r in df_new.iterrows():
            lic = str(r["license"]).upper()
            self.assertNotIn("NC", lic, f"Non-commercial license in active evaluation cohort: {r['file_id']}")

    def test_14_wilson_score_interval_math(self):
        """14. Mathematical bounds of 95% Wilson score confidence intervals."""
        from backend.research.stage_8_9_40.scripts.evaluate_frozen_models import wilson_score_interval
        # Edge cases
        p, low, high = wilson_score_interval(0, 100)
        self.assertEqual(p, 0.0)
        self.assertAlmostEqual(low, 0.0, places=5)
        self.assertGreater(high, 0.0)
        p, low, high = wilson_score_interval(100, 100)
        self.assertEqual(p, 1.0)
        self.assertLess(low, 1.0)
        self.assertAlmostEqual(high, 1.0, places=5)

    def test_15_latency_deadlines_and_gate_5(self):
        """15. Audio-hop deadline compliance (100 ms) and Gate 5 (<= 25 ms) verification."""
        results_path = STAGE40_DIR / "results" / "metrics" / "latency_benchmark_results.json"
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Gate 5
        self.assertEqual(data["gate_5_verification"]["candidate_b"]["gate_5_status"], "PASS")
        self.assertEqual(data["gate_5_verification"]["candidate_d"]["gate_5_status"], "PASS")
        self.assertLessEqual(data["gate_5_verification"]["candidate_b"]["forward_pass_p95_ms"], 25.0)
        self.assertLessEqual(data["gate_5_verification"]["candidate_d"]["forward_pass_p95_ms"], 25.0)
        # Config B streaming concurrency across 1, 2, 4, 8 streams
        streams_b = data["concurrent_streaming_verification"]["b"]
        for s_level in ["1_streams", "2_streams", "4_streams", "8_streams"]:
            self.assertEqual(streams_b[s_level]["deadline_misses"], 0, f"Config B deadline miss on {s_level}!")

if __name__ == "__main__":
    unittest.main()
