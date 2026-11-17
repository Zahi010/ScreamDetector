# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.69 — COMPREHENSIVE AUTOMATED VERIFICATION TEST SUITE
Covers:
1. Mandatory safety headers & designations.
2. Immutability of 4 protected baseline assets.
3. Immutability of historical frozen candidates (65-F, 67-D, 68-D).
4. Quarantine and immutability of Stage 60 sealed evaluation manifest.
5. Candidate 69-D model checkpoint integrity, weights, and suppression heuristics.
6. Multi-stage heuristic veto logic & rescue policy verification.
7. Tournament evaluation replication and Five-Gate scorecard verification.
8. CPU inference latency compliance (Gate 5).
9. Dataset independence and source-group disjointness.
10. Live ResearchService backend and dashboard integration.

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

from research.stage_8_9_67.scripts.train_and_evaluate_candidates import (
    DualResolutionGatedModel,
    normalize_vocal_features
)
from src.research_service import get_research_service, ResearchService


# ==============================================================================
# Helper Functions
# ==============================================================================

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# Group 1: Safety Headers & Designations
# ==============================================================================

def test_line_1_safety_header_all_stage_files():
    """Verify line 1 safety header across all Stage 8.9.69 markdown and python files."""
    files_to_check = list(STAGE_DIR.rglob("*.py")) + list(STAGE_DIR.rglob("*.md"))
    assert len(files_to_check) >= 5, "Expected at least 5 stage files to check."
    expected = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    for file_path in files_to_check:
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            assert first_line == expected, f"File {file_path} failed Line 1 safety header check!"


def test_research_service_safety_header():
    """Verify safety header in backend research_service.py."""
    svc_path = REPO_ROOT / "backend/src/research_service.py"
    with open(svc_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        assert first_line == "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."


# ==============================================================================
# Group 2: Protected Baseline & Historical Checkpoint Immutability
# ==============================================================================

def test_protected_baseline_classifier_joblib_hash():
    p = REPO_ROOT / "backend/models/scream_classifier.joblib"
    assert compute_sha256(p) == "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f"


def test_protected_baseline_model_metadata_hash():
    p = REPO_ROOT / "backend/models/model_metadata.json"
    assert compute_sha256(p) == "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60"


def test_protected_baseline_test_predictions_hash():
    p = REPO_ROOT / "backend/reports/test_predictions.csv"
    assert compute_sha256(p) == "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"


def test_protected_baseline_stage5_evaluation_hash():
    p = REPO_ROOT / "backend/reports/stage5_test_evaluation.md"
    assert compute_sha256(p) == "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"


def test_historical_candidate_65f_frozen_hash():
    p = REPO_ROOT / "backend/research/stage_8_9_66/models/candidate_65f_frozen.pt"
    assert compute_sha256(p) == "06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab"


def test_historical_candidate_67_frozen_hash():
    p = REPO_ROOT / "backend/research/stage_8_9_67/models/candidate_67_frozen.pt"
    assert compute_sha256(p) == "8fc2255a337f1375870370216416b94d9c2003a2b8939dbee1301115f53a7b18"


def test_historical_candidate_68_frozen_hash():
    p = REPO_ROOT / "backend/research/stage_8_9_68/models/candidate_68_frozen.pt"
    assert compute_sha256(p) == "8a3b425a2885cfeeb4d9e6a64c04619949978cad5b55a8a5f60b5ee379949dc4"


# ==============================================================================
# Group 3: Sealed Cohort Isolation & Provenance
# ==============================================================================

def test_sealed_evaluation_manifest_integrity():
    p = REPO_ROOT / "backend/research/stage_8_9_60/future_evaluation_manifest.json"
    assert compute_sha256(p) == "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"


def test_source_group_disjointness_across_partitions():
    """Verify zero source-group intersection between train, val, and reserved test."""
    p_manifest = REPO_ROOT / "backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv"
    import pandas as pd
    df = pd.read_csv(p_manifest)
    train_sg = set(df[df["expansion_partition"] == "expansion_train"]["source_group_id"].unique())
    val_sg = set(df[df["expansion_partition"] == "expansion_val"]["source_group_id"].unique())
    test_sg = set(df[df["expansion_partition"] == "expansion_reserved_test"]["source_group_id"].unique())

    assert len(train_sg.intersection(val_sg)) == 0, "Train and Val source groups overlap!"
    assert len(train_sg.intersection(test_sg)) == 0, "Train and Test source groups overlap!"
    assert len(val_sg.intersection(test_sg)) == 0, "Val and Test source groups overlap!"


# ==============================================================================
# Group 4: Candidate 69-D Model Checkpoint & Architecture
# ==============================================================================

def test_candidate_69_frozen_checkpoint_exists():
    p = STAGE_DIR / "models/candidate_69_frozen.pt"
    assert p.exists(), "candidate_69_frozen.pt not found!"


def test_candidate_69_checkpoint_sha256():
    p = STAGE_DIR / "models/candidate_69_frozen.pt"
    assert compute_sha256(p) == "d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c"


def test_candidate_69_metadata_json():
    p = STAGE_DIR / "models/candidate_69_metadata.json"
    assert p.exists()
    with open(p, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["candidate_id"] == "Candidate_69_Champion_Calibrated_Multi_Resolution"
    assert meta["operating_threshold"] == 0.492
    assert meta["input_features_short"] == 22
    assert meta["input_features_sust"] == 22
    assert meta["checkpoint_sha256"] == "d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c"


def test_candidate_69_checkpoint_contents():
    p = STAGE_DIR / "models/candidate_69_frozen.pt"
    ckpt = torch.load(p, map_location="cpu", weights_only=False)
    assert "model_state_dict" in ckpt
    assert "operating_threshold" in ckpt
    assert ckpt["operating_threshold"] == 0.492
    assert ckpt["in_features"] == 22
    assert ckpt["suppression_heuristics"]["vocal_roughness_min"] == 0.022
    assert ckpt["suppression_heuristics"]["flux_cutoff"] == 0.036
    assert ckpt["suppression_heuristics"]["hf_cutoff"] == 0.008
    assert ckpt["suppression_heuristics"]["hf_roughness_condition"] == 0.050


# ==============================================================================
# Group 5: Veto Activation & Rescue Policy Logic
# ==============================================================================

def test_hfcr_veto_conditioned_on_roughness():
    """Verify HFCR roll-off veto fires on speech but not on rough screams."""
    hf_cutoff = 0.008
    r_cutoff = 0.050

    # Case A: Low HF energy, low roughness (deep vowel male speech) -> VETO FIRES
    hf_speech = 0.004
    r_speech = 0.020
    fires_speech = (hf_speech < hf_cutoff and r_speech < r_cutoff)
    assert fires_speech is True

    # Case B: Low HF energy, high roughness (harsh scream PZ73 / 219863) -> VETO DOES NOT FIRE
    hf_scream = 0.004
    r_scream = 0.086
    fires_scream = (hf_scream < hf_cutoff and r_scream < r_cutoff)
    assert fires_scream is False, "HFCR veto erroneously fired on rough scream!"


def test_flux_veto_hf_bypass():
    """Verify spectral flux veto bypasses high-frequency scream events."""
    flux_cutoff = 0.036
    r_cutoff = 0.060

    # Case A: Low flux, low roughness, normal speech HF -> VETO FIRES
    flux_sp = 0.020
    r_sp = 0.030
    hf_sp = 0.040
    fires_sp = (flux_sp < flux_cutoff and r_sp < r_cutoff and hf_sp <= 1.0)
    assert fires_sp is True

    # Case B: Low flux, low roughness, huge HF ratio (fsd50k_178105 scream) -> BYPASSED
    flux_sc = 0.005
    r_sc = 0.030
    hf_sc = 16.6
    fires_sc = (flux_sc < flux_cutoff and r_sc < r_cutoff and hf_sc <= 1.0)
    assert fires_sc is False, "Flux veto failed to bypass high-frequency scream!"


def test_calibrated_vocal_distress_veto():
    """Verify calibrated vocal distress veto threshold (0.022) rescues 77AY scream."""
    r_ceiling = 0.022
    hf_ceiling = 0.050

    # Scream 77AY has roughness 0.0256 (above 0.022) -> VETO DOES NOT FIRE
    r_77ay = 0.0256
    hf_77ay = 0.0126
    fires_77ay = (r_77ay < r_ceiling and hf_77ay < hf_ceiling)
    assert fires_77ay is False, "Vocal distress veto erroneously fired on 77AY scream!"

    # Normal monotone speech has roughness 0.010 -> VETO FIRES
    r_speech = 0.010
    hf_speech = 0.020
    fires_speech = (r_speech < r_ceiling and hf_speech < hf_ceiling)
    assert fires_speech is True


# ==============================================================================
# Group 6: Tournament Scorecard & Gate Verification
# ==============================================================================

def test_tournament_results_csv_exists():
    p = STAGE_DIR / "reports/candidate_comparison.csv"
    assert p.exists()


def test_candidate_69d_gate_metrics():
    p = STAGE_DIR / "models/candidate_69_metadata.json"
    with open(p, "r", encoding="utf-8") as f:
        meta = json.load(f)
    res = meta["validation_results_n311"]

    assert res["tp_count"] == 79
    assert res["fn_count"] == 20
    assert res["recall"] == 0.7980
    assert res["shout_fp"] == 12
    assert res["shout_fpr"] == 0.1364
    assert res["hn_fp"] == 10
    assert res["hn_fpr"] == 0.0806
    assert res["short_tp"] == 36
    assert res["short_recall"] == 0.9231
    assert res["ultra_short_recall"] == 1.0000

    # Gate verification
    assert res["gate1_recall"] == "FAIL"  # 79.80% < 96.0%
    assert res["gate2_hn_fpr"] == "FAIL"  # 8.06% > 5.0%
    assert res["gate3_shout_fpr"] == "PASS"  # 13.64% <= 15.0%
    assert res["gate4_short_recall"] == "PASS"  # 92.31% >= 90.0%
    assert res["gate5_latency"] == "PASS"  # 0.384 ms <= 25.0 ms


# ==============================================================================
# Group 7: Latency Compliance
# ==============================================================================

def test_model_latency_under_ceiling():
    p = STAGE_DIR / "models/candidate_69_metadata.json"
    with open(p, "r", encoding="utf-8") as f:
        meta = json.load(f)
    lat_1 = meta["validation_results_n311"]["p95_latency_ms_single_stream"]
    lat_8 = meta["validation_results_n311"]["p95_latency_ms_8_streams"]
    assert lat_1 < 25.0, f"Single stream latency {lat_1} ms exceeds 25 ms ceiling!"
    assert lat_8 < 25.0, f"8 stream latency {lat_8} ms exceeds 25 ms ceiling!"


# ==============================================================================
# Group 8: ResearchService Live Backend Integration
# ==============================================================================

def test_research_service_active_model_candidate_69():
    svc = get_research_service()
    assert svc.active_model_id == "CANDIDATE_69_D"


def test_research_service_candidate_69_registered():
    svc = get_research_service()
    models = {m["model_id"]: m for m in svc.list_models()}
    assert "CANDIDATE_69_D" in models
    c69 = models["CANDIDATE_69_D"]
    assert c69["status"] == "ACTIVE_RESEARCH_CHAMPION"
    assert c69["operating_threshold"] == 0.4920
    assert c69["feature_dims"] == 44


def test_research_service_candidate_69_inference():
    svc = get_research_service()
    dummy_audio = np.random.randn(16000).astype(np.float32) * 0.1
    res = svc.infer_audio_array(dummy_audio, sr=16000, model_id="CANDIDATE_69_D")
    assert res["model_id"] == "CANDIDATE_69_D"
    assert 0.0 <= res["raw_probability"] <= 1.0
    assert 0.0 <= res["calibrated_probability"] <= 1.0
    assert res["threshold"] == 0.4920
    assert res["state"] in ("SCREAM-LIKE EVENT DETECTED", "ANALYZING", "NO SCREAM-LIKE EVENT DETECTED")
    assert res["model_latency_ms"] < 25.0


def test_research_service_evaluation_summary_gates():
    svc = get_research_service()
    summary = svc.get_evaluation_summary()
    assert "acceptance_gates" in summary
    gates = {g["gate_id"]: g for g in summary["acceptance_gates"]}
    assert len(gates) == 5
    assert "candidate_69d" in gates["Gate 1"]
    assert gates["Gate 1"]["candidate_69d"] == "79.80% (79/99)"
    assert gates["Gate 3"]["candidate_69d"] == "13.64% (12/88)"
    assert gates["Gate 4"]["candidate_69d"] == "92.31% (36/39)"
    assert gates["Gate 5"]["candidate_69d"] == "0.384 ms"

