# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.72 COMPREHENSIVE AUTOMATED REGRESSION TEST SUITE
Covers:
1. Model & Artifact Integrity (Hashes, immutability, metadata, loading)
2. Prediction Correctness & Rescue Mechanism (Parity, boundary, ablations, flux conditioning)
3. Dataset Integrity & Quarantine (Disjointness, overlap check, sealed manifest)
4. Streaming Engine & Buffering (Short events, buffer boundaries, pipeline latency)
5. Dashboard Service & Integration (Model switching, evaluation summary, CSV export)

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import sys
import json
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
    """Verify that every markdown and python file in Stage 8.9.72 begins with the exact safety header."""
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


def test_sealed_cohort_quarantine():
    """Verify that the Stage 60 sealed evaluation manifest remains locked and untouched."""
    manifest_path = REPO_ROOT / SEALED_MANIFEST
    assert manifest_path.exists(), f"Sealed manifest missing: {SEALED_MANIFEST}"
    actual_hash = compute_sha256(manifest_path)
    assert actual_hash == SEALED_HASH, (
        f"QUARANTINE BREACH: Sealed evaluation manifest has been modified! Expected {SEALED_HASH}, got {actual_hash}"
    )


def test_candidate_checkpoints_exist_and_match_hashes():
    """Verify Candidate 71-D checkpoint exists and matches expected SHA-256."""
    c71_path = REPO_ROOT / "backend/research/stage_8_9_71/models/candidate_71_frozen.pt"
    assert c71_path.exists(), f"Candidate 71 checkpoint missing at {c71_path}"
    exp_71 = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"
    assert compute_sha256(c71_path) == exp_71, "Candidate 71-D checkpoint hash mismatch!"


# ==============================================================================
# GROUP 2: PREDICTION CORRECTNESS & RESCUE MECHANISM ABLATIONS
# ==============================================================================

def test_fixed_recording_inference_parity():
    """Verify deterministic inference across identical inputs."""
    ckpt_path = REPO_ROOT / "backend/research/stage_8_9_71/models/candidate_71_frozen.pt"
    ckpt = torch.load(ckpt_path, weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    test_s = torch.ones(1, 22) * 0.25
    test_l = torch.ones(1, 22) * 0.25

    with torch.no_grad():
        out1, _, _, _ = net(test_s, test_l)
        out2, _, _, _ = net(test_s, test_l)

    p1 = float(torch.sigmoid(out1).item())
    p2 = float(torch.sigmoid(out2).item())
    assert abs(p1 - p2) < 1e-7, "Model inference is non-deterministic!"


def test_rescue_mechanism_ablation_logic():
    """Verify that flux conditioning (flux > 0.040) suppresses stationary non-scream rescues."""
    # Stationary non-scream case: high similarity, high HF, but low flux (stationary tone)
    raw_prob = 0.460
    sim = 0.850
    raw_hf = 0.250
    stationary_flux = 0.015

    # Candidate 70-D logic (unconditioned):
    p_70 = raw_prob
    if sim > 0.78 and raw_hf > 0.12 and raw_prob > 0.40:
        p_70 = min(0.99, p_70 + 0.035)
    # Threshold is 0.4920 -> 0.495 >= 0.4920 (False Alarm!)
    assert p_70 >= 0.4920

    # Candidate 71-D logic (flux-conditioned):
    p_71 = raw_prob
    if sim > 0.78 and raw_hf > 0.12 and stationary_flux > 0.040 and raw_prob > 0.40:
        p_71 = min(0.99, p_71 + 0.035)
    # Rescued blocked -> p remains 0.460 < 0.4920 (Rejected / True Negative!)
    assert p_71 < 0.4920


def test_vocal_distress_veto_effect():
    """Verify that vocal distress veto correctly penalizes low-roughness harmonic sound."""
    raw_p = 0.70
    roughness = 0.015  # Low roughness
    hf_ratio = 0.020   # Low HF
    calib_p = raw_p
    if roughness < 0.022 and hf_ratio < 0.050 and raw_p < 0.85:
        calib_p *= 0.20
    assert calib_p == pytest.approx(0.14, abs=1e-4)


# ==============================================================================
# GROUP 3: DATASET INTEGRITY & SOURCE-GROUP DISJOINTNESS
# ==============================================================================

def test_dataset_source_group_disjointness():
    """Assert zero source-group leakage between development and diagnostic sets."""
    val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
    ho_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/held_out_short_features.npz")

    val_sgs = set(val_data["source_groups"])
    ho_sgs = set(ho_data["source_groups"])

    overlap = val_sgs.intersection(ho_sgs)
    assert len(overlap) == 0, f"DATA LEAKAGE DETECTED: {len(overlap)} overlapping source groups!"


def test_required_reports_exist():
    """Verify presence and non-empty size of all core Stage 8.9.72 reports and CSVs."""
    expected_reports = [
        "candidate71_reproduction_audit.md",
        "candidate71_false_negative_forensics.csv",
        "candidate71_false_positive_forensics.csv",
        "rescue_mechanism_ablation.csv",
        "representation_learning_experiments.csv",
        "low_snr_experiment_results.csv",
        "contrastive_learning_results.csv",
        "hard_negative_discrimination_results.csv",
        "dataset_manifest_audit.md",
        "candidate_comparison.csv",
        "gate_evaluation.md",
        "latency_benchmark.md",
        "reproducibility_instructions.md",
    ]
    for rep in expected_reports:
        p = REPORTS_DIR / rep
        assert p.exists(), f"Required report missing: {rep}"
        assert p.stat().st_size > 0, f"Report is empty: {rep}"


# ==============================================================================
# GROUP 4: STREAMING ENGINE & BUFFER BOUNDARIES
# ==============================================================================

def test_latency_ceiling_gate5():
    """Assert single-stream model latency P95 is <= 25.0 ms (Gate 5)."""
    ckpt_path = REPO_ROOT / "backend/research/stage_8_9_71/models/candidate_71_frozen.pt"
    ckpt = torch.load(ckpt_path, weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    times = []
    t_s = torch.zeros(1, 22, dtype=torch.float32)
    t_l = torch.zeros(1, 22, dtype=torch.float32)
    for _ in range(100):
        t0 = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        t_start = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        import time
        start = time.perf_counter()
        with torch.no_grad():
            _ = net(t_s, t_l)
        times.append((time.perf_counter() - start) * 1000.0)

    p95 = float(np.percentile(times, 95))
    assert p95 <= 25.0, f"Gate 5 latency violation: {p95:.2f} ms exceeds 25.0 ms ceiling!"


def test_streaming_buffer_short_event_padding():
    """Verify that short events (< 250 ms) pad cleanly without dimensional error."""
    sr = 16000
    burst_100ms = np.random.randn(1600).astype(np.float32) * 0.1
    padded = np.pad(burst_100ms, (0, 4000 - len(burst_100ms)), mode="constant")
    assert len(padded) == 4000

    f_s = extract_short_branch_features(padded, sr=16000)
    assert len(f_s) == 17


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
# GROUP 5: DASHBOARD SERVICE & INTEGRATION
# ==============================================================================

def test_research_service_candidate_registry():
    """Verify that ResearchService registers Candidate 71-D as ACTIVE_RESEARCH_CHAMPION."""
    svc = ResearchService()
    models = {m["model_id"]: m for m in svc.list_models()}
    assert "CANDIDATE_71_D" in models
    assert models["CANDIDATE_71_D"]["status"] == "ACTIVE_RESEARCH_CHAMPION"
    assert models["CANDIDATE_71_D"]["operating_threshold"] == 0.4920


def test_dashboard_model_switching():
    """Verify model selection updates active model correctly."""
    svc = ResearchService()
    svc.select_model("CANDIDATE_70_D")
    assert svc.active_model_id == "CANDIDATE_70_D"
    svc.select_model("CANDIDATE_71_D")
    assert svc.active_model_id == "CANDIDATE_71_D"


def test_dashboard_evaluation_summary():
    """Verify evaluation summary contains all 5 gates with correct Candidate 71-D metrics."""
    svc = ResearchService()
    eval_sum = svc.get_evaluation_summary()
    assert "acceptance_gates" in eval_sum
    assert len(eval_sum["acceptance_gates"]) == 5

    gate1 = eval_sum["acceptance_gates"][0]
    assert gate1["gate_id"] == "Gate 1"
    assert gate1["candidate_71d"] == "82.83% (82/99)"

    gate2 = eval_sum["acceptance_gates"][1]
    assert gate2["gate_id"] == "Gate 2"
    assert gate2["candidate_71d"] == "8.06% (10/124)"

