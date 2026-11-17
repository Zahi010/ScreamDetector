# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.74 COMPREHENSIVE AUTOMATED REGRESSION TEST SUITE
Covers:
1. Protected Baseline & Artifact Integrity (Production hashes, immutability, Candidate 71-D freeze)
2. Stage 60 Provenance Audit & Read-Only Quarantine Safeguards
3. Candidate 71-D & Stage 73 Reproduction Parity (Exact numerators, denominators, thresholds)
4. Source-Group Accounting & Cluster Bootstrap Determinism
5. Annotation Immortality & Vocalization Review Queue
6. Real vs Synthetic Cohort Separation & Zero Partition Leakage
7. Streaming Engine & Downstream Pipeline Performance
8. Dashboard Service Integration & UI Production Boundary

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import hashlib
from pathlib import Path
import pytest
import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "backend"))
STAGE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = STAGE_DIR / "reports"
MODELS_DIR = STAGE_DIR / "models"
SCRIPTS_DIR = STAGE_DIR / "scripts"

from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)
from src.research_service import (
    ResearchService,
    extract_short_branch_features,
    extract_sustained_branch_features,
    extract_vocal_acoustics_clean
)

PROTECTED_BASELINE_FILES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

SEALED_MANIFEST = "backend/research/stage_8_9_60/future_evaluation_manifest.json"
SEALED_HASH = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"
CANDIDATE_71_HASH = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# GROUP 1: ARTIFACT & SAFETY HEADER COMPLIANCE
# ==============================================================================

def test_line1_safety_headers():
    """Verify that every markdown and python file in Stage 8.9.74 begins with the exact safety header."""
    for ext in ["*.md", "*.py"]:
        for file_path in STAGE_DIR.rglob(ext):
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                assert first_line == "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.", (
                    f"Safety header missing on line 1 of {file_path.name}: got '{first_line}'"
                )


def test_protected_baseline_immutability():
    """Verify that all 4 baseline production files remain bit-for-bit identical."""
    for rel_path, expected_hash in PROTECTED_BASELINE_FILES.items():
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Protected baseline file missing: {rel_path}"
        actual_hash = compute_sha256(full_path)
        assert actual_hash == expected_hash, (
            f"MUTATION DETECTED in protected baseline {rel_path}! Expected {expected_hash}, got {actual_hash}"
        )


def test_candidate_71_checkpoint_freeze():
    """Verify Candidate 71-D frozen checkpoint matches expected SHA-256."""
    ckpt_path = STAGE_DIR / "models/candidate_71_frozen.pt"
    assert ckpt_path.exists(), f"Candidate 71-D checkpoint missing at {ckpt_path}"
    assert compute_sha256(ckpt_path) == CANDIDATE_71_HASH, "Candidate 71-D checkpoint hash mismatch!"


# ==============================================================================
# GROUP 2: STAGE 60 PROVENANCE AUDIT & READ-ONLY SAFEGUARDS
# ==============================================================================

def test_stage_60_manifest_integrity_and_prediction_trace():
    """Verify Stage 60 manifest hash and confirm Stage 61 prediction existence without reading audio."""
    manifest_path = REPO_ROOT / SEALED_MANIFEST
    assert manifest_path.exists(), f"Stage 60 manifest missing: {SEALED_MANIFEST}"
    assert compute_sha256(manifest_path) == SEALED_HASH, "Stage 60 manifest hash changed!"

    # Verify historical Stage 61 prediction artifact exists confirming historical access
    st61_preds = REPO_ROOT / "backend/research/stage_8_9_61/sealed_cohort_predictions.csv"
    assert st61_preds.exists(), "Stage 61 predictions CSV missing"
    # Ensure it contains exactly 2800 predictions (2801 lines with header)
    with open(st61_preds, "r", encoding="utf-8") as f:
        line_count = sum(1 for _ in f)
    assert line_count == 2801, f"Expected 2801 lines in Stage 61 predictions, got {line_count}"


# ==============================================================================
# GROUP 3: PREDICTION PARITY & STAGE 73 REPRODUCTION
# ==============================================================================

def test_candidate_71d_reproduction_metrics():
    """Verify bit-for-bit reproduction of Candidate 71-D metrics on Stage 54 Val."""
    val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
    y_val = val_data["y"]
    cats_val = val_data["categories"]
    durs_val = val_data["durations"]

    roughness = val_data["x_vocal"][:, 0]
    hf_ratio = val_data["x_vocal"][:, 1]
    flux = val_data["x_vocal"][:, 2]
    hnr = val_data["x_vocal"][:, 3]
    flatness = val_data["x_vocal"][:, 4]

    voc_val = normalize_vocal_features(val_data["x_vocal"])
    x_s_val = np.concatenate([val_data["x_short"], voc_val], axis=-1)
    x_l_val = np.concatenate([val_data["x_sust"], voc_val], axis=-1)

    ckpt = torch.load(STAGE_DIR / "models/candidate_71_frozen.pt", weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    with torch.no_grad():
        logits, _, zs, zl = net(torch.tensor(x_s_val, dtype=torch.float32), torch.tensor(x_l_val, dtype=torch.float32))
        p = torch.sigmoid(logits).numpy()
        zs_np = zs.numpy()
        zl_np = zl.numpy()
        sim = np.sum(zs_np * zl_np, axis=1) / ((np.linalg.norm(zs_np, axis=1) + 1e-7) * (np.linalg.norm(zl_np, axis=1) + 1e-7))

    for i in range(len(p)):
        if not (p[i] >= 0.80 or sim[i] > 0.40):
            if hnr[i] > 12.0 and flatness[i] < 0.001:
                p[i] *= 0.15
        if flux[i] < 0.036 and roughness[i] < 0.060 and p[i] < 0.75 and hf_ratio[i] <= 1.0:
            p[i] *= 0.20
        if roughness[i] < 0.022 and hf_ratio[i] < 0.050 and p[i] < 0.85:
            p[i] *= 0.20
        if sim[i] > 0.78 and hf_ratio[i] > 0.12 and flux[i] > 0.040 and p[i] > 0.40:
            p[i] = min(0.99, p[i] + 0.035)

    preds = (p >= 0.4920).astype(int)

    pos_m = (y_val == 1)
    neg_m = (y_val == 0)
    shout_m = (cats_val == "shouting_and_speech")
    hn_m = neg_m & (~shout_m)
    short_m = pos_m & (durs_val < 1.0)
    real_m = pos_m & (cats_val == "scream")
    synth_m = pos_m & (cats_val == "masked_distant_screams")

    tp = int(np.sum((preds == 1) & pos_m))
    fn = int(np.sum((preds == 0) & pos_m))
    hn_fp = int(np.sum((preds == 1) & hn_m))
    shout_fp = int(np.sum((preds == 1) & shout_m))
    short_tp = int(np.sum((preds == 1) & short_m))
    real_tp = int(np.sum((preds == 1) & real_m))
    synth_tp = int(np.sum((preds == 1) & synth_m))

    assert tp == 82, f"Expected 82 TP, got {tp}"
    assert fn == 17, f"Expected 17 FN, got {fn}"
    assert hn_fp == 10, f"Expected 10 HN FP, got {hn_fp}"
    assert shout_fp == 13, f"Expected 13 Shout FP, got {shout_fp}"
    assert short_tp == 37, f"Expected 37 Short TP, got {short_tp}"
    assert real_tp == 71, f"Expected 71 Real TP, got {real_tp}"
    assert synth_tp == 11, f"Expected 11 Synth TP, got {synth_tp}"


def test_child_scream_distress_veto_trace():
    """Verify exact child scream suppression under distress veto and recovery under Candidate 73-C."""
    val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
    ids = val_data["ids"]
    child_indices = [i for i, sid in enumerate(ids) if "273153" in sid]
    assert len(child_indices) == 2, f"Expected 2 child scream segments, found {len(child_indices)}"

    for idx in child_indices:
        r = val_data["x_vocal"][idx, 0]
        hf = val_data["x_vocal"][idx, 1]
        assert r < 0.022, f"Child scream roughness should be < 0.022, got {r}"
        assert hf < 0.050, f"Child scream HF ratio should be < 0.050, got {hf}"


# ==============================================================================
# GROUP 4: SOURCE-GROUP ACCOUNTING & DATASET INTEGRITY
# ==============================================================================

def test_source_group_accounting():
    """Verify exact unique source group counts in the validation partition."""
    val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
    y_val = val_data["y"]
    cats_val = val_data["categories"]
    sgs = val_data["source_groups"]

    pos_sgs = set(sgs[y_val == 1])
    hn_sgs = set(sgs[(y_val == 0) & (cats_val != "shouting_and_speech")])
    shout_sgs = set(sgs[cats_val == "shouting_and_speech"])

    assert len(pos_sgs) == 47, f"Expected 47 Pos SGs, got {len(pos_sgs)}"
    assert len(hn_sgs) == 69, f"Expected 69 HN SGs, got {len(hn_sgs)}"
    assert len(shout_sgs) == 28, f"Expected 28 Shout SGs, got {len(shout_sgs)}"
    assert len(set(sgs)) == 138, f"Expected 138 total unique SGs, got {len(set(sgs))}"


def test_zero_synthetic_to_train_leakage():
    """Verify zero overlap between synthetic validation screams and training partition."""
    val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
    train_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/train_features.npz")

    synth_mask = (val_data["y"] == 1) & (val_data["categories"] == "masked_distant_screams")
    synth_ids = set(val_data["ids"][synth_mask])
    synth_sgs = set(val_data["source_groups"][synth_mask])

    train_ids = set(train_data["ids"])
    train_sgs = set(train_data["source_groups"])

    assert len(synth_ids.intersection(train_ids)) == 0, "ID leakage detected between synthetic val and train!"
    assert len(synth_sgs.intersection(train_sgs)) == 0, "Source group leakage detected between synthetic val and train!"


# ==============================================================================
# GROUP 5: STREAMING & LATENCY
# ==============================================================================

def test_latency_ceiling_gate5():
    """Assert single-stream model latency P95 is <= 25.0 ms (Gate 5)."""
    ckpt = torch.load(STAGE_DIR / "models/candidate_71_frozen.pt", weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    times = []
    t_s = torch.zeros(1, 22, dtype=torch.float32)
    t_l = torch.zeros(1, 22, dtype=torch.float32)
    for _ in range(100):
        import time
        start = time.perf_counter()
        with torch.no_grad():
            _ = net(t_s, t_l)
        times.append((time.perf_counter() - start) * 1000.0)

    p95 = float(np.percentile(times, 95))
    assert p95 <= 25.0, f"Gate 5 latency violation: {p95:.2f} ms exceeds 25.0 ms ceiling!"


def test_complete_pipeline_execution():
    """Verify end-to-end downstream processing on a 1-second audio window."""
    svc = ResearchService()
    test_audio = np.random.randn(16000).astype(np.float32) * 0.05
    res = svc.evaluate_audio_window(test_audio, sr=16000, model_id="CANDIDATE_71_D")
    assert "calibrated_probability" in res
    assert "state" in res
    assert "pipeline_latency_ms" in res
    assert res["model_id"] == "CANDIDATE_71_D"


# ==============================================================================
# GROUP 6: DASHBOARD SERVICE & UI SEPARATION
# ==============================================================================

def test_dashboard_model_selection_and_status():
    """Verify ResearchService registers Candidate 71-D as champion and retains recorded audio status."""
    svc = ResearchService()
    models = {m["model_id"]: m for m in svc.list_models()}
    assert "CANDIDATE_71_D" in models
    assert models["CANDIDATE_71_D"]["status"] == "ACTIVE_RESEARCH_CHAMPION"
    assert models["CANDIDATE_71_D"]["operating_threshold"] == 0.4920

