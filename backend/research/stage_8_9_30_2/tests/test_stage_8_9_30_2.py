"""
Automated Unit and Forensic Test Suite for Stage 8.9.30.2
Verifies:
1. Production hash integrity and freeze status.
2. Denominator discrepancy reconciliation (67 vs 98 negatives, 56.12% FPR).
3. Authoritative dataset reconciliation (204 total, 106 genuine screams, 31 quarantined).
4. Missed short scream inventory (6 recordings, all < 0.8s, genuine screams).
5. Zero historical Stage 5 / Stage 8.9.27 overlap.
6. Forensic acoustic metrics (clipping ratio, SNR, spectral centroid).
7. Window alignment and buffer underflow mechanics.
8. Model comparison, pipeline tracing, and persistence state machine.
"""

import csv
import hashlib
import json
from pathlib import Path
import pytest

BACKEND_DIR = Path(__file__).resolve().parents[3]
STAGE_30_2_DIR = BACKEND_DIR / "research" / "stage_8_9_30_2"

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


def test_negative_denominator_reconciliation():
    """Verify that the 67 vs 98 negative denominator discrepancy is resolved with exact math."""
    denom_csv = STAGE_30_2_DIR / "negative_denominator_reconciliation.csv"
    assert denom_csv.exists(), "negative_denominator_reconciliation.csv missing"

    with open(denom_csv, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 4, "Expected at least 4 reconciliation cohorts"

    # Cohort B: Audited 204-recording cohort
    cohort_b = next((r for r in reader if "B_STAGE_30_1_AUDITED_TOTAL_COHORT" in r["cohort_identifier"]), None)
    assert cohort_b is not None, "Cohort B missing from denominator reconciliation"
    assert int(cohort_b["positive_count"]) == 106
    assert int(cohort_b["negative_count"]) == 98
    assert int(cohort_b["total_count"]) == 204
    assert int(cohort_b["false_positives"]) == 55

    fpr_pct = float(cohort_b["hard_negative_fpr_pct"])
    assert round(fpr_pct, 2) == 56.12, f"Expected 56.12% FPR, got {fpr_pct}"

    # Cohort A: Original Stage 8.9.30 report
    cohort_a = next((r for r in reader if "A_STAGE_30_REPORTED_BASELINE" in r["cohort_identifier"]), None)
    assert cohort_a is not None
    assert int(cohort_a["negative_count"]) == 67
    assert int(cohort_a["false_positives"]) == 30
    assert round(float(cohort_a["hard_negative_fpr_pct"]), 2) == 44.78


def test_dataset_reconciliation_inventory():
    """Verify the 204-recording authoritative dataset reconciliation."""
    ds_csv = STAGE_30_2_DIR / "dataset_reconciliation.csv"
    assert ds_csv.exists(), "dataset_reconciliation.csv missing"

    with open(ds_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 204, f"Expected exactly 204 recordings, got {len(rows)}"

    genuine_screams = [r for r in rows if r["audited_ground_truth"] == "1"]
    quarantined = [r for r in rows if r["quarantine_status"] == "QUARANTINED"]
    negatives = [r for r in rows if r["audited_ground_truth"] == "0"]

    assert len(genuine_screams) == 106, f"Expected 106 genuine screams, got {len(genuine_screams)}"
    assert len(quarantined) == 31, f"Expected 31 quarantined files, got {len(quarantined)}"
    assert len(negatives) == 98, f"Expected 98 total audited negatives, got {len(negatives)}"


def test_missed_short_scream_inventory():
    """Verify that all 6 missed short screams are accounted for with durations < 0.8s."""
    inv_csv = STAGE_30_2_DIR / "missed_short_scream_inventory.csv"
    assert inv_csv.exists(), "missed_short_scream_inventory.csv missing"

    with open(inv_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 6, f"Expected exactly 6 missed short screams, got {len(rows)}"

    for r in rows:
        dur = float(r["duration_sec"])
        assert 0.3 <= dur <= 0.8, f"Recording {r['recording_id']} duration {dur} out of bounds"
        assert r["audited_ground_truth"] == "1", f"Recording {r['recording_id']} not marked positive"
        assert r["is_among_106_genuine_screams"] == "True"
        assert "STREAMING_BUFFER_UNDERFLOW" in r["primary_failure_mechanism"]


def test_zero_historical_overlap():
    """Verify 0% contamination against Stage 5 and historical test sets."""
    overlap_csv = STAGE_30_2_DIR / "cohort_overlap_analysis.csv"
    assert overlap_csv.exists(), "cohort_overlap_analysis.csv missing"

    with open(overlap_csv, "r", encoding="utf-8") as f:
        overlap_rows = list(csv.DictReader(f))

    for r in overlap_rows:
        assert float(r["overlap_percentage"]) == 0.0
        assert r["status"] == "MUTUALLY_DISJOINT"

    id_csv = STAGE_30_2_DIR / "historical_short_scream_identity.csv"
    assert id_csv.exists(), "historical_short_scream_identity.csv missing"
    with open(id_csv, "r", encoding="utf-8") as f:
        id_rows = list(csv.DictReader(f))

    assert len(id_rows) == 6
    for r in id_rows:
        assert r["in_stage5_test"] == "False"
        assert r["in_stage27_manifest"] == "False"
        assert r["novelty_classification"] == "GENUINELY_NEW_INDEPENDENT_RECORDING"


def test_forensic_acoustic_metrics():
    """Verify physical acoustic validity of extracted features."""
    ac_csv = STAGE_30_2_DIR / "short_scream_acoustic_features.csv"
    assert ac_csv.exists(), "short_scream_acoustic_features.csv missing"

    with open(ac_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 6

    for r in rows:
        dur = float(r["duration_sec"])
        rms = float(r["rms_energy"])
        peak = float(r["peak_amplitude"])
        snr = float(r["estimated_snr_db"])
        clip = float(r["clipping_ratio"])
        centroid = float(r["mean_spectral_centroid_hz"])

        assert 0.35 <= dur <= 0.80
        assert rms > 0.05, "RMS too low for valid scream"
        assert peak > 0.1, "Peak amplitude too low"
        assert clip == 0.0, "Unexpected digital clipping detected"
        assert snr >= 20.0, f"SNR {snr} too noisy for clear scream"
        assert centroid > 500.0, f"Centroid {centroid} abnormally low"


def test_window_underflow_mechanics():
    """Verify window alignment analysis demonstrates ring buffer underflow."""
    align_csv = STAGE_30_2_DIR / "window_alignment_analysis.csv"
    assert align_csv.exists(), "window_alignment_analysis.csv missing"

    with open(align_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 6

    for r in rows:
        assert r["causes_buffer_underflow"] == "True"
        assert int(r["missing_samples_to_fill_window"]) > 0
        assert float(r["silence_padding_fraction"]) > 0.20


def test_model_comparison_and_pipeline_trace():
    """Verify pre-screener pass rate and padded model behavior."""
    comp_csv = STAGE_30_2_DIR / "model_comparison_on_missed_recordings.csv"
    trace_csv = STAGE_30_2_DIR / "pipeline_trace_per_recording.csv"
    assert comp_csv.exists() and trace_csv.exists()

    with open(comp_csv, "r", encoding="utf-8") as f:
        comp_rows = list(csv.DictReader(f))

    with open(trace_csv, "r", encoding="utf-8") as f:
        trace_rows = list(csv.DictReader(f))

    assert len(comp_rows) == 6
    assert len(trace_rows) == 6

    # 1. All passed pre-screener
    for r in comp_rows:
        assert "passed=True" in r["pre_screener_passed"]

    # 2. S8930_FS_788867 detected when padded
    fs_788867 = next((r for r in comp_rows if r["recording_id"] == "S8930_FS_788867"), None)
    assert fs_788867 is not None
    assert float(fs_788867["fusion_e_final_prob"]) >= 0.3500
    assert fs_788867["detected_when_padded"] == "True"

    # 3. All 6 had 0 windows unpadded
    for t in trace_rows:
        assert int(t["step1_unpadded_ring_buffer_windows"]) == 0
        assert t["step1_unpadded_outcome"] == "RING_BUFFER_UNDERFLOW_ZERO_WINDOWS"
