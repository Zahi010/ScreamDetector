import joblib
import numpy as np
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
MODEL_PATH = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation" / "models" / "model_h_v5_snr.joblib"

m = joblib.load(MODEL_PATH)
pipe = m["pipe"]
clf = pipe.named_steps["clf"]
scaler = pipe.named_steps["scaler"]

print("Pipeline steps:", list(pipe.named_steps.keys()))
print("Coef shape:", clf.coef_.shape)
print("Mean of scaler mean_:", np.mean(scaler.mean_))
print("Mean of scaler scale_:", np.mean(scaler.scale_))

# Turbulence features are at [5120:5136]
turb_coefs = clf.coef_[0][5120:5136]
print("Turbulence coefs min/max/mean:", np.min(turb_coefs), np.max(turb_coefs), np.mean(turb_coefs))
print("Turbulence coefs:", np.round(turb_coefs, 4))

# SNR features are at [5144:5148]
snr_coefs = clf.coef_[0][5144:5148]
print("SNR coefs:", np.round(snr_coefs, 4))

# Top 20 overall features
top_indices = np.argsort(np.abs(clf.coef_[0]))[::-1][:20]
print("Top 20 absolute coef indices and values:")
for idx in top_indices:
    print(f"  Index {idx:4d}: coef={clf.coef_[0][idx]:+.4f}, mean={scaler.mean_[idx]:.4f}, scale={scaler.scale_[idx]:.4f}")
