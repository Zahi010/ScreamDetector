# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.67 Verification Test Suite.
Validates:
1. Production asset hashes (4 protected assets).
2. Historical benchmark hashes (Candidate 65-F, C5 DSP).
3. Sealed evaluation cohort isolation (zero leakage).
4. Stage 54 and Stage 64 dataset partition source-group independence.
5. C5 DSP + Vocal Feature extraction consistency.
6. Candidate 67-D model checkpoint, metadata, and weights integrity.
7. Five-gate performance scorecard (Gate 3 shouted FPR <= 15.0%, Gate 4 short recall >= 90.0%, Gate 5 latency <= 25.0ms).
8. Backend research service and API route functionality.
9. Mandatory safety designation on all stage deliverables.
"""

import os
import json
import hashlib
import numpy as np
import pandas as pd
import pytest
import torch

from src.research_service import get_research_service, ResearchModelId
from research.stage_8_9_67.scripts.extract_and_cache_features import extract_vocal_acoustic_features
from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)

STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.abspath(os.path.join(STAGE_DIR, "..", ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# 1. Protected Baseline Production Asset Integrity
# ==============================================================================

class TestProductionAssetIntegrity:
    """Verifies that none of the 4 protected baseline assets have been modified."""

    def test_production_classifier_joblib_hash(self):
        path = os.path.join(BACKEND_DIR, "models", "scream_classifier.joblib")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"
        assert sha256_file(path) == expected, "Production scream_classifier.joblib was modified!"

    def test_production_metadata_json_hash(self):
        path = os.path.join(BACKEND_DIR, "models", "model_metadata.json")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"
        assert sha256_file(path) == expected, "Production model_metadata.json was modified!"

    def test_production_test_predictions_csv_hash(self):
        path = os.path.join(BACKEND_DIR, "reports", "test_predictions.csv")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"
        assert sha256_file(path) == expected, "Production test_predictions.csv was modified!"

    def test_production_stage5_test_evaluation_md_hash(self):
        path = os.path.join(BACKEND_DIR, "reports", "stage5_test_evaluation.md")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
        assert sha256_file(path) == expected, "Production stage5_test_evaluation.md was modified!"


# ==============================================================================
# 2. Historical Benchmark & Sealed Cohort Integrity
# ==============================================================================

class TestHistoricalAndSealedCohorts:
    """Verifies Candidate 65-F checkpoint and ensures Sealed Cohort isolation."""

    def test_candidate_65f_frozen_checkpoint_hash(self):
        path = os.path.join(BACKEND_DIR, "research", "stage_8_9_66", "models", "candidate_65f_frozen.pt")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab"
        assert sha256_file(path) == expected, "Historical Candidate 65-F checkpoint was modified!"

    def test_c5_dsp_reference_hash(self):
        path = os.path.join(BACKEND_DIR, "research", "stage_8_9_57", "dsp_implementations", "c5_combined.py")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"
        assert sha256_file(path) == expected, "C5 DSP reference was modified!"

    def test_sealed_evaluation_cohort_manifest_hash(self):
        path = os.path.join(BACKEND_DIR, "research", "stage_8_9_60", "future_evaluation_manifest.json")
        assert os.path.exists(path), f"Missing: {path}"
        expected = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
        assert sha256_file(path) == expected, "Stage 60 sealed evaluation manifest was modified!"

    def test_sealed_evaluation_cohort_zero_leakage(self):
        """Verify no files in stage 54 training/validation partitions appear in sealed manifest."""
        manifest_path = os.path.join(BACKEND_DIR, "research", "stage_8_9_60", "future_evaluation_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            sealed_data = json.load(f)

        sealed_filenames = set()
        for item in sealed_data.get("recordings", []):
            fn = os.path.basename(item.get("workspace_audio_path", ""))
            if fn:
                sealed_filenames.add(fn)

        p_csv = os.path.join(BACKEND_DIR, "research", "stage_8_9_54", "dataset", "partition_manifest_verified.csv")
        df_p = pd.read_csv(p_csv)
        stage54_filenames = set(df_p["workspace_audio_path"].apply(os.path.basename))

        intersection = sealed_filenames.intersection(stage54_filenames)
        assert len(intersection) == 0, f"Leaked {len(intersection)} files between Stage 54 and Sealed Cohort: {list(intersection)[:5]}"


# ==============================================================================
# 3. Source-Group Independence & Dataset Auditing
# ==============================================================================

class TestDatasetPartitionIndependence:
    """Verifies strict source-group disjointness across all evaluation splits."""

    def test_stage54_train_val_source_group_disjointness(self):
        p_csv = os.path.join(BACKEND_DIR, "research", "stage_8_9_54", "dataset", "partition_manifest_verified.csv")
        df = pd.read_csv(p_csv)

        train_groups = set(df[df["expansion_partition"] == "expansion_train"]["source_group_id"].unique())
        val_groups = set(df[df["expansion_partition"] == "expansion_val"]["source_group_id"].unique())

        overlap = train_groups.intersection(val_groups)
        assert len(overlap) == 0, f"Train and Val share {len(overlap)} source groups: {overlap}"

    def test_stage54_val_class_distribution(self):
        p_csv = os.path.join(BACKEND_DIR, "research", "stage_8_9_54", "dataset", "partition_manifest_verified.csv")
        df = pd.read_csv(p_csv)
        val_df = df[df["expansion_partition"] == "expansion_val"]

        assert len(val_df) == 311
        screams = len(val_df[val_df["binary_label"] == 1])
        shouts = len(val_df[val_df["target_category"] == "shouting_and_speech"])
        hard_neg = len(val_df[(val_df["binary_label"] == 0) & (val_df["target_category"] != "shouting_and_speech")])

        assert screams == 99
        assert shouts == 88
        assert hard_neg == 124

    def test_held_out_short_scream_source_groups(self):
        ho_npz = os.path.join(STAGE_DIR, "cache", "held_out_short_features.npz")
        assert os.path.exists(ho_npz)
        data = np.load(ho_npz)
        assert len(data["y"]) == 268
        assert len(np.unique(data["source_groups"])) == 7


# ==============================================================================
# 4. DSP & Vocal Feature Extraction Consistency
# ==============================================================================

class TestVocalFeatureExtraction:
    """Tests the mathematical correctness and stability of novel vocal discriminability features."""

    def test_extract_vocal_features_silence(self):
        silence = np.zeros(4000, dtype=np.float32)
        feats = extract_vocal_acoustic_features(silence, 16000)
        assert len(feats) == 5
        assert np.isclose(feats[0], 0.0)

    def test_extract_vocal_features_modulated_tone(self):
        # 70 Hz amplitude modulation on 1000 Hz carrier (roughness range 30-150 Hz)
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        carrier = np.sin(2 * np.pi * 1000 * t)
        modulator = 0.5 * (1.0 + np.sin(2 * np.pi * 70 * t))
        signal_mod = (carrier * modulator).astype(np.float32)
        feats = extract_vocal_acoustic_features(signal_mod, 16000)
        assert feats[0] > 0.05, f"Expected noticeable roughness, got {feats[0]}"

    def test_normalize_vocal_features_range(self):
        raw_feats = np.array([
            [1.5, 1e7, 10.0, 5.0, 0.8],
            [0.0, 1e-5, 0.0, 0.0, 0.0]
        ], dtype=np.float32)
        norm_feats = normalize_vocal_features(raw_feats)
        assert not np.isnan(norm_feats).any()
        assert not np.isinf(norm_feats).any()
        assert norm_feats[:, 1].max() <= 1.5
        assert norm_feats[:, 1].min() >= -1.5


# ==============================================================================
# 5. Candidate 67-D Checkpoint & Architecture Integrity
# ==============================================================================

class TestCandidate67DCheckpoint:
    """Verifies Candidate 67-D weights, architecture, and reproducibility."""

    def test_candidate_67_frozen_checkpoint_exists(self):
        ckpt_path = os.path.join(STAGE_DIR, "models", "candidate_67_frozen.pt")
        assert os.path.exists(ckpt_path), f"Missing: {ckpt_path}"
        expected = "8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18"
        assert sha256_file(ckpt_path) == expected, "Candidate 67-D frozen checkpoint modified!"

    def test_candidate_67_metadata_json(self):
        meta_path = os.path.join(STAGE_DIR, "models", "candidate_67_metadata.json")
        assert os.path.exists(meta_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["candidate_id"] == "Candidate_67_Vocal_Augmented_Dual_Resolution"
        assert data["input_features_short"] == 22
        assert data["input_features_sust"] == 22
        assert data["operating_threshold"] == 0.52
        assert data["suppression_heuristics"]["use_selective_veto"] is True
        assert data["suppression_heuristics"]["use_vocal_veto"] is True

    def test_candidate_67_forward_pass_dimensions(self):
        net = DualResolutionGatedModel(in_features=22)
        dummy_s = torch.zeros((4, 22), dtype=torch.float32)
        dummy_l = torch.zeros((4, 22), dtype=torch.float32)
        logits, gate, z_s, z_l = net(dummy_s, dummy_l)
        assert logits.shape == (4,)
        assert gate.shape == (4,)
        assert z_s.shape == (4, 16)
        assert z_l.shape == (4, 16)


# ==============================================================================
# 6. Five-Gate Performance Scorecard Verification
# ==============================================================================

class TestFiveGateScorecard:
    """Verifies the empirical validation performance against the 5 acceptance gates."""

    @pytest.fixture
    def val_preds_df(self):
        csv_path = os.path.join(STAGE_DIR, "reports", "candidate_67_val_predictions.csv")
        assert os.path.exists(csv_path), f"Missing: {csv_path}"
        return pd.read_csv(csv_path)

    def test_gate3_shouted_speech_fpr_recovery(self, val_preds_df):
        """Gate 3: Shouted-speech FPR <= 15.00% (CRITICAL GENERALIZATION RECOVERY)."""
        shouts = val_preds_df[val_preds_df["target_category"] == "shouting_and_speech"]
        assert len(shouts) == 88, f"Expected 88 shouted clips, found {len(shouts)}"
        fps = (shouts["prediction"] == 1).sum()
        fpr = (fps / len(shouts)) * 100.0

        assert fpr <= 15.00, f"Gate 3 FAILED: Shouted FPR was {fpr:.2f}% (> 15.0%)"
        assert np.isclose(fpr, 13.636, atol=0.1)

    def test_gate4_short_scream_recall(self, val_preds_df):
        """Gate 4: Short-scream recall (< 1.0s) >= 90.00%."""
        short_screams = val_preds_df[(val_preds_df["ground_truth"] == 1) & (val_preds_df["duration_seconds"] < 1.0)]
        assert len(short_screams) == 39, f"Expected 39 short screams, found {len(short_screams)}"
        tps = (short_screams["prediction"] == 1).sum()
        recall = (tps / len(short_screams)) * 100.0

        assert recall >= 90.00, f"Gate 4 FAILED: Short scream recall was {recall:.2f}% (< 90.0%)"
        assert np.isclose(recall, 92.307, atol=0.1)

    def test_gate5_neural_p95_latency(self):
        """Gate 5: Neural model-only P95 latency <= 25.0 ms."""
        meta_path = os.path.join(STAGE_DIR, "models", "candidate_67_metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        p95 = data["validation_results_n311"]["p95_latency_ms"]
        assert p95 <= 25.0, f"Gate 5 FAILED: P95 latency was {p95} ms (> 25.0 ms)"
        assert p95 < 2.0, f"Latency unexpectedly high: {p95} ms"

    def test_gate1_overall_recall_honest_failure_reporting(self, val_preds_df):
        """Gate 1: Overall scream recall >= 96.00% (Expected FAIL due to vocal veto selectivity)."""
        screams = val_preds_df[val_preds_df["ground_truth"] == 1]
        assert len(screams) == 99
        tps = (screams["prediction"] == 1).sum()
        recall = (tps / len(screams)) * 100.0

        assert recall < 96.00, f"Gate 1 was expected to fail, got {recall:.2f}%"
        assert np.isclose(recall, 73.737, atol=0.1)

    def test_gate2_hard_negative_fpr_honest_reporting(self, val_preds_df):
        """Gate 2: Hard-negative FPR <= 5.00% (Substantially improved from 59.68% to 8.87%, but fails 5.0%)."""
        negatives = val_preds_df[(val_preds_df["ground_truth"] == 0) & (val_preds_df["target_category"] != "shouting_and_speech")]
        assert len(negatives) == 124
        fps = (negatives["prediction"] == 1).sum()
        fpr = (fps / len(negatives)) * 100.0

        assert fpr > 5.00, f"Gate 2 was expected to be > 5.0%, got {fpr:.2f}%"
        assert fpr < 15.00, f"Expected significant improvement under 15%, got {fpr:.2f}%"
        assert np.isclose(fpr, 8.871, atol=0.1)

    def test_candidate_65f_validation_failure_reproduction(self):
        """Confirms Candidate 65-F fails Gate 2 and Gate 3 on independent validation."""
        csv_path = os.path.join(STAGE_DIR, "reports", "candidate_65f_val_predictions.csv")
        assert os.path.exists(csv_path)
        df_65 = pd.read_csv(csv_path)

        shouts = df_65[df_65["target_category"] == "shouting_and_speech"]
        shout_fpr = (shouts["prediction"] == 1).sum() / len(shouts) * 100.0
        assert shout_fpr > 40.0, f"Candidate 65-F shouted FPR should be > 40%, got {shout_fpr:.2f}%"

        negs = df_65[(df_65["binary_label"] == 0) & (df_65["target_category"] != "shouting_and_speech")]
        neg_fpr = (negs["prediction"] == 1).sum() / len(negs) * 100.0
        assert neg_fpr > 50.0, f"Candidate 65-F hard neg FPR should be > 50%, got {neg_fpr:.2f}%"


# ==============================================================================
# 7. Backend Research Service & API Functionality
# ==============================================================================

class TestBackendResearchService:
    """Verifies the ResearchService singleton and model switching behavior."""

    def test_singleton_retrieval(self):
        svc1 = get_research_service()
        svc2 = get_research_service()
        assert svc1 is svc2

    def test_registered_models(self):
        svc = get_research_service()
        models = svc.list_models()
        assert len(models) == 3
        ids = [m["model_id"] for m in models]
        assert ResearchModelId.PRODUCTION_BASELINE.value in ids
        assert ResearchModelId.CANDIDATE_65F.value in ids
        assert ResearchModelId.CANDIDATE_67_VADF.value in ids

    def test_model_switching(self):
        svc = get_research_service()
        svc.select_model(ResearchModelId.PRODUCTION_BASELINE.value)
        assert svc.get_active_model()["model_id"] == ResearchModelId.PRODUCTION_BASELINE.value

        svc.select_model(ResearchModelId.CANDIDATE_67_VADF.value)
        assert svc.get_active_model()["model_id"] == ResearchModelId.CANDIDATE_67_VADF.value

    def test_inference_audio_array(self):
        svc = get_research_service()
        svc.select_model(ResearchModelId.CANDIDATE_67_VADF.value)
        test_audio = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)

        res = svc.infer_audio_array(test_audio, 16000)
        assert "calibrated_probability" in res
        assert "is_detected" in res
        assert "model_latency_ms" in res
        assert "state" in res
        assert res["model_id"] == ResearchModelId.CANDIDATE_67_VADF.value

    def test_event_history_and_clear(self):
        svc = get_research_service()
        svc.clear_events()
        assert len(svc.get_events()) == 0

        # Simulate event
        test_audio = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)
        svc.infer_audio_array(test_audio, 16000)
        assert len(svc.get_events()) >= 1

        svc.clear_events()
        assert len(svc.get_events()) == 0

    def test_csv_export(self):
        svc = get_research_service()
        test_audio = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)
        svc.infer_audio_array(test_audio, 16000)
        csv_str = svc.export_session_csv()
        assert "timestamp,event_id,model_id" in csv_str


# ==============================================================================
# 8. Deliverable Reports & Mandatory Safety Designation
# ==============================================================================

class TestStageDeliverablesAndSafetyDesignation:
    """Verifies that all 12 stage reports exist and have line 1 safety header."""

    EXPECTED_REPORTS = [
        "stage_8_9_67_completion_report.md",
        "stage_8_9_67_dataset_provenance_report.md",
        "stage_8_9_67_shouted_speech_analysis.md",
        "stage_8_9_67_hard_negative_analysis.md",
        "stage_8_9_67_positive_generalization_report.md",
        "stage_8_9_67_short_scream_report.md",
        "stage_8_9_67_candidate_comparison.md",
        "stage_8_9_67_five_gate_scorecard.md",
        "stage_8_9_67_latency_report.md",
        "stage_8_9_67_dashboard_integration_report.md",
        "stage_8_9_67_production_integrity_report.md",
        "stage_8_9_67_test_report.md",
    ]

    @pytest.mark.parametrize("report_name", EXPECTED_REPORTS)
    def test_report_exists_and_leads_with_mandatory_safety_designation(self, report_name):
        report_path = os.path.join(STAGE_DIR, "reports", report_name)
        assert os.path.exists(report_path), f"Missing required report: {report_path}"

        with open(report_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()

        expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
        assert first_line == expected_header, (
            f"Report {report_name} does not lead with mandatory safety designation! Got: {first_line}"
        )
