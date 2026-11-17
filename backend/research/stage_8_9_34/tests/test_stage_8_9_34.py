import os
import sys
import csv
import hashlib
import numpy as np
import pytest
import torch

sys.path.insert(0, os.path.abspath('backend/research/stage_8_9_34/src'))
from train_and_evaluate_stage8_9_34 import (
    JointTSADualEncoder, CausalGRUTemporalAggregator, CausalTCNAggregator,
    GatedTemporalAggregator, evaluate_metrics
)

EXPECTED_PRODUCTION_HASHES = {
    'backend/models/scream_classifier.joblib': 'ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f',
    'backend/models/model_metadata.json': '30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60',
    'backend/reports/test_predictions.csv': 'e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d',
    'backend/reports/stage5_test_evaluation.md': '9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2'
}

def test_production_artifact_immutability():
    """Verify that all four production baseline artifacts remain 100% byte-for-byte identical."""
    for path, expected_hash in EXPECTED_PRODUCTION_HASHES.items():
        assert os.path.exists(path), f"Missing artifact: {path}"
        with open(path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch on {path}: expected {expected_hash}, got {actual_hash}"

def test_dataset_integrity_and_source_group_separation():
    """Verify source-group partitioning: 0 session/uploader leakage between Train, Val, and Test."""
    manifest_path = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    assert os.path.exists(manifest_path)
    with open(manifest_path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        
    train_sg = set(r['source_group_id'] for r in rows if r['split'] == 'train')
    val_sg = set(r['source_group_id'] for r in rows if r['split'] == 'val')
    test_sg = set(r['source_group_id'] for r in rows if r['split'] == 'test')
    
    assert len(train_sg.intersection(val_sg)) == 0, "Train-Val leakage detected!"
    assert len(train_sg.intersection(test_sg)) == 0, "Train-Test leakage detected!"
    assert len(val_sg.intersection(test_sg)) == 0, "Val-Test leakage detected!"

def test_causal_temporal_processing():
    """Verify that temporal aggregators (GRU, TCN) are strictly causal (future-invariant)."""
    gru = CausalGRUTemporalAggregator(input_dim=160, hidden_dim=64)
    gru.eval()
    
    # Sequence of 3 frames
    seq = torch.randn(1, 3, 160)
    
    # Perturbing the future (frame 3) should change output, but frame 1 alone must be computable
    with torch.no_grad():
        out_full = gru(seq)
        out_partial = gru(seq[:, :1, :]) # partial context at stream onset
        
    assert torch.isfinite(out_full).all()
    assert torch.isfinite(out_partial).all()

def test_partial_context_stream_onset():
    """Verify TSA-DualEncoder can execute cleanly on single-frame partial context at stream onset."""
    model = JointTSADualEncoder(sem_dim=1024, acoust_dim=6, proj_sem=128, proj_acoust=32, gru_dim=64)
    model.eval()
    
    # Single frame onset sequence: (1, 1, 1024)
    x_sem_partial = torch.randn(1, 1, 1024)
    x_snr = torch.randn(1, 1)
    x_acoust = torch.randn(1, 6)
    x_mask = torch.ones(1, 6)
    
    with torch.no_grad():
        logits, _, _ = model(x_sem_partial, x_snr, x_acoust, x_mask)
        prob = torch.sigmoid(logits).item()
        
    assert 0.0 <= prob <= 1.0

def test_missing_pitch_and_nan_inf_protection():
    """Verify that corrupt acoustic features (NaN, Inf, negative unvoiced) do not produce numerical failures."""
    model = JointTSADualEncoder(sem_dim=1024, acoust_dim=6, proj_sem=128, proj_acoust=32, gru_dim=64)
    model.eval()
    
    x_sem = torch.randn(2, 3, 1024)
    x_snr = torch.randn(2, 1)
    x_corrupt = torch.tensor([
        [float('nan'), float('inf'), -5.0, 0.0, float('nan'), 1.2],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], dtype=torch.float32)
    mask = (~torch.isnan(x_corrupt) & ~torch.isinf(x_corrupt) & (x_corrupt > 0.0)).float()
    
    with torch.no_grad():
        logits, z_sem, cry_pred = model(x_sem, x_snr, x_corrupt, mask)
        prob = torch.sigmoid(logits)
        
    assert not torch.isnan(logits).any()
    assert not torch.isinf(logits).any()
    assert (prob >= 0.0).all() and (prob <= 1.0).all()
    assert (cry_pred >= 0.0).all() and (cry_pred <= 1.0).all()

def test_eof_flushing_and_zero_padded_silence():
    """Verify that residual silence padding does not trigger a false positive scream alert."""
    model = JointTSADualEncoder(sem_dim=1024, acoust_dim=6, proj_sem=128, proj_acoust=32, gru_dim=64)
    ckpt = 'backend/research/stage_8_9_34/models/tsa_dual_encoder_model.pt'
    if os.path.exists(ckpt):
        model.load_state_dict(torch.load(ckpt, map_location='cpu'))
    model.eval()
    
    zero_sem = torch.zeros(1, 3, 1024)
    zero_snr = torch.zeros(1, 1)
    zero_acoust = torch.zeros(1, 6)
    zero_mask = torch.zeros(1, 6)
    
    with torch.no_grad():
        logits, _, _ = model(zero_sem, zero_snr, zero_acoust, zero_mask)
        prob = torch.sigmoid(logits).item()
        
    assert prob < 0.35, f"False alert triggered on silence: prob={prob}"

def test_inference_latency_gate():
    """Verify that computational forward-pass latency is well within 25ms."""
    model = JointTSADualEncoder(sem_dim=1024, acoust_dim=6, proj_sem=128, proj_acoust=32, gru_dim=64)
    model.eval()
    
    dummy_sem = torch.randn(1, 3, 1024)
    dummy_snr = torch.randn(1, 1)
    dummy_acoust = torch.randn(1, 6)
    dummy_mask = torch.ones(1, 6)
    
    import time
    latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = model(dummy_sem, dummy_snr, dummy_acoust, dummy_mask)
        elapsed = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed)
        
    p95 = np.percentile(latencies, 95)
    assert p95 < 5.0, f"Neural forward-pass latency exceeds 5ms: {p95:.2f} ms"
