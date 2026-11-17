import sys
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parents[3]
WORKSPACE_DIR = BACKEND_DIR / "research" / "stage_8_9_22"
sys.path.insert(0, str(WORKSPACE_DIR))

from src.sddfr_classifier import SDDFRTwoTierClassifier
from src.dynamic_feature_router import DynamicFeatureRouter

f17_path = BACKEND_DIR / "experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz"
f18_path = BACKEND_DIR / "experiments/stage8_9_18_temporal_phonation/data/features_stage8_9_18_temporal.npz"

d17 = np.load(f17_path, allow_pickle=True)
d18 = np.load(f18_path, allow_pickle=True)

splits = d17["splits"]
y_binary = d17["y_binary"].astype(int)
cats = d17["canonical_categories"]
durs = d18["durations"]
file_ids = d17["file_ids"]

features_yamnet = d17["features_yamnet"]
mean_yamnet = features_yamnet[:, 0:1024]
features_temporal = d18["features_temporal"]
features_seq = d18["features_seq_16"]

X_t1 = np.hstack([mean_yamnet, features_temporal]).astype(np.float32)

seq_e_b1 = np.sum(features_seq[:, :, 0:4], axis=-1)
seq_e_b2 = np.sum(features_seq[:, :, 4:8], axis=-1)
seq_e_b3 = np.sum(features_seq[:, :, 8:12], axis=-1)
seq_e_b4 = np.sum(features_seq[:, :, 12:16], axis=-1)
seq_tot = seq_e_b1 + seq_e_b2 + seq_e_b3 + seq_e_b4 + 1e-6

e1_r = np.mean(seq_e_b1 / seq_tot, axis=1, keepdims=True)
e2_r = np.mean(seq_e_b2 / seq_tot, axis=1, keepdims=True)
e3_r = np.mean(seq_e_b3 / seq_tot, axis=1, keepdims=True)
e4_r = np.mean(seq_e_b4 / seq_tot, axis=1, keepdims=True)
turb_pers = np.mean(seq_e_b4 / seq_tot, axis=1, keepdims=True)
turb_mod = np.std(seq_e_b4 / seq_tot, axis=1, keepdims=True)

f_disp = np.abs(np.argmax(features_seq[:, :, 4:8], axis=-1) - np.argmax(features_seq[:, :, 0:4], axis=-1))
f_disp_m = np.mean(f_disp, axis=1, keepdims=True) * 200.0 + 400.0
formant_avail = (features_temporal[:, 20:21] > 0.30).astype(np.float32)

raw_pitch_fail = features_temporal[:, 21:22]
he_pitch_fail = np.clip(raw_pitch_fail * (features_temporal[:, 4:5] / 0.20), 0.0, 1.0)
hnr_proxy = (features_temporal[:, 23:24] * 25.0) - 5.0
hnr_instab = features_temporal[:, 24:25] * 5.0
shr_db_proxy = np.where(he_pitch_fail > 0.3, -4.5, -25.0).astype(np.float32).reshape(-1, 1)

X_t2 = np.hstack([
    he_pitch_fail, raw_pitch_fail, features_temporal[:, 19:21],
    shr_db_proxy, shr_db_proxy + 20.0,
    hnr_proxy, hnr_instab,
    f_disp_m, formant_avail,
    turb_pers, turb_mod, e1_r, e2_r, e3_r, e4_r,
    features_temporal[:, 0:4],
    features_temporal[:, 12:16]
]).astype(np.float32)

tr = (splits == "train")
va = (splits == "val")
te = (splits == "test")

sddfr = SDDFRTwoTierClassifier(tier1_threshold=0.35, random_state=42)
sddfr.fit(
    X_t1_tr=X_t1[tr], y_tr=y_binary[tr], X_t2_tr=X_t2[tr],
    X_t1_va=X_t1[va], y_va=y_binary[va], X_t2_va=X_t2[va]
)

X_t1_te_s = sddfr.scaler_t1.transform(X_t1[te])
t1_probs = sddfr.clf_t1.predict_proba(X_t1_te_s)[:, 1]
t1_preds = (t1_probs >= 0.35).astype(int)

test_cats = cats[te]
test_y = y_binary[te]
is_shout = (test_cats == "SHOUTING_EXCITED_SPEECH")
is_scream = (test_y == 1)
is_hard_neg = (test_y == 0)

print(f"Total test shouts: {np.sum(is_shout)}")
print(f"Tier 1 shout positive alerts: {np.sum(t1_preds[is_shout])} / {np.sum(is_shout)} = {np.mean(t1_preds[is_shout]):.4f}")
print(f"Tier 1 scream detections: {np.sum(t1_preds[is_scream])} / {np.sum(is_scream)} = {np.mean(t1_preds[is_scream]):.4f}")
print(f"Tier 1 hard negative false alarms: {np.sum(t1_preds[is_hard_neg])} / {np.sum(is_hard_neg)} = {np.mean(t1_preds[is_hard_neg]):.4f}")

# Check 17/84 vs 17/42:
print(f"17 / 84 = {17/84:.4f}")
