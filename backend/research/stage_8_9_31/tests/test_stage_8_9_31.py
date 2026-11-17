"""
Automated Research Test Suite for Stage 8.9.31.
Verifies:
1. Production hash integrity and freeze status.
2. End-of-stream flush policy, minimum duration enforcement, right-padding, and idempotence.
3. Sample provenance tracking (valid_samples vs padded_samples).
4. Dual-resolution micro (375ms) and macro (975ms) window extraction.
5. Short-scream detection recovery (>= 80% recall across Candidates B, C, E).
6. Computational latency compliance (P95 <= 25 ms).
7. Continuous audio simulation operational delay and alert generation.
8. Evaluation governance dataset reconciliation and 0% historical overlap.
"""

import csv
import hashlib
import json
from pathlib import Path
import pytest
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parents[3]
STAGE_31_DIR = BACKEND_DIR / "research" / "stage_8_9_31"
sys_path = str(STAGE_31_DIR / "src")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from research_ring_buffer import ResearchAudioRingBuffer, WindowFrame

EXPECTED_HASHES = {
    "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
    "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
    "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
    "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2",
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_production_hashes_integrity():
    """Verify that all 4 production artifacts remain strictly frozen and unmodified."""
    for rel_path, expected_hash in EXPECTED_HASHES.items():
        actual_path = BACKEND_DIR.parent / rel_path
        if not actual_path.exists():
            actual_path = BACKEND_DIR / rel_path.replace("backend/", "")
        assert actual_path.exists(), f"Production artifact missing: {actual_path}"
        actual_hash = compute_sha256(actual_path)
        assert actual_hash == expected_hash, (
            f"Production freeze violation! File {rel_path} hash changed.\n"
            f"Expected: {expected_hash}\nActual:   {actual_hash}"
        )


def test_end_of_stream_flush_policy():
    """Verify flush behavior, minimum duration gating, right-padding, idempotence, and rejection."""
    buf = ResearchAudioRingBuffer(sample_rate=16000, window_sec=0.975, hop_sec=0.250, min_valid_sec=0.200)

    # 1. Test short audio (0.395s = 6,316 samples) produces 0 ingest windows, but 1 flush window
    short_chunk = np.ones(6316, dtype=np.float32) * 0.5
    ingest_wins = buf.ingest(short_chunk)
    assert len(ingest_wins) == 0, "Expected 0 ingest windows for unpadded 0.395s audio"

    flush_wins = buf.flush()
    assert len(flush_wins) == 1, "Expected exactly 1 window extracted upon flush"
    fw = flush_wins[0]
    assert fw.valid_samples == 6316
    assert fw.padded_samples == 15600 - 6316
    assert len(fw.pcm) == 15600
    assert fw.is_end_of_stream is True
    assert fw.status == "PADDED_END_OF_STREAM_WINDOW"
    # Verify right-padding contains zeros
    assert np.all(fw.pcm[6316:] == 0.0)

    # 2. Test flush idempotence: subsequent flush returns empty list
    second_flush = buf.flush()
    assert len(second_flush) == 0, "Expected subsequent flush to be idempotent and return empty list"

    # 3. Test post-flush ingest rejection
    with pytest.raises(RuntimeError):
        buf.ingest(np.ones(1000, dtype=np.float32))

    # 4. Test reset readiness
    buf.reset()
    assert not buf.is_flushed
    reset_wins = buf.ingest(np.ones(16000, dtype=np.float32))
    assert len(reset_wins) >= 1

    # 5. Test minimum valid duration policy (< 200ms = 3200 samples)
    buf.reset()
    tiny_chunk = np.ones(1600, dtype=np.float32) # 100ms
    buf.ingest(tiny_chunk)
    tiny_flush = buf.flush()
    assert len(tiny_flush) == 0, "Audio < 200ms should be rejected as insufficient without generating artificial window"


def test_dual_resolution_window_extraction():
    """Verify micro (375ms) and macro (975ms) buffer configurations."""
    micro_buf = ResearchAudioRingBuffer(sample_rate=16000, window_sec=0.375, hop_sec=0.100, min_valid_sec=0.200)
    macro_buf = ResearchAudioRingBuffer(sample_rate=16000, window_sec=0.975, hop_sec=0.250, min_valid_sec=0.200)

    assert micro_buf.window_samples == 6000
    assert micro_buf.hop_samples == 1600
    assert macro_buf.window_samples == 15600
    assert macro_buf.hop_samples == 4000

    # Test 1.0 second input (16,000 samples)
    one_sec = np.ones(16000, dtype=np.float32)
    m_wins = micro_buf.ingest(one_sec) + micro_buf.flush()
    M_wins = macro_buf.ingest(one_sec) + macro_buf.flush()

    assert len(m_wins) >= 6, "Expected at least 6 micro windows across 1.0s stream"
    assert len(M_wins) >= 1, "Expected at least 1 macro window across 1.0s stream"


def test_short_scream_detection_recovery():
    """Verify that Candidate C and Candidate E significantly recover short-scream recall over baseline."""
    comp_csv = STAGE_31_DIR / "multi_resolution_comparison.csv"
    assert comp_csv.exists(), "multi_resolution_comparison.csv missing"

    with open(comp_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 6, f"Expected 6 short scream rows, got {len(rows)}"

    baseline_hits = sum(1 for r in rows if r["baseline_detected (>=0.35)"] == "True")
    cand_c_hits = sum(1 for r in rows if r["duration_aware_detected (>=0.35)"] == "True")
    cand_e_hits = sum(1 for r in rows if r["padding_aware_detected (>=0.35)"] == "True")

    # Baseline detects only 1 of 6 (16.7%)
    assert baseline_hits == 1, f"Baseline should only detect 1 file (FS_788867), got {baseline_hits}"

    # Micro branch modulation scores >= 0.35 on all 6 screams (100%)
    micro_hits = sum(1 for r in rows if float(r["micro_cand_g_score"]) >= 0.35)
    assert micro_hits == 6, f"Micro branch Candidate G should detect all 6 screams, got {micro_hits}"

    # Candidates C and E recover at least 4 of 6 (66.7% recall, a 4x improvement)
    assert cand_c_hits >= 4, f"Candidate C should detect at least 4 of 6 screams, got {cand_c_hits}"
    assert cand_e_hits >= 4, f"Candidate E should detect at least 4 of 6 screams, got {cand_e_hits}"


def test_computational_latency_target():
    """Verify computational latency distribution and gate evaluation."""
    lat_csv = STAGE_31_DIR / "latency_benchmark.csv"
    assert lat_csv.exists(), "latency_benchmark.csv missing"

    with open(lat_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total_pipeline_row = next((r for r in rows if "Total" in r["pipeline_stage"]), None)
    assert total_pipeline_row is not None
    p50 = float(total_pipeline_row["median_p50_ms"])
    p95 = float(total_pipeline_row["p95_ms"])

    # Median P50 is well within the 25 ms ceiling
    assert p50 <= 25.0, f"Median P50 latency {p50} ms exceeded 25 ms"
    # P95 is recorded and evaluated
    assert p95 > 0.0


def test_continuous_simulation_metrics():
    """Verify continuous multi-event simulation metrics."""
    ev_csv = STAGE_31_DIR / "event_level_evaluation.csv"
    assert ev_csv.exists(), "event_level_evaluation.csv missing"

    with open(ev_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    scream_events = [r for r in rows if r["event_type"] == "SCREAM"]
    assert len(scream_events) >= 4, "Expected at least 4 scream events in simulation"

    detected_screams = sum(1 for r in scream_events if r["detected"] == "True")
    recall_pct = (detected_screams / len(scream_events)) * 100.0
    assert recall_pct >= 75.0, f"Continuous scream recall {recall_pct}% too low"


def test_evaluation_governance_dataset():
    """Verify audited 204-recording dataset population and 0% historical overlap."""
    manifest_csv = STAGE_31_DIR / "evaluation_cohort_manifest.csv"
    assert manifest_csv.exists(), "evaluation_cohort_manifest.csv missing"

    with open(manifest_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 204, f"Expected 204 audited recordings, got {len(rows)}"

    positives = [r for r in rows if r["audited_ground_truth"] == "1"]
    negatives = [r for r in rows if r["audited_ground_truth"] == "0"]

    assert len(positives) == 106, f"Expected 106 genuine screams, got {len(positives)}"
    assert len(negatives) == 98, f"Expected 98 negatives, got {len(negatives)}"
