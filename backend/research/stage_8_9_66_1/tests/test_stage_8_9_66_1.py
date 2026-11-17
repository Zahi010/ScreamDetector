# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.66.1 — AUTOMATED VERIFICATION TEST SUITE
Candidate 65-F Data Provenance Audit, Unseen-Data Verification & Independent Evaluation Readiness

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = STAGE_DIR / "reports"
SCRIPTS_DIR = STAGE_DIR / "scripts"

# Immutable Production Asset Expected Hashes
EXPECTED_PRODUCTION_HASHES = {
    "scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

# Immutable Candidate 65-F Artifact Expected Hashes
EXPECTED_CANDIDATE_HASHES = {
    "candidate_65f_frozen.pt": "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab",
    "candidate_freeze_metadata.json": "a40672a42e3a8d1f38f1ff067cb92b6c45e122b12a25c127f7513d78327944d4",
    "c5_combined.py": "d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58",
    "reproduce_candidate_65f.py": "f78d78161994a76a3f84ca87404dc5d180d6a06d219476029efbfa60cb9d4877",
}

EXPECTED_SEALED_MANIFEST_HASH = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# 1. Protected Production Asset Integrity Tests (Section 9 Compliance)
# ==============================================================================

def test_production_scream_classifier_hash():
    target = REPO_ROOT / "backend" / "models" / "scream_classifier.joblib"
    assert target.exists(), f"Missing production asset: {target}"
    assert compute_sha256(target) == EXPECTED_PRODUCTION_HASHES["scream_classifier.joblib"]


def test_production_model_metadata_hash():
    target = REPO_ROOT / "backend" / "models" / "model_metadata.json"
    assert target.exists(), f"Missing production asset: {target}"
    assert compute_sha256(target) == EXPECTED_PRODUCTION_HASHES["model_metadata.json"]


def test_production_test_predictions_hash():
    target = REPO_ROOT / "backend" / "reports" / "test_predictions.csv"
    assert target.exists(), f"Missing production asset: {target}"
    assert compute_sha256(target) == EXPECTED_PRODUCTION_HASHES["test_predictions.csv"]


def test_production_stage5_evaluation_hash():
    target = REPO_ROOT / "backend" / "reports" / "stage5_test_evaluation.md"
    assert target.exists(), f"Missing production asset: {target}"
    assert compute_sha256(target) == EXPECTED_PRODUCTION_HASHES["stage5_test_evaluation.md"]


# ==============================================================================
# 2. Candidate 65-F Frozen Checkpoint & Pipeline Integrity Tests
# ==============================================================================

def test_candidate_65f_frozen_checkpoint_hash():
    target = REPO_ROOT / "backend" / "research" / "stage_8_9_66" / "models" / "candidate_65f_frozen.pt"
    assert target.exists(), f"Missing candidate checkpoint: {target}"
    assert compute_sha256(target) == EXPECTED_CANDIDATE_HASHES["candidate_65f_frozen.pt"]


def test_candidate_freeze_metadata_hash():
    target = REPO_ROOT / "backend" / "research" / "stage_8_9_66" / "models" / "candidate_freeze_metadata.json"
    assert target.exists(), f"Missing freeze metadata: {target}"
    assert compute_sha256(target) == EXPECTED_CANDIDATE_HASHES["candidate_freeze_metadata.json"]


def test_c5_dsp_combined_hash():
    target = REPO_ROOT / "backend" / "research" / "stage_8_9_57" / "dsp_implementations" / "c5_combined.py"
    assert target.exists(), f"Missing C5 DSP implementation: {target}"
    assert compute_sha256(target) == EXPECTED_CANDIDATE_HASHES["c5_combined.py"]


def test_reproduce_candidate_65f_hash():
    target = REPO_ROOT / "backend" / "research" / "stage_8_9_66" / "scripts" / "reproduce_candidate_65f.py"
    assert target.exists(), f"Missing evaluation reproduction script: {target}"
    assert compute_sha256(target) == EXPECTED_CANDIDATE_HASHES["reproduce_candidate_65f.py"]


def test_candidate_65f_state_dict_structure():
    checkpoint_path = REPO_ROOT / "backend" / "research" / "stage_8_9_66" / "models" / "candidate_65f_frozen.pt"
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    assert isinstance(checkpoint, dict), "Checkpoint is not a dictionary"
    assert "model_state_dict" in checkpoint or "state_dict" in checkpoint or len(checkpoint) > 0


# ==============================================================================
# 3. Artifact Inventory & Checkpoint Record Verification
# ==============================================================================

def test_artifact_inventory_csv_exists_and_populated():
    target = REPORTS_DIR / "artifact_inventory.csv"
    assert target.exists(), "artifact_inventory.csv does not exist"
    df = pd.read_csv(target)
    assert len(df) >= 30, f"Expected at least 30 cataloged artifacts, found {len(df)}"
    assert "artifact_name" in df.columns
    assert "sha256" in df.columns
    assert "status" in df.columns
    assert (df["status"] == "VERIFIED").all(), "Some cataloged artifacts are not VERIFIED"


def test_candidate_65f_checkpoint_hash_record():
    target = REPORTS_DIR / "candidate_65f_checkpoint_hash_record.json"
    assert target.exists(), "candidate_65f_checkpoint_hash_record.json does not exist"
    with open(target, "r") as f:
        data = json.load(f)
    assert data["checkpoint_sha256"] == EXPECTED_CANDIDATE_HASHES["candidate_65f_frozen.pt"]
    hp = data["frozen_hyperparameters"]
    assert hp["decision_threshold"] == 0.48
    assert hp["high_confidence_bypass"] == 0.80
    assert hp["narrow_band_whistle_hnr_db"] == 12.0
    assert hp["narrow_band_whistle_flatness"] == 0.001
    assert hp["branch_cosine_agreement_threshold"] == 0.40
    assert hp["attenuation_factor"] == 0.15


# ==============================================================================
# 4. N=312 Development Cohort Classification Tests
# ==============================================================================

def test_n312_development_manifest_size_and_integrity():
    manifest_path = REPO_ROOT / "backend" / "research" / "stage_8_9_63" / "stage_63_development_manifest.csv"
    assert manifest_path.exists(), f"Missing dev manifest: {manifest_path}"
    df = pd.read_csv(manifest_path)
    assert len(df) == 312, f"Expected exactly 312 recordings, got {len(df)}"
    assert (df["binary_label"] == 1).sum() == 195
    assert (df["binary_label"] == 0).sum() == 117
    assert df["recording_id"].nunique() == 312, "Duplicate recording_id in N=312 manifest"


def test_n312_cohort_classification_report_verdict():
    report_path = REPORTS_DIR / "stage_8_9_66_1_n312_cohort_classification.md"
    assert report_path.exists(), "Missing n312 cohort classification report"
    content = report_path.read_text(encoding="utf-8")
    assert "DEFINITIVELY REFUTED" in content
    assert "Development Benchmark" in content


def test_n312_cohort_role_categorization():
    report_path = REPORTS_DIR / "stage_8_9_66_1_n312_cohort_classification.md"
    content = report_path.read_text(encoding="utf-8")
    assert "A. Training Data" in content
    assert "B. Validation Data" in content
    assert "C. Development Benchmark" in content
    assert "D. Final Model Selection" in content
    assert "E. Untouched Independent Test Set" in content


# ==============================================================================
# 5. Overlap Matrix & Source Group Independence Tests
# ==============================================================================

def test_overlap_matrix_file_exists():
    target = REPORTS_DIR / "recording_source_group_overlap_matrix.csv"
    assert target.exists(), "Missing recording_source_group_overlap_matrix.csv"
    df = pd.read_csv(target)
    assert len(df) > 0


def test_dev_cohort_zero_overlap_with_sealed_cohort():
    target = REPORTS_DIR / "recording_source_group_overlap_matrix.csv"
    df = pd.read_csv(target)
    match = df[
        (df["dataset_a"] == "N=312 Development Cohort") & 
        (df["dataset_b"] == "Stage 60 Sealed Cohort (N=700)")
    ]
    assert len(match) == 1, "Could not find overlap matrix row between dev and sealed cohorts"
    row = match.iloc[0]
    assert row["exact_pcm_overlap"] == 0, f"Expected 0 PCM overlap, found {row['exact_pcm_overlap']}"
    assert row["source_group_overlap"] == 0, f"Expected 0 source group overlap, found {row['source_group_overlap']}"


def test_dev_cohort_zero_overlap_with_historical_partitions():
    target = REPORTS_DIR / "recording_source_group_overlap_matrix.csv"
    df = pd.read_csv(target)
    for partition in ["Stage 54 Train Partition", "Stage 54 Validation Partition", "Stage 54 Reserved Test"]:
        match = df[
            (df["dataset_a"] == "N=312 Development Cohort") & 
            (df["dataset_b"] == partition)
        ]
        if len(match) > 0:
            row = match.iloc[0]
            assert row["exact_pcm_overlap"] == 0, f"Found PCM overlap with {partition}"
            assert row["source_group_overlap"] == 0, f"Found source group overlap with {partition}"


# ==============================================================================
# 6. Expanded Negative Exposure Classification Tests
# ==============================================================================

def test_dataset_exposure_classification_csv():
    target = REPORTS_DIR / "dataset_exposure_classification.csv"
    assert target.exists(), "Missing dataset_exposure_classification.csv"
    df = pd.read_csv(target)
    assert len(df) == 991, f"Expected 991 total negative rows, got {len(df)}"

    hard_negs = df[df["cohort"] == "hard_negatives"]
    shouted = df[df["cohort"] == "shouted_speech"]

    assert len(hard_negs) == 462, f"Expected 462 hard negatives, got {len(hard_negs)}"
    assert len(shouted) == 529, f"Expected 529 shouted speech files, got {len(shouted)}"

    # Hard negatives: 0 eligible unseen
    assert (hard_negs["exposure_classification"] == "CONFIRMED_UNSEEN").sum() == 0
    assert hard_negs["eligible_for_frozen_inference"].sum() == 0

    # Shouted speech: exactly 111 eligible unseen
    assert (shouted["exposure_classification"] == "CONFIRMED_UNSEEN").sum() == 111
    assert shouted["eligible_for_frozen_inference"].sum() == 111


def test_exposure_classification_categories_sum_to_total():
    target = REPORTS_DIR / "dataset_exposure_classification.csv"
    df = pd.read_csv(target)
    counts = df["exposure_classification"].value_counts()
    assert counts.get("PREVIOUSLY_EXPOSED", 0) == 833
    assert counts.get("CONFIRMED_UNSEEN", 0) == 111
    assert counts.get("SOURCE_GROUP_OVERLAP", 0) == 47
    assert counts.sum() == 991


# ==============================================================================
# 7. Frozen Inference on Unseen Shouted Speech Tests (Gate 3 Verification)
# ==============================================================================

def test_frozen_inference_predictions_count_and_labels():
    target = REPORTS_DIR / "frozen_inference_shouted_speech_predictions.csv"
    assert target.exists(), "Missing frozen_inference_shouted_speech_predictions.csv"
    df = pd.read_csv(target)
    assert len(df) == 111, f"Expected 111 predictions, got {len(df)}"
    assert (df["ground_truth"] == 0).all(), "All shouted speech samples should be ground truth negative (0)"
    assert set(df["prediction"].unique()).issubset({0, 1})


def test_frozen_inference_gate3_catastrophic_failure():
    target = REPORTS_DIR / "frozen_inference_shouted_speech_predictions.csv"
    df = pd.read_csv(target)
    fp_count = df["false_positive"].sum()
    tn_count = df["true_negative"].sum()

    assert fp_count == 49, f"Expected exactly 49 false alarms, got {fp_count}"
    assert tn_count == 62, f"Expected exactly 62 true rejections, got {tn_count}"

    observed_fpr = fp_count / len(df)
    expected_fpr = 49 / 111
    assert abs(observed_fpr - expected_fpr) < 1e-4

    # Gate 3 strictly requires FPR <= 15.00%
    assert observed_fpr > 0.1500, "Gate 3 did not fail as expected!"
    assert observed_fpr >= 0.4400, f"Observed FPR {observed_fpr:.4f} is unexpectedly low"


def test_frozen_inference_wilson_confidence_interval():
    # Verify Wilson score interval [35.26%, 53.42%]
    n = 111
    k = 49
    p = k / n
    z = 1.95996  # 95% confidence
    denominator = 1 + z**2 / n
    centre_adjusted_probability = (p + z**2 / (2 * n)) / denominator
    adjusted_standard_error = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator
    lower = centre_adjusted_probability - adjusted_standard_error
    upper = centre_adjusted_probability + adjusted_standard_error

    assert abs(lower - 0.3526) < 0.005, f"Lower CI {lower:.4f} differs from expected ~0.3526"
    assert abs(upper - 0.5342) < 0.005, f"Upper CI {upper:.4f} differs from expected ~0.5342"
    assert lower > 0.15, "Entire 95% CI is strictly above Gate 3 limit (15.00%)"


def test_unseen_shouted_speech_disjoint_from_sealed_cohort():
    target = REPORTS_DIR / "frozen_inference_shouted_speech_predictions.csv"
    df_pred = pd.read_csv(target)
    unseen_ids = set(df_pred["recording_id"])

    sealed_manifest_path = REPO_ROOT / "backend" / "research" / "stage_8_9_60" / "future_evaluation_manifest.json"
    with open(sealed_manifest_path, "r") as f:
        manifest = json.load(f)
    sealed_ids = {r["recording_id"] for r in manifest.get("recordings", [])}

    overlap = unseen_ids.intersection(sealed_ids)
    assert len(overlap) == 0, f"Unseen test data leaked into sealed manifest: {len(overlap)} overlapping IDs"


def test_unseen_shouted_speech_disjoint_from_dev_cohort():
    target = REPORTS_DIR / "frozen_inference_shouted_speech_predictions.csv"
    df_pred = pd.read_csv(target)
    unseen_ids = set(df_pred["recording_id"])

    dev_manifest_path = REPO_ROOT / "backend" / "research" / "stage_8_9_63" / "stage_63_development_manifest.csv"
    df_dev = pd.read_csv(dev_manifest_path)
    dev_ids = set(df_dev["recording_id"])

    overlap = unseen_ids.intersection(dev_ids)
    assert len(overlap) == 0, f"Unseen test data leaked into dev manifest: {len(overlap)} overlapping IDs"


# ==============================================================================
# 8. Sealed Cohort Administrative & Sealing Integrity Tests
# ==============================================================================

def test_sealed_cohort_manifest_hash_and_counts():
    target = REPO_ROOT / "backend" / "research" / "stage_8_9_60" / "future_evaluation_manifest.json"
    assert target.exists(), f"Missing sealed manifest: {target}"
    assert compute_sha256(target) == EXPECTED_SEALED_MANIFEST_HASH

    with open(target, "r") as f:
        manifest = json.load(f)

    assert manifest["cohort_status"] == "SEALED_CRYPTOGRAPHICALLY_FROZEN"
    assert manifest["total_recordings"] == 700
    assert manifest["positive_recordings"] == 200
    assert manifest["negative_recordings"] == 500
    assert manifest["unique_source_groups"] == 453

    recordings = manifest.get("recordings", [])
    assert len(recordings) == 700
    pos_count = sum(1 for r in recordings if r.get("binary_label") == 1)
    neg_count = sum(1 for r in recordings if r.get("binary_label") == 0)
    assert pos_count == 200, f"Expected 200 positives, got {pos_count}"
    assert neg_count == 500, f"Expected 500 negatives, got {neg_count}"


def test_sealed_cohort_no_wav_files_decoded_in_stage_dir():
    # Ensure no audio wav files or cached decoded spectrograms exist in stage_8_9_66_1
    wav_files = list(STAGE_DIR.rglob("*.wav"))
    assert len(wav_files) == 0, f"Found unsealed raw wav files in stage directory: {len(wav_files)}"


# ==============================================================================
# 9. Deliverables and Markdown Structure Integrity
# ==============================================================================

def test_all_stage_reports_exist():
    expected_reports = [
        "stage_8_9_66_1_candidate_provenance_audit.md",
        "stage_8_9_66_1_n312_cohort_classification.md",
        "stage_8_9_66_1_source_group_leakage_audit.md",
        "stage_8_9_66_1_expanded_negative_provenance.md",
        "stage_8_9_66_1_sealed_cohort_integrity.md",
        "stage_8_9_66_1_candidate_artifact_integrity.md",
        "stage_8_9_66_1_independent_evaluation_readiness.md",
        "stage_8_9_66_1_completion_report.md",
    ]
    for rep in expected_reports:
        target = REPORTS_DIR / rep
        assert target.exists(), f"Missing stage report: {rep}"
        assert target.stat().st_size > 500, f"Report {rep} is unexpectedly small"


def test_reports_line_1_safety_header():
    expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    md_files = list(REPORTS_DIR.glob("*.md"))
    assert len(md_files) >= 8, f"Expected at least 8 markdown reports, found {len(md_files)}"

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        assert first_line == expected_header, f"File {md_file.name} missing mandatory safety header on line 1"


def test_scripts_docstring_safety_header():
    expected_token = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    py_files = list(SCRIPTS_DIR.glob("*.py"))
    assert len(py_files) >= 3, f"Expected at least 3 python scripts, found {len(py_files)}"

    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        assert expected_token in content, f"Script {py_file.name} missing mandatory safety designation"


def test_readiness_report_contains_authoritative_verdicts():
    target = REPORTS_DIR / "stage_8_9_66_1_independent_evaluation_readiness.md"
    content = target.read_text(encoding="utf-8")
    assert "OPTION B — HISTORICAL DEVELOPMENT RESULTS ONLY" in content
    assert "NOT READY FOR INDEPENDENT EVALUATION" in content
    assert "44.14%" in content
    assert "Gate 3" in content
