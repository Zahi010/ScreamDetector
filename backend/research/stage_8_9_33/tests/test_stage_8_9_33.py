import os
import sys
import hashlib
import csv
import json
import numpy as np
import pytest
import torch

# Add src to path
sys.path.insert(0, os.path.abspath('backend/research/stage_8_9_33/src'))
from train_and_evaluate_stage8_9_33 import DualEncoderAcousticModel, SemanticProjectionHead, evaluate_metrics

EXPECTED_PRODUCTION_HASHES = {
    'backend/models/scream_classifier.joblib': 'ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f',
    'backend/models/model_metadata.json': '30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60',
    'backend/reports/test_predictions.csv': 'e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d',
    'backend/reports/stage5_test_evaluation.md': '9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2'
}

def test_production_artifact_immutability():
    """Verify that all four production artifacts remain 100% byte-for-byte identical."""
    for path, expected_hash in EXPECTED_PRODUCTION_HASHES.items():
        assert os.path.exists(path), f"Production artifact missing: {path}"
        with open(path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch on {path}: expected {expected_hash}, got {actual_hash}"

def test_dataset_manifest_integrity_and_splits():
    """Verify that dataset manifest exists, contains required splits, and has 0 source group leakage."""
    manifest_path = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    assert os.path.exists(manifest_path)
    
    with open(manifest_path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        
    assert len(rows) > 1000
    train_sg = set()
    val_sg = set()
    test_sg = set()
    
    for r in rows:
        sg = r['source_group_id']
        split = r['split']
        assert float(r['duration_seconds']) > 0.0
        assert r['license'] != ''
        
        if split == 'train':
            train_sg.add(sg)
        elif split == 'val':
            val_sg.add(sg)
        elif split == 'test':
            test_sg.add(sg)
            
    # Assert complete source-group separation (zero leakage)
    assert len(train_sg.intersection(val_sg)) == 0, "Train-Val source group leakage detected!"
    assert len(train_sg.intersection(test_sg)) == 0, "Train-Test source group leakage detected!"
    assert len(val_sg.intersection(test_sg)) == 0, "Val-Test source group leakage detected!"

def test_missing_pitch_and_nan_inf_protection():
    """Verify that DualEncoder handles NaN/Inf, missing pitches, and unvoiced signals safely."""
    model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model.eval()
    
    # Create corrupted inputs with NaNs, Infs, and negative values
    x_sem = torch.randn(2, 1024)
    x_acoust_corrupted = torch.tensor([
        [float('nan'), float('inf'), -5.0, 0.0, float('nan'), 1.2],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], dtype=torch.float32)
    
    mask = (~torch.isnan(x_acoust_corrupted) & ~torch.isinf(x_acoust_corrupted) & (x_acoust_corrupted > 0.0)).float()
    
    with torch.no_grad():
        logits, z_sem, z_acoust = model(x_sem, x_acoust_corrupted, mask)
        prob = torch.sigmoid(logits)
        
    assert not torch.isnan(logits).any(), "NaN found in model logits!"
    assert not torch.isinf(logits).any(), "Inf found in model logits!"
    assert not torch.isnan(z_acoust).any(), "NaN found in acoustic projection!"
    assert (prob >= 0.0).all() and (prob <= 1.0).all(), "Probability outside [0, 1] bounds!"

def test_dual_encoder_model_checkpoint():
    """Verify that saved dual encoder model checkpoint loads and produces valid predictions."""
    ckpt_path = 'backend/research/stage_8_9_33/models/dual_encoder_model.pt'
    assert os.path.exists(ckpt_path)
    
    model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    state = torch.load(ckpt_path, map_location='cpu')
    model.load_state_dict(state)
    model.eval()
    
    dummy_sem = torch.randn(1, 1024)
    dummy_acoust = torch.randn(1, 6)
    dummy_mask = torch.ones(1, 6)
    
    with torch.no_grad():
        logits, z_sem, z_acoust = model(dummy_sem, dummy_acoust, dummy_mask)
        prob = torch.sigmoid(logits).item()
        
    assert 0.0 <= prob <= 1.0
    assert z_sem.shape == (1, 128)
    assert z_acoust.shape == (1, 32)
    # Check L2 unit normalization
    assert np.isclose(torch.norm(z_sem, p=2, dim=-1).item(), 1.0, atol=1e-4)
    assert np.isclose(torch.norm(z_acoust, p=2, dim=-1).item(), 1.0, atol=1e-4)

def test_eof_flushing_and_residual_padding():
    """Verify that residual audio shorter than window is zero-padded without creating false positive scream artifacts."""
    # Test that silence-padded frame yields low scream probability
    ckpt_path = 'backend/research/stage_8_9_33/models/dual_encoder_model.pt'
    assert os.path.exists(ckpt_path)
    model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model.load_state_dict(torch.load(ckpt_path, map_location='cpu'))
    model.eval()
    
    # Pure zero/silence input
    zero_sem = torch.zeros(1, 1024)
    zero_acoust = torch.zeros(1, 6)
    zero_mask = torch.zeros(1, 6) # All features masked out
    
    with torch.no_grad():
        logits, _, _ = model(zero_sem, zero_acoust, zero_mask)
        prob = torch.sigmoid(logits).item()
        
    # Silence should never trigger an alert at 0.35 threshold
    assert prob < 0.35, f"False positive alert triggered on zero-padded silence: prob={prob}"

def test_inference_latency_gate():
    """Verify that computational forward-pass latency is well under 25ms."""
    model = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model.eval()
    
    dummy_sem = torch.randn(1, 1024)
    dummy_acoust = torch.randn(1, 6)
    dummy_mask = torch.ones(1, 6)
    
    import time
    latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = model(dummy_sem, dummy_acoust, dummy_mask)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed_ms)
        
    p95 = np.percentile(latencies, 95)
    # Neural forward pass alone must be < 5.0ms
    assert p95 < 5.0, f"Neural inference latency too high: {p95:.2f} ms"

def test_evaluation_metrics_calculator():
    """Verify the metrics evaluation logic behaves consistently."""
    y_true = np.array([1, 1, 0, 0, 1])
    y_prob = np.array([0.9, 0.4, 0.1, 0.6, 0.2])
    # At threshold 0.35:
    # Preds: [1, 1, 0, 1, 0] -> TP=2, FN=1, FP=1, TN=1
    m = evaluate_metrics(y_true, y_prob, threshold=0.35)
    assert m['tp'] == 2
    assert m['fn'] == 1
    assert m['fp'] == 1
    assert m['tn'] == 1
    assert np.isclose(m['recall'], 2/3)
    assert np.isclose(m['precision'], 2/3)
    assert np.isclose(m['fpr'], 1/2)
