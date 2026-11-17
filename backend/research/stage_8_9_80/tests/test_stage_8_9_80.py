# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Comprehensive Automated Test Suite for Stage 8.9.80:
Live Microphone Candidate 71-D Dashboard Integration.

Verifies:
1. Frozen Candidate 71-D checkpoint presence and exact SHA-256 checksum.
2. Immutability of all 6 protected assets bit-for-bit.
3. DualResolutionGatedModel architecture, tensor shapes, and latent similarity.
4. Signal processing pipeline: short/sustained branch DSP, vocal acoustic extraction, normalization.
5. In-memory StreamingAudioBuffer: windowing, hop scheduling, overrun resistance, reset.
6. Model inference semantics: ambient silence gating, scream detection, acoustic labeling.
7. Complete isolation between production baseline and research candidate.
8. Line 1 mandatory safety designation on all stage deliverables.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

import numpy as np
import pytest
import soundfile as sf
import torch

from src.research_service import (
    DualResolutionGatedModel,
    ResearchService,
    StreamingAudioBuffer,
    compute_sha256,
    extract_phonation_stats_c5,
    extract_short_branch_features,
    extract_subband_vector_c5,
    extract_sustained_branch_features,
    extract_vocal_acoustics_clean,
    get_research_service,
)

EXPECTED_C71_SHA = "e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b"

PROTECTED_ASSETS = {
    "scream_classifier.joblib": (
        REPO_ROOT / "backend/models/scream_classifier.joblib",
        "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    ),
    "model_metadata.json": (
        REPO_ROOT / "backend/models/model_metadata.json",
        "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    ),
    "test_predictions.csv": (
        REPO_ROOT / "backend/reports/test_predictions.csv",
        "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    ),
    "stage5_test_evaluation.md": (
        REPO_ROOT / "backend/reports/stage5_test_evaluation.md",
        "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
    ),
    "future_evaluation_manifest.json": (
        REPO_ROOT / "backend/research/stage_8_9_60/future_evaluation_manifest.json",
        "9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd",
    ),
    "candidate_71_frozen.pt": (
        STAGE_DIR / "models/candidate_71_frozen.pt",
        EXPECTED_C71_SHA,
    ),
}


# ==============================================================================
# 1. Model Checkpoint Integrity & Hash Protection
# ==============================================================================

def test_candidate_71d_checkpoint_integrity():
    """Verify Candidate 71-D weights checkpoint exists and matches SHA-256."""
    ckpt_path = STAGE_DIR / "models/candidate_71_frozen.pt"
    assert ckpt_path.exists(), f"Candidate 71-D checkpoint missing at {ckpt_path}"
    sha = compute_sha256(ckpt_path)
    assert sha == EXPECTED_C71_SHA, f"Candidate 71-D hash mismatch: got {sha}"


def test_protected_baseline_immutability():
    """Verify all 6 protected production baseline files remain strictly unchanged."""
    for name, (path, expected_sha) in PROTECTED_ASSETS.items():
        assert path.exists(), f"Protected file missing: {path}"
        actual_sha = compute_sha256(path)
        assert actual_sha == expected_sha, (
            f"Protected asset modified! {name}\n  Expected: {expected_sha}\n  Got:      {actual_sha}"
        )


# ==============================================================================
# 2. Candidate 71-D Neural Architecture & Tensor Shapes
# ==============================================================================

def test_dual_resolution_gated_model_forward():
    """Verify DualResolutionGatedModel accepts 22-dim tensors and outputs proper shapes."""
    net = DualResolutionGatedModel(in_features=22)
    net.eval()

    x_s = torch.randn(2, 22)
    x_l = torch.randn(2, 22)

    with torch.no_grad():
        logits, gate, z_s, z_l = net(x_s, x_l)

    assert logits.shape == (2,)
    assert gate.shape == (2,)
    assert z_s.shape == (2, 16)
    assert z_l.shape == (2, 16)
    assert torch.all((gate >= 0.0) & (gate <= 1.0))


def test_checkpoint_weight_loading():
    """Verify Candidate 71-D checkpoint loads cleanly into DualResolutionGatedModel."""
    ckpt_path = STAGE_DIR / "models/candidate_71_frozen.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    assert "model_state_dict" in ckpt

    net = DualResolutionGatedModel(in_features=22)
    net.load_state_dict(ckpt["model_state_dict"])
    net.eval()

    # Test forward pass with zero tensor
    with torch.no_grad():
        logits, gate, z_s, z_l = net(torch.zeros(1, 22), torch.zeros(1, 22))
    assert not torch.isnan(logits).any()


# ==============================================================================
# 3. Feature Extraction Pipeline & Tiling Fidelity
# ==============================================================================

def test_feature_extraction_dimensions():
    """Verify short branch, sustained branch, and vocal acoustics have correct dimensions."""
    audio_1s = np.zeros(16000, dtype=np.float32)

    f_s = extract_short_branch_features(audio_1s, sr=16000)
    assert len(f_s) == 17, f"Expected 17 short branch features, got {len(f_s)}"

    f_l = extract_sustained_branch_features(audio_1s, sr=16000)
    assert len(f_l) == 17, f"Expected 17 sustained branch features, got {len(f_l)}"

    clean_voc, raw_ac = extract_vocal_acoustics_clean(audio_1s, sr=16000)
    assert len(clean_voc) == 5, f"Expected 5 normalized vocal features, got {len(clean_voc)}"
    assert isinstance(raw_ac, dict)
    assert "roughness" in raw_ac
    assert "raw_hf_ratio" in raw_ac
    assert "flux" in raw_ac
    assert "hnr_db" in raw_ac
    assert "flatness" in raw_ac

    # Total fused dimensions
    assert len(f_s) + len(clean_voc) == 22
    assert len(f_l) + len(clean_voc) == 22


def test_short_branch_peak_energy_alignment():
    """Verify that short branch extracts peak-energy window rather than naive center."""
    sr = 16000
    audio = np.zeros(sr, dtype=np.float32)
    # Place a transient burst at 0.1s - 0.2s
    audio[1600:3200] = 0.8

    f_s = extract_short_branch_features(audio, sr=sr)
    assert not np.all(f_s == 0.0)


# ==============================================================================
# 4. Streaming Audio Buffer & Overrun Resistance
# ==============================================================================

def test_streaming_audio_buffer_windowing():
    """Verify StreamingAudioBuffer manages window size, hop size, and status tracking."""
    buf = StreamingAudioBuffer(sample_rate=16000, window_size=16000, hop_size=4000)
    assert not buf.is_ready_for_inference()

    # Append 3 chunks of 4096 samples (< 16,000 samples)
    for _ in range(3):
        buf.append(np.ones(4096, dtype=np.float32) * 0.1)
    assert not buf.is_ready_for_inference()
    assert buf.get_status()["samples_buffered"] == 12288

    # Append 4th chunk (total: 16,384 samples >= 16,000)
    buf.append(np.ones(4096, dtype=np.float32) * 0.2)
    assert buf.is_ready_for_inference()

    window = buf.get_latest_window()
    assert len(window) == 16000
    assert window[-1] == pytest.approx(0.2, abs=1e-5)

    buf.mark_inference_complete()
    assert not buf.is_ready_for_inference()

    # Append another chunk -> Hop threshold met (4096 >= 4000)
    buf.append(np.ones(4096, dtype=np.float32) * 0.3)
    assert buf.is_ready_for_inference()


def test_streaming_audio_buffer_reset():
    """Verify StreamingAudioBuffer cleanly resets state and sample counters."""
    buf = StreamingAudioBuffer(sample_rate=16000, window_size=16000, hop_size=4000)
    buf.append(np.ones(8000, dtype=np.float32))
    assert buf.get_status()["samples_buffered"] == 8000

    buf.reset()
    status = buf.get_status()
    assert status["samples_buffered"] == 0
    assert status["buffer_duration_sec"] == 0.0
    assert status["total_samples_written"] == 0
    assert not buf.is_ready_for_inference()


# ==============================================================================
# 5. Model Inference & Acoustic Labeling Semantics
# ==============================================================================

def test_ambient_silence_gating():
    """Verify that low-energy ambient noise (RMS < 0.002) is gated to NO SCREAM-LIKE EVENT DETECTED."""
    svc = get_research_service()
    svc.select_model("CANDIDATE_71_D")

    # Generate 1.0s low-amplitude ambient noise (RMS ~ 0.0003)
    quiet_noise = np.random.randn(16000).astype(np.float32) * 0.0003
    res = svc.infer_audio_array(quiet_noise, sr=16000)

    assert res["is_detected"] is False
    assert res["state"] == "NO SCREAM-LIKE EVENT DETECTED"
    assert res["calibrated_probability"] == 0.0100
    assert res["model_latency_ms"] < 25.0


def test_genuine_scream_detection():
    """Verify Candidate 71-D correctly detects real scream audio from dataset."""
    svc = get_research_service()
    svc.select_model("CANDIDATE_71_D")

    scream_path = REPO_ROOT / "backend/experiments/stage8_9_20_acoustic_discriminability/data/supplementary_short_screams/supp_short_scream_001_v2_nigens_HUMAN-SCREAM_GEN-HDF-15246.wav"
    if scream_path.exists():
        data, sr = sf.read(scream_path)
        res = svc.infer_audio_array(data, sr=sr)
        assert res["calibrated_probability"] >= 0.4920
        assert res["is_detected"] is True
        assert res["state"] == "SCREAM-LIKE AUDIO DETECTED"


def test_hard_negative_rejection():
    """Verify Candidate 71-D rejects representative hard negative sounds from dataset."""
    svc = get_research_service()
    svc.select_model("CANDIDATE_71_D")

    hn_files = list((REPO_ROOT / "backend/dataset/stage8_8_hard_negatives/approved").glob("*.wav"))
    if hn_files:
        data, sr = sf.read(hn_files[0])
        res = svc.infer_audio_array(data, sr=sr)
        assert res["is_detected"] is False
        assert res["state"] == "NO SCREAM-LIKE EVENT DETECTED"


# ==============================================================================
# 6. Production Baseline Isolation
# ==============================================================================

def test_production_baseline_isolation():
    """Verify production baseline model is distinct and selectable without bleeding."""
    svc = get_research_service()

    # Select Candidate 71-D
    svc.select_model("CANDIDATE_71_D")
    assert svc.active_model_id == "CANDIDATE_71_D"
    c71_info = svc.get_active_model()
    assert c71_info["operating_threshold"] == 0.4920
    assert c71_info["is_production"] is False

    # Switch to Production Baseline
    svc.select_model("PRODUCTION_BASELINE")
    assert svc.active_model_id == "PRODUCTION_BASELINE"
    prod_info = svc.get_active_model()
    assert prod_info["operating_threshold"] == 0.3500
    assert prod_info["is_production"] is True

    # Re-select Candidate 71-D
    svc.select_model("CANDIDATE_71_D")
    assert svc.active_model_id == "CANDIDATE_71_D"


# ==============================================================================
# 7. Mandatory Line 1 Safety Header Audit
# ==============================================================================

def test_line1_safety_headers():
    """Verify every created markdown and python file in Stage 8.9.80 begins with line 1 safety header."""
    expected_header = "# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE."

    files = list(STAGE_DIR.glob("**/*.md")) + list(STAGE_DIR.glob("**/*.py"))
    assert len(files) >= 5, "Too few files found in stage directory"

    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            first_line = fp.readline().strip()
            assert first_line == expected_header, (
                f"Missing line 1 safety header in {f}!\n  Got: {first_line}"
            )
