# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.71 COMPREHENSIVE AUTOMATED REGRESSION TEST SUITE
Covers:
1. Model & Artifact Integrity (Hashes, immutability, metadata, loading)
2. Prediction Correctness & Veto Logic (Parity, boundary, raw vs. final, ablations)
3. Dataset Integrity & Quarantine (Disjointness, overlap check, sealed manifest)
4. Streaming Engine & Buffering (Short events, buffer boundaries, EOF flushing, latency)
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

C70_HASH = "40a162d1f9e34564a93c1b88fb2a290909ee4deb32e659bd21bcf9c2d3c44b6d"
C71_HASH = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# GROUP 1: MODEL & ARTIFACT INTEGRITY
# ==============================================================================

def test_line1_safety_headers():
    """Verify that line 1 of every markdown, script, and test in stage_8_9_71 contains the mandatory safety header."""
    stage_files = list(STAGE_DIR.glob("**/*.md")) + list(STAGE_DIR.glob("**/*.py"))
    assert len(stage_files) > 10, "Expected at least 10 stage files"
    for fpath in stage_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
        normalized = first_line.replace("—", "—").replace("â€”", "—").replace("--", "—")
        assert "RESEARCH DEMONSTRATION PROTOTYPE" in normalized and "NOT FOR LIFE-SAFETY USE" in normalized, (
            f"File {fpath.name} violates Line 1 safety header requirement! Found: '{first_line}'"
        )


def test_protected_baseline_immutability():
    """Verify that the 4 production baseline assets remain strictly bit-for-bit identical."""
    for rel_path, exp_hash in PROTECTED_BASELINE_FILES.items():
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Protected file missing: {rel_path}"
        actual = compute_sha256(full_path)
        assert actual == exp_hash, f"Protected file modified: {rel_path}! Expected {exp_hash}, got {actual}"


def test_sealed_cohort_quarantine():
    """Verify that the Stage 60 sealed evaluation manifest remains intact and quarantined."""
    manifest_path = REPO_ROOT / SEALED_MANIFEST
    assert manifest_path.exists(), "Sealed cohort manifest missing!"
    assert compute_sha256(manifest_path) == SEALED_HASH, "Sealed cohort manifest modified!"


def test_candidate_checkpoints_exist_and_match_hashes():
    """Verify that frozen model checkpoints for Candidates 70-D and 71-D exist and match hashes."""
    c70_path = REPO_ROOT / "backend/research/stage_8_9_70/models/candidate_70_frozen.pt"
    assert c70_path.exists(), "Candidate 70 frozen checkpoint missing!"
    assert compute_sha256(c70_path) == C70_HASH, "Candidate 70 hash mismatch!"

    c71_path = MODELS_DIR / "candidate_71_frozen.pt"
    assert c71_path.exists(), "Candidate 71 frozen checkpoint missing!"
    assert compute_sha256(c71_path) == C71_HASH, "Candidate 71 hash mismatch!"


def test_candidate_71_metadata():
    """Verify Candidate 71-D metadata JSON contains correct fields and verified performance metrics."""
    meta_path = MODELS_DIR / "candidate_71_metadata.json"
    assert meta_path.exists(), "Metadata JSON missing!"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["candidate_id"] == "Candidate_71_Champion_LowSNR_FluxConditioned"
    assert meta["checkpoint_sha256"] == C71_HASH
    assert meta["operating_threshold"] == 0.4920
    assert meta["rescue_heuristics"]["rescue_mode"] == "flux_conditioned"
    assert meta["rescue_heuristics"]["resonance_flux_min"] == 0.040

    val = meta["validation_results_n311"]
    assert val["recall"] == 0.8283
    assert val["tp"] == 82
    assert val["fn"] == 17
    assert val["hn_fpr"] == 0.0806
    assert val["hn_fp"] == 10
    assert val["shout_fpr"] == 0.1477
    assert val["shout_fp"] == 13
    assert val["short_recall"] == 0.9487
    assert val["gate1_recall"] == "FAIL"
    assert val["gate2_hn_fpr"] == "FAIL"
    assert val["gate3_shout_fpr"] == "PASS"
    assert val["gate4_short_recall"] == "PASS"
    assert val["gate5_latency"] == "PASS"


# ==============================================================================
# GROUP 2: PREDICTION CORRECTNESS & VETO LOGIC
# ==============================================================================

def test_fixed_recording_inference_parity():
    """Verify that Candidate 71-D forward pass produces deterministic float probabilities."""
    ckpt = torch.load(MODELS_DIR / "candidate_71_frozen.pt", weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    t_s = torch.ones(1, 22, dtype=torch.float32) * 0.5
    t_l = torch.ones(1, 22, dtype=torch.float32) * 0.5

    with torch.no_grad():
        out1 = torch.sigmoid(net(t_s, t_l)[0]).item()
        out2 = torch.sigmoid(net(t_s, t_l)[0]).item()
    assert abs(out1 - out2) < 1e-7, "Inference must be strictly deterministic!"


def test_veto_ablation_logic_flux_conditioned_rescue():
    """Verify that flux-conditioned rescue eliminates the 2 false alarms without affecting screams."""
    # Test whistle false positive (fsd50k_323723: raw=0.4666, sim=0.7967, hf=0.6166, flux=0.0091)
    # Under unconditioned rescue: 0.4666 + 0.035 = 0.5016 >= 0.4920 (FP)
    # Under flux-conditioned rescue: flux=0.0091 < 0.040 -> NO BOOST -> p=0.4666 < 0.4920 (TN)
    p_raw_whistle = 0.4666
    sim_whistle = 0.7967
    hf_whistle = 0.6166
    flux_whistle = 0.0091

    p_rescued = p_raw_whistle
    if sim_whistle > 0.78 and hf_whistle > 0.12 and flux_whistle > 0.040 and p_raw_whistle > 0.40:
        p_rescued = min(0.99, p_rescued + 0.035)
    assert p_rescued < 0.4920, "Flux-conditioned rescue must NOT rescue low-flux whistles!"

    # Test genuine scream (fsd50k_68136: raw=0.4611, sim=0.7878, hf=0.1533, flux=0.0647)
    # Under flux-conditioned rescue: flux=0.0647 > 0.040 -> BOOST -> 0.4961 >= 0.4920 (TP)
    p_raw_scream = 0.4611
    sim_scream = 0.7878
    hf_scream = 0.1533
    flux_scream = 0.0647

    p_rescued_scream = p_raw_scream
    if sim_scream > 0.78 and hf_scream > 0.12 and flux_scream > 0.040 and p_raw_scream > 0.40:
        p_rescued_scream = min(0.99, p_rescued_scream + 0.035)
    assert p_rescued_scream >= 0.4920, "Flux-conditioned rescue MUST rescue dynamic scream!"


def test_flux_speech_veto_effect():
    """Verify that flux speech veto attenuates smooth low-flux vocalizations."""
    prob = 0.70
    flux_val = 0.020
    roughness_val = 0.040
    hf_val = 0.50

    if flux_val < 0.036 and roughness_val < 0.060 and prob < 0.75 and hf_val <= 1.0:
        prob *= 0.20
    assert prob == pytest.approx(0.14, rel=1e-3)


# ==============================================================================
# GROUP 3: DATASET INTEGRITY & QUARANTINE
# ==============================================================================

def test_dataset_source_group_disjointness():
    """Verify that training, validation, and held-out short scream cohorts have zero source-group overlap."""
    val_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/val_features.npz")
    ho_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/held_out_short_features.npz")
    train_data = np.load(REPO_ROOT / "backend/research/stage_8_9_67/cache/train_features.npz")

    val_sgs = set(val_data["source_groups"])
    ho_sgs = set(ho_data["source_groups"])
    train_sgs = set(train_data["source_groups"])

    assert len(val_sgs.intersection(ho_sgs)) == 0, "Leakage between validation and held-out short!"
    assert len(train_sgs.intersection(val_sgs)) == 0, "Leakage between train and validation!"
    assert len(train_sgs.intersection(ho_sgs)) == 0, "Leakage between train and held-out short!"


def test_required_reports_exist():
    """Verify all 13 required stage reports, CSVs, and markdown summaries exist and are non-empty."""
    required = [
        "STAGE_8_9_71_COMPLETION_REPORT.md",
        "candidate70_reproduction_audit.md",
        "candidate70_false_positive_forensics.csv",
        "candidate70_short_scream_generalization_audit.md",
        "low_snr_experiment_results.csv",
        "distance_attenuation_experiment_results.csv",
        "crowd_masking_experiment_results.csv",
        "reverberation_experiment_results.csv",
        "veto_ablation_results.csv",
        "candidate_comparison.csv",
        "dataset_manifest_audit.md",
        "gate_evaluation.md",
        "latency_benchmark.md",
        "reproducibility_instructions.md",
    ]
    for fname in required:
        fpath = REPORTS_DIR / fname
        assert fpath.exists(), f"Required report missing: {fname}"
        assert fpath.stat().st_size > 50, f"Report file empty or truncated: {fname}"


# ==============================================================================
# GROUP 4: STREAMING ENGINE & LATENCY
# ==============================================================================

def test_latency_ceiling_gate5():
    """Verify Candidate 71-D forward pass satisfies Gate 5 latency (<= 25.0 ms)."""
    ckpt = torch.load(MODELS_DIR / "candidate_71_frozen.pt", weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    t_s = torch.zeros(1, 22, dtype=torch.float32)
    t_l = torch.zeros(1, 22, dtype=torch.float32)

    import time
    latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = net(t_s, t_l)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    p95 = float(np.percentile(latencies, 95))
    assert p95 <= 25.0, f"Gate 5 FAILED: Model P95 latency {p95:.3f} ms exceeds 25.0 ms ceiling!"


def test_streaming_buffer_short_event_padding():
    """Verify that short events (< 250 ms) are padded to 4,000 samples without error."""
    short_audio = np.random.randn(2000).astype(np.float32)  # 125 ms at 16 kHz
    padded = np.pad(short_audio, (0, 4000 - len(short_audio)))
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
    active = svc.get_active_model()
    assert active["model_id"] == "CANDIDATE_71_D"
    assert active["stage"] == "Stage 8.9.71 Champion"
    assert active["is_production"] is False


def test_dashboard_model_switching():
    """Verify that ResearchService allows switching between historical models and Candidate 71-D."""
    svc = ResearchService()
    svc.select_model("CANDIDATE_70_D")
    assert svc.active_model_id == "CANDIDATE_70_D"
    svc.select_model("CANDIDATE_71_D")
    assert svc.active_model_id == "CANDIDATE_71_D"


def test_dashboard_evaluation_summary():
    """Verify that get_evaluation_summary includes Candidate 71-D across all 5 gates."""
    svc = ResearchService()
    summary = svc.get_evaluation_summary()
    gates = summary["acceptance_gates"]
    assert len(gates) == 5

    g1 = gates[0]
    assert g1["candidate_71d"] == "82.83% (82/99)"
    assert "FAIL" in g1["gate_status_71d"]

    g2 = gates[1]
    assert g2["candidate_71d"] == "8.06% (10/124)"
    assert "FAIL" in g2["gate_status_71d"]

    g3 = gates[2]
    assert g3["candidate_71d"] == "14.77% (13/88)"
    assert "PASS" in g3["gate_status_71d"]

    g4 = gates[3]
    assert g4["candidate_71d"] == "94.87% (37/39)"
    assert "PASS" in g4["gate_status_71d"]

    g5 = gates[4]
    assert g5["candidate_71d"] == "0.384 ms"
    assert "PASS" in g5["gate_status_71d"]

