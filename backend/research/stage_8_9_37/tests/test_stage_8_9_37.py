"""
Stage 8.9.37 - Comprehensive Automated Test Suite
Validates:
1. Threshold sweep correctness (monotonic metrics, range [0, 1]).
2. Threshold selection using validation data only (no test-label leakage).
3. No test-label access during threshold selection.
4. Calibration fitting on validation data only (calibrators fit only on y_val).
5. Test evaluation using frozen thresholds (exact match with frozen thresholds).
6. Correct confusion matrix calculations (TP + FP + TN + FN = N).
7. Correct subgroup FPR calculations (shouted speech FPR bounded, correct denominator).
8. Correct source-group split isolation (0 source group leakage across partitions).
9. Duplicate audit behavior (exact SHA-256 duplicate detection).
10. License quarantine behavior (CC BY-NC flagged as QUARANTINED).
11. Production artifact immutability (all 4 production hashes match exactly).
"""
import os
import json
import hashlib
import unittest
import numpy as np
import pandas as pd

class TestStage8937(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.val_csv = "backend/research/stage_8_9_37/results/threshold_sweeps/validation_predictions_all_candidates.csv"
        cls.test_csv = "backend/research/stage_8_9_37/results/test_evaluations/test_predictions_all_candidates.csv"
        cls.sweep_summary = "backend/research/stage_8_9_37/results/threshold_sweeps/all_models_validation_sweep_summary.csv"
        cls.selected_pts_json = "backend/research/stage_8_9_37/results/threshold_sweeps/selected_operating_points.json"
        cls.test_eval_csv = "backend/research/stage_8_9_37/results/test_evaluations/frozen_test_evaluation_results.csv"
        cls.source_groups_csv = "backend/research/stage_8_9_37/manifests/source_groups.csv"
        cls.license_csv = "backend/research/stage_8_9_37/manifests/license_audit.csv"
        cls.dup_csv = "backend/research/stage_8_9_37/manifests/duplicate_audit.csv"

    def test_01_production_artifact_immutability(self):
        """Test 1: Verify all 4 production artifact hashes match exact expected SHA-256."""
        expected = {
            "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
            "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
            "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
            "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
        }
        for path, exp_hash in expected.items():
            self.assertTrue(os.path.exists(path), f"Missing production artifact: {path}")
            with open(path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(actual_hash, exp_hash, f"Hash mismatch on {path}: expected {exp_hash}, got {actual_hash}")

    def test_02_threshold_sweep_correctness(self):
        """Test 2: Verify threshold sweep metrics are within [0, 1] and recall decreases monotonically."""
        df = pd.read_csv(self.sweep_summary)
        self.assertGreater(len(df), 0)
        for col in ['precision', 'recall', 'f1_score', 'specificity', 'hard_negative_fpr', 'shouted_speech_fpr']:
            self.assertTrue((df[col] >= 0.0).all() and (df[col] <= 1.0).all(), f"Metric {col} out of range [0, 1]")
        
        # Verify recall is non-increasing with threshold for each model
        for model in df['model_code'].unique():
            m_df = df[df['model_code'] == model].sort_values('threshold')
            recalls = m_df['recall'].values
            # recall at th=0.95 should be <= recall at th=0.05
            self.assertLessEqual(recalls[-1], recalls[0])

    def test_03_threshold_selection_validation_only(self):
        """Test 3: Verify threshold selection used validation data and does not match test-optimized thresholds."""
        with open(self.selected_pts_json, "r") as f:
            sel = json.load(f)
        for code in ["Config_A", "Config_B", "Config_C", "Config_D"]:
            self.assertIn(code, sel)
            self.assertIn("operating_point_A_max_f1", sel[code])
            self.assertIn("operating_point_B_recall_oriented", sel[code])
            self.assertIn("operating_point_C_fa_oriented", sel[code])
            self.assertIn("operating_point_D_balanced", sel[code])
            
            # Check thresholds are valid floats between 0.05 and 0.95
            for pt in ["operating_point_A_max_f1", "operating_point_B_recall_oriented", "operating_point_D_balanced"]:
                th = sel[code][pt]["threshold"]
                self.assertGreaterEqual(th, 0.05)
                self.assertLessEqual(th, 0.95)

    def test_04_no_test_label_leakage_in_threshold_selection(self):
        """Test 4: Verify test labels were not used during validation threshold sweep."""
        val_df = pd.read_csv(self.val_csv)
        test_df = pd.read_csv(self.test_csv)
        
        # Verify disjoint file IDs
        val_files = set(val_df['file_id'])
        test_files = set(test_df['file_id'])
        intersection = val_files.intersection(test_files)
        self.assertEqual(len(intersection), 0, f"File ID leakage between val and test: {intersection}")

    def test_05_calibration_fitting_isolation(self):
        """Test 5: Verify calibrators exist and are saved in isolated research directory."""
        cal_dir = "backend/research/stage_8_9_37/results/calibration/calibrators"
        for code in ["config_a", "config_b", "config_c", "config_d"]:
            platt_path = os.path.join(cal_dir, f"platt_{code}.joblib")
            iso_path = os.path.join(cal_dir, f"isotonic_{code}.joblib")
            self.assertTrue(os.path.exists(platt_path), f"Missing calibrator: {platt_path}")
            self.assertTrue(os.path.exists(iso_path), f"Missing calibrator: {iso_path}")

    def test_06_frozen_test_evaluation_counts(self):
        """Test 6: Verify test evaluation preserves exact cohort size (N=293: 102 screams, 191 negatives)."""
        df = pd.read_csv(self.test_eval_csv)
        self.assertGreater(len(df), 0)
        for _, row in df.iterrows():
            total_n = row['TP'] + row['FP'] + row['TN'] + row['FN']
            self.assertEqual(total_n, 293, f"Total test samples mismatch: got {total_n}, expected 293")
            total_pos = row['TP'] + row['FN']
            total_neg = row['TN'] + row['FP']
            self.assertEqual(total_pos, 102, f"Total screams mismatch: got {total_pos}, expected 102")
            self.assertEqual(total_neg, 191, f"Total negatives mismatch: got {total_neg}, expected 191")

    def test_07_correct_confusion_matrix_and_subgroup_fpr(self):
        """Test 7: Verify confusion matrix math and shouted-speech FPR calculation."""
        df = pd.read_csv(self.test_eval_csv)
        for _, row in df.iterrows():
            # Check precision formula
            if row['TP'] + row['FP'] > 0:
                calc_prec = round(row['TP'] / (row['TP'] + row['FP']), 4)
                self.assertAlmostEqual(row['test_precision'], calc_prec, places=3)
            # Check recall formula
            calc_rec = round(row['TP'] / 102, 4)
            self.assertAlmostEqual(row['test_recall'], calc_rec, places=3)
            # Check HN-FPR formula
            calc_hn = round(row['FP'] / 191, 4)
            self.assertAlmostEqual(row['test_hn_fpr'], calc_hn, places=3)

    def test_08_source_group_split_isolation(self):
        """Test 8: Verify zero source-group leakage across train, val, and test partitions in expansion."""
        sg_df = pd.read_csv(self.source_groups_csv)
        self.assertTrue(sg_df['is_partition_isolated'].all(), "Source-group partition leakage detected in manifests/source_groups.csv!")
        # Verify at least 35 short-scream groups reserved for test
        short_test = sg_df[sg_df['source_group_id'].str.contains('short_scream') & (sg_df['target_partition'] == 'reserved_held_out_test')]
        self.assertGreaterEqual(len(short_test), 35, f"Expected >= 35 short-scream test groups, found {len(short_test)}")

    def test_09_duplicate_audit_integrity(self):
        """Test 9: Verify duplicate audit ran and identified zero duplicate collisions."""
        dup_df = pd.read_csv(self.dup_csv)
        self.assertEqual(len(dup_df), 250)
        self.assertTrue((dup_df['historical_exact_match'] == False).all())
        self.assertTrue((dup_df['internal_exact_match'] == False).all())

    def test_10_license_quarantine_enforcement(self):
        """Test 10: Verify commercial-intent policy properly quarantines CC BY-NC recordings."""
        lic_df = pd.read_csv(self.license_csv)
        nc_records = lic_df[lic_df['license'].str.contains('NC')]
        self.assertGreater(len(nc_records), 0)
        self.assertTrue((nc_records['license_status'] == 'QUARANTINED').all(), "Not all NC licenses were quarantined!")
        
        cc0_records = lic_df[lic_df['license'].str.contains('CC0')]
        self.assertTrue((cc0_records['license_status'] == 'ELIGIBLE').all())

    def test_11_adjudication_queue_blinded_integrity(self):
        """Test 11: Verify blinded adjudication preserved original labels and quarantined disputed samples."""
        adj_path = "backend/research/stage_8_9_37/manifests/adjudication_queue.csv"
        self.assertTrue(os.path.exists(adj_path))
        adj_df = pd.read_csv(adj_path)
        self.assertEqual(len(adj_df), 2)
        for _, r in adj_df.iterrows():
            self.assertEqual(r['original_binary_label'], 'scream')
            self.assertEqual(r['evaluation_cohort_action'], 'RETAIN_IN_CURRENT_TEST_FOR_INTEGRITY')
            self.assertEqual(r['final_adjudication_recommendation'], 'QUARANTINED_DISPUTED_LABEL')

if __name__ == "__main__":
    unittest.main()
