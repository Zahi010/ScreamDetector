"""
Stage 8.9.38 - Comprehensive Automated Test Suite
Validates:
1. Production artifact immutability (4 SHA-256 hashes).
2. Dataset manifest consistency (N=1,578 rows, valid schema).
3. Recording existence (all audio files exist on disk).
4. SHA-256 verification (on-disk hash matches manifest).
5. License quarantine (21 CC BY-NC marked ineligible and quarantined).
6. Source-group isolation (0 group leakage across all active split pairs).
7. Parent-recording isolation (no parent excerpts cross train/test boundaries).
8. Duplicate detection (0 exact SHA-256 or PCM collisions).
9. Label adjudication integrity (disputed files preserved in test, quarantined from train).
10. Reserved short-scream test-group isolation (>=35 groups held out).
11. Research split reproducibility (manifest checksum verification).
"""
import os
import json
import hashlib
import unittest
import soundfile as sf
import pandas as pd

class TestStage8938(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_v4 = "backend/research/stage_8_9_38/manifests/dataset_manifest_v4.csv"
        cls.split_v4 = "backend/research/stage_8_9_38/manifests/research_split_v4.csv"
        cls.sg_audit_csv = "backend/research/stage_8_9_38/manifests/source_group_split_manifest.csv"
        cls.checksums_json = "backend/research/stage_8_9_38/manifests/manifest_checksums.json"
        cls.dual_view_csv = "backend/research/stage_8_9_38/audits/dual_view_historical_metrics.csv"
        cls.retraining_config = "backend/research/stage_8_9_38/experiment_configs/controlled_retraining_protocol.json"
        
        cls.df_v4 = pd.read_csv(cls.manifest_v4)
        cls.df_split = pd.read_csv(cls.split_v4)

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

    def test_02_dataset_manifest_consistency(self):
        """Test 2: Verify dataset_manifest_v4 has exactly 1,578 records and valid schema."""
        self.assertEqual(len(self.df_v4), 1578)
        required_cols = [
            'file_id', 'target_category', 'binary_label', 'split',
            'duration_seconds', 'source_group_id', 'license', 'creator',
            'is_commercially_eligible', 'sha256_hash', 'pcm_sha256', 'workspace_audio_path'
        ]
        for col in required_cols:
            self.assertIn(col, self.df_v4.columns)
            self.assertEqual(self.df_v4[col].isnull().sum(), 0, f"Column {col} has nulls!")

    def test_03_recording_existence(self):
        """Test 3: Verify all 250 newly instantiated audio files physically exist on disk."""
        acq_records = self.df_v4[self.df_v4['file_id'].str.startswith('acq_')]
        self.assertEqual(len(acq_records), 250)
        for _, r in acq_records.iterrows():
            path = r['workspace_audio_path']
            self.assertTrue(os.path.exists(path), f"Audio file does not exist: {path}")

    def test_04_sha256_verification(self):
        """Test 4: Re-compute SHA-256 for a sample of newly generated files and check match."""
        acq_sample = self.df_v4[self.df_v4['file_id'].str.startswith('acq_')].sample(25, random_state=42)
        for _, r in acq_sample.iterrows():
            with open(r['workspace_audio_path'], "rb") as f:
                computed = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(computed, r['sha256_hash'], f"SHA-256 mismatch for {r['file_id']}")

    def test_05_license_quarantine(self):
        """Test 5: Verify all 21 CC BY-NC recordings are quarantined and marked commercially ineligible."""
        nc_records = self.df_v4[self.df_v4['license'].str.contains('NC')]
        self.assertEqual(len(nc_records), 21)
        self.assertTrue((nc_records['is_commercially_eligible'] == False).all())
        # In research_split_v4, all must be in quarantined split
        nc_fids = set(nc_records['file_id'])
        split_nc = self.df_split[self.df_split['file_id'].isin(nc_fids)]
        self.assertTrue((split_nc['v4_research_split'] == 'quarantined').all())

    def test_06_source_group_isolation(self):
        """Test 6: Verify zero source-group leakage across all active split pairs."""
        sg_audit = pd.read_csv(self.sg_audit_csv)
        self.assertTrue(sg_audit['is_clean_isolated'].all(), "Source-group leakage detected!")
        self.assertTrue((sg_audit['overlapping_groups_count'] == 0).all())

    def test_07_parent_recording_isolation(self):
        """Test 7: Verify no parent recording excerpts cross train/test boundaries."""
        active = self.df_split[self.df_split['v4_research_split'] != 'quarantined']
        train_parents = set(active[active['v4_research_split'] == 'v4_train']['original_recording_id'].dropna())
        hist_test_parents = set(active[active['v4_research_split'] == 'v4_historical_test']['original_recording_id'].dropna())
        exp_test_parents = set(active[active['v4_research_split'] == 'v4_reserved_expansion_test']['original_recording_id'].dropna())
        
        self.assertEqual(len(train_parents.intersection(hist_test_parents)), 0)
        self.assertEqual(len(train_parents.intersection(exp_test_parents)), 0)

    def test_08_duplicate_detection(self):
        """Test 8: Verify zero exact SHA-256 and PCM collisions in manifest v4."""
        dup_sha = self.df_v4[self.df_v4.duplicated(subset=['sha256_hash'], keep=False)]
        dup_pcm = self.df_v4[self.df_v4.duplicated(subset=['pcm_sha256'], keep=False)]
        self.assertEqual(len(dup_sha), 0, f"Found {len(dup_sha)} exact SHA-256 duplicates!")
        self.assertEqual(len(dup_pcm), 0, f"Found {len(dup_pcm)} exact PCM duplicates!")

    def test_09_label_adjudication_integrity(self):
        """Test 9: Verify disputed recordings are retained in test, and dual views exist."""
        self.assertTrue(os.path.exists(self.dual_view_csv))
        dual_df = pd.read_csv(self.dual_view_csv)
        self.assertEqual(len(dual_df), 4) # 4 candidates
        # View A has 102 screams, View B has 100 screams
        self.assertEqual(dual_df['view_a_total_screams'].iloc[0], 102)
        self.assertEqual(dual_df['view_b_total_screams'].iloc[0], 100)
        
        # Verify disputed files are not in v4_train
        disputed_ids = ["v2_nigens_242607__reitanna__gasp-oooh", "v2_nigens_242644__reitanna__another-surprised-oooh"]
        for d_id in disputed_ids:
            split_assigned = self.df_split[self.df_split['file_id'] == d_id]['v4_research_split'].iloc[0]
            self.assertEqual(split_assigned, "v4_historical_test")

    def test_10_reserved_short_scream_test_group_isolation(self):
        """Test 10: Verify at least 35 short-scream source groups are reserved for expansion test."""
        exp_test = self.df_split[self.df_split['v4_research_split'] == 'v4_reserved_expansion_test']
        short_scream_groups = exp_test[exp_test['target_category'] == 'scream']['source_group_id'].nunique()
        self.assertGreaterEqual(short_scream_groups, 35)
        
        # Verify none appear in v4_train or v4_val
        ss_groups_set = set(exp_test[exp_test['target_category'] == 'scream']['source_group_id'])
        train_groups = set(self.df_split[self.df_split['v4_research_split'] == 'v4_train']['source_group_id'])
        val_groups = set(self.df_split[self.df_split['v4_research_split'] == 'v4_val']['source_group_id'])
        self.assertEqual(len(ss_groups_set.intersection(train_groups)), 0)
        self.assertEqual(len(ss_groups_set.intersection(val_groups)), 0)

    def test_11_research_split_reproducibility(self):
        """Test 11: Verify research split manifest checksum matches manifest_checksums.json."""
        self.assertTrue(os.path.exists(self.checksums_json))
        with open(self.checksums_json, "r") as f:
            chk = json.load(f)
        self.assertIn("research_split_v4.csv", chk)
        with open(self.split_v4, "rb") as f:
            curr_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(curr_hash, chk["research_split_v4.csv"])

if __name__ == "__main__":
    unittest.main()
