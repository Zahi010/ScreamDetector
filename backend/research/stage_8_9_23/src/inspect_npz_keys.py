import numpy as np

d17 = np.load("experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz", allow_pickle=True)
print("Keys in features_stage8_9_17.npz:", list(d17.keys()))
for k in d17.keys():
    if hasattr(d17[k], 'shape'):
        print(f"  {k}: shape={d17[k].shape}, dtype={d17[k].dtype}")
    else:
        print(f"  {k}: type={type(d17[k])}")

d18 = np.load("experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz", allow_pickle=True)
print("\nKeys in features_stage8_9_18_temporal.npz:", list(d18.keys()))
for k in d18.keys():
    if hasattr(d18[k], 'shape'):
        print(f"  {k}: shape={d18[k].shape}, dtype={d18[k].dtype}")
    else:
        print(f"  {k}: type={type(d18[k])}")
