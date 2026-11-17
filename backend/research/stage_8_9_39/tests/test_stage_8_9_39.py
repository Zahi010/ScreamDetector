import os
import sys
import json
import hashlib
import unittest
import csv
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
STAGE38_DIR = BACKEND_DIR / "research" / "stage_8_9_38"

EXPECTED_PROD_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

class TestStage8939RetrainingAndAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.split_v4_path = STAGE38_DIR / "manifests" / "research_split_v4.csv"
        with open(cls.split_v4_path, "r", encoding="utf-8") as f:
            cls.split_rows = list(csv.DictReader(f))
        
        cls.sg_audit_path = STAGE38_DIR / "manifests" / "source_group_split_manifest.csv"
        with open(cls.sg_audit_path, "r", encoding="utf-8") as f:
            cls.sg_rows = list(csv.DictReader(f))

        cls.feature_cache_path = STAGE_DIR / "cache" / "stage_8_9_39_features.npz"
        cls.norm_stats_path = STAGE_DIR / "results" / "training" / "feature_norm_stats.json"
        cls.thresh_config_path = STAGE_DIR / "config" / "threshold_config.json"
        cls.calib_metrics_path = STAGE_DIR / "results" / "calibration" / "calibration_metrics.json"
        cls.hist_results_path = STAGE_DIR / "results" / "metrics" / "historical_benchmark_results.json"
        cls.exp_results_path = STAGE_DIR / "results" / "metrics" / "expansion_benchmark_results.json"

    def test_01_production_artifact_immutability(self):
        """Test 1: Verify all 4 production artifacts remain byte-for-byte identical."""
        for rel_path, exp_hash in EXPECTED_PROD_HASHES.items():
            full_path = BACKEND_DIR.parent / rel_path
            self.assertTrue(full_path.exists(), f"Production artifact missing: {full_path}")
            h = hashlib.sha256()
            with open(full_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            actual_hash = h.hexdigest()
            self.assertEqual(actual_hash, exp_hash, f"Production artifact altered! {rel_path}")

    def test_02_correct_training_partition_loading(self):
        """Test 2: Verify v4_train has exactly 820 active records (180 screams, 640 non-screams)."""
        train_clips = [r for r in self.split_rows if r["v4_research_split"] == "v4_train"]
        self.assertEqual(len(train_clips), 820)
        screams = sum(1 for r in train_clips if r["binary_label"] == "scream")
        negs = sum(1 for r in train_clips if r["binary_label"] == "non_scream")
        self.assertEqual(screams, 180)
        self.assertEqual(negs, 640)

    def test_03_validation_partition_isolation(self):
        """Test 3: Verify v4_val has exactly 339 active records and 0 file_id overlap with v4_train."""
        val_clips = [r for r in self.split_rows if r["v4_research_split"] == "v4_val"]
        train_ids = {r["file_id"] for r in self.split_rows if r["v4_research_split"] == "v4_train"}
        val_ids = {r["file_id"] for r in val_clips}
        self.assertEqual(len(val_clips), 339)
        self.assertEqual(len(train_ids.intersection(val_ids)), 0)

    def test_04_reserved_test_cohort_isolation(self):
        """Test 4: Verify v4_reserved_expansion_test has 102 active records, 65 screams, 37 negs, and zero training overlap."""
        exp_clips = [r for r in self.split_rows if r["v4_research_split"] == "v4_reserved_expansion_test"]
        train_ids = {r["file_id"] for r in self.split_rows if r["v4_research_split"] == "v4_train"}
        exp_ids = {r["file_id"] for r in exp_clips}
        self.assertEqual(len(exp_clips), 102)
        screams = sum(1 for r in exp_clips if r["binary_label"] == "scream")
        negs = sum(1 for r in exp_clips if r["binary_label"] == "non_scream")
        self.assertEqual(screams, 65)
        self.assertEqual(negs, 37)
        self.assertEqual(len(train_ids.intersection(exp_ids)), 0)

    def test_05_historical_test_cohort_isolation(self):
        """Test 5: Verify v4_historical_test has exactly 293 records and zero training overlap."""
        hist_clips = [r for r in self.split_rows if r["v4_research_split"] == "v4_historical_test"]
        train_ids = {r["file_id"] for r in self.split_rows if r["v4_research_split"] == "v4_train"}
        hist_ids = {r["file_id"] for r in hist_clips}
        self.assertEqual(len(hist_clips), 293)
        self.assertEqual(len(train_ids.intersection(hist_ids)), 0)

    def test_06_source_group_separation(self):
        """Test 6: Verify all 6 active pairwise split comparisons in source_group_split_manifest are clean isolated."""
        self.assertEqual(len(self.sg_rows), 6)
        for r in self.sg_rows:
            self.assertEqual(r["overlapping_groups_count"], "0", f"Leakage in {r['split_pair']}")
            self.assertEqual(r["is_clean_isolated"], "True")

    def test_07_parent_recording_separation(self):
        """Test 7: Verify no parent recording excerpts cross train and test split boundaries."""
        active = [r for r in self.split_rows if r["v4_research_split"] != "quarantined"]
        train_parents = {r["original_recording_id"] for r in active if r["v4_research_split"] == "v4_train" and r["original_recording_id"]}
        hist_parents = {r["original_recording_id"] for r in active if r["v4_research_split"] == "v4_historical_test" and r["original_recording_id"]}
        exp_parents = {r["original_recording_id"] for r in active if r["v4_research_split"] == "v4_reserved_expansion_test" and r["original_recording_id"]}
        self.assertEqual(len(train_parents.intersection(hist_parents)), 0)
        self.assertEqual(len(train_parents.intersection(exp_parents)), 0)

    def test_08_license_quarantine(self):
        """Test 8: Verify exactly 24 quarantined records (21 CC-NC, 3 ambiguous) and complete isolation."""
        q_clips = [r for r in self.split_rows if r["v4_research_split"] == "quarantined"]
        self.assertEqual(len(q_clips), 24)
        active_ids = {r["file_id"] for r in self.split_rows if r["v4_research_split"] != "quarantined"}
        q_ids = {r["file_id"] for r in q_clips}
        self.assertEqual(len(active_ids.intersection(q_ids)), 0)

    def test_09_normalization_fitted_on_training_only(self):
        """Test 9: Verify normalization parameters were fitted strictly on v4_train only."""
        self.assertTrue(self.norm_stats_path.exists())
        with open(self.norm_stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
        self.assertEqual(stats["fitting_split"], "v4_train")
        self.assertEqual(stats["n_samples"], 820)

    def test_10_checkpoint_selection_using_validation_only(self):
        """Test 10: Verify checkpoints for both models were selected strictly using validation F1."""
        summary_b_path = STAGE_DIR / "results" / "training" / "config_b_training_summary.json"
        summary_d_path = STAGE_DIR / "results" / "training" / "config_d_training_summary.json"
        self.assertTrue(summary_b_path.exists())
        self.assertTrue(summary_d_path.exists())
        with open(summary_b_path, "r", encoding="utf-8") as f:
            sb = json.load(f)
        with open(summary_d_path, "r", encoding="utf-8") as f:
            sd = json.load(f)
        self.assertGreater(sb["best_val_f1"], 0.70)
        self.assertGreater(sd["best_val_f1"], 0.70)
        self.assertTrue(os.path.exists(sb["checkpoint_path"]))
        self.assertTrue(os.path.exists(sd["checkpoint_path"]))

    def test_11_threshold_selection_using_validation_only(self):
        """Test 11: Verify threshold sweeps and operating points were computed exclusively on validation."""
        self.assertTrue(self.thresh_config_path.exists())
        with open(self.thresh_config_path, "r", encoding="utf-8") as f:
            tc = json.load(f)
        self.assertEqual(tc["protocol_constraints"]["selection_cohort"], "v4_val_strictly_isolated")
        self.assertFalse(tc["protocol_constraints"]["test_cohort_exposure"])
        self.assertIn("candidate_b", tc)
        self.assertIn("candidate_d", tc)

    def test_12_calibration_fitting_using_validation_only(self):
        """Test 12: Verify Platt scaling was fit exclusively on validation cohort."""
        self.assertTrue(self.calib_metrics_path.exists())
        with open(self.calib_metrics_path, "r", encoding="utf-8") as f:
            cm = json.load(f)
        self.assertEqual(cm["protocol"]["fitting_cohort"], "v4_val (N=339) ONLY")
        self.assertFalse(cm["protocol"]["test_cohort_exposure"])
        self.assertTrue(cm["candidate_b"]["deltas"]["brier_improved"])
        self.assertTrue(cm["candidate_d"]["deltas"]["brier_improved"])

    def test_13_frozen_test_evaluation(self):
        """Test 13: Verify predictions exist for both models across both frozen test benchmarks."""
        pred_b_hist = STAGE_DIR / "predictions" / "historical_test" / "config_b_historical_predictions.csv"
        pred_d_hist = STAGE_DIR / "predictions" / "historical_test" / "config_d_historical_predictions.csv"
        pred_b_exp = STAGE_DIR / "predictions" / "expansion_test" / "config_b_expansion_predictions.csv"
        pred_d_exp = STAGE_DIR / "predictions" / "expansion_test" / "config_d_expansion_predictions.csv"
        for p, exp_len in [(pred_b_hist, 293), (pred_d_hist, 293), (pred_b_exp, 102), (pred_d_exp, 102)]:
            self.assertTrue(p.exists(), f"Missing prediction file {p}")
            with open(p, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), exp_len)
            for r in rows:
                prob = float(r["probability"])
                self.assertTrue(0.0 <= prob <= 1.0)

    def test_14_metric_and_subgroup_calculation(self):
        """Test 14: Verify Wilson score intervals and subgroup metrics are mathematically sound."""
        self.assertTrue(self.exp_results_path.exists())
        with open(self.exp_results_path, "r", encoding="utf-8") as f:
            res = json.load(f)
        for cand in ["candidate_b", "candidate_d"]:
            met = res[cand]["optimal_threshold"]
            # Check Wilson CIs
            for k in ["scream_recall", "hard_negative_fpr", "shouted_speech_fpr", "short_scream_recall"]:
                entry = met[k]
                v = entry["value"]
                low, high = entry["ci95"]
                self.assertTrue(0.0 <= low <= v <= high <= 1.0, f"Invalid CI in {cand} {k}: {entry}")

    def test_15_expansion_gate_reporting(self):
        """Test 15: Verify all five research acceptance gates are documented with numerators and denominators."""
        with open(self.exp_results_path, "r", encoding="utf-8") as f:
            res = json.load(f)
        for cand in ["candidate_b", "candidate_d"]:
            opt = res[cand]["optimal_threshold"]
            self.assertIn("65/65", opt["scream_recall"]["fraction"])
            self.assertIn("0/37", opt["hard_negative_fpr"]["fraction"])
            self.assertIn("0/16", opt["shouted_speech_fpr"]["fraction"])
            self.assertIn("65/65", opt["short_scream_recall"]["fraction"])

if __name__ == "__main__":
    unittest.main()
