import sys, time
from pathlib import Path
import soundfile as sf
import numpy as np
import pandas as pd

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

print("Loading YAMNet...")
t0 = time.time()
yamnet = YAMNetLoader()
yamnet.load()
print(f"YAMNet loaded in {time.time()-t0:.2f}s")

manifest = pd.read_csv(REPO_ROOT / "backend/research/stage_8_9_53/evaluation/reserved_test_manifest_verified.csv")
for i in range(3):
    row = manifest.iloc[i]
    p = REPO_ROOT / row["workspace_audio_path"]
    t1 = time.time()
    wf, sr = load_audio(p, target_sr=TARGET_SAMPLE_RATE)
    preds, embs, _ = yamnet.infer(wf)
    dur = len(wf) / sr
    print(f"Clip {i} ({row['expansion_file_id']}) dur: {dur:.2f}s infer time: {time.time()-t1:.3f}s, embs shape: {embs.shape}")

