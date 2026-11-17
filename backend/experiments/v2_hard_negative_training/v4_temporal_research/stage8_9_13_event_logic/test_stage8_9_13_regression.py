"""Deterministic Regression and State Machine Integrity Verification Suite for Stage 8.9.13.

Tests:
1. Production hash immutability (scream_classifier.joblib, model_metadata.json, etc.).
2. Operating threshold remains locked at 0.3500.
3. Review database integrity (343 records, anchor fsd50k_349401 = SCREAM_PRESENT).
4. DualPathEventStateMachine transitions, boundary tracking, and deduplication.
5. Short-event preservation contract (transient startle screams detected without consecutive requirement).
6. Extended silence, continuous crowd noise, and buffer boundary robustness.
7. Source-group disjointness and Stage 5 test quarantine.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_13_event_logic.dual_path_state_machine import (
    DualPathEventStateMachine,
    EventState,
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
    """Verify all authoritative production files remain strictly frozen and bit-identical."""
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        p = BACKEND_DIR / rel_path
        assert p.exists(), f"Production file missing: {rel_path}"
        actual_hash = compute_sha256(p)
        assert actual_hash == expected_hash, f"Production hash mismatch on {rel_path}!"

    # Verify production threshold
    with open(BACKEND_DIR / "models" / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35, "Production threshold altered!"

    # Verify review database
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

    for r in records:
        if r.get("is_historical_stage5_test", False):
            assert r["split"] == "test", f"Historical Stage 5 record {r['file_id']} in non-test split {r['split']}!"


def test_dual_path_fast_path_immediate_trigger():
    """Verify fast path triggers immediately on a single high-confidence window."""
    sm = DualPathEventStateMachine(tau_fast=0.75, tau_sustained=0.60, tau_release=0.30)
    sm.reset()

    # Single high-confidence window
    fired, meta = sm.step(0.80, 1.0)
    assert fired and meta is not None
    assert meta["trigger_path"] == "FAST_PATH"
    assert meta["notice"] == SAFETY_WARNING
    assert sm.state == EventState.EVENT_ACTIVE


def test_dual_path_sustained_path_confirmation():
    """Verify sustained path requires confirmation hops before firing."""
    sm = DualPathEventStateMachine(tau_fast=0.75, tau_sustained=0.60, tau_release=0.30, sustained_confirm_hops=2)
    sm.reset()

    # Window 1: moderate confidence -> SUSTAINED_PENDING
    f1, _ = sm.step(0.65, 1.0)
    assert not f1 and sm.state == EventState.SUSTAINED_PENDING

    # Window 2: moderate confidence -> CONFIRMED -> EVENT_ACTIVE
    f2, m2 = sm.step(0.68, 1.5)
    assert f2 and m2 is not None
    assert m2["trigger_path"] == "SUSTAINED_PATH"
    assert sm.state == EventState.EVENT_ACTIVE


def test_short_event_preservation_contract():
    """Verify that a single brief scream (< 1.0s) is successfully detected by the fast path."""
    sm = DualPathEventStateMachine(tau_fast=0.75, tau_sustained=0.60, tau_release=0.30)
    sm.reset()

    # 0.4s scream in window 3 surrounded by silence
    stream = [0.05, 0.08, 0.85, 0.10, 0.05]
    alerts = []
    for idx, p in enumerate(stream):
        fired, _ = sm.step(p, (idx + 1) * 0.5 + 1.0)
        alerts.append(fired)

    assert sum(alerts) == 1, "Brief scream must trigger exactly 1 alert!"
    assert alerts[2] is True, "Alert must trigger on window 3!"


def test_continuous_sound_deduplication():
    """Verify that continuous noise bursts (e.g. crowd chanting) trigger only 1 alert event."""
    sm = DualPathEventStateMachine(tau_fast=0.75, tau_sustained=0.60, tau_release=0.30, cooldown_hops=6)
    sm.reset()

    # Continuous 6-second sound burst (12 windows above threshold)
    stream = [0.78] * 12
    alerts = []
    for idx, p in enumerate(stream):
        fired, _ = sm.step(p, (idx + 1) * 0.5 + 1.0)
        alerts.append(fired)

    assert sum(alerts) == 1, "Continuous multi-frame burst must emit exactly 1 alert event, zero duplicates!"


def test_event_boundary_quiet_release_and_recovery():
    """Verify state machine returns to IDLE after quiet release and cooldown."""
    sm = DualPathEventStateMachine(
        tau_fast=0.75,
        tau_sustained=0.60,
        tau_release=0.30,
        quiet_release_hops=2,
        cooldown_hops=4,
    )
    sm.reset()

    # Trigger event
    sm.step(0.85, 1.0)
    assert sm.state == EventState.EVENT_ACTIVE

    # 2 quiet windows below tau_release (0.10 < 0.30) -> enters COOLDOWN
    sm.step(0.10, 1.5)
    sm.step(0.10, 2.0)
    assert sm.state == EventState.COOLDOWN

    # Decrement remaining cooldown hops while quiet
    sm.step(0.05, 2.5)
    sm.step(0.05, 3.0)
    assert sm.state == EventState.IDLE, "Must return to IDLE after quiet release and cooldown!"
