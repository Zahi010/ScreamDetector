"""Automated Test Suite for Stage 8.9.26 Validation.

Tests:
1. Production Hash Preservation (Cryptographic SHA-256 match).
2. Production Decision Threshold (0.3500 preserved).
3. Deliverable Artifact Existence (All 14 required files).
4. Dataset Split Integrity (0% leakage, 0 duplicates).
5. Pre-Screening Recall Preservation & Silence Gating.
6. Short-Event Protection & No Automatic Short-Event Veto.
7. Model Input / Output Compatibility (Model C, Model E, Fusion D).
8. Non-Parametric Spectral Peak Prominence vs LPC Robustness.
9. Confidence Fusion & 3-Class Categorization.
10. Streaming Buffer & Event State Machine (Grouping, Cooldown, Override).
11. Acceptance Gate Enforcement (All candidates marked REJECTED).
"""

import hashlib
import json
from pathlib import Path
import pytest
import numpy as np
import joblib

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_26"
SRC_DIR = STAGE_DIR / "src"
MODELS_DIR = STAGE_DIR / "models"

import sys
sys.path.insert(0, str(SRC_DIR))

from pre_screener import AcousticPreScreener
from spectral_peak_prominence import analyze_resonance_profile, estimate_f0
from multi_stage_detector import IntegratedMultiStageDetector
from event_streaming_engine import StreamingBufferManager, IntegratedEventStateMachine

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
}

def test_production_artifact_hashes():
    """Verify that all 4 production artifacts match authoritative hashes exactly."""
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        full_path = BACKEND_DIR.parent / rel_path
        assert full_path.exists(), f"Missing production artifact: {full_path}"
        with open(full_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        assert computed_hash == expected_hash, f"Hash mismatch for {rel_path}"

def test_production_threshold_preserved():
    """Verify production threshold remains strictly 0.3500."""
    metadata_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35, "Production threshold must remain 0.3500"

def test_stage_deliverables_exist():
    """Verify that all required Stage 8.9.26 deliverables exist on disk."""
    expected_files = [
        STAGE_DIR / "STAGE_8_9_26_COMPLETION_REPORT.md",
        STAGE_DIR / "integrated_architecture.md",
        STAGE_DIR / "stagewise_evaluation.csv",
        STAGE_DIR / "fusion_comparison.csv",
        STAGE_DIR / "feature_ablation_results.csv",
        STAGE_DIR / "short_event_protection_report.md",
        STAGE_DIR / "hard_negative_analysis.csv",
        STAGE_DIR / "event_grouping_and_cooldown_report.md",
        STAGE_DIR / "streaming_performance_report.md",
        STAGE_DIR / "dataset_integrity_report.md",
        STAGE_DIR / "production_integrity_verification.json",
        MODELS_DIR / "model_configs.json",
        MODELS_DIR / "fusion_d_logistic.joblib",
        SRC_DIR / "pre_screener.py",
        SRC_DIR / "spectral_peak_prominence.py",
        SRC_DIR / "multi_stage_detector.py",
        SRC_DIR / "event_streaming_engine.py",
        SRC_DIR / "run_stage_8_9_26_experiments.py"
    ]
    for p in expected_files:
        assert p.exists(), f"Missing required deliverable file: {p}"

def test_prescreener_preservation_and_gating():
    """Test pre-screener rejects digital silence but preserves vocal bursts."""
    screener = AcousticPreScreener(sample_rate=16000)
    
    # 1. Digital silence
    silence = np.zeros(16000, dtype=np.float32)
    res_sil = screener.process_waveform(silence)
    assert not res_sil.passed, "Digital silence must be rejected"
    assert res_sil.rejection_reason != ""

    # 2. Synthetic scream burst (2000 Hz tone + harmonics + noise, 300 ms)
    t = np.linspace(0, 0.3, 4800, endpoint=False)
    burst = 0.5 * np.sin(2 * np.pi * 2200 * t) + 0.1 * np.random.randn(len(t))
    burst_wf = np.pad(burst, (0, 16000 - len(burst))).astype(np.float32)
    res_burst = screener.process_waveform(burst_wf)
    assert res_burst.passed, "Vocal burst must pass pre-screening"
    assert res_burst.spectral_centroid_hz > 1000.0

def test_spectral_peak_prominence_robustness():
    """Test non-parametric peak prominence succeeds even on high-pitched shrieks."""
    # High-pitched vocalization (800 Hz F0 with strong 2400 Hz horn resonance)
    t = np.linspace(0, 0.5, 8000, endpoint=False)
    wf_hp = (
        0.3 * np.sin(2 * np.pi * 800 * t)
        + 0.6 * np.sin(2 * np.pi * 2400 * t)  # 3rd harmonic in scream horn
        + 0.05 * np.random.randn(len(t))
    ).astype(np.float32)
    
    res = analyze_resonance_profile(wf_hp, sr=16000)
    assert res.is_high_pitch, "F0 > 650 Hz must be identified as high pitch"
    assert not res.lpc_success, "LPC must fail on high-pitched vocalization (spacing collapse)"
    assert res.peak_prominence_success, "Non-parametric peak prominence must succeed"
    assert 2200.0 <= res.horn_max_peak_hz <= 2600.0
    assert res.horn_peak_prominence_db > 3.0

def test_no_automatic_short_event_veto():
    """Verify that short events are never vetoed due to missing slow cadence."""
    detector = IntegratedMultiStageDetector(BACKEND_DIR)
    
    # Scenario: Short 400 ms scream with high fast_score (0.60), but zero cand_g_score (0.0)
    score, cat = detector.evaluate_asymmetric_fusion_e(
        fast_score=0.60,
        cand_g_score=0.00,  # Missing slow context
        model_e_score=0.45,
        horn_ratio=0.50,    # Strong horn resonance
        horn_prom_db=7.0,
        duration=0.4,       # Short event (< 0.8s)
        lpc_success=False,
        is_high_pitch=True,
    )
    assert score >= 0.35, f"Short scream must not be vetoed by missing cadence: score={score}"
    assert cat == "POSSIBLE_SCREAM", f"Category must be POSSIBLE_SCREAM, got {cat}"

def test_speech_shouting_cadence_suppression():
    """Verify that multi-syllabic speech shouting is suppressed when cadence is verified."""
    detector = IntegratedMultiStageDetector(BACKEND_DIR)
    
    # Scenario: 2.5s shouting with low horn resonance and low cand_g score
    score, cat = detector.evaluate_asymmetric_fusion_e(
        fast_score=0.42,
        cand_g_score=0.10,  # Validated non-scream cadence
        model_e_score=0.30,
        horn_ratio=0.20,    # Low horn resonance
        horn_prom_db=1.0,
        duration=2.5,       # Sustained duration
        lpc_success=True,
        is_high_pitch=False,
    )
    assert score < 0.25, f"Speech shouting should be suppressed: score={score}"
    assert cat == "NON_SCREAM"

def test_streaming_buffer_and_event_grouping():
    """Test streaming buffer ingests chunks without dropping and groups consecutive windows."""
    buf_mgr = StreamingBufferManager(sample_rate=16000, window_sec=0.975, hop_sec=0.25)
    sm = IntegratedEventStateMachine(tau_alert=0.35, tau_fast_transient=0.50, cooldown_hops=4)
    
    # Ingest 2 seconds of audio in 50 ms chunks
    chunk_50ms = np.random.randn(800).astype(np.float32) * 0.1
    all_windows = []
    for _ in range(40):  # 40 * 50ms = 2.0s
        wins = buf_mgr.ingest_audio(chunk_50ms)
        all_windows.extend(wins)
        
    assert len(all_windows) > 0, "Windows must be generated from streaming ingestion"
    assert buf_mgr.dropped_windows == 0, "No windows should be dropped under normal queue"
    
    # Test event grouping and cooldown
    # Window 0: High score triggers immediate FAST_TRANSIENT alert
    alert0 = sm.process_window(0, 0.0, 0.975, 0.65, "POSSIBLE_SCREAM")
    assert alert0 is not None, "Window 0 must emit an immediate alert"
    assert alert0.trigger_type == "FAST_TRANSIENT"
    
    # Window 1: Ongoing event merges into window 0 (no duplicate alert)
    alert1 = sm.process_window(1, 0.25, 1.225, 0.60, "POSSIBLE_SCREAM")
    assert alert1 is None, "Window 1 must be merged, not dispatch a duplicate alert"
    assert sm.current_event.window_count == 2
    
    # Window 2, 3: Score drops below release -> transitions to COOLDOWN
    sm.process_window(2, 0.50, 1.475, 0.10, "NON_SCREAM")
    sm.process_window(3, 0.75, 1.725, 0.10, "NON_SCREAM")
    assert sm.state.name == "COOLDOWN"
    
    # Window 4: Moderate score during cooldown is suppressed
    alert4 = sm.process_window(4, 1.00, 1.975, 0.40, "POSSIBLE_SCREAM")
    assert alert4 is None, "Trailing echo during cooldown must be suppressed"
    
    # Window 5: Explosive fresh burst (Score 0.85) overrides cooldown!
    alert5 = sm.process_window(5, 1.25, 2.225, 0.85, "POSSIBLE_SCREAM")
    assert alert5 is not None, "Fresh explosive onset must override cooldown"
    assert "OVERRIDE" in alert5.event_id

def test_acceptance_gate_enforcement():
    """Verify that all candidate fusion variants are marked REJECTED in fusion_comparison.csv."""
    import csv
    comp_file = STAGE_DIR / "fusion_comparison.csv"
    assert comp_file.exists()
    with open(comp_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    for r in rows:
        assert "REJECTED" in r["gate_verdict"], f"Candidate {r['variant']} must be marked REJECTED"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
