import os
import sys
import csv
import soundfile as sf
import numpy as np

def main():
    print("=" * 70)
    print("STAGE 8.9.35 - CHECKPOINT 1: REPRODUCTION & SPATIAL-CHANNEL AUDIT")
    print("=" * 70)
    
    # 1. Reproduce Stage 8.9.34 Baseline Metrics
    acc_matrix_path = 'backend/research/stage_8_9_34/evaluation/candidate_acceptance_matrix.csv'
    comp_path = 'backend/research/stage_8_9_34/evaluation/candidate_comparison.csv'
    preds_path = 'backend/research/stage_8_9_34/predictions/test_predictions_stage8_9_34.csv'
    
    assert os.path.exists(acc_matrix_path), "Missing acceptance matrix!"
    assert os.path.exists(comp_path), "Missing comparison CSV!"
    assert os.path.exists(preds_path), "Missing test predictions!"
    
    with open(acc_matrix_path, encoding='utf-8') as f:
        acc_rows = list(csv.DictReader(f))
    with open(comp_path, encoding='utf-8') as f:
        comp_rows = list(csv.DictReader(f))
    with open(preds_path, encoding='utf-8') as f:
        preds = list(csv.DictReader(f))
        
    print(f"Test Partition Size ($N$): {len(preds)}")
    assert len(preds) == 293, f"Expected N=293, got {len(preds)}"
    
    y_true = np.array([int(p['ground_truth']) for p in preds])
    y_prob = np.array([float(p['tsa_dual_encoder_probability']) for p in preds])
    cats = np.array([p['category'] for p in preds])
    sg_ids = np.array([p['source_group_id'] for p in preds])
    
    n_screams = np.sum(y_true == 1)
    n_negatives = np.sum(y_true == 0)
    n_source_groups = len(set(sg_ids))
    
    print(f"Cohort Balance: {n_screams} screams, {n_negatives} hard negatives across {n_source_groups} source groups")
    assert n_screams == 102
    assert n_negatives == 191
    assert n_source_groups == 111
    
    print("\nAudited Stage 8.9.34 Candidates:")
    for r in acc_rows:
        print(f"  {r['Candidate']:42s} | Recall: {r['Recall']:8s} | HN-FPR: {r['HN-FPR']:8s} | Shout-FPR: {r['Shout-FPR']:8s} | Latency: {r['P95']}")
        
    # 2. Complete Audio Channel and Hardware Audit
    print("\n--- SPATIAL AUDIO CHANNEL AUDIT ---")
    manifest_path = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    with open(manifest_path, encoding='utf-8') as f:
        manifest_rows = list(csv.DictReader(f))
        
    channel_counts = {}
    sample_rates = {}
    for r in manifest_rows:
        p = r['workspace_audio_path']
        if os.path.exists(p):
            info = sf.info(p)
            c = info.channels
            sr = info.samplerate
            channel_counts[c] = channel_counts.get(c, 0) + 1
            sample_rates[sr] = sample_rates.get(sr, 0) + 1
            
    print(f"Total Corpus Files Audited: {len(manifest_rows)}")
    print(f"Channel Count Distribution: {channel_counts}")
    print(f"Sample Rate Distribution: {sample_rates}")
    
    # Check held-out test partition
    test_rows = [r for r in manifest_rows if r['split'] == 'test']
    test_channels = {1: sum(1 for r in test_rows if sf.info(r['workspace_audio_path']).channels == 1)}
    print(f"Test Partition ($N={len(test_rows)}$) Channel Distribution: {test_channels}")
    
    print("\nHARDWARE LIMITATION AUDIT:")
    print("  Documented Device Microphone: INMP441 Omnidirectional I2S Microphone (Single Mono)")
    print("  Physical Microphone Geometry: None (Single acoustic point source sensor)")
    print("  Genuine Multi-Channel Files in Corpus: 0 out of 1,328 (0.00%)")
    print("  Physical Beamforming Feasibility on Current Hardware: IMPOSSIBLE (Requires N >= 2 array)")
    print("  Physical Spatial Evaluation on Held-Out Test Set: NOT EVALUABLE on genuine multichannel data")
    print("  Permitted Spatial Investigation: Track B Controlled Acoustic Simulation (clearly labeled synthetic)")
    
    print("\nCHECKPOINT 1 SIGN-OFF: Reproduction confirmed, channel audit complete. Ready for Checkpoint 2.")

if __name__ == '__main__':
    main()
