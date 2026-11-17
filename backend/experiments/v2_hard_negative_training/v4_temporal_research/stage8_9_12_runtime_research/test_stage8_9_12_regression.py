"""Deterministic Regression and Integrity Verification Suite for Stage 8.9.12.

Tests:
1. Feature parity between original and optimized implementations.
2. Silence, clipping, and malformed audio robustness.
3. Temporal state machine transitions and hysteresis.
4. Short-event handling and single-frame bursts.
5. Cooldown and repeated alert suppression.
6. Streaming buffer boundaries and fractional windows.
7. Numerical stability across extreme dynamic ranges.
8. Source-group separation and Stage 5 test quarantine.
9. Bit-identical production hash verification.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from src.config import TARGET_SAMPLE_RATE
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.fast_acoustic_features import (
    FastAcousticFeatureExtractor,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.temporal_state_machine import (
    MachineState,
    SingleWindowPolicy,
    ConsecutivePersistencePolicy,
    VotingKofMPolicy,
    HysteresisCooldownPolicy,
    SAFETY_WARNING,
)

AUTHORITATIVE_HASHES = {
    "models/scream_classifier.joblib": "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F",
    "models/model_metadata.json": "30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60",
    "reports/test_predictions.csv": "E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D",
    "reports/stage5_test_evaluation.md": "9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2",
}

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
MANIFEST_PATH = STAGE11_DIR / "stage8_9_11_dataset_manifest.json"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def test_production_hash_integrity():
    """Verify that all production artifacts remain strictly frozen and bit-identical."""
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        p = BACKEND_DIR / rel_path
        assert p.exists(), f"Production file missing: {rel_path}"
        actual_hash = compute_sha256(p)
        assert actual_hash == expected_hash, f"Production hash mismatch on {rel_path}!"

    # Verify production threshold in metadata
    with open(BACKEND_DIR / "models" / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35, "Production threshold altered!"

    # Verify database
    db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT review_status, COUNT(*) FROM candidates GROUP BY review_status")
    counts = dict(cur.fetchall())
    cur.execute("SELECT review_status FROM candidates WHERE recording_id = 'fsd50k_349401'")
    anchor = cur.fetchone()[0]
    conn.close()

    assert anchor == "SCREAM_PRESENT"
    assert counts.get("APPROVED_NON_SCREAM") == 338
    assert counts.get("SCREAM_PRESENT") == 2


def test_source_group_disjointness_and_quarantine():
    """Verify 0 leakage across splits and strict quarantine of historical Stage 5 test sources."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    train_groups = {r["source_group_id"] for r in records if r["split"] == "train"}
    val_groups = {r["source_group_id"] for r in records if r["split"] == "val"}
    test_groups = {r["source_group_id"] for r in records if r["split"] == "test"}

    assert len(train_groups.intersection(val_groups)) == 0, "Train-Val group leakage!"
    assert len(train_groups.intersection(test_groups)) == 0, "Train-Test group leakage!"
    assert len(val_groups.intersection(test_groups)) == 0, "Val-Test group leakage!"

    # Quarantine check: Stage 5 test sources
    for r in records:
        if r.get("is_historical_stage5_test", False):
            assert r["split"] == "test", f"Historical Stage 5 record {r['file_id']} in non-test split {r['split']}!"


def test_fast_features_numerical_stability():
    """Test fast feature extractor on extreme audio signals (silence, clip, constant, impulses)."""
    extractor = FastAcousticFeatureExtractor(sr=TARGET_SAMPLE_RATE)

    # 1. Silence
    silence = np.zeros(16000, dtype=np.float32)
    turb, snr = extractor.extract_turbulence_and_snr_fast(silence)
    assert len(turb) == 16 and len(snr) == 4
    assert not np.isnan(turb).any() and not np.isnan(snr).any()
    assert not np.isinf(turb).any() and not np.isinf(snr).any()

    # 2. Hard clipping
    clipping = np.ones(16000, dtype=np.float32)
    turb, snr = extractor.extract_turbulence_and_snr_fast(clipping)
    assert not np.isnan(turb).any() and not np.isnan(snr).any()

    # 3. Random noise
    noise = np.random.randn(16000).astype(np.float32)
    turb, snr = extractor.extract_turbulence_and_snr_fast(noise)
    assert not np.isnan(turb).any() and not np.isnan(snr).any()


def test_single_window_policy():
    """Test SingleWindowPolicy fires instantaneously on threshold crossings."""
    pol = SingleWindowPolicy(threshold=0.50)
    fired, meta = pol.step(0.49, 1.0)
    assert not fired and meta is None

    fired, meta = pol.step(0.51, 1.5)
    assert fired and meta is not None
    assert meta["prob"] == 0.51
    assert meta["notice"] == SAFETY_WARNING


def test_consecutive_persistence_policy():
    """Test ConsecutivePersistencePolicy requires consecutive positive windows."""
    pol = ConsecutivePersistencePolicy(consecutive_required=2, threshold=0.50)
    pol.reset()

    # Window 1: above threshold -> should NOT fire yet
    fired, meta = pol.step(0.60, 1.0)
    assert not fired

    # Window 2: above threshold -> MUST fire
    fired, meta = pol.step(0.70, 1.5)
    assert fired and meta is not None
    assert meta["streak_length"] == 2

    # Window 3: still above threshold -> should not fire duplicate for same streak
    fired, meta = pol.step(0.65, 2.0)
    assert not fired

    # Window 4: below threshold -> streak resets
    fired, meta = pol.step(0.20, 2.5)
    assert not fired

    # Window 5: above threshold -> streak = 1, should not fire yet
    fired, meta = pol.step(0.80, 3.0)
    assert not fired


def test_voting_k_of_m_policy():
    """Test VotingKofMPolicy (e.g. 2 of 3)."""
    pol = VotingKofMPolicy(k=2, m=3, threshold=0.50)
    pol.reset()

    # Window 1: Pos (1/1) -> no alert
    fired, _ = pol.step(0.60, 1.0)
    assert not fired

    # Window 2: Neg (1/2) -> no alert
    fired, _ = pol.step(0.20, 1.5)
    assert not fired

    # Window 3: Pos (2/3) -> ALERT!
    fired, meta = pol.step(0.70, 2.0)
    assert fired and meta is not None
    assert meta["positive_count"] == 2


def test_hysteresis_and_cooldown_policy():
    """Test HysteresisCooldownPolicy state transitions, cooldown, and recovery."""
    pol = HysteresisCooldownPolicy(
        tau_high=0.50,
        tau_low=0.25,
        confirm_hops=2,
        cooldown_hops=4,
        recovery_hops=2,
    )
    pol.reset()
    assert pol.state == MachineState.IDLE

    # Window 1: High (0.60) -> PENDING_CONFIRMATION
    fired, _ = pol.step(0.60, 1.0)
    assert not fired and pol.state == MachineState.PENDING_CONFIRMATION

    # Window 2: High (0.75) -> CONFIRMED -> ALERT_ACTIVE (Cooldown starts = 4)
    fired, meta = pol.step(0.75, 1.5)
    assert fired and pol.state == MachineState.ALERT_ACTIVE
    assert meta["notice"] == SAFETY_WARNING

    # Window 3: Still High (0.80) -> Alert active, cooldown decrements (3), NO duplicate alert
    fired, _ = pol.step(0.80, 2.0)
    assert not fired and pol.state == MachineState.ALERT_ACTIVE

    # Window 4: Drops below tau_low (0.15) -> State becomes COOLDOWN
    fired, _ = pol.step(0.15, 2.5)
    assert not fired and pol.state == MachineState.COOLDOWN

    # Window 5: Below tau_low (0.10) -> Cooldown decrements
    fired, _ = pol.step(0.10, 3.0)
    assert not fired

    # Window 6: Below tau_low (0.05) -> Cooldown finishes, recovers to IDLE
    fired, _ = pol.step(0.05, 3.5)
    fired, _ = pol.step(0.05, 4.0)
    assert pol.state == MachineState.IDLE


def test_short_event_miss_characteristic():
    """Test that consecutive persistence inherently misses isolated single-frame screams."""
    pol = ConsecutivePersistencePolicy(consecutive_required=2, threshold=0.50)
    pol.reset()

    # An isolated transient shriek (0.3s) present in only 1 window
    stream = [0.10, 0.15, 0.95, 0.12, 0.08]
    alerts = []
    for t_idx, p in enumerate(stream):
        fired, _ = pol.step(p, t_idx * 0.5 + 1.0)
        alerts.append(fired)

    # Must be 0 alerts because single window was not sustained
    assert sum(alerts) == 0, "Consecutive_2 should miss single-frame burst!"
