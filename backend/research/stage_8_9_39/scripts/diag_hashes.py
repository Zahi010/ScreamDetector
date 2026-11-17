import os
import hashlib
import pandas as pd
import soundfile as sf
import numpy as np

v4 = pd.read_csv("backend/research/stage_8_9_38/manifests/dataset_manifest_v4.csv")
print("Total rows:", len(v4))
print("acq_ rows:", len(v4[v4['file_id'].str.startswith('acq_')]))
print("historical rows:", len(v4[~v4['file_id'].str.startswith('acq_')]))

hist = v4[~v4['file_id'].str.startswith('acq_')]
mismatch = 0
match = 0
for _, r in hist.head(10).iterrows():
    p = r['workspace_audio_path']
    with open(p, 'rb') as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest()
    data, sr = sf.read(p, dtype='int16')
    pcm_sha = hashlib.sha256(data.tobytes()).hexdigest()
    print(f"ID: {r['file_id']}")
    print(f"  On disk exists: {os.path.exists(p)}")
    print(f"  Manifest sha256_hash: {r['sha256_hash']}")
    print(f"  Actual file sha256:   {actual_sha}")
    print(f"  Match: {actual_sha == r['sha256_hash']}")
    print(f"  Manifest pcm_sha256:  {r['pcm_sha256']}")
    print(f"  Actual pcm_sha256:    {pcm_sha}")
    print(f"  PCM Match: {pcm_sha == r['pcm_sha256']}")

# Also check acq_ records
acq = v4[v4['file_id'].str.startswith('acq_')]
acq_matches = 0
for _, r in acq.iterrows():
    p = r['workspace_audio_path']
    with open(p, 'rb') as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest()
    if actual_sha == r['sha256_hash']:
        acq_matches += 1
print(f"\nAcq records matching SHA-256: {acq_matches} / {len(acq)}")
