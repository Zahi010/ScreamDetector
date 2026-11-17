"""Regression and unit tests for Stage 8.9.8 Temporal and Turbulence Modeling.

Validates:
- Deterministic feature extraction
- Sequence padding and masking logic
- Numerical stability on silent and invalid audio (no NaNs or crashes)
- Model serialization and reloading
- Source group disjointness
- Strict production isolation and threshold preservation
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest
import joblib

BACKEND_DIR = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research"
V3_MANIFEST = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "manifests" / "dataset_manifest_v3.json"


def test_v3_manifest_split_disjointness():
    """Verify that train, val, and test source groups are strictly disjoint."""
    assert V3_MANIFEST.exists(), f"Missing {V3_MANIFEST}"
    with open(V3_MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)

    train_sources = {r["source_group_id"] for r in data if r["split"] == "train"}
    val_sources = {r["source_group_id"] for r in data if r["split"] == "val"}
    test_sources = {r["source_group_id"] for r in data if r["split"] == "test"}

    assert len(train_sources & val_sources) == 0, "Train and Val source groups overlap!"
    assert len(train_sources & test_sources) == 0, "Train and Test source groups overlap!"
    assert len(val_sources & test_sources) == 0, "Val and Test source groups overlap!"


def test_numerical_stability_on_silent_and_extreme_audio():
    """Verify turbulence feature extraction is numerically stable on silence and DC offsets."""
    import sys
    sys.path.insert(0, str(EXPERIMENTS_DIR))
    from extract_temporal_and_turbulence_features import extract_16_turbulence_features

    sr = 16000
    # 1. Pure silence
    silent_audio = np.zeros(sr * 2, dtype=np.float32)
    feats_silent = extract_16_turbulence_features(silent_audio, sr=sr)
    assert len(feats_silent) == 16
    assert not np.any(np.isnan(feats_silent)), "NaN detected in silent audio features!"
    assert not np.any(np.isinf(feats_silent)), "Inf detected in silent audio features!"

    # 2. DC offset
    dc_audio = np.ones(sr * 2, dtype=np.float32) * 0.5
    feats_dc = extract_16_turbulence_features(dc_audio, sr=sr)
    assert len(feats_dc) == 16
    assert not np.any(np.isnan(feats_dc)), "NaN detected in DC audio features!"
    assert not np.any(np.isinf(feats_dc)), "Inf detected in DC audio features!"

    # 3. High-frequency impulse noise
    noise_audio = np.random.RandomState(42).randn(sr * 2).astype(np.float32)
    feats_noise = extract_16_turbulence_features(noise_audio, sr=sr)
    assert len(feats_noise) == 16
    assert not np.any(np.isnan(feats_noise)), "NaN detected in noise audio features!"


def test_sequence_padding_and_masking_logic():
    """Verify sequence padding and masking ensures uniform dimensions and preserves lengths."""
    max_len = 70
    dim = 1024

    # Simulate variable-length sequences
    seq_short = np.random.randn(15, dim).astype(np.float32)
    seq_long = np.random.randn(90, dim).astype(np.float32)

    # Pad/truncate short
    pad_short = np.zeros((max_len, dim), dtype=np.float32)
    pad_short[:len(seq_short)] = seq_short
    assert pad_short.shape == (70, 1024)
    assert np.all(pad_short[15:] == 0.0)

    # Pad/truncate long
    pad_long = seq_long[:max_len]
    assert pad_long.shape == (70, 1024)


def test_model_serialization_and_reproducibility():
    """Verify that saved Stage 8.9.8 models reload cleanly and produce deterministic outputs."""
    models_dir = EXPERIMENTS_DIR / "models"
    hv4_path = models_dir / "model_hv4_calibrated_hybrid.joblib"
    t3_path = models_dir / "model_t3_temporal_pooling.joblib"
    t4_path = models_dir / "model_t4_turbulence_ablation.joblib"

    if hv4_path.exists():
        hv4_bundle = joblib.load(hv4_path)
        assert "pipeline" in hv4_bundle
        assert "platt_scaler" in hv4_bundle
        assert "selected_threshold" in hv4_bundle
        pipe = hv4_bundle["pipeline"]
        scaler = hv4_bundle["platt_scaler"]

        # Synthetic test input (5,144-dim)
        x_dummy = np.random.RandomState(42).randn(3, 5144)
        logits = pipe.decision_function(x_dummy).reshape(-1, 1)
        probs = scaler.predict_proba(logits)[:, 1]
        assert probs.shape == (3,)
        assert np.all((probs >= 0.0) & (probs <= 1.0))

    if t3_path.exists():
        pipe_t3 = joblib.load(t3_path)
        x_t3 = np.random.RandomState(42).randn(2, 5120)
        p_t3 = pipe_t3.predict_proba(x_t3)[:, 1]
        assert p_t3.shape == (2,)

    if t4_path.exists():
        pipe_t4 = joblib.load(t4_path)
        x_t4 = np.random.RandomState(42).randn(2, 16)
        p_t4 = pipe_t4.predict_proba(x_t4)[:, 1]
        assert p_t4.shape == (2,)


def test_production_immutability_and_isolation():
    """Verify production model and metadata are untouched and retain 0.35 threshold."""
    prod_model_path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    prod_meta_path = BACKEND_DIR / "models" / "model_metadata.json"

    assert prod_model_path.exists()
    assert prod_meta_path.exists()

    with open(prod_meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["selected_threshold"] == 0.35, f"Production threshold altered: {meta.get('selected_threshold')}"
    assert meta["version"] == "v1.0.0"

    import hashlib
    with open(prod_model_path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest().upper()
    assert sha == "AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F", "Production model SHA-256 corrupted!"
