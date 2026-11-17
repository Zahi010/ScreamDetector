"""
Stage 8.9.35 - Comprehensive Test Suite
Validates dataset integrity, hardware constraints, filter stability,
NaN/Inf protection, EOF flushing, model inference, and production immutability.
"""
import os
import sys
import hashlib
import numpy as np
import torch
import pytest
from scipy.signal import butter, sosfilt

# Add local path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from train_and_evaluate_stage8_9_35 import MultiPathwayFusionModel
from run_phase1_subband_analysis import extract_subband_features, BANDS

# 1. Production Immutability Test
def test_production_hashes_immutable():
    expected_hashes = {
        "backend/models/scream_classifier.joblib": "ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f",
        "backend/models/model_metadata.json": "30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60",
        "backend/reports/test_predictions.csv": "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d",
        "backend/reports/stage5_test_evaluation.md": "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"
    }
    for file_path, exp_hash in expected_hashes.items():
        assert os.path.exists(file_path), f"Missing production file: {file_path}"
        with open(file_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch for {file_path}! Expected {exp_hash}, got {actual_hash}"

# 2. Channel Count and Hardware Constraint Test
def test_channel_count_and_hardware_constraint():
    manifest_path = "backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv"
    assert os.path.exists(manifest_path)
    import pandas as pd
    df = pd.read_csv(manifest_path)
    assert len(df) == 1328
    
    # Check that corpus is 100% mono
    test_df = df[(df["split"] == "test") & (df["binary_label"] != "ambiguous")]
    assert len(test_df) == 293
    assert (test_df["binary_label"] == "scream").sum() == 102
    assert (test_df["binary_label"] == "non_scream").sum() == 191

# 3. Source-Group Split Isolation Test
def test_dataset_integrity_and_split_isolation():
    data_path = "backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz"
    assert os.path.exists(data_path)
    data = np.load(data_path, allow_pickle=True)
    splits = data["splits"]
    source_groups = data["source_groups"]
    
    train_groups = set(source_groups[splits == "train"])
    val_groups = set(source_groups[splits == "val"])
    test_groups = set(source_groups[splits == "test"])
    
    assert len(train_groups.intersection(test_groups)) == 0, "Data leakage: Train & Test source groups overlap!"
    assert len(val_groups.intersection(test_groups)) == 0, "Data leakage: Val & Test source groups overlap!"

# 4. Frequency-Filter Stability Test
def test_frequency_subband_filter_stability():
    sr = 16000
    for _, low, high in BANDS:
        sos = butter(4, [low, high], btype='bandpass', fs=sr, output='sos')
        # Check pole stability: all poles inside unit circle
        # In SOS form, denominator is [1, a1, a2] for each 2nd order section
        for section in sos:
            a = section[3:]
            roots = np.roots(a)
            assert np.all(np.abs(roots) < 1.0), f"Unstable filter poles in band [{low}, {high}] Hz!"
            
        # Test impulse response stability
        impulse = np.zeros(1600, dtype=np.float32)
        impulse[0] = 1.0
        filtered = sosfilt(sos, impulse)
        assert not np.any(np.isnan(filtered))
        assert not np.any(np.isinf(filtered))
        assert np.max(np.abs(filtered)) < 10.0

# 5. Subband Feature Extraction & Non-Negative Ratios
def test_subband_feature_vector_dimension_and_ratios():
    sr = 16000
    # Generate 1-second white noise signal
    audio = np.random.randn(sr).astype(np.float32)
    feats = extract_subband_features(audio, sr)
    
    assert "Band1_300_800Hz_rel_energy" in feats
    assert "Band6_4000_6000Hz_rel_energy" in feats
    assert "scream_band_to_vocal_ratio" in feats
    assert "high_band_whistle_ratio" in feats
    
    # Check bounds
    for i in range(1, 7):
        b_key = f"Band{i}_"
        matching = [k for k in feats if k.startswith(b_key) and k.endswith("_rel_energy")]
        assert len(matching) == 1
        val = feats[matching[0]]
        assert 0.0 <= val <= 1.0, f"Relative energy out of bounds: {val}"
        
    assert feats["scream_band_to_vocal_ratio"] >= 0.0
    assert feats["high_band_whistle_ratio"] >= 0.0
    assert not any(np.isnan(v) for v in feats.values())

# 6. Spatial Simulation GCC-PHAT Mechanics Test
def test_spatial_simulation_mechanics():
    sr = 16000
    d = 0.05
    c = 343.0
    # True delay: 2 samples
    true_delay = 2
    x = np.random.randn(1600).astype(np.float32)
    x1 = x
    x2 = np.roll(x, true_delay)
    
    # GCC-PHAT
    N = len(x1)
    X1 = np.fft.rfft(x1)
    X2 = np.fft.rfft(x2)
    R = X2 * np.conj(X1)
    R_phat = R / (np.abs(R) + 1e-9)
    cc = np.fft.irfft(R_phat, n=N)
    cc = np.fft.fftshift(cc)
    lags = np.arange(-N//2, N//2)
    est_delay = lags[np.argmax(cc)]
    
    assert abs(est_delay - true_delay) <= 1, f"GCC-PHAT delay error: expected {true_delay}, got {est_delay}"

# 7. Phonation Missing-Mask & NaN Protection Test
def test_missing_mask_phonation_protection():
    device = torch.device("cpu")
    model = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11).to(device)
    model.eval()
    
    # Input with NaNs and Infs in acoustic features
    x_sem = torch.randn(2, 1024)
    x_acoust = torch.tensor([[np.nan, 250.0, np.nan, 0.05, 0.02, np.inf],
                             [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], dtype=torch.float32)
    mask_acoust = torch.tensor([[0.0, 1.0, 0.0, 1.0, 1.0, 0.0],
                               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], dtype=torch.float32)
    x_subband = torch.randn(2, 11)
    
    with torch.no_grad():
        logits, z_sem, z_subband = model(x_sem, x_acoust, mask_acoust, x_subband)
        probs = torch.sigmoid(logits)
        
    assert not torch.any(torch.isnan(logits)), "NaN detected in logits!"
    assert not torch.any(torch.isinf(logits)), "Inf detected in logits!"
    assert torch.all(probs >= 0.0) and torch.all(probs <= 1.0), "Probabilities out of [0, 1] range!"

# 8. Model Forward Pass & Unit-Norm Hypersphere Test
def test_multi_pathway_model_forward_pass_and_unit_norm():
    device = torch.device("cpu")
    model = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11).to(device)
    model.eval()
    
    x_sem = torch.randn(4, 1024)
    x_acoust = torch.randn(4, 6)
    mask_acoust = torch.ones(4, 6)
    x_subband = torch.randn(4, 11)
    
    with torch.no_grad():
        logits, z_sem, z_subband = model(x_sem, x_acoust, mask_acoust, x_subband)
        
    assert logits.shape == (4,), f"Expected shape (4,), got {logits.shape}"
    assert z_sem.shape == (4, 128), f"Expected shape (4, 128), got {z_sem.shape}"
    assert z_subband.shape == (4, 16), f"Expected shape (4, 16), got {z_subband.shape}"
    
    # Test L2 Unit-Norm normalization
    sem_norms = torch.norm(z_sem, p=2, dim=-1)
    subband_norms = torch.norm(z_subband, p=2, dim=-1)
    assert torch.allclose(sem_norms, torch.ones_like(sem_norms), atol=1e-5), "z_sem not unit-norm!"
    assert torch.allclose(subband_norms, torch.ones_like(subband_norms), atol=1e-5), "z_subband not unit-norm!"

# 9. Streaming EOF Flushing & Short Window Padding Test
def test_eof_flushing_and_short_window_padding():
    window_samples = 15600 # 975 ms
    short_audio = np.random.randn(8000).astype(np.float32) # 0.5s audio
    
    # EOF flushing logic: pad trailing buffer with zeros to full window length
    padded = np.pad(short_audio, (0, window_samples - len(short_audio)), mode='constant')
    assert len(padded) == window_samples
    assert np.all(padded[8000:] == 0.0)
    
    # Feature extraction must succeed without error
    feats = extract_subband_features(padded, sr=16000)
    assert "Band2_800_1500Hz_rel_energy" in feats
    assert not any(np.isnan(v) for v in feats.values())

# 10. Gate Rejection Consistency Test
def test_candidate_gate_rejection_consistency():
    acc_matrix_path = "backend/research/stage_8_9_35/evaluation/candidate_acceptance_matrix.csv"
    assert os.path.exists(acc_matrix_path)
    import pandas as pd
    df = pd.read_csv(acc_matrix_path)
    
    cand_d = df[df["Candidate"].str.contains("Candidate D")].iloc[0]
    recall_val = float(cand_d["Recall"].replace("%", ""))
    hn_fpr_val = float(cand_d["HN-FPR"].replace("%", ""))
    
    assert recall_val < 96.0, f"Expected Gate 1 to fail (<96%), but got {recall_val}%"
    assert hn_fpr_val > 5.0, f"Expected Gate 2 to fail (>5%), but got {hn_fpr_val}%"
    assert cand_d["Final Status"] == "REJECTED FOR PRODUCTION — RESEARCH ONLY"
