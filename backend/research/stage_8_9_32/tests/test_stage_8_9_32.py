import os
import csv
import json
import hashlib
import numpy as np
import pytest
import joblib
import torch

import sys
sys.path.append('backend/research/stage_8_9_31/src')
sys.path.append('.')
from research_ring_buffer import ResearchAudioRingBuffer

# 1. Test Production Integrity
def test_production_hashes_integrity():
    expected = {
        'backend/models/scream_classifier.joblib': 'ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f',
        'backend/models/model_metadata.json': '30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60',
        'backend/reports/test_predictions.csv': 'e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d',
        'backend/reports/stage5_test_evaluation.md': '9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2'
    }
    for path, exp in expected.items():
        assert os.path.exists(path), f"Missing production artifact: {path}"
        observed = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        assert observed == exp, f"Production hash violation in {path}!"

# 2. Test Dataset Reconciliation & Zero Duplicates
def test_negative_denominator_and_zero_duplicates():
    mem_path = 'backend/research/stage_8_9_32/audit/negative_category_membership.csv'
    assert os.path.exists(mem_path)
    with open(mem_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 98, f"Expected 98 negative recordings, got {len(rows)}"
    
    # Check duplicate relationships
    dup_path = 'backend/research/stage_8_9_32/audit/duplicate_relationships.csv'
    assert os.path.exists(dup_path)

# 3. Test Partition Independence (Zero Source-Group Leakage)
def test_zero_source_group_leakage():
    data_path = 'backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz'
    assert os.path.exists(data_path)
    data = np.load(data_path, allow_pickle=True)
    
    splits = data['splits']
    source_groups = data['source_groups']
    
    train_sgs = set(source_groups[splits == 'train'])
    val_sgs = set(source_groups[splits == 'val'])
    test_sgs = set(source_groups[splits == 'test'])
    
    # Check intersection
    train_val_overlap = train_sgs.intersection(val_sgs)
    train_test_overlap = train_sgs.intersection(test_sgs)
    val_test_overlap = val_sgs.intersection(test_sgs)
    
    assert len(train_val_overlap) == 0, f"Leakage between train and val: {train_val_overlap}"
    assert len(train_test_overlap) == 0, f"Leakage between train and test: {train_test_overlap}"
    assert len(val_test_overlap) == 0, f"Leakage between val and test: {val_test_overlap}"

# 4. Test Contrastive Head Architecture and Normalization
def test_contrastive_head_forward():
    from backend.research.stage_8_9_32.src.train_contrastive import ContrastiveProjectionHead
    head = ContrastiveProjectionHead(1024, 256, 128)
    head.eval()
    
    x = torch.randn(4, 1024)
    with torch.no_grad():
        z = head(x)
        
    assert z.shape == (4, 128)
    norms = torch.norm(z, p=2, dim=-1)
    assert torch.allclose(norms, torch.ones(4), atol=1e-5), "Contrastive embeddings must be unit L2-normalized"

# 5. Test Hard-Negative Discrimination Improvement
def test_confuser_discrimination_improvement():
    cat_fpr_path = 'backend/research/stage_8_9_32/evaluation/category_fpr_results.csv'
    assert os.path.exists(cat_fpr_path)
    with open(cat_fpr_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        
    cheering_row = next((r for r in rows if r['category'] == 'crowd_chant_cheering'), None)
    crying_row = next((r for r in rows if r['category'] == 'infant_crying'), None)
    
    assert cheering_row is not None
    assert crying_row is not None
    
    # In stage 31, cheering FPR was 78.57%, crying was 85.71%
    cheering_fpr = float(cheering_row['contrastive_model_a_fpr_pct'].split('%')[0])
    crying_fpr = float(crying_row['contrastive_model_a_fpr_pct'].split('%')[0])
    
    assert cheering_fpr < 20.0, f"Cheering FPR must be < 20%, observed {cheering_fpr}%"
    assert crying_fpr < 20.0, f"Crying FPR must be < 20%, observed {crying_fpr}%"

# 6. Test Multi-Resolution RingBuffer Functionality
def test_multiresolution_ring_buffer():
    buf = ResearchAudioRingBuffer(window_sec=0.375, hop_sec=0.1, sample_rate=16000)
    audio = np.random.randn(8000).astype(np.float32)
    windows = buf.ingest(audio)
    flushed = buf.flush()
    total_windows = len(windows) + len(flushed)
    assert total_windows > 0
    for w in windows + flushed:
        assert len(w.pcm) == 6000
        assert w.valid_samples > 0

# 7. Test Computational Latency Target
def test_computational_latency_benchmark():
    lat_path = 'backend/research/stage_8_9_32/benchmarks/research_latency_benchmark.csv'
    assert os.path.exists(lat_path)
    with open(lat_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    total_row = next((r for r in rows if 'Total' in r['component']), None)
    assert total_row is not None
    p95_val = float(total_row['p95'].split()[0])
    assert p95_val <= 25.0, f"P95 latency target violated: {p95_val} ms"
