"""Stage 8.9.14 Deterministic Regression Tests.

Validates:
1. Production asset hashes match authoritative ledger exactly.
2. Production threshold remains 0.3500.
3. Review database integrity (343 records, anchor fsd50k_349401 = SCREAM_PRESENT).
4. Source-group disjointness (zero overlap between train, val, test).
5. Acoustic discriminability feature extractor dimensions, finite outputs, and edge-case handling.
6. Short-scream preservation contract and evaluation artifact integrity.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from pathlib import Path
import pytest
import numpy as np

import sys
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
STAGE14_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_14_acoustic_discriminability"

from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_14_acoustic_discriminability.acoustic_discriminability_features import (
    AcousticDiscriminabilityExtractor,
    ALL_FEATURE_NAMES,
    FAMILY_A_NAMES,
    FAMILY_B_NAMES,
    FAMILY_C_NAMES,
    FAMILY_D_NAMES,
)

AUTHORITATIVE_HASHES = {
    "backend/models/scream_classifier.joblib": "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F",
    "backend/models/model_metadata.json": "30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60",
    "backend/reports/test_predictions.csv": "E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D",
    "backend/reports/stage5_test_evaluation.md": "9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2",
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def test_production_hash_integrity():
    for rel_path, expected_hash in AUTHORITATIVE_HASHES.items():
        sub_rel = rel_path.replace("backend/", "")
        p = BACKEND_DIR / sub_rel
        assert p.exists(), f"Missing production file: {rel_path}"
        actual = compute_sha256(p)
        assert actual == expected_hash, f"Hash mismatch on {rel_path}!"


def test_production_threshold_and_database_frozen():
    meta_path = BACKEND_DIR / "models" / "model_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta.get("selected_threshold") == 0.35, "Operating threshold must remain 0.3500!"

    db_path = BACKEND_DIR / "database" / "stage8_9_reviews.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT review_status, COUNT(*) FROM candidates GROUP BY review_status")
    counts = dict(cur.fetchall())
    total_reviewed = sum(v for k, v in counts.items() if k != "UNREVIEWED")
    cur.execute("SELECT review_status FROM candidates WHERE recording_id = 'fsd50k_349401'")
    anchor_row = cur.fetchone()
    conn.close()

    assert total_reviewed == 343, f"Expected 343 reviewed records, got {total_reviewed}"
    assert anchor_row is not None and anchor_row[0] == "SCREAM_PRESENT", "Anchor decision mismatch!"


def test_source_group_disjointness():
    audit_json = STAGE14_DIR / "source_group_split_audit.json"
    assert audit_json.exists(), "Missing source_group_split_audit.json"
    with open(audit_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["strictly_disjoint"] is True, "Source group disjointness violation detected!"
    overlaps = data["source_group_overlap_violations"]
    assert len(overlaps["train_val"]) == 0
    assert len(overlaps["train_test"]) == 0
    assert len(overlaps["val_test"]) == 0


def test_acoustic_feature_extractor_structure():
    assert len(ALL_FEATURE_NAMES) == 30
    assert len(FAMILY_A_NAMES) == 8
    assert len(FAMILY_B_NAMES) == 8
    assert len(FAMILY_C_NAMES) == 8
    assert len(FAMILY_D_NAMES) == 6

    extractor = AcousticDiscriminabilityExtractor(sr=16000)
    wave = np.random.randn(16000).astype(np.float32) * 0.1
    f_all = extractor.extract_features(wave)
    assert f_all.shape == (30,)
    assert np.all(np.isfinite(f_all))

    f_a = extractor.extract_family(wave, "A")
    assert f_a.shape == (8,)
    assert np.allclose(f_a, f_all[:8])

    f_b = extractor.extract_family(wave, "B")
    assert f_b.shape == (8,)
    assert np.allclose(f_b, f_all[8:16])

    f_c = extractor.extract_family(wave, "C")
    assert f_c.shape == (8,)
    assert np.allclose(f_c, f_all[16:24])

    f_d = extractor.extract_family(wave, "D")
    assert f_d.shape == (6,)
    assert np.allclose(f_d, f_all[24:30])


def test_acoustic_feature_extractor_edge_cases():
    extractor = AcousticDiscriminabilityExtractor(sr=16000)
    edge_cases = [
        np.zeros(16000, dtype=np.float32),                        # Silence
        np.ones(16000, dtype=np.float32) * 0.5,                   # DC offset
        np.sign(np.sin(np.linspace(0, 100, 16000))).astype(np.float32),  # Clipping
        np.random.randn(400).astype(np.float32),                  # Very short buffer
        np.array([1.0, -1.0] * 8000, dtype=np.float32),          # Nyquist oscillation
    ]
    for wave in edge_cases:
        feat = extractor.extract_features(wave)
        assert feat.shape == (30,)
        assert np.all(np.isfinite(feat)), "Feature extractor output non-finite values!"


def test_short_event_dataset_audit_contract():
    audit_csv = STAGE14_DIR / "short_event_dataset_audit.csv"
    assert audit_csv.exists(), "Missing short_event_dataset_audit.csv"
    with open(audit_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    assert len(records) >= 200, f"Expected >= 200 short event records, got {len(records)}"
    screams = [r for r in records if "scream" in r["target_category"].lower()]
    assert len(screams) >= 25, f"Expected >= 25 short screams, got {len(screams)}"

    for r in records:
        assert float(r["duration_seconds"]) <= 1.5
        assert r["split"] in ["train", "val", "test"]
        assert len(r["source_group_id"]) > 0
        assert len(r["license"]) > 0


def test_ablation_and_test_metrics_integrity():
    abl_csv = STAGE14_DIR / "feature_ablation_results.csv"
    test_csv = STAGE14_DIR / "held_out_test_metrics.csv"
    assert abl_csv.exists(), "Missing feature_ablation_results.csv"
    assert test_csv.exists(), "Missing held_out_test_metrics.csv"

    with open(test_csv, "r", encoding="utf-8") as f:
        t_records = list(csv.DictReader(f))

    assert len(t_records) >= 7, "Expected at least 7 candidate models in test evaluation"
    for r in t_records:
        rec = float(r["test_recall_pct"])
        fpr = float(r["test_fpr_pct"])
        shout_fpr = float(r["test_shouted_speech_fpr_pct"])
        assert 0.0 <= rec <= 100.0
        assert 0.0 <= fpr <= 100.0
        assert 0.0 <= shout_fpr <= 100.0
        assert r["final_acceptance_verdict"] == "NOT CERTIFIED", "No candidate should be automatically certified!"
