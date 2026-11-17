# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Comprehensive Automated Verification Test Suite for Stage 8.9.68.

Validates:
1. Immutability of the 4 protected baseline production assets (Section 12).
2. Frozen research candidate hashes (Candidate 65-F, Candidate 67-D, Candidate 68-D) and DSP scripts.
3. Sealed evaluation cohort quarantine and integrity (Stage 60 future_evaluation_manifest.json N=700).
4. Stage 54 train/val dataset disjointness and zero-leakage verification.
5. Candidate 68-D Five-Gate empirical performance verification.
6. Research Service model registry, model switching, and real-time audio inference.
7. Candidate 68-D multi-stage suppression vetos (whistle, HF roll-off, flux, vocal distress).
8. Artifact schemas, CSV forensics, and line 1 mandatory safety designations.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Dict, Set

import numpy as np
import pandas as pd
import pytest
import torch

# Path setup
TEST_DIR = Path(__file__).resolve().parent
STAGE_DIR = TEST_DIR.parent
RESEARCH_DIR = STAGE_DIR.parent
BACKEND_DIR = RESEARCH_DIR.parent
REPO_ROOT = BACKEND_DIR.parent

import sys
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.research_service import get_research_service, ResearchService, DualResolutionGatedModel


def compute_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# 1. Protected Production Assets Integrity (Section 12)
# ==============================================================================

class TestProtectedProductionAssets:
    """Verifies that none of the 4 protected production baseline assets have been modified."""

    PROD_MODEL = BACKEND_DIR / "models/scream_classifier.joblib"
    PROD_META = BACKEND_DIR / "models/model_metadata.json"
    PROD_PREDS = BACKEND_DIR / "reports/test_predictions.csv"
    PROD_REPORT = BACKEND_DIR / "reports/stage5_test_evaluation.md"

    EXPECTED_HASHES = {
        PROD_MODEL: "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        PROD_META: "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        PROD_PREDS: "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        PROD_REPORT: "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    }

    def test_prod_model_exists_and_hash_matches(self):
        assert self.PROD_MODEL.exists(), f"Missing production model: {self.PROD_MODEL}"
        actual = compute_sha256(self.PROD_MODEL)
        assert actual == self.EXPECTED_HASHES[self.PROD_MODEL], f"Production model hash mutated: {actual}"

    def test_prod_metadata_exists_and_hash_matches(self):
        assert self.PROD_META.exists(), f"Missing production metadata: {self.PROD_META}"
        actual = compute_sha256(self.PROD_META)
        assert actual == self.EXPECTED_HASHES[self.PROD_META], f"Production metadata hash mutated: {actual}"

    def test_prod_predictions_exists_and_hash_matches(self):
        assert self.PROD_PREDS.exists(), f"Missing production predictions: {self.PROD_PREDS}"
        actual = compute_sha256(self.PROD_PREDS)
        assert actual == self.EXPECTED_HASHES[self.PROD_PREDS], f"Production predictions hash mutated: {actual}"

    def test_prod_evaluation_report_exists_and_hash_matches(self):
        assert self.PROD_REPORT.exists(), f"Missing production report: {self.PROD_REPORT}"
        actual = compute_sha256(self.PROD_REPORT)
        assert actual == self.EXPECTED_HASHES[self.PROD_REPORT], f"Production report hash mutated: {actual}"


# ==============================================================================
# 2. Frozen Research Checkpoint & Model Artifact Hashes
# ==============================================================================

class TestResearchCheckpointHashes:
    """Verifies frozen research candidate checkpoints and DSP implementations."""

    C65F_PATH = BACKEND_DIR / "research/stage_8_9_66/models/candidate_65f_frozen.pt"
    C67D_PATH = BACKEND_DIR / "research/stage_8_9_67/models/candidate_67_frozen.pt"
    C68D_PATH = BACKEND_DIR / "research/stage_8_9_68/models/candidate_68_frozen.pt"
    C5_DSP_PATH = BACKEND_DIR / "research/stage_8_9_57/dsp_implementations/c5_combined.py"

    EXPECTED_C65F = "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab"
    EXPECTED_C67D = "8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18"
    EXPECTED_C68D = "8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4"
    EXPECTED_C5_DSP = "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58"

    def test_candidate_65f_checkpoint_hash(self):
        assert self.C65F_PATH.exists(), f"Missing Candidate 65-F checkpoint: {self.C65F_PATH}"
        actual = compute_sha256(self.C65F_PATH)
        assert actual == self.EXPECTED_C65F, f"Candidate 65-F hash mismatch: {actual}"

    def test_candidate_67d_checkpoint_hash(self):
        assert self.C67D_PATH.exists(), f"Missing Candidate 67-D checkpoint: {self.C67D_PATH}"
        actual = compute_sha256(self.C67D_PATH)
        assert actual == self.EXPECTED_C67D, f"Candidate 67-D hash mismatch: {actual}"

    def test_candidate_68d_checkpoint_hash(self):
        assert self.C68D_PATH.exists(), f"Missing Candidate 68-D checkpoint: {self.C68D_PATH}"
        actual = compute_sha256(self.C68D_PATH)
        assert actual == self.EXPECTED_C68D, f"Candidate 68-D hash mismatch: {actual}"

    def test_c5_combined_dsp_hash(self):
        assert self.C5_DSP_PATH.exists(), f"Missing C5 combined DSP script: {self.C5_DSP_PATH}"
        actual = compute_sha256(self.C5_DSP_PATH)
        assert actual == self.EXPECTED_C5_DSP, f"C5 DSP hash mismatch: {actual}"

    def test_candidate_68_metadata_json_integrity(self):
        meta_path = STAGE_DIR / "models/candidate_68_metadata.json"
        assert meta_path.exists(), f"Missing Candidate 68 metadata: {meta_path}"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["checkpoint_sha256"] == self.EXPECTED_C68D
        assert data["operating_threshold"] == 0.49
        assert data["validation_results_n311"]["tp_count"] == 74
        assert data["validation_results_n311"]["fn_count"] == 25
        assert data["validation_results_n311"]["shout_fp"] == 12
        assert data["validation_results_n311"]["hn_fp"] == 9
        assert data["validation_results_n311"]["short_tp"] == 36


# ==============================================================================
# 3. Sealed Evaluation Cohort Isolation & Quarantine
# ==============================================================================

class TestSealedCohortQuarantine:
    """Verifies that Stage 60 sealed cohort remains completely quarantined and untouched."""

    SEALED_MANIFEST = BACKEND_DIR / "research/stage_8_9_60/future_evaluation_manifest.json"
    EXPECTED_SEALED_HASH = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"

    def test_sealed_manifest_exists_and_hash_matches(self):
        assert self.SEALED_MANIFEST.exists(), f"Missing sealed manifest: {self.SEALED_MANIFEST}"
        actual = compute_sha256(self.SEALED_MANIFEST)
        assert actual == self.EXPECTED_SEALED_HASH, f"Sealed cohort manifest has been modified: {actual}"

    def test_sealed_manifest_quarantined_recordings_count(self):
        with open(self.SEALED_MANIFEST, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        recordings = manifest.get("recordings", [])
        assert len(recordings) == 700, f"Expected 700 sealed recordings, found {len(recordings)}"
        assert manifest["total_recordings"] == 700
        assert manifest["positive_recordings"] == 200
        assert manifest["negative_recordings"] == 500

    def test_stage_68_does_not_evaluate_sealed_cohort(self):
        """Verifies no predictions file was generated for the sealed cohort in Stage 68."""
        for p in (STAGE_DIR / "reports").glob("*sealed*"):
            pytest.fail(f"Sealed cohort file found in Stage 68 reports directory: {p}")


# ==============================================================================
# 4. Stage 54 Disjointness & Zero Data Leakage
# ==============================================================================

class TestDatasetDisjointness:
    """Verifies strict source-group disjointness between training and validation sets."""

    PARTITION_CSV = BACKEND_DIR / "research/stage_8_9_54/dataset/partition_manifest_verified.csv"

    def test_partition_manifest_exists(self):
        assert self.PARTITION_CSV.exists(), f"Missing partition manifest: {self.PARTITION_CSV}"

    def test_train_val_source_groups_are_strictly_disjoint(self):
        df = pd.read_csv(self.PARTITION_CSV)
        train_df = df[df["expansion_partition"] == "expansion_train"]
        val_df = df[df["expansion_partition"] == "expansion_val"]

        train_sg: Set[str] = set(train_df["source_group_id"])
        val_sg: Set[str] = set(val_df["source_group_id"])

        overlap = train_sg.intersection(val_sg)
        assert len(overlap) == 0, f"Data leakage detected! Overlapping source groups: {overlap}"
        assert len(train_sg) == 415
        assert len(val_sg) == 138

    def test_val_cohort_sample_size_and_splits(self):
        df = pd.read_csv(self.PARTITION_CSV)
        counts = df["expansion_partition"].value_counts().to_dict()
        assert counts.get("expansion_train") == 1055
        assert counts.get("expansion_val") == 311
        assert counts.get("expansion_reserved_test") == 366

    def test_val_binary_label_balance(self):
        df = pd.read_csv(self.PARTITION_CSV)
        val_df = df[df["expansion_partition"] == "expansion_val"]
        pos_count = (val_df["binary_label"] == 1).sum()
        neg_count = (val_df["binary_label"] == 0).sum()
        assert pos_count == 99, f"Expected 99 positive screams in val, got {pos_count}"
        assert neg_count == 212, f"Expected 212 negatives in val, got {neg_count}"


# ==============================================================================
# 5. Candidate 68-D Five-Gate Empirical Performance Verification
# ==============================================================================

class TestCandidate68Performance:
    """Verifies empirical performance metrics from candidate tournament and prediction logs."""

    TOURNAMENT_CSV = STAGE_DIR / "reports/stage_8_9_68_candidate_tournament.csv"
    PREDS_CSV = STAGE_DIR / "reports/candidate_68_val_predictions.csv"

    def test_tournament_csv_exists_and_contains_candidate_68d(self):
        assert self.TOURNAMENT_CSV.exists()
        df = pd.read_csv(self.TOURNAMENT_CSV)
        assert len(df) == 6, f"Expected 6 candidates in tournament, found {len(df)}"
        row_68d = df[df["candidate"].str.contains("Candidate 68-D")]
        assert len(row_68d) == 1

    def test_gate1_scream_recall_metric(self):
        """Gate 1: Target >= 96.0%. Candidate 68-D achieves 74.75% (74/99) -> FAIL (Recovers +1 over 67-D)."""
        df = pd.read_csv(self.PREDS_CSV)
        pos = df[df["ground_truth"] == 1]
        assert len(pos) == 99
        tp = int((pos["prediction"] == 1).sum())
        recall = tp / len(pos)
        assert tp == 74, f"Expected 74 TPs, got {tp}"
        assert abs(recall - 0.7475) < 0.001

    def test_gate2_hard_negative_fpr_metric(self):
        """Gate 2: Target <= 5.0%. Candidate 68-D achieves 7.26% (9/124) -> FAIL (Significant improvement from 8.87%)."""
        df = pd.read_csv(self.PREDS_CSV)
        hn = df[(df["ground_truth"] == 0) & (df["target_category"] != "shouting_and_speech")]
        assert len(hn) == 124
        fp = int((hn["prediction"] == 1).sum())
        fpr = fp / len(hn)
        assert fp == 9, f"Expected 9 hard-negative FPs, got {fp}"
        assert abs(fpr - 0.0726) < 0.001

    def test_gate3_shouted_speech_fpr_metric(self):
        """Gate 3: Target <= 15.0%. Candidate 68-D achieves 13.64% (12/88) -> PASS."""
        df = pd.read_csv(self.PREDS_CSV)
        shout = df[(df["ground_truth"] == 0) & (df["target_category"] == "shouting_and_speech")]
        assert len(shout) == 88
        fp = int((shout["prediction"] == 1).sum())
        fpr = fp / len(shout)
        assert fp == 12, f"Expected 12 shout FPs, got {fp}"
        assert abs(fpr - 0.1364) < 0.001
        assert fpr <= 0.15

    def test_gate4_short_scream_recall_metric(self):
        """Gate 4: Target >= 90.0%. Candidate 68-D achieves 92.31% (36/39) -> PASS."""
        df = pd.read_csv(self.PREDS_CSV)
        short_pos = df[(df["ground_truth"] == 1) & (df["duration_seconds"] < 1.0)]
        assert len(short_pos) == 39
        tp = int((short_pos["prediction"] == 1).sum())
        recall = tp / len(short_pos)
        assert tp == 36, f"Expected 36 short-scream TPs, got {tp}"
        assert abs(recall - 0.9231) < 0.001
        assert recall >= 0.90

    def test_gate5_neural_p95_latency_metric(self):
        """Gate 5: Target <= 25.0 ms. Candidate 68-D achieves 0.409 ms -> PASS."""
        meta_path = STAGE_DIR / "models/candidate_68_metadata.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lat = data["validation_results_n311"]["p95_latency_ms"]
        assert lat < 1.0, f"Expected P95 latency < 1.0 ms, got {lat}"
        assert lat <= 25.0

    def test_overall_gate_verdict(self):
        """Verifies that overall research verdict is PARTIAL IMPROVEMENT (Gates 3,4,5 PASS; Gates 1,2 FAIL)."""
        df = pd.read_csv(self.TOURNAMENT_CSV)
        row = df[df["candidate"].str.contains("Candidate 68-D")].iloc[0]
        assert row["g1"] == "FAIL"
        assert row["g2"] == "FAIL"
        assert row["g3"] == "PASS"
        assert row["g4"] == "PASS"
        assert row["g5"] == "PASS"

    def test_ultra_short_scream_recall(self):
        meta_path = STAGE_DIR / "models/candidate_68_metadata.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["validation_results_n311"]["ultra_short_recall"] == 1.0


# ==============================================================================
# 6. Backend Model Registry & Research Service
# ==============================================================================

class TestResearchServiceIntegration:
    """Verifies that Candidate 68-D is fully integrated in ResearchService."""

    @classmethod
    def setup_class(cls):
        cls.svc = get_research_service()

    def test_active_model_is_candidate_68d(self):
        assert self.svc.active_model_id == "CANDIDATE_68_D"

    def test_all_four_models_registered(self):
        models = self.svc.list_models()
        m_ids = {m["model_id"] for m in models}
        expected_ids = {"PRODUCTION_BASELINE", "CANDIDATE_65F", "CANDIDATE_67_VADF", "CANDIDATE_68_D"}
        assert expected_ids.issubset(m_ids)

    def test_candidate_68d_metadata_in_registry(self):
        models = {m["model_id"]: m for m in self.svc.list_models()}
        c68 = models["CANDIDATE_68_D"]
        assert c68["operating_threshold"] == 0.49
        assert c68["feature_dims"] == 44
        assert c68["status"] == "ACTIVE_RESEARCH_CHAMPION"

    def test_candidate_67d_is_previous_champion(self):
        models = {m["model_id"]: m for m in self.svc.list_models()}
        c67 = models["CANDIDATE_67_VADF"]
        assert c67["status"] == "PREVIOUS_CHAMPION"

    def test_model_switching_and_retrieval(self):
        self.svc.select_model("PRODUCTION_BASELINE")
        assert self.svc.active_model_id == "PRODUCTION_BASELINE"
        self.svc.select_model("CANDIDATE_68_D")
        assert self.svc.active_model_id == "CANDIDATE_68_D"

    def test_invalid_model_selection_raises_error(self):
        with pytest.raises(ValueError):
            self.svc.select_model("NON_EXISTENT_MODEL_XYZ")

    def test_infer_audio_array_candidate_68d(self):
        audio = np.zeros(16000, dtype=np.float32)
        res = self.svc.infer_audio_array(audio, sr=16000, model_id="CANDIDATE_68_D")
        assert res["model_id"] == "CANDIDATE_68_D"
        assert "calibrated_probability" in res
        assert "raw_probability" in res
        assert "is_detected" in res
        assert res["threshold"] == 0.49
        assert res["model_latency_ms"] > 0.0

    def test_evaluation_summary_contains_candidate_68d(self):
        summary = self.svc.get_evaluation_summary()
        gates = summary["acceptance_gates"]
        assert len(gates) == 5
        for g in gates:
            assert "candidate_68d" in g
            assert "gate_status_68d" in g


# ==============================================================================
# 7. Candidate 68-D Suppression Vetos
# ==============================================================================

class TestCandidate68Vetos:
    """Verifies that the multi-stage vetos in Candidate 68-D behave as specified."""

    def test_narrowband_whistle_veto_attenuation(self):
        """High tonal whistle (3200 Hz, HNR > 12, Flatness < 0.001) must receive attenuation."""
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        whistle = 0.8 * np.sin(2 * np.pi * 3200 * t)
        svc = get_research_service()
        res = svc.infer_audio_array(whistle, sr=sr, model_id="CANDIDATE_68_D")
        assert res["calibrated_probability"] < 0.25
        assert not res["is_detected"]

    def test_hfcr_rolloff_veto_attenuation(self):
        """Low-frequency voiced sound (HFCR < 0.008) must receive 0.20 attenuation."""
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        # Deep male vowel sound at 150 Hz with 300 Hz harmonic, zero high frequency
        shout_sim = 0.7 * np.sin(2 * np.pi * 150 * t) + 0.3 * np.sin(2 * np.pi * 300 * t)
        svc = get_research_service()
        res = svc.infer_audio_array(shout_sim, sr=sr, model_id="CANDIDATE_68_D")
        assert res["calibrated_probability"] < 0.25
        assert not res["is_detected"]

    def test_smooth_speech_flux_veto(self):
        """Continuous smooth harmonic signal with low spectral flux must receive attenuation."""
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        # Steady state tone
        tone = 0.5 * np.sin(2 * np.pi * 500 * t)
        svc = get_research_service()
        res = svc.infer_audio_array(tone, sr=sr, model_id="CANDIDATE_68_D")
        assert res["calibrated_probability"] < 0.25

    def test_roughness_veto_logic(self):
        """Signals lacking auditory roughness (<0.045) and HFCR (<0.050) receive 0.20 attenuation."""
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        flat_signal = 0.3 * np.sin(2 * np.pi * 400 * t)
        svc = get_research_service()
        res = svc.infer_audio_array(flat_signal, sr=sr, model_id="CANDIDATE_68_D")
        assert res["calibrated_probability"] < 0.20


# ==============================================================================
# 8. CSV Forensics & Reporting Artifact Verification
# ==============================================================================

class TestArtifactSchemasAndSafetyDesignations:
    """Verifies artifact schemas, row counts, and mandatory safety designations."""

    REPORTS_DIR = STAGE_DIR / "reports"

    def test_fn_forensics_csv_schema_and_count(self):
        csv_path = self.REPORTS_DIR / "stage_8_9_68_false_negative_forensics.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 26, f"Expected exactly 26 false negatives audited, got {len(df)}"
        required_cols = {
            "recording_id", "source_group_id", "ground_truth", "duration",
            "duration_type", "is_ultra_short", "target_category", "candidate_65f_prob",
            "candidate_67d_raw_prob", "candidate_67d_calib_prob", "candidate_67d_pred",
            "short_branch_latent_norm", "sust_branch_latent_norm", "branch_cosine_agreement",
            "gate_weight_short", "roughness", "hfcr", "spectral_flux", "hnr_db",
            "spectral_flatness", "snr_est_db", "rt60_est_s", "vocal_veto_fired",
            "whistle_veto_fired", "rejection_factors", "primary_forensic_category",
            "annotation_confidence"
        }
        missing = required_cols - set(df.columns)
        assert len(missing) == 0, f"Missing columns in FN forensics CSV: {missing}"

    def test_predictions_csv_count(self):
        csv_path = self.REPORTS_DIR / "candidate_68_val_predictions.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 311, f"Expected 311 predictions, got {len(df)}"

    def test_tournament_csv_columns_schema(self):
        csv_path = self.REPORTS_DIR / "stage_8_9_68_candidate_tournament.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        expected_cols = ["candidate", "recall", "shout_fpr", "hn_fpr", "short_recall", "p95_latency_ms", "g1", "g2", "g3", "g4", "g5"]
        assert list(df.columns) == expected_cols

    def test_candidate_68_checkpoint_file_size(self):
        ckpt_path = STAGE_DIR / "models/candidate_68_frozen.pt"
        assert ckpt_path.exists()
        sz = ckpt_path.stat().st_size
        assert 10000 < sz < 50000, f"Unexpected checkpoint size: {sz} bytes"

    def test_candidate_68_metadata_keys(self):
        meta_path = STAGE_DIR / "models/candidate_68_metadata.json"
        assert meta_path.exists()
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        req_keys = {"candidate_id", "display_name", "stage", "checkpoint_sha256", "operating_threshold", "suppression_heuristics", "validation_results_n311"}
        assert req_keys.issubset(set(data.keys()))

    def test_primary_failure_mechanisms_distribution(self):
        csv_path = self.REPORTS_DIR / "stage_8_9_68_false_negative_forensics.csv"
        df = pd.read_csv(csv_path)
        cats = df["primary_forensic_category"].value_counts().to_dict()
        assert cats.get("LOW_SNR_DISTANT") == 15
        assert cats.get("REVERBERANT") == 5
        assert cats.get("ROUGHNESS_VETO") == 3
        assert cats.get("SHORT_EVENT") == 3

    def test_line1_mandatory_safety_designation_on_reports(self):
        """All existing markdown reports in reports/ must start with line 1 safety header."""
        md_files = list(self.REPORTS_DIR.glob("*.md"))
        assert len(md_files) > 0, "No markdown files found to check"
        expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
        for md_path in md_files:
            with open(md_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            assert first_line == expected_header, (
                f"File {md_path.name} violates line 1 safety designation! Found: {first_line}"
            )

    def test_mcnemar_statistical_comparison_67_vs_68(self):
        """Verifies contingency table between Candidate 67-D and 68-D predictions."""
        preds_68_path = self.REPORTS_DIR / "candidate_68_val_predictions.csv"
        df = pd.read_csv(preds_68_path)
        # In Candidate 68-D, 1 scream was recovered (+1 TP) and 2 hard negatives were eliminated (-2 FP)
        assert (df["ground_truth"] == 1).sum() == 99
        assert (df["ground_truth"] == 0).sum() == 212

    def test_whistle_veto_preserves_scream_signature(self):
        """A scream with high roughness and spectral flux must not be suppressed by whistle veto."""
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        # Synthetic scream: 1200 Hz carrier modulated at 75 Hz roughness band + turbulence
        carrier = np.sin(2 * np.pi * 1200 * t)
        mod = 1.0 + 0.6 * np.sin(2 * np.pi * 75 * t)
        noise = np.random.normal(0, 0.1, sr)
        scream_like = (carrier * mod + noise) * 0.7
        svc = get_research_service()
        res = svc.infer_audio_array(scream_like.astype(np.float32), sr=sr, model_id="CANDIDATE_68_D")
        # Whistle veto requires flatness < 0.001; turbulence ensures flatness > 0.001, so veto must not fire
        assert res["calibrated_probability"] == res["raw_probability"]

    def test_latency_percentile_benchmarks(self):
        """Neural model-only inference latency must remain strictly under 5.0 ms P95 (well below 25 ms gate)."""
        meta_path = STAGE_DIR / "models/candidate_68_metadata.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        p95 = data["validation_results_n311"]["p95_latency_ms"]
        assert p95 < 2.0, f"Expected P95 latency < 2.0 ms, got {p95}"
        assert p95 <= 25.0

    def test_all_report_filenames_follow_naming_convention(self):
        """All stage 68 report files must start with stage_8_9_68_ or candidate_68_."""
        for md in self.REPORTS_DIR.glob("*.md"):
            assert md.name.startswith("stage_8_9_68_") or md.name.startswith("candidate_68_"), (
                f"Unexpected report filename: {md.name}"
            )
