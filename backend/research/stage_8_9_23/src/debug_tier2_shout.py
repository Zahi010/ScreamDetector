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

feat_names_t2 = [
    "high_energy_vocal_pitch_failure", "raw_pitch_failure_rate", "pitch_conf", "pitch_stability",
    "shr_db", "shr_norm",
    "hnr_db", "hnr_instability",
    "formant_dispersion", "formant_available",
    "turb_persistence", "turb_mod", "e1_ratio", "e2_ratio", "e3_ratio", "e4_ratio",
    "attack_time", "log_attack", "crest_factor_db", "peak_time",
    "am_flutter", "fm_depth", "spectral_flatness", "spectral_entropy"
]

tr = (splits == "train")
va = (splits == "val")
te = (splits == "test")

sddfr = SDDFRTwoTierClassifier(tier1_threshold=0.35, random_state=42)
sddfr.fit(
    X_t1_tr=X_t1[tr], y_tr=y_binary[tr], X_t2_tr=X_t2[tr],
    X_t1_va=X_t1[va], y_va=y_binary[va], X_t2_va=X_t2[va]
)

router = DynamicFeatureRouter()

test_cats = cats[te]
test_ids = file_ids[te]
test_y = y_binary[te]
is_shout = (test_cats == "SHOUTING_EXCITED_SPEECH")

X_t1_te_s = sddfr.scaler_t1.transform(X_t1[te])
t1_probs = sddfr.clf_t1.predict_proba(X_t1_te_s)[:, 1]

shout_indices = np.where(is_shout)[0]
t1_pos_shouts = [idx for idx in shout_indices if t1_probs[idx] >= 0.35]

print(f"Total test shouts: {len(shout_indices)}")
print(f"Tier 1 positive shouts (p >= 0.35): {len(t1_pos_shouts)}")

suppressed_count = 0
for idx in t1_pos_shouts:
    snr_mock = float(8.0 + 4.0 * np.cos(idx))
    snr_info = {
        "estimated_snr_db": snr_mock,
        "snr_confidence": 0.85,
        "routing_region": "HIGH_SNR" if snr_mock > 10.0 else "INTERMEDIATE_SNR" if snr_mock >= 5.0 else "LOW_SNR"
    }
    acoustic_confs = {
        "pitch_confidence": 0.80,
        "shr_confidence": 0.75,
        "hnr_confidence": 0.80,
        "formant_confidence": 0.70,
        "temporal_confidence": 0.85
    }
    routing_weights = router.compute_routing_weights(snr_info, acoustic_confs)

    pred_obj = sddfr.predict_sample(
        x_t1=X_t1[te][idx],
        x_t2=X_t2[te][idx],
        routing_weights=routing_weights,
        feature_names_t2=feat_names_t2
    )

    if pred_obj["final_decision"] == 0:
        suppressed_count += 1
        print(f"  SUPPRESSED: {test_ids[idx]} (p1={t1_probs[idx]:.3f}, p2={pred_obj['tier2_prob']:.3f}, reason={pred_obj['reason']})")
    else:
        print(f"  SURVIVED FP: {test_ids[idx]} (p1={t1_probs[idx]:.3f}, p2={pred_obj['tier2_prob']:.3f}, status={pred_obj['status']}, reason={pred_obj['reason']})")

print(f"\nTotal Tier 1 positive shouts: {len(t1_pos_shouts)}")
print(f"Total Suppressed by Tier 2: {suppressed_count}")
print(f"Total Remaining Shouting False Positives: {len(t1_pos_shouts) - suppressed_count}")
