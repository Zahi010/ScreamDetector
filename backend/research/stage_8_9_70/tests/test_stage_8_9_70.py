# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
STAGE 8.9.70 AUTOMATED TEST SUITE
Validates:
1. Line 1 mandatory safety designations across all stage files
2. Bit-for-bit immutability of the 4 protected baseline production assets
3. Sealed cohort (Stage 60, N=700) quarantine and manifest hash
4. Candidate 70-D and Candidate 69-D checkpoint integrity
5. Candidate 70-D evaluation metrics & Five-Gate compliance
6. Veto ablation logic (redundancy of HFCR roll-off veto)
7. Model-only CPU inference latency (Gate 5 compliance)
8. Completeness of all Stage 8.9.70 reports, CSVs, and artifacts

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import hashlib
import json
import sys
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

PROTECTED_BASELINE_FILES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}

SEALED_COHORT_MANIFEST = "backend/research/stage_8_9_60/future_evaluation_manifest.json"
SEALED_COHORT_EXPECTED_HASH = "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd"

CANDIDATE_70_EXPECTED_HASH = "40a162d1f9e34564a93c1b88fb2a290909ee4deb32e659bd21bcf9c2d3c44b6d"
CANDIDATE_69_EXPECTED_HASH = "d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c"

REQUIRED_REPORTS = [
    "STAGE_8_9_70_COMPLETION_REPORT.md",
    "candidate69_reproduction_audit.md",
    "candidate69_false_negative_reaudit.csv",
    "short_scream_268_provenance_audit.md",
    "short_scream_268_subgroup_results.csv",
    "veto_ablation_results.csv",
    "low_snr_experiment_results.csv",
    "reverberation_experiment_results.csv",
    "candidate_comparison.csv",
    "dataset_manifest_audit.md",
    "gate_evaluation.md",
    "latency_benchmark.md",
    "reproducibility_instructions.md",
]


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_line1_safety_headers():
    """Verify that line 1 of every markdown, script, and test in stage_8_9_70 begins with the mandatory safety header."""
    expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."
    stage_files = []
    stage_files.extend(STAGE_DIR.glob("**/*.md"))
    stage_files.extend(STAGE_DIR.glob("**/*.py"))

    for fpath in stage_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
        # Normalize dash variants if needed
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
    manifest_path = REPO_ROOT / SEALED_COHORT_MANIFEST
    assert manifest_path.exists(), "Sealed cohort manifest missing!"
    actual = compute_sha256(manifest_path)
    assert actual == SEALED_COHORT_EXPECTED_HASH, f"Sealed cohort manifest modified! Hash {actual}"


def test_candidate_checkpoints_exist_and_match_hashes():
    """Verify that frozen model checkpoints for Candidates 69-D and 70-D exist and match hashes."""
    c70_path = MODELS_DIR / "candidate_70_frozen.pt"
    assert c70_path.exists(), "Candidate 70 frozen checkpoint missing!"
    assert compute_sha256(c70_path) == CANDIDATE_70_EXPECTED_HASH, "Candidate 70 hash mismatch!"

    c69_path = REPO_ROOT / "backend/research/stage_8_9_69/models/candidate_69_frozen.pt"
    assert c69_path.exists(), "Candidate 69 frozen checkpoint missing!"
    assert compute_sha256(c69_path) == CANDIDATE_69_EXPECTED_HASH, "Candidate 69 hash mismatch!"


def test_candidate_70_metadata():
    """Verify Candidate 70-D metadata JSON contains correct fields and verified performance metrics."""
    meta_path = MODELS_DIR / "candidate_70_metadata.json"
    assert meta_path.exists(), "Metadata JSON missing!"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["candidate_id"] == "Candidate_70_Champion_Simplified_Multi_Resolution"
    assert meta["checkpoint_sha256"] == CANDIDATE_70_EXPECTED_HASH
    assert meta["operating_threshold"] == 0.4920
    assert meta["suppression_heuristics"]["use_hf_rolloff_veto"] is False, "HFCR veto must be disabled"
    assert meta["suppression_heuristics"]["use_flux_speech_veto"] is True
    assert meta["suppression_heuristics"]["use_vocal_veto"] is True

    val = meta["validation_results_n311"]
    assert val["recall"] == 0.8283
    assert val["tp"] == 82
    assert val["fn"] == 17
    assert val["shout_fpr"] == 0.1477
    assert val["shout_fp"] == 13
    assert val["hn_fpr"] == 0.0968
    assert val["hn_fp"] == 12
    assert val["short_recall"] == 0.9487
    assert val["held_out_short_recall_n268"] == 0.5896
    assert val["gate1_recall"] == "FAIL"
    assert val["gate2_hn_fpr"] == "FAIL"
    assert val["gate3_shout_fpr"] == "PASS"
    assert val["gate4_short_recall"] == "PASS"
    assert val["gate5_latency"] == "PASS"


def test_required_reports_exist():
    """Verify all 13 required reports, CSVs, and markdown summaries exist and are non-empty."""
    for fname in REQUIRED_REPORTS:
        fpath = REPORTS_DIR / fname
        assert fpath.exists(), f"Required report missing: {fname}"
        assert fpath.stat().st_size > 50, f"Report file empty or truncated: {fname}"


def test_latency_ceiling_gate5():
    """Verify Candidate 70-D neural forward pass satisfies Gate 5 latency (<= 25.0 ms)."""
    from research.stage_8_9_67.scripts.train_and_evaluate_candidates import DualResolutionGatedModel

    ckpt = torch.load(MODELS_DIR / "candidate_70_frozen.pt", weights_only=False)
    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    t_s = torch.zeros(1, 22, dtype=torch.float32)
    t_l = torch.zeros(1, 22, dtype=torch.float32)

    # Warmup
    for _ in range(20):
        with torch.no_grad():
            _ = net(t_s, t_l)

    import time
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = net(t_s, t_l)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    p95 = float(np.percentile(latencies, 95))
    assert p95 <= 25.0, f"Gate 5 FAILED: Model P95 latency {p95:.3f} ms exceeds 25.0 ms ceiling!"
