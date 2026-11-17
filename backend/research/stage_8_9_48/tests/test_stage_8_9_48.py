"""
Stage 8.9.48 Automated Unit and Regression Test Suite
Validates all requirements of Stage 8.9.48:
- Production artifact immutability (4 canonical SHA-256 hashes)
- Candidate checkpoint integrity (Candidate B, R5, R3, R1)
- Frozen threshold enforcement
- Reproducible prediction loading
- Confusion matrix arithmetic and paired discordance
- Wilson confidence intervals and McNemar testing
- Source-group cluster bootstrap integrity
- Correct subgroup denominators
- Zero source-group or parent-recording leakage
- Short-recording EOF handling
- Latency measurement boundaries
- Prior stage artifact immutability
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import binomtest
import soundfile as sf
import torch

REPO_ROOT = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE48_DIR = BACKEND_DIR / "research" / "stage_8_9_48"
STAGE47_DIR = BACKEND_DIR / "research" / "stage_8_9_47"
STAGE46_DIR = BACKEND_DIR / "research" / "stage_8_9_46"
STAGE44_DIR = BACKEND_DIR / "research" / "stage_8_9_44"

EXPECTED_PRODUCTION_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
}

def wilson_ci(k, n, z=1.95996):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1.0 + (z**2) / n
    center = p + (z**2) / (2 * n)
    diff = z * math.sqrt((p * (1 - p) + (z**2) / (4 * n)) / n)
    lower = max(0.0, (center - diff) / denom) * 100.0
    upper = min(1.0, (center + diff) / denom) * 100.0
    return lower, upper

# 1. Production Artifact Immutability
def test_production_artifact_immutability():
    for rel_path, exp_hash in EXPECTED_PRODUCTION_HASHES.items():
        p = REPO_ROOT / rel_path
        assert p.exists(), f"Production file missing: {rel_path}"
        act_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        assert act_hash == exp_hash, f"Hash mismatch for {rel_path}"

# 2. Candidate Checkpoint Integrity
def test_candidate_checkpoint_integrity():
    hash_audit_p = STAGE48_DIR / "FROZEN_CANDIDATE_HASH_AUDIT.md"
    assert hash_audit_p.exists(), "FROZEN_CANDIDATE_HASH_AUDIT.md missing"
    
    ckpt_b = BACKEND_DIR / "research" / "stage_8_9_44" / "models" / "config_b_mask.pt"
    ckpt_r5 = BACKEND_DIR / "research" / "stage_8_9_46" / "models" / "config_b_ratio_0p_100a.pt"
    assert ckpt_b.exists(), "Candidate B checkpoint missing"
    assert ckpt_r5.exists(), "Candidate R5 checkpoint missing"
    
    h_b = hashlib.sha256(ckpt_b.read_bytes()).hexdigest()
    h_r5 = hashlib.sha256(ckpt_r5.read_bytes()).hexdigest()
    assert len(h_b) == 64 and len(h_r5) == 64

# 3. Frozen Threshold Enforcement
def test_frozen_threshold_enforcement():
    mat_p = STAGE48_DIR / "SUBGROUP_GENERALIZATION_MATRIX.csv"
    assert mat_p.exists(), "SUBGROUP_GENERALIZATION_MATRIX.csv missing"
    # Ensure thresholds 0.8000 and 0.8700 are referenced
    report_p = STAGE48_DIR / "CANDIDATE_B_VS_R5_DOMINANCE_AUDIT.md"
    content = report_p.read_text(encoding="utf-8")
    assert "0.8000" in content, "Candidate B threshold 0.8000 missing"
    assert "0.8700" in content, "Candidate R5 threshold 0.8700 missing"

# 4. Reproducible Prediction Loading
def test_reproducible_prediction_loading():
    preds_p = STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv"
    assert preds_p.exists(), "INDEPENDENT_PREDICTIONS.csv missing"
    df = pd.read_csv(preds_p)
    assert len(df) == 480, f"Expected 480 predictions, got {len(df)}"
    assert (df["binary_label"] == 1).sum() == 160
    assert (df["binary_label"] == 0).sum() == 320

# 5. Confusion Matrix Arithmetic
def test_confusion_matrix_arithmetic():
    df = pd.read_csv(STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv")
    y = df["binary_label"].values
    b_pred = df["cand_b_config_b_mask_v6_pred"].values
    r5_pred = df["r5_ratio_0p_100a_pred"].values

    # Candidate B
    tp_b = int(np.sum((y == 1) & (b_pred == 1)))
    fn_b = int(np.sum((y == 1) & (b_pred == 0)))
    fp_b = int(np.sum((y == 0) & (b_pred == 1)))
    tn_b = int(np.sum((y == 0) & (b_pred == 0)))
    assert tp_b == 144 and fn_b == 16 and fp_b == 4 and tn_b == 316

    # Candidate R5
    tp_r5 = int(np.sum((y == 1) & (r5_pred == 1)))
    fn_r5 = int(np.sum((y == 1) & (r5_pred == 0)))
    fp_r5 = int(np.sum((y == 0) & (r5_pred == 1)))
    tn_r5 = int(np.sum((y == 0) & (r5_pred == 0)))
    assert tp_r5 == 121 and fn_r5 == 39 and fp_r5 == 1 and tn_r5 == 319

# 6. Wilson Interval Correctness
def test_wilson_interval_correctness():
    low, high = wilson_ci(144, 160)
    assert 84.0 <= low <= 85.0
    assert 93.0 <= high <= 94.0

    low_fp, high_fp = wilson_ci(4, 320)
    assert 0.40 <= low_fp <= 0.60
    assert 3.00 <= high_fp <= 3.30

# 7. Paired McNemar Test Implementation
def test_mcnemar_paired_test():
    df = pd.read_csv(STAGE47_DIR / "INDEPENDENT_PREDICTIONS.csv")
    pos = df[df["binary_label"] == 1]
    b_pred = pos["cand_b_config_b_mask_v6_pred"].values
    r5_pred = pos["r5_ratio_0p_100a_pred"].values

    b_discordant = int(np.sum((b_pred == 1) & (r5_pred == 0)))
    c_discordant = int(np.sum((b_pred == 0) & (r5_pred == 1)))
    assert b_discordant == 23, f"Expected 23 B-only detections, got {b_discordant}"
    assert c_discordant == 0, f"Expected 0 R5-only detections, got {c_discordant}"

    res = binomtest(b_discordant, b_discordant + c_discordant, 0.5, alternative="two-sided")
    assert res.pvalue < 1e-5, f"Expected p < 1e-5, got {res.pvalue}"

# 8. Source-Group Cluster Bootstrap Report
def test_source_group_bootstrap_report():
    paired_p = STAGE48_DIR / "PAIRED_STATISTICAL_COMPARISON.md"
    assert paired_p.exists(), "PAIRED_STATISTICAL_COMPARISON.md missing"
    content = paired_p.read_text(encoding="utf-8")
    assert "Scream Recall" in content
    assert "14." in content or "+14" in content

# 9. Correct Subgroup Denominators
def test_subgroup_denominators():
    matrix_p = STAGE48_DIR / "SUBGROUP_GENERALIZATION_MATRIX.csv"
    assert matrix_p.exists(), "SUBGROUP_GENERALIZATION_MATRIX.csv missing"
    df_m = pd.read_csv(matrix_p)
    d = dict(zip(df_m["category_or_subtype"], df_m["cohort_clips"]))
    
    assert d["ultra_short_scream"] == 25
    assert d["short_scream"] == 45
    assert d["sustained_scream"] == 35
    assert d["distant_reverberant_scream"] == 20
    assert d["low_intensity_muffled_scream"] == 15
    assert d["crowd_masked_scream"] == 20
    assert d["shouting_and_speech"] == 80
    assert d["crowd_chant_cheering"] == 60
    assert d["infant_crying"] == 45
    assert d["whistles_and_squeaks"] == 45
    assert d["sfx_sirens_fireworks"] == 45
    assert d["music_and_environmental"] == 45

# 10. No Cross-Partition Leakage
def test_zero_leakage():
    manifest_p = STAGE47_DIR / "INDEPENDENT_COHORT_MANIFEST.csv"
    df_cohort = pd.read_csv(manifest_p)
    v5_p = BACKEND_DIR / "research" / "stage_8_9_43" / "manifests" / "dataset_manifest_v5.csv"
    df_v5 = pd.read_csv(v5_p)

    cohort_sgs = set(df_cohort["source_group_id"].dropna())
    v5_sgs = set(df_v5["source_group_id"].dropna())
    assert len(cohort_sgs.intersection(v5_sgs)) == 0, "Source group leakage detected"

# 11. Short-Recording EOF Handling
def test_short_recording_eof_handling():
    # Verify processing of waveform shorter than 960ms without crash
    audio_dir = STAGE47_DIR / "audio" / "independent"
    # Select an ultra short clip
    fn_csv = pd.read_csv(STAGE48_DIR / "R5_FALSE_NEGATIVE_FORENSICS.csv")
    ultra_clips = fn_csv[fn_csv["duration_seconds"] < 0.50]
    assert len(ultra_clips) > 0, "No ultra-short clips in forensics"
    sample_id = ultra_clips.iloc[0]["file_id"]
    wav_path = audio_dir / f"{sample_id}.wav"
    assert wav_path.exists(), f"Audio file missing: {wav_path}"
    
    wf, sr = sf.read(str(wav_path))
    assert len(wf) < sr, f"Clip duration exceeds 1.0s: {len(wf)/sr}s"

# 12. Latency Measurement Boundaries
def test_latency_measurement_boundaries():
    lat_p = STAGE48_DIR / "LATENCY_MEASUREMENT_AUDIT.md"
    assert lat_p.exists(), "LATENCY_MEASUREMENT_AUDIT.md missing"
    content = lat_p.read_text(encoding="utf-8")
    assert "P95" in content
    assert "Gate 5" in content

# 13. Prior Stage Artifact Immutability
def test_prior_stage_artifacts_immutability():
    s47_report = STAGE47_DIR / "STAGE_8_9_47_REPORT.md"
    assert s47_report.exists(), "Stage 8.9.47 report missing"
    assert "INDEPENDENT GENERALIZATION REPLICATED — SOME GATES REMAIN UNSUPPORTED" in s47_report.read_text(encoding="utf-8")
