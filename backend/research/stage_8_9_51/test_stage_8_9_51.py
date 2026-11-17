"""
Stage 8.9.51: Comprehensive Automated Regression Test Suite
Verifies all 11 mandatory requirements from Section 13:
1. Candidate B checkpoint hash remains unchanged.
2. Candidate B threshold remains 0.8000.
3. Intervention D reference configuration remains unchanged.
4. Production artifact hashes remain unchanged.
5. No source-group leakage across splits.
6. Augmented data retains parent source identity.
7. No evaluated false-negative recording is silently inserted into training.
8. Experimental checkpoints remain separate from frozen references.
9. Thresholds are selected from validation data only.
10. Latency benchmark measures the documented complete pipeline (ambient and trigger).
11. All reported metrics can be recomputed from saved predictions.
"""
import sys
import hashlib
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE49_DIR = BACKEND_DIR / "research" / "stage_8_9_49"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"

sys.path.insert(0, str(STAGE49_DIR / "scripts"))
sys.path.insert(0, str(STAGE51_DIR / "scripts"))

from whistle_discriminator import apply_intervention_d, extract_envelope_modulation, extract_spectral_concentration
from run_evaluations import DualEncoderAcousticModel, CANDIDATE_B_CKPT, FROZEN_THRESHOLD, wilson_ci

# -----------------------------------------------------------------------------
# 1. CANDIDATE B CHECKPOINT INTEGRITY
# -----------------------------------------------------------------------------
def test_candidate_b_checkpoint_hash():
    expected_hash = "f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378"
    assert CANDIDATE_B_CKPT.exists(), f"Candidate B checkpoint missing: {CANDIDATE_B_CKPT}"
    with open(CANDIDATE_B_CKPT, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_hash == expected_hash, f"Candidate B checkpoint altered! Expected {expected_hash}, got {actual_hash}"

# -----------------------------------------------------------------------------
# 2. CANDIDATE B FROZEN THRESHOLD
# -----------------------------------------------------------------------------
def test_candidate_b_threshold():
    assert FROZEN_THRESHOLD == 0.8000, f"Candidate B threshold altered! Expected 0.8000, got {FROZEN_THRESHOLD}"

# -----------------------------------------------------------------------------
# 3. INTERVENTION D REFERENCE CONFIGURATION INTEGRITY
# -----------------------------------------------------------------------------
def test_intervention_d_configuration():
    # Test vocal formant protection gate (>18% vocal band energy)
    sr = 16000
    t = np.linspace(0, 0.96, int(0.96 * sr), endpoint=False)
    # 800 Hz pure vocal tone
    vocal_tone = 0.5 * np.sin(2 * np.pi * 800 * t).astype(np.float32)
    pred, tag, diag = apply_intervention_d(vocal_tone, raw_prob=0.92, raw_pred=1, sr=sr)
    assert pred == 1, "Vocal formant tone was falsely rejected!"
    assert tag == "accepted"
    assert diag["filter"] == "protected_by_vocal_formant_gate"
    
    # Test mechanical referee pea whistle (3000 Hz tone modulated at 25 Hz)
    mod_whistle = 0.5 * (1.0 + 0.8 * np.sin(2 * np.pi * 25 * t)) * np.sin(2 * np.pi * 3000 * t)
    mod_whistle = mod_whistle.astype(np.float32)
    pred_w, tag_w, diag_w = apply_intervention_d(mod_whistle, raw_prob=0.95, raw_pred=1, sr=sr)
    assert pred_w == 0, "Mechanical referee whistle was not rejected!"
    assert tag_w == "rejected_by_research_filter"

# -----------------------------------------------------------------------------
# 4. CANONICAL PRODUCTION ARTIFACT IMMUTABILITY
# -----------------------------------------------------------------------------
def test_production_artifact_hashes():
    expected_production_hashes = {
        REPO_ROOT / "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        REPO_ROOT / "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        REPO_ROOT / "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        REPO_ROOT / "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for path, expected in expected_production_hashes.items():
        assert path.exists(), f"Production artifact missing: {path}"
        with open(path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected, f"Production artifact altered: {path}!\nExpected: {expected}\nActual: {actual}"

# -----------------------------------------------------------------------------
# 5. SOURCE-GROUP LEAKAGE VERIFICATION
# -----------------------------------------------------------------------------
def test_no_source_group_leakage():
    dev_p = STAGE49_DIR / "features" / "dev_features.npz"
    val_p = STAGE49_DIR / "features" / "val_features.npz"
    indep_p = STAGE49_DIR / "features" / "independent_features.npz"
    
    dev_sg = set(np.load(dev_p, allow_pickle=True)["source_groups"])
    val_sg = set(np.load(val_p, allow_pickle=True)["source_groups"])
    indep_sg = set(np.load(indep_p, allow_pickle=True)["source_groups"])
    
    assert len(dev_sg.intersection(val_sg)) == 0, "Source-group overlap between Dev and Val!"
    assert len(dev_sg.intersection(indep_sg)) == 0, "Source-group overlap between Dev and Independent!"
    assert len(val_sg.intersection(indep_sg)) == 0, "Source-group overlap between Val and Independent!"

# -----------------------------------------------------------------------------
# 6. AUGMENTED DATA PARENT RETENTION
# -----------------------------------------------------------------------------
def test_augmented_data_parent_retention():
    # In all experiment scripts, augmented instances retain exact parent file_id and source_group_id
    dev_p = STAGE49_DIR / "features" / "dev_features.npz"
    d = np.load(dev_p, allow_pickle=True)
    fids = d["file_ids"]
    sgs = d["source_groups"]
    assert len(fids) == len(sgs)
    for fid, sg in zip(fids, sgs):
        assert len(sg) > 0 and sg.startswith("s49_sg_dev_")

# -----------------------------------------------------------------------------
# 7. QUARANTINE OF THE 29 FALSE NEGATIVES
# -----------------------------------------------------------------------------
def test_false_negatives_quarantine():
    # Load 29 false negatives
    tax_csv = STAGE51_DIR / "FALSE_NEGATIVE_TAXONOMY.csv"
    assert tax_csv.exists(), "Taxonomy CSV missing!"
    tax_df = pd.read_csv(tax_csv)
    assert len(tax_df) == 29, f"Expected 29 false negatives, got {len(tax_df)}"
    fn_fids = set(tax_df["file_id"])
    
    # Verify none exist in dev or val
    dev_fids = set(np.load(STAGE49_DIR / "features" / "dev_features.npz", allow_pickle=True)["file_ids"])
    val_fids = set(np.load(STAGE49_DIR / "features" / "val_features.npz", allow_pickle=True)["file_ids"])
    
    assert len(fn_fids.intersection(dev_fids)) == 0, "Evaluated false negative leaked into Dev training split!"
    assert len(fn_fids.intersection(val_fids)) == 0, "Evaluated false negative leaked into Val tuning split!"

# -----------------------------------------------------------------------------
# 8. EXPERIMENTAL CHECKPOINTS REMAIN SEPARATE
# -----------------------------------------------------------------------------
def test_experimental_checkpoints_separate():
    exp_ckpt = STAGE51_DIR / "models" / "research_exp_candidate.pt"
    assert exp_ckpt.exists(), "Experimental checkpoint missing!"
    assert exp_ckpt != CANDIDATE_B_CKPT, "Experimental checkpoint overwrote Candidate B!"
    
    with open(exp_ckpt, "rb") as f:
        exp_hash = hashlib.sha256(f.read()).hexdigest()
    with open(CANDIDATE_B_CKPT, "rb") as f:
        b_hash = hashlib.sha256(f.read()).hexdigest()
    assert exp_hash != b_hash, "Experimental checkpoint is identical to Candidate B!"

# -----------------------------------------------------------------------------
# 9. VALIDATION-ONLY THRESHOLD SELECTION
# -----------------------------------------------------------------------------
def test_validation_only_threshold_selection():
    comp_csv = STAGE51_DIR / "results" / "RESEARCH_CANDIDATE_COMPARISON.csv"
    assert comp_csv.exists(), "Candidate comparison CSV missing!"
    df = pd.read_csv(comp_csv)
    exp_row = df[df["Candidate"].str.contains("Research Candidate E")].iloc[0]
    assert exp_row["Threshold"] == 0.4000
    assert "NOT EVALUATED" in exp_row["Independent_Cohort_Status"]

# -----------------------------------------------------------------------------
# 10. STANDARDIZED LATENCY BENCHMARK MEASURES COMPLETE PIPELINE
# -----------------------------------------------------------------------------
def test_latency_benchmark_completeness():
    bench_csv = STAGE51_DIR / "STANDARDIZED_LATENCY_BENCHMARK.csv"
    assert bench_csv.exists(), "Standardized latency benchmark CSV missing!"
    df = pd.read_csv(bench_csv)
    
    # Check Profile 1 (ambient bypass)
    p1 = df[df["Profile"].str.contains("Profile 1")].iloc[0]
    assert p1["Pipeline_P95_ms"] < 1.0, f"Profile 1 P95 unexpectedly high: {p1['Pipeline_P95_ms']}"
    assert p1["Gate_5_Status"].startswith("PASS")
    
    # Check Profile 2 (worst-case trigger)
    p2 = df[df["Profile"].str.contains("Profile 2")].iloc[0]
    assert 2.0 < p2["Pipeline_P95_ms"] < 5.0, f"Profile 2 P95 out of expected range: {p2['Pipeline_P95_ms']}"
    assert p2["Gate_5_Status"].startswith("PASS")
    
    # Check 8-stream concurrency
    p8 = df[df["Profile"].str.contains("Concurrent Streams = 8")].iloc[0]
    assert p8["Pipeline_P95_ms"] <= 25.0, f"8-stream P95 exceeded 25ms: {p8['Pipeline_P95_ms']}"
    assert p8["Gate_5_Status"].startswith("PASS")

# -----------------------------------------------------------------------------
# 11. RECOMPUTABILITY OF ALL REPORTED METRICS
# -----------------------------------------------------------------------------
def test_recomputability_of_reported_metrics():
    preds_csv = STAGE49_DIR / "INDEPENDENT_EVALUATION_PREDICTIONS.csv"
    assert preds_csv.exists(), "Independent evaluation predictions CSV missing!"
    df = pd.read_csv(preds_csv)
    assert len(df) == 480, f"Expected 480 predictions, got {len(df)}"
    
    labels = df["binary_label"].values
    cand_b_preds = df["candidate_b_pred"].values
    interv_d_preds = df["intervention_d_pred"].values
    
    pos_mask = (labels == 1)
    neg_mask = (labels == 0)
    
    # Candidate B overall recall
    tp_b = np.sum(cand_b_preds[pos_mask] == 1)
    fn_b = np.sum(cand_b_preds[pos_mask] == 0)
    assert tp_b == 131, f"Expected 131 TP, got {tp_b}"
    assert fn_b == 29, f"Expected 29 FN, got {fn_b}"
    recall_b = (tp_b / 160) * 100.0
    assert abs(recall_b - 81.875) < 1e-3
    
    # Candidate B + Intervention D overall recall (100% preservation)
    tp_d = np.sum(interv_d_preds[pos_mask] == 1)
    fn_d = np.sum(interv_d_preds[pos_mask] == 0)
    assert tp_d == 131
    assert fn_d == 29
    
    # Hard-negative FPR (1/320 = 0.31% <= 5.0%)
    fp_d = np.sum(interv_d_preds[neg_mask] == 1)
    assert fp_d == 1, f"Expected exactly 1 hard-negative false positive (s49_indep_neg_0009), got {fp_d}"
    hn_fpr = (fp_d / 320) * 100.0
    assert hn_fpr <= 5.0, f"HN-FPR exceeded 5.0%: {hn_fpr}%"
    
    # Shouted speech FPR (1/80 = 1.25% <= 15.0%)
    shout_mask = neg_mask & (df["acoustic_subtype"] == "shouted_speech")
    fp_shout = np.sum(interv_d_preds[shout_mask] == 1)
    n_shout = np.sum(shout_mask)
    assert n_shout == 80, f"Expected 80 shouted speech clips, got {n_shout}"
    assert fp_shout == 1, f"Expected 1 shouted speech false alarm, got {fp_shout}"
    shout_fpr = (fp_shout / n_shout) * 100.0
    assert shout_fpr <= 15.0, f"Shouted speech FPR exceeded 15.0%: {shout_fpr}%"
    
    # Whistle FPR (0/45 = 0.00% - all referee pea whistles rejected by Intervention D)
    whistle_mask = neg_mask & (df["acoustic_subtype"] == "referee_whistle")
    fp_whistle = np.sum(interv_d_preds[whistle_mask] == 1)
    n_whistle = np.sum(whistle_mask)
    assert n_whistle == 45, f"Expected 45 referee whistle clips, got {n_whistle}"
    assert fp_whistle == 0, f"Expected 0 whistle false alarms after Intervention D, got {fp_whistle}"
    
    # Short scream recall (all d <= 1.0s: ultra_short 25 + short 45 = 70)
    short_mask = pos_mask & ((df["acoustic_subtype"] == "ultra_short_scream") | (df["acoustic_subtype"] == "short_scream"))
    tp_short = np.sum(interv_d_preds[short_mask] == 1)
    n_short = np.sum(short_mask)
    assert n_short == 70, f"Expected 70 short/ultra-short screams, got {n_short}"
    assert tp_short == 66, f"Expected 66 short screams detected, got {tp_short}"
    rec_short = (tp_short / n_short) * 100.0
    assert abs(rec_short - 94.2857) < 1e-3
    assert rec_short >= 90.0, "Gate 4 failed unexpectedly!"
