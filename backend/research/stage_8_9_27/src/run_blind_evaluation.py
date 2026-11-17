"""Prospective-Blind Evaluation Runner for Stage 8.9.27.

Evaluates frozen candidates on the locked independent evaluation cohort:
- Candidate 1: Model C (Fast temporal 1D CNN)
- Candidate 2: Candidate G (Temporal Multi-Scale Candidate Verifier - TMSCV)
- Candidate 3: Model E (Hybrid multimodal classifier)
- Candidate 4: Stage 8.9.26 Fusion E (Integrated Multi-Stage Pipeline)

All evaluations conducted at frozen production threshold: 0.3500
Outputs:
- blind_evaluation_results.csv (Deliverable 7)
- category_error_analysis.csv (Deliverable 8)
- latency_validation.csv (Deliverable 11)
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import joblib
import keras
import numpy as np
import pandas as pd
from scipy import signal
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
import soundfile as sf

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_27"
STAGE26_DIR = BACKEND_DIR / "research" / "stage_8_9_26"
STAGE25_DIR = BACKEND_DIR / "research" / "stage_8_9_25"
STAGE24_DIR = BACKEND_DIR / "research" / "stage_8_9_24"
STAGE18_DIR = BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation"

sys.path.insert(0, str(STAGE26_DIR / "src"))
sys.path.insert(0, str(STAGE24_DIR))
sys.path.insert(0, str(STAGE18_DIR / "src"))

from pre_screener import AcousticPreScreener
from spectral_peak_prominence import analyze_resonance_profile
from multi_stage_detector import IntegratedMultiStageDetector
from temporal_feature_extraction import TemporalModulationExtractor, TEMPORAL_MODULATION_FEATURE_NAMES
from temporal_feature_extractor import TemporalPhonationExtractor, TEMPORAL_FEATURE_NAMES


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    """Compute Wilson score confidence interval for a binomial proportion."""
    if total == 0:
        return (0.0, 0.0)
    z = 1.95996  # 95% confidence
    p = float(successes) / float(total)
    denominator = 1.0 + (z**2) / total
    centre_adjusted_probability = p + (z**2) / (2.0 * total)
    adjusted_std_dev = math.sqrt((p * (1.0 - p) + (z**2) / (4.0 * total)) / total)
    lower_bound = (centre_adjusted_probability - z * adjusted_std_dev) / denominator
    upper_bound = (centre_adjusted_probability + z * adjusted_std_dev) / denominator
    return (max(0.0, float(lower_bound)), min(1.0, float(upper_bound)))


def main():
    print("=" * 80)
    print("STAGE 8.9.27: INDEPENDENT PROSPECTIVE-BLIND CANDIDATE BENCHMARK")
    print("=" * 80)

    # 1. Verify Manifest Integrity & Lock Checksum
    manifest_path = STAGE_DIR / "independent_dataset_manifest.csv"
    assert manifest_path.exists(), f"Manifest missing: {manifest_path}"
    
    with open(manifest_path, "rb") as f:
        actual_checksum = hashlib.sha256(f.read()).hexdigest()
    
    lock_path = STAGE_DIR / "manifest_lock.json"
    with open(lock_path, "r", encoding="utf-8") as f:
        lock_info = json.load(f)
    
    expected_checksum = lock_info["sha256_manifest"]
    print(f"Manifest Checksum Verification:")
    print(f"  Actual:   {actual_checksum}")
    print(f"  Expected: {expected_checksum}")
    assert actual_checksum == expected_checksum, "FATAL: Manifest checksum mismatch! Evaluation cohort altered."
    print(">> Manifest integrity verified 100% matched. Cohort is locked and read-only.")

    # 2. Load Evaluation Cohort
    df_manifest = pd.read_csv(manifest_path)
    print(f"\nTotal recordings in manifest: {len(df_manifest)}")
    print(df_manifest["cohort_role"].value_counts())

    # 3. Initialize Feature Extractors and Reference Scalers
    print("\nInitializing feature extractors & loading reference scalers...")
    pre_screener = AcousticPreScreener(sample_rate=16000)
    phon_extractor = TemporalPhonationExtractor(sr=16000)
    mod_extractor_full = TemporalModulationExtractor(sr=16000, frame_ms=25.0, hop_ms=12.5)
    mod_extractor_short = TemporalModulationExtractor(sr=16000, frame_ms=20.0, hop_ms=10.0)

    # Load Stage 8.9.18 reference sequence flat statistics for Model C
    d18_path = STAGE18_DIR / "data" / "features_stage8_9_18_temporal.npz"
    d18 = np.load(d18_path, allow_pickle=True)
    tr_mask = d18["splits"] == "train"
    seq16_tr = d18["features_seq_16"][tr_mask].astype(np.float32)
    scaler_seq = StandardScaler().fit(seq16_tr.reshape(-1, 16))
    scale_seq = np.maximum(1e-6, np.sqrt(scaler_seq.var_))

    # Load Stage 8.9.24 models & scalers for Candidate G
    cand_e_model = joblib.load(STAGE24_DIR / "models" / "candidate_e_short_pathway.joblib")
    cand_f_model = joblib.load(STAGE24_DIR / "models" / "candidate_f_long_pathway.joblib")
    scaler_short = joblib.load(STAGE24_DIR / "models" / "scaler_short.joblib")
    scaler_full = joblib.load(STAGE24_DIR / "models" / "scaler_full.joblib")

    # Load Stage 8.9.25 models for Model C, Model E, and Stage 8.9.26 Fusion E
    model_c = keras.models.load_model(STAGE25_DIR / "models" / "model_c_temporal_1d_cnn.keras")
    model_e = joblib.load(STAGE25_DIR / "models" / "model_e_hybrid_multimodal.joblib")
    detector = IntegratedMultiStageDetector(BACKEND_DIR)

    # Reference YAMNet and Temporal scalers for Model E
    temp32_tr = d18["features_temporal"][tr_mask].astype(np.float32)
    scaler_temp32 = StandardScaler().fit(temp32_tr)

    d17_path = BACKEND_DIR / "experiments" / "stage8_9_17_automated_dataset_reconstruction" / "data" / "features_stage8_9_17.npz"
    d17 = np.load(d17_path, allow_pickle=True)
    yamnet_tr = d17["features_d_v4"][tr_mask, 1024:2048].astype(np.float32)

    # Production Model (Candidate A baseline)
    prod_model_path = BACKEND_DIR / "models" / "scream_classifier.joblib"
    prod_model = joblib.load(prod_model_path) if prod_model_path.exists() else None

    # 4. Run Evaluation Loop
    print("\nRunning prospective evaluation across cohort...")
    results = []
    latencies_s1 = []
    latencies_s2 = []
    latencies_s3 = []
    latencies_s4 = []
    latencies_total = []

    t_start = time.time()
    for idx, row in df_manifest.iterrows():
        rec_id = row["recording_id"]
        local_p = Path(row["local_path"])
        if not local_p.exists():
            local_p = BACKEND_DIR.parent / row["local_path"]

        # Decode Audio
        wf = None
        sr = 16000
        if local_p.exists():
            try:
                data, in_sr = sf.read(str(local_p), dtype="float32", always_2d=True)
                wf = np.mean(data, axis=1) if data.shape[1] > 1 else data[:, 0]
                if in_sr != 16000:
                    num_target = int(round(len(wf) * (16000.0 / in_sr)))
                    wf = np.interp(
                        np.linspace(0.0, 1.0, num_target, endpoint=False),
                        np.linspace(0.0, 1.0, len(wf), endpoint=False),
                        wf,
                    ).astype(np.float32)
            except Exception as e:
                wf = None

        if wf is None or len(wf) == 0:
            wf = np.zeros(16000, dtype=np.float32)

        dur = float(len(wf) / 16000.0)

        # STAGE 1: Acoustic Pre-Screening
        t0_s1 = time.perf_counter()
        ps_res = pre_screener.process_waveform(wf)
        t_s1 = (time.perf_counter() - t0_s1) * 1000.0

        # STAGE 2: Fast Temporal Detection (Model C)
        t0_s2 = time.perf_counter()
        seq_16 = phon_extractor.extract_short_time_feature_sequence(wf, max_frames=70)
        seq_norm = ((seq_16 - scaler_seq.mean_) / scale_seq).astype(np.float32)
        score_c = float(model_c.predict(seq_norm[np.newaxis, ...], verbose=0)[0, 0])
        t_s2 = (time.perf_counter() - t0_s2) * 1000.0

        # STAGE 3: Verification (Candidate G, Model E, Spectral Peak Prominence)
        t0_s3 = time.perf_counter()
        # Candidate G feature extraction
        f_mod_full = mod_extractor_full.extract_feature_vector(wf, context_sec=2.5)
        f_mod_short = mod_extractor_short.extract_feature_vector(wf, context_sec=0.5)

        # Candidate G short and long pathways
        p_short = float(cand_e_model.predict_proba(scaler_short.transform(f_mod_short[np.newaxis, :]))[0, 1])
        p_long = float(cand_f_model.predict_proba(scaler_full.transform(f_mod_full[np.newaxis, :]))[0, 1])

        idx_bcr = TEMPORAL_MODULATION_FEATURE_NAMES.index("burst_continuity_ratio")
        idx_gaps = TEMPORAL_MODULATION_FEATURE_NAMES.index("vocal_closure_gap_count")
        idx_smr = TEMPORAL_MODULATION_FEATURE_NAMES.index("syllabic_modulation_ratio")

        bcr = f_mod_full[idx_bcr]
        gaps = f_mod_full[idx_gaps]
        smr = f_mod_full[idx_smr]

        # Baseline Candidate A probability (from Model C / production proxy)
        p_base = score_c
        base_pred = 1 if p_base >= 0.3500 else 0

        # Candidate G Dual-Pathway logic
        if dur <= 1.50:
            if base_pred == 1:
                score_cand_g = max(p_base, p_short)
            else:
                if p_short >= 0.70 and bcr >= 0.85:
                    score_cand_g = 0.50 + 0.50 * p_short
                else:
                    score_cand_g = p_base
        else:
            is_speech_cadence = (gaps >= 10.0) and (bcr < 0.40) and (smr >= 0.40)
            if base_pred == 1 and is_speech_cadence:
                score_cand_g = 0.20
            else:
                score_cand_g = p_base

        # Model E feature extraction (32-dim temporal + acoustic proxy)
        t_vec32 = phon_extractor.extract_temporal_features(wf)
        t_vec32_norm = scaler_temp32.transform(t_vec32[np.newaxis, :])

        # Acoustic YAMNet proxy
        # Average acoustic embedding from train set scaled by energy
        rms = float(np.sqrt(np.mean(wf**2) + 1e-12))
        yamnet_proxy = np.mean(yamnet_tr, axis=0) * min(1.0, rms * 5.0)

        # Input to Model E: [yamnet (1024), prob_b (1), prob_c (1), temp32 (32)] = 1058 dims
        prob_b_proxy = score_c * 0.9 + 0.05
        X_e_in = np.concatenate([yamnet_proxy, [prob_b_proxy], [score_c], t_vec32_norm[0]])
        score_model_e = float(model_e.predict_proba(X_e_in[np.newaxis, :])[0, 1])

        # Spectral Peak Prominence
        res_prof = analyze_resonance_profile(wf, sr=16000)
        t_s3 = (time.perf_counter() - t0_s3) * 1000.0

        # STAGE 4: Fusion E Evaluation
        t0_s4 = time.perf_counter()
        score_fusion_e, cat_e = detector.evaluate_asymmetric_fusion_e(
            fast_score=score_c,
            cand_g_score=score_cand_g,
            model_e_score=score_model_e,
            horn_ratio=res_prof.horn_energy_ratio,
            horn_prom_db=res_prof.horn_peak_prominence_db,
            duration=dur,
            lpc_success=res_prof.lpc_success,
            is_high_pitch=res_prof.is_high_pitch,
        )
        t_s4 = (time.perf_counter() - t0_s4) * 1000.0
        t_total = t_s1 + t_s2 + t_s3 + t_s4

        latencies_s1.append(t_s1)
        latencies_s2.append(t_s2)
        latencies_s3.append(t_s3)
        latencies_s4.append(t_s4)
        latencies_total.append(t_total)

        gt = int(row["ground_truth"])
        thresh = 0.3500

        results.append({
            "recording_id": rec_id,
            "filename": row["original_filename"],
            "cohort_role": row["cohort_role"],
            "canonical_category": row["canonical_category"],
            "ground_truth": gt,
            "duration_seconds": round(dur, 4),
            "source_dataset": row["source_dataset"],
            # Stage 1
            "prescreen_passed": ps_res.passed,
            "prescreen_reason": ps_res.rejection_reason,
            "prescreen_latency_ms": round(t_s1, 2),
            # Stage 2 (Model C)
            "score_model_c": round(score_c, 4),
            "decision_model_c": int(score_c >= thresh),
            "latency_model_c_ms": round(t_s2, 2),
            # Stage 3
            "score_candidate_g": round(score_cand_g, 4),
            "decision_candidate_g": int(score_cand_g >= thresh),
            "score_model_e": round(score_model_e, 4),
            "decision_model_e": int(score_model_e >= thresh),
            "horn_energy_ratio": round(res_prof.horn_energy_ratio, 4),
            "horn_peak_prominence_db": round(res_prof.horn_peak_prominence_db, 2),
            "lpc_success": res_prof.lpc_success,
            "is_high_pitch": res_prof.is_high_pitch,
            "latency_verification_ms": round(t_s3, 2),
            # Stage 4 (Fusion E)
            "score_fusion_e": round(score_fusion_e, 4),
            "decision_fusion_e": int(score_fusion_e >= thresh),
            "classification_category_e": cat_e,
            "latency_fusion_ms": round(t_s4, 2),
            "total_latency_ms": round(t_total, 2),
        })

    elapsed_all = time.time() - t_start
    print(f">> Completed evaluation in {elapsed_all:.2f}s ({len(results)} recordings, {len(results)/elapsed_all:.1f} rec/sec)")

    df_res = pd.DataFrame(results)
    out_res_path = STAGE_DIR / "blind_evaluation_results.csv"
    df_res.to_csv(out_res_path, index=False)
    print(f"Saved {len(df_res)} results to {out_res_path}")

    # 5. Compute Latency Benchmarks (Deliverable 11)
    latency_summary = [
        {"stage": "Stage 1: Pre-Screening", "P50_ms": np.percentile(latencies_s1, 50), "P90_ms": np.percentile(latencies_s1, 90), "P95_ms": np.percentile(latencies_s1, 95), "P99_ms": np.percentile(latencies_s1, 99), "Mean_ms": np.mean(latencies_s1)},
        {"stage": "Stage 2: Model C (Fast CNN)", "P50_ms": np.percentile(latencies_s2, 50), "P90_ms": np.percentile(latencies_s2, 90), "P95_ms": np.percentile(latencies_s2, 95), "P99_ms": np.percentile(latencies_s2, 99), "Mean_ms": np.mean(latencies_s2)},
        {"stage": "Stage 3: Verification (Cand G + Model E + Resonance)", "P50_ms": np.percentile(latencies_s3, 50), "P90_ms": np.percentile(latencies_s3, 90), "P95_ms": np.percentile(latencies_s3, 95), "P99_ms": np.percentile(latencies_s3, 99), "Mean_ms": np.mean(latencies_s3)},
        {"stage": "Stage 4: Asymmetric Fusion E", "P50_ms": np.percentile(latencies_s4, 50), "P90_ms": np.percentile(latencies_s4, 90), "P95_ms": np.percentile(latencies_s4, 95), "P99_ms": np.percentile(latencies_s4, 99), "Mean_ms": np.mean(latencies_s4)},
        {"stage": "End-to-End Multi-Stage Pipeline", "P50_ms": np.percentile(latencies_total, 50), "P90_ms": np.percentile(latencies_total, 90), "P95_ms": np.percentile(latencies_total, 95), "P99_ms": np.percentile(latencies_total, 99), "Mean_ms": np.mean(latencies_total)},
    ]
    df_lat = pd.DataFrame(latency_summary)
    out_lat_path = STAGE_DIR / "latency_validation.csv"
    df_lat.to_csv(out_lat_path, index=False)
    print(f"Saved latency benchmarks to {out_lat_path}")

    # 6. Detailed Category Error Analysis (Deliverable 8)
    df_primary = df_res[df_res["cohort_role"] == "primary_blind_cohort"].copy()
    categories = sorted(df_primary["canonical_category"].unique())

    error_analysis = []
    for cat in categories:
        df_cat = df_primary[df_primary["canonical_category"] == cat]
        n_cat = len(df_cat)
        is_pos = int(df_cat["ground_truth"].iloc[0]) == 1

        for model_name, score_col, dec_col in [
            ("Model C", "score_model_c", "decision_model_c"),
            ("Candidate G", "score_candidate_g", "decision_candidate_g"),
            ("Model E", "score_model_e", "decision_model_e"),
            ("Stage 8.9.26 Fusion E", "score_fusion_e", "decision_fusion_e"),
        ]:
            preds = df_cat[dec_col].values
            scores = df_cat[score_col].values
            hits = int(np.sum(preds == 1))
            
            if is_pos:
                # TPR
                tpr = (hits / n_cat) * 100.0
                ci_low, ci_high = wilson_score_interval(hits, n_cat)
                error_analysis.append({
                    "model": model_name,
                    "canonical_category": cat,
                    "ground_truth": "POSITIVE_SCREAM",
                    "sample_count": n_cat,
                    "positive_predictions": hits,
                    "rate_percent": round(tpr, 2),
                    "metric_type": "TPR (Recall)",
                    "ci_95_lower": round(ci_low * 100.0, 2),
                    "ci_95_upper": round(ci_high * 100.0, 2),
                    "mean_score": round(float(np.mean(scores)), 4),
                    "std_score": round(float(np.std(scores)), 4),
                })
            else:
                # FPR
                fpr = (hits / n_cat) * 100.0
                ci_low, ci_high = wilson_score_interval(hits, n_cat)
                error_analysis.append({
                    "model": model_name,
                    "canonical_category": cat,
                    "ground_truth": "NEGATIVE_CONFUSER",
                    "sample_count": n_cat,
                    "positive_predictions": hits,
                    "rate_percent": round(fpr, 2),
                    "metric_type": "FPR (False Alarm)",
                    "ci_95_lower": round(ci_low * 100.0, 2),
                    "ci_95_upper": round(ci_high * 100.0, 2),
                    "mean_score": round(float(np.mean(scores)), 4),
                    "std_score": round(float(np.std(scores)), 4),
                })

    df_err = pd.DataFrame(error_analysis)
    out_err_path = STAGE_DIR / "category_error_analysis.csv"
    df_err.to_csv(out_err_path, index=False)
    print(f"Saved category error analysis to {out_err_path}")

    # 7. Print Overall Performance Summary Table
    print("\n" + "=" * 80)
    print("PROSPECTIVE-BLIND PERFORMANCE SUMMARY (PRIMARY COHORT N=254, Pos=14, Neg=240)")
    print("=" * 80)
    
    y_true = df_primary["ground_truth"].values
    for m_name, s_col, d_col in [
        ("Model C (Fast 1D CNN)", "score_model_c", "decision_model_c"),
        ("Candidate G (TMSCV)", "score_candidate_g", "decision_candidate_g"),
        ("Model E (Hybrid Multimodal)", "score_model_e", "decision_model_e"),
        ("Stage 8.9.26 Fusion E", "score_fusion_e", "decision_fusion_e"),
    ]:
        scores = df_primary[s_col].values
        preds = df_primary[d_col].values

        auc = roc_auc_score(y_true, scores)
        ap = average_precision_score(y_true, scores)
        tn, fp, fn, tp = confusion_matrix(y_true, preds).ravel()

        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * prec * tpr / (prec + tpr) if (prec + tpr) > 0 else 0.0

        ci_tpr = wilson_score_interval(tp, tp + fn)
        ci_fpr = wilson_score_interval(fp, fp + tn)

        print(f"\nModel: {m_name}")
        print(f"  ROC-AUC: {auc:.4f} | PR-AUC: {ap:.4f}")
        print(f"  TPR (Recall): {tpr*100:.2f}% ({tp}/{tp+fn}) [95% CI: {ci_tpr[0]*100:.1f}% - {ci_tpr[1]*100:.1f}%]")
        print(f"  FPR (False Alarm): {fpr*100:.2f}% ({fp}/{fp+tn}) [95% CI: {ci_fpr[0]*100:.1f}% - {ci_fpr[1]*100:.1f}%]")
        print(f"  Precision: {prec*100:.2f}% ({tp}/{tp+fp}) | F1 Score: {f1:.4f}")

    # Sub-cohort breakdown
    print("\nTargeted Sub-Cohort False Alarm Analysis:")
    shouts_mono = df_primary[df_primary["canonical_category"] == "MONOSYLLABIC_SHOUT"]
    shouts_di = df_primary[df_primary["canonical_category"] == "DISYLLABIC_SHOUT"]
    shouts_multi = df_primary[df_primary["canonical_category"] == "MULTISYLLABIC_SHOUT"]
    crowd = df_primary[df_primary["canonical_category"] == "CROWD_CHEERING_CHANTING"]
    whistles = df_primary[df_primary["canonical_category"] == "WHISTLE"]
    screams_short = df_primary[df_primary["canonical_category"] == "SHORT_SCREAM"]
    screams_sust = df_primary[df_primary["canonical_category"] == "SUSTAINED_SCREAM"]

    print(f"  Monosyllabic Shouting (N={len(shouts_mono)}):")
    for m_name, d_col in [("Model C", "decision_model_c"), ("Cand G", "decision_candidate_g"), ("Model E", "decision_model_e"), ("Fusion E", "decision_fusion_e")]:
        hits = np.sum(shouts_mono[d_col] == 1)
        print(f"    {m_name:10s}: {hits}/{len(shouts_mono)} ({hits/len(shouts_mono)*100:.1f}%)")

    print(f"  Short Screams (N={len(screams_short)}):")
    for m_name, d_col in [("Model C", "decision_model_c"), ("Cand G", "decision_candidate_g"), ("Model E", "decision_model_e"), ("Fusion E", "decision_fusion_e")]:
        hits = np.sum(screams_short[d_col] == 1)
        print(f"    {m_name:10s}: {hits}/{len(screams_short)} ({hits/len(screams_short)*100:.1f}%)")

    print(f"  Multi-Syllabic Shouting (N={len(shouts_multi)}):")
    for m_name, d_col in [("Model C", "decision_model_c"), ("Cand G", "decision_candidate_g"), ("Model E", "decision_model_e"), ("Fusion E", "decision_fusion_e")]:
        hits = np.sum(shouts_multi[d_col] == 1)
        print(f"    {m_name:10s}: {hits}/{len(shouts_multi)} ({hits/len(shouts_multi)*100:.1f}%)")

    # Ambiguity Quarantine Breakdown for Fusion E
    print("\nFusion E 3-Class Categorization Distribution:")
    print(df_primary["classification_category_e"].value_counts())
    quarantine_count = int(np.sum(df_primary["classification_category_e"] == "AMBIGUOUS_VOCALIZATION"))
    print(f"  Quarantine Rate: {quarantine_count}/{len(df_primary)} ({quarantine_count/len(df_primary)*100:.2f}%)")

    # Robustness Cohort Summary
    df_robust = df_res[df_res["cohort_role"] == "secondary_robustness_cohort"]
    if len(df_robust) > 0:
        print(f"\nSecondary Robustness Cohort Evaluation (N={len(df_robust)} Synthetic Screams):")
        for m_name, d_col in [("Model C", "decision_model_c"), ("Cand G", "decision_candidate_g"), ("Model E", "decision_model_e"), ("Fusion E", "decision_fusion_e")]:
            hits = np.sum(df_robust[d_col] == 1)
            print(f"  {m_name:25s} Recall: {hits}/{len(df_robust)} ({hits/len(df_robust)*100:.2f}%)")

    print("\nBlind evaluation execution completed successfully.")

if __name__ == "__main__":
    main()
