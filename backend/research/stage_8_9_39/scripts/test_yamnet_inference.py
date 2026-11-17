import sys
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
sys.path.insert(0, str(BACKEND_DIR))

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from src.model.yamnet_loader import YAMNetLoader

print("Testing YAMNetLoader initialization...")
yamnet = YAMNetLoader()
print("YAMNetLoader initialized successfully!")

test_audio = BACKEND_DIR / "research" / "stage_8_9_38" / "audio" / "short_screams" / "acq_short_scream_0001.wav"
print("Loading audio:", test_audio)
wf, sr = load_audio(test_audio, target_sr=TARGET_SAMPLE_RATE)
print(f"Waveform shape: {wf.shape}, sample rate: {sr}")
preds, embs, _ = yamnet.infer(wf)
print(f"Preds shape: {preds.shape}, Embs shape: {embs.shape}")
print("YAMNet extraction works perfectly!")
