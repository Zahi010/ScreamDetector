import os
import numpy as np
import pandas as pd

npz_path = "backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz"
data = np.load(npz_path, allow_pickle=True)
print("Keys in yamnet_features_v3.npz:", list(data.keys()))
print("features_mean shape:", data['features_mean'].shape)
print("vocal_features shape:", data['vocal_features'].shape)
print("file_ids count:", len(data['file_ids']))
print("First 3 file_ids:", data['file_ids'][:3])
print("First 3 vocal_features:\n", data['vocal_features'][:3])

# Check subband csv
sb_path = "backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv"
if os.path.exists(sb_path):
    df_sb = pd.read_csv(sb_path)
    print("\nSubband CSV rows:", len(df_sb))
    print("Subband columns:", list(df_sb.columns))
else:
    print("\nSubband CSV not found at", sb_path)

# Check how many of the 1578 records in v4 are in yamnet_features_v3.npz
df_split = pd.read_csv("backend/research/stage_8_9_38/manifests/research_split_v4.csv")
v3_fids = set(data['file_ids'])
v4_fids = set(df_split['file_id'])
print(f"\nTotal v4 records: {len(v4_fids)}")
print(f"Overlap with v3 cache: {len(v4_fids.intersection(v3_fids))}")
print(f"New records needing feature extraction: {len(v4_fids - v3_fids)}")
missing_fids = sorted(list(v4_fids - v3_fids))
print(f"Sample of missing records (should be the 250 acq_ records):", missing_fids[:5])
print(f"All missing records start with acq_?", all(f.startswith('acq_') for f in missing_fids))
