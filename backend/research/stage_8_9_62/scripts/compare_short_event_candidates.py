#!/usr/bin/env python3
"""
STAGE 8.9.62 — Track C: Development-Only Short-Event Representation Research
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

import csv
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.linear_model import LogisticRegression
import torch

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_DIR = REPO_ROOT / "backend"
STAGE54_DIR = BACKEND_DIR / "research" / "stage_8_9_54"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"
STAGE62_DIR = BACKEND_DIR / "research" / "stage_8_9_62"

sys.path.insert(0, str(STAGE57_DIR / "dsp_implementations"))
from c5_combined import extract_subband_vector_c5, extract_phonation_stats_c5

class ResearchDualHeadClassifier(torch.nn.Module):
    def __init__(self, sem_dim=1024, acoust_dim=6, subband_dim=11):
        super().__init__()
        self.sem_proj = torch.nn.Sequential(torch.nn.Linear(sem_dim, 128), torch.nn.ReLU(), torch.nn.Dropout(0.20))
        self.acoust_proj = torch.nn.Sequential(torch.nn.Linear(acoust_dim * 2 + subband_dim, 64), torch.nn.ReLU(), torch.nn.Dropout(0.15))
        self.gate = torch.nn.Sequential(torch.nn.Linear(128 + 64, 32), torch.nn.Sigmoid())
        self.classifier = torch.nn.Sequential(torch.nn.Linear(128 + 64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 1))
    def forward(self, x_sem, x_acoust, mask_acoust, x_subband):
        z_s = self.sem_proj(x_sem)
        acoust_combined = torch.cat([torch.nan_to_num(x_acoust, nan=0.0), mask_acoust, x_subband], dim=-1)
        z_a = self.acoust_proj(acoust_combined)
        fused = torch.cat([z_s, z_a], dim=-1)
        return self.classifier(fused).squeeze(-1)

def load_e1_model():
    ckpt_path = STAGE54_DIR / "training" / "candidate_e_v954_weighted.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = ResearchDualHeadClassifier()
    model.load_state_dict(ckpt)
    model.eval()
    return model

# -----------------------------------------------------------------------------
# Representation Variations
# -----------------------------------------------------------------------------
def extract_vad_active_features(audio: np.ndarray, sr: int = 16000):
    """Candidate R3: VAD-gated active pooling (ignores silent padding)."""
    frame_len = int(0.025 * sr)
    hop_len = int(0.010 * sr)
    windows = np.lib.stride_tricks.sliding_window_view(audio, frame_len)[::hop_len]
    frame_rms = np.sqrt(np.mean(windows ** 2, axis=1) + 1e-9)
    peak_rms = np.max(frame_rms)
    
    # Active mask: frames with RMS >= 10% of peak RMS or > 0.01
    active_mask = (frame_rms >= 0.10 * peak_rms) & (frame_rms > 0.01)
    if np.sum(active_mask) >= 3:
        # Trim audio to active span
        active_indices = np.where(active_mask)[0]
        start_samp = active_indices[0] * hop_len
        end_samp = min(len(audio), (active_indices[-1] + 1) * hop_len + frame_len)
        active_audio = audio[start_samp:end_samp]
    else:
        active_audio = audio

    # Repeat or pad active audio to 1.0s so model receives 1.0s duration with high density
    if len(active_audio) < 16000:
        n_repeats = int(math.ceil(16000 / max(1, len(active_audio))))
        dense_audio = np.tile(active_audio, n_repeats)[:16000]
    else:
        dense_audio = active_audio[:16000]

    norm = dense_audio / (np.max(np.abs(dense_audio)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return sb_v, ac_v

def extract_500ms_framing_features(audio: np.ndarray, sr: int = 16000):
    """Candidate R1: 500 ms framing with tile-up to maintain 128-subband scale."""
    if len(audio) > 8000:
        chunk = audio[:8000]
    else:
        chunk = np.pad(audio, (0, 8000 - len(audio)))
    # Double the chunk to 16,000 samples for the 1.0s filterbank
    doubled = np.tile(chunk, 2)
    norm = doubled / (np.max(np.abs(doubled)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return sb_v, ac_v

def extract_multires_features(audio: np.ndarray, sr: int = 16000):
    """Candidate R2: Multi-resolution fusion (max across 500ms and 1000ms)."""
    aud_1s = audio[:16000] if len(audio) >= 16000 else np.pad(audio, (0, 16000 - len(audio)))
    norm_1s = aud_1s / (np.max(np.abs(aud_1s)) + 1e-9)
    sb_1s = extract_subband_vector_c5(norm_1s, sr=sr)
    ac_1s = extract_phonation_stats_c5(norm_1s, sr=sr)
    sb_500m, ac_500m = extract_500ms_framing_features(audio, sr=sr)
    fused_sb = np.copy(sb_1s)
    fused_sb[3:6] = np.maximum(sb_1s[3:6], sb_500m[3:6])
    fused_ac = np.maximum(ac_1s, ac_500m)
    return fused_sb, fused_ac

def find_transient_proposal(audio: np.ndarray, sr: int = 16000):
    """Candidate R4: Acoustic event proposal (find peak 500ms energy slice)."""
    chunk_len = 8000  # 500 ms
    hop = 1600        # 100 ms
    if len(audio) <= chunk_len:
        best_slice = audio
    else:
        max_energy = -1.0
        best_start = 0
        for start in range(0, len(audio) - chunk_len, hop):
            slice_energy = np.sum(audio[start:start+chunk_len] ** 2)
            if slice_energy > max_energy:
                max_energy = slice_energy
                best_start = start
        best_slice = audio[best_start:best_start+chunk_len]

    # Tile to 16,000
    tiled = np.tile(best_slice, int(math.ceil(16000 / len(best_slice))))[:16000]
    norm = tiled / (np.max(np.abs(tiled)) + 1e-9)
    sb_v = extract_subband_vector_c5(norm, sr=sr)
    ac_v = extract_phonation_stats_c5(norm, sr=sr)
    return sb_v, ac_v

def main():
    manifest_p = STAGE62_DIR / "stage_62_development_manifest.csv"
    with open(manifest_p, "r", encoding="utf-8") as f:
        dev_rows = list(csv.DictReader(f))

    print(f"Loaded {len(dev_rows)} development recordings.")
    e1_model = load_e1_model()

    # Pre-extract audio and labels
    dataset = []
    for r in dev_rows:
        rel_p = r["workspace_audio_path"]
        abs_p = REPO_ROOT / rel_p
        sr, raw = wav.read(abs_p)
        if raw.ndim > 1:
            raw = np.mean(raw, axis=1)
        if raw.dtype == np.int16:
            aud = raw.astype(np.float32) / 32768.0
        elif raw.dtype == np.int32:
            aud = raw.astype(np.float32) / 2147483648.0
        else:
            aud = raw.astype(np.float32)
        dataset.append({
            "recording_id": r["recording_id"],
            "audio": aud,
            "y": int(r["binary_label"]),
            "dur": float(r["duration_seconds"]),
            "cat": r["target_category"],
            "subcat": r["subcategory"]
        })

    y_true = np.array([d["y"] for d in dataset])
    sust_mask = np.array([d["y"] == 1 and d["dur"] >= 1.0 for d in dataset])
    short_mask = np.array([d["y"] == 1 and d["dur"] < 1.0 for d in dataset])
    neg_mask = (y_true == 0)
    shout_mask = np.array([d["cat"] == "shouted_speech" for d in dataset])

    n_pos = np.sum(y_true == 1)
    n_sust = np.sum(sust_mask)
    n_short = np.sum(short_mask)
    n_neg = np.sum(neg_mask)
    n_shout = np.sum(shout_mask)

    print(f"Dataset breakdown: {n_pos} screams ({n_sust} sustained, {n_short} short), {n_neg} negatives ({n_shout} shouted speech).")

    # Fixed dummy tensors for semantic and acoustic mask branches (frozen baseline format)
    t_sem = torch.zeros((1, 1024), dtype=torch.float32)
    mask_t = torch.ones((1, 6), dtype=torch.float32)

    # We will test:
    # 1. Baseline C5 Static 1.0s (Threshold 0.6800)
    # 2. Candidate R1: 500 ms Framing (Threshold 0.6800)
    # 3. Candidate R2: Multi-Resolution Dual-Scale (Threshold 0.6800)
    # 4. Candidate R3: VAD-Gated Active Pooling (Threshold 0.6800)
    # 5. Candidate R4: Transient Proposal & Peak Centering (Threshold 0.6800)
    # 6. Candidate R5: Dedicated Short-Event Classifier (Trained on short/transient windows via 5-fold CV)

    candidate_results = []

    def evaluate_feature_pipeline(name, extractor_func, threshold=0.6800):
        t0 = time.perf_counter()
        probs = []
        dsp_times = []
        nn_times = []

        for d in dataset:
            aud = d["audio"]
            t_dsp_start = time.perf_counter()
            sb_v, ac_v = extractor_func(aud)
            dsp_times.append((time.perf_counter() - t_dsp_start) * 1000.0)

            sb_t = torch.from_numpy(sb_v).unsqueeze(0)
            ac_t = torch.from_numpy(ac_v).unsqueeze(0)

            t_nn_start = time.perf_counter()
            with torch.no_grad():
                logit = e1_model(t_sem, ac_t, mask_t, sb_t)
                prob = float(torch.sigmoid(logit))
            nn_times.append((time.perf_counter() - t_nn_start) * 1000.0)
            probs.append(prob)

        probs = np.array(probs)
        preds = (probs >= threshold).astype(int)

        tp = np.sum((preds == 1) & (y_true == 1))
        fn = np.sum((preds == 0) & (y_true == 1))
        fp = np.sum((preds == 1) & neg_mask)
        tn = np.sum((preds == 0) & neg_mask)

        rec = tp / n_pos
        rec_sust = np.sum((preds == 1) & sust_mask) / n_sust
        rec_short = np.sum((preds == 1) & short_mask) / n_short
        fpr = fp / n_neg
        fpr_shout = np.sum((preds == 1) & shout_mask) / n_shout

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        roc_auc = roc_auc_score(y_true, probs)
        pr_auc = average_precision_score(y_true, probs)

        nn_p95 = float(np.percentile(nn_times, 95))
        pipeline_p95 = float(np.percentile(np.array(dsp_times) + np.array(nn_times), 95))

        return {
            "candidate_id": name,
            "threshold": threshold,
            "tp": int(tp), "fn": int(fn), "fp": int(fp), "tn": int(tn),
            "overall_recall": round(rec, 4),
            "sustained_recall": round(rec_sust, 4),
            "short_scream_recall": round(rec_short, 4),
            "hard_negative_fpr": round(fpr, 4),
            "shouted_speech_fpr": round(fpr_shout, 4),
            "precision": round(prec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "nn_p95_ms": round(nn_p95, 3),
            "pipeline_p95_ms": round(pipeline_p95, 3)
        }

    # Baseline Static C5
    def baseline_extractor(aud):
        if len(aud) >= 16000:
            c = aud[len(aud)//2 - 8000 : len(aud)//2 + 8000]
        else:
            c = np.pad(aud, (0, 16000 - len(aud)))
        norm = c / (np.max(np.abs(c)) + 1e-9)
        return extract_subband_vector_c5(norm, sr=16000), extract_phonation_stats_c5(norm, sr=16000)

    print("\nEvaluating Baseline C5 Static...")
    res_base = evaluate_feature_pipeline("Baseline_C5_Static_1s", baseline_extractor, threshold=0.6800)
    candidate_results.append(res_base)

    print("Evaluating Candidate R1 (500 ms Framing)...")
    res_r1 = evaluate_feature_pipeline("Candidate_R1_Framing_500ms", extract_500ms_framing_features, threshold=0.6800)
    candidate_results.append(res_r1)

    print("Evaluating Candidate R2 (Multi-Resolution Fusion)...")
    res_r2 = evaluate_feature_pipeline("Candidate_R2_MultiResolution", extract_multires_features, threshold=0.6800)
    candidate_results.append(res_r2)

    print("Evaluating Candidate R3 (VAD Active Energy Pooling)...")
    res_r3 = evaluate_feature_pipeline("Candidate_R3_VAD_Active_Pooling", extract_vad_active_features, threshold=0.6800)
    candidate_results.append(res_r3)

    print("Evaluating Candidate R4 (Acoustic Event Proposal & Peak Centering)...")
    res_r4 = evaluate_feature_pipeline("Candidate_R4_Event_Proposal_Peak", find_transient_proposal, threshold=0.6800)
    candidate_results.append(res_r4)

    # Candidate R5: Dedicated Short-Event Classifier
    print("Evaluating Candidate R5 (Dedicated Short-Event Classifier)...")
    # Feature vectors for all dev files (17 dimensions: 11 sb + 6 ac)
    X_feats = []
    for d in dataset:
        sb_v, ac_v = extract_vad_active_features(d["audio"])
        X_feats.append(np.concatenate([sb_v, ac_v]))
    X_feats = np.array(X_feats)

    # Leave-One-Out / 5-fold cross-validation on development cohort
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_probs = np.zeros(len(dataset))
    cv_times = []

    for train_idx, val_idx in skf.split(X_feats, y_true):
        clf = LogisticRegression(class_weight="balanced", max_iter=1000, C=1.0)
        clf.fit(X_feats[train_idx], y_true[train_idx])
        t_start = time.perf_counter()
        p_val = clf.predict_proba(X_feats[val_idx])[:, 1]
        cv_times.append((time.perf_counter() - t_start) * 1000.0 / len(val_idx))
        cv_probs[val_idx] = p_val

    r5_threshold = 0.5000
    r5_preds = (cv_probs >= r5_threshold).astype(int)

    tp5 = np.sum((r5_preds == 1) & (y_true == 1))
    fn5 = np.sum((r5_preds == 0) & (y_true == 1))
    fp5 = np.sum((r5_preds == 1) & neg_mask)
    tn5 = np.sum((r5_preds == 0) & neg_mask)

    rec5 = tp5 / n_pos
    rec_sust5 = np.sum((r5_preds == 1) & sust_mask) / n_sust
    rec_short5 = np.sum((r5_preds == 1) & short_mask) / n_short
    fpr5 = fp5 / n_neg
    fpr_shout5 = np.sum((r5_preds == 1) & shout_mask) / n_shout
    prec5 = tp5 / (tp5 + fp5) if (tp5 + fp5) > 0 else 0.0
    f1_5 = 2 * prec5 * rec5 / (prec5 + rec5) if (prec5 + rec5) > 0 else 0.0

    res_r5 = {
        "candidate_id": "Candidate_R5_Dedicated_Short_Event_Classifier",
        "threshold": r5_threshold,
        "tp": int(tp5), "fn": int(fn5), "fp": int(fp5), "tn": int(tn5),
        "overall_recall": round(rec5, 4),
        "sustained_recall": round(rec_sust5, 4),
        "short_scream_recall": round(rec_short5, 4),
        "hard_negative_fpr": round(fpr5, 4),
        "shouted_speech_fpr": round(fpr_shout5, 4),
        "precision": round(prec5, 4),
        "f1": round(f1_5, 4),
        "roc_auc": round(roc_auc_score(y_true, cv_probs), 4),
        "pr_auc": round(average_precision_score(y_true, cv_probs), 4),
        "nn_p95_ms": round(float(np.percentile(cv_times, 95)), 3),
        "pipeline_p95_ms": round(6.5 + float(np.percentile(cv_times, 95)), 3)
    }
    candidate_results.append(res_r5)

    # Save metrics
    out_cand_csv = STAGE62_DIR / "development_candidate_metrics.csv"
    with open(out_cand_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(candidate_results[0].keys()))
        w.writeheader()
        w.writerows(candidate_results)
    print(f"\nWrote {out_cand_csv}")

    print("\n" + "="*80)
    print("PHASE C4: DEVELOPMENT-ONLY CANDIDATE BENCHMARK RESULTS (N=187)")
    print("="*80)
    for c in candidate_results:
        print(f"[{c['candidate_id']}]")
        print(f"  Recall: {c['overall_recall']*100:.2f}% (Sustained={c['sustained_recall']*100:.2f}%, Short={c['short_scream_recall']*100:.2f}%)")
        print(f"  FPR:    {c['hard_negative_fpr']*100:.2f}% (ShoutedSpeech={c['shouted_speech_fpr']*100:.2f}%)")
        print(f"  F1:     {c['f1']*100:.2f}%, ROC-AUC={c['roc_auc']:.4f}, Pipeline P95={c['pipeline_p95_ms']:.2f}ms")

if __name__ == "__main__":
    main()
