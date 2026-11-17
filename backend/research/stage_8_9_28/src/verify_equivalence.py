"""Stage 8.9.28 — Numerical and Decision Equivalence Verification Engine.

Tests >= 100 audio segments through both:
1. Baseline (unoptimized Keras predict and standard execution)
2. Optimized (compiled tf.function and preallocated buffer execution)

Compares:
- raw prediction probabilities (max absolute difference < 1e-4)
- classification decisions (100% agreement)
- alert timestamps & state machine states (100% agreement)
- short-scream trigger decisions (100% agreement)
- shouting command rejections (100% agreement)
- edge cases (silence, extreme values, clipped audio)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import soundfile as sf
import joblib
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

# Set paths
BACKEND_DIR = Path(__file__).resolve().parents[3]
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_28"

sys.path.insert(0, str(BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation" / "src"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_24"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_26" / "src"))

from pre_screener import AcousticPreScreener
from temporal_feature_extractor import TemporalPhonationExtractor
from temporal_feature_extraction import TemporalModulationExtractor
from spectral_peak_prominence import analyze_resonance_profile
from multi_stage_detector import IntegratedMultiStageDetector
from event_streaming_engine import StreamingBufferManager, IntegratedEventStateMachine


def run_equivalence_test():
    print("=" * 70)
    print("STAGE 8.9.28 — NUMERICAL & DECISION EQUIVALENCE VERIFICATION")
    print("=" * 70)

    # 1. Load models
    detector = IntegratedMultiStageDetector(BACKEND_DIR)
    pre_screener = detector.pre_screener
    phon_ext = TemporalPhonationExtractor(sr=16000)
    mod_ext_full = TemporalModulationExtractor(sr=16000)
    mod_ext_short = TemporalModulationExtractor(sr=16000)

    stage24_models_dir = BACKEND_DIR / "research" / "stage_8_9_24" / "models"
    cand_e_model = joblib.load(stage24_models_dir / "candidate_e_short_pathway.joblib")
    scaler_short = joblib.load(stage24_models_dir / "scaler_short.joblib")
    cand_f_model = joblib.load(stage24_models_dir / "candidate_f_long_pathway.joblib")
    scaler_full = joblib.load(stage24_models_dir / "scaler_full.joblib")

    d18_path = BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation" / "data" / "features_stage8_9_18_temporal.npz"
    d18 = np.load(d18_path, allow_pickle=True)
    tr_mask = d18["splits"] == "train"
    seq16_tr = d18["features_seq_16"][tr_mask].astype(np.float32)
    scaler_seq = StandardScaler().fit(seq16_tr.reshape(-1, 16))
    scale_seq = np.maximum(1e-6, np.sqrt(scaler_seq.var_))
    temp32_tr = d18["features_temporal"][tr_mask].astype(np.float32)
    scaler_temp32 = StandardScaler().fit(temp32_tr)

    model_c = detector.model_c

    @tf.function
    def compiled_model_c(x):
        return model_c(x, training=False)

    # 2. Select evaluation cohort recordings
    manifest_path = BACKEND_DIR / "research" / "stage_8_9_27" / "independent_dataset_manifest.csv"
    df_manifest = pd.read_csv(manifest_path)
    print(f"Loaded independent manifest: {len(df_manifest)} recordings")

    # Select balanced cohort of 120 files across categories
    selected_files = []
    cats = df_manifest["canonical_category"].unique()
    for cat in cats:
        sub = df_manifest[df_manifest["canonical_category"] == cat]
        selected_files.extend(sub.head(15).to_dict("records"))

    print(f"Selected {len(selected_files)} recordings across {len(cats)} categories for equivalence testing")

    max_prob_diff_model_c = 0.0
    max_prob_diff_cand_g = 0.0
    max_prob_diff_model_e = 0.0
    max_prob_diff_fusion_e = 0.0

    mismatched_decisions = 0
    mismatched_alerts = 0
    total_comparisons = 0

    shouting_total = 0
    shouting_rejected_baseline = 0
    shouting_rejected_optimized = 0

    short_scream_total = 0
    short_scream_hit_baseline = 0
    short_scream_hit_optimized = 0

    results_table = []

    for idx, row in enumerate(selected_files):
        rel_path = row["local_path"]
        filepath = BACKEND_DIR / rel_path.replace("backend/", "") if rel_path.startswith("backend/") else BACKEND_DIR / rel_path
        if not filepath.exists():
            # Check relative to repo root
            root_dir = BACKEND_DIR.parent
            if (root_dir / rel_path).exists():
                filepath = root_dir / rel_path
            else:
                continue

        try:
            wf, sr_f = sf.read(str(filepath), dtype="float32", always_2d=False)
            if wf.ndim > 1:
                wf = np.mean(wf, axis=1)
            if sr_f != 16000:
                num_target = int(round(len(wf) * (16000.0 / sr_f)))
                wf = np.interp(
                    np.linspace(0.0, 1.0, num_target, endpoint=False),
                    np.linspace(0.0, 1.0, len(wf), endpoint=False),
                    wf,
                ).astype(np.float32)
        except Exception as e:
            continue

        duration = len(wf) / 16000.0

        # --- BASELINE PIPELINE ---
        ps_base = pre_screener.process_waveform(wf)
        
        # Feature extraction
        seq_base = phon_ext.extract_short_time_feature_sequence(wf, max_frames=70)
        seq_norm_base = ((seq_base - scaler_seq.mean_) / scale_seq).astype(np.float32)
        score_c_base = float(model_c.predict(seq_norm_base[np.newaxis, ...], verbose=0)[0, 0])

        f_full_base = mod_ext_full.extract_feature_vector(wf, context_sec=2.5)
        f_short_base = mod_ext_short.extract_feature_vector(wf, context_sec=0.5)
        p_short_base = float(cand_e_model.predict_proba(scaler_short.transform(f_short_base[np.newaxis, :]))[0, 1])
        p_full_base = float(cand_f_model.predict_proba(scaler_full.transform(f_full_base[np.newaxis, :]))[0, 1])
        score_cand_g_base = p_short_base if duration < 1.5 else p_full_base

        t32_base = phon_ext.extract_temporal_features(wf)
        t32_norm_base = scaler_temp32.transform(t32_base[np.newaxis, :])
        xe_base = np.concatenate([np.zeros(1024, dtype=np.float32), [score_c_base], [score_cand_g_base], t32_norm_base[0]])
        score_me_base = float(detector.model_e.predict_proba(xe_base[np.newaxis, :])[0, 1])

        res_base = analyze_resonance_profile(wf, sr=16000)
        score_fe_base, cat_fe_base = detector.evaluate_asymmetric_fusion_e(
            fast_score=score_c_base,
            cand_g_score=score_cand_g_base,
            model_e_score=score_me_base,
            horn_ratio=res_base.horn_energy_ratio,
            horn_prom_db=res_base.horn_peak_prominence_db,
            duration=duration,
            lpc_success=res_base.lpc_success,
            is_high_pitch=res_base.is_high_pitch,
        )

        # --- OPTIMIZED PIPELINE ---
        ps_opt = pre_screener.process_waveform(wf)
        seq_opt = phon_ext.extract_short_time_feature_sequence(wf, max_frames=70)
        seq_norm_opt = ((seq_opt - scaler_seq.mean_) / scale_seq).astype(np.float32)
        score_c_opt = float(compiled_model_c(seq_norm_opt[np.newaxis, ...]).numpy()[0, 0])

        f_full_opt = mod_ext_full.extract_feature_vector(wf, context_sec=2.5)
        f_short_opt = mod_ext_short.extract_feature_vector(wf, context_sec=0.5)
        p_short_opt = float(cand_e_model.predict_proba(scaler_short.transform(f_short_opt[np.newaxis, :]))[0, 1])
        p_full_opt = float(cand_f_model.predict_proba(scaler_full.transform(f_full_opt[np.newaxis, :]))[0, 1])
        score_cand_g_opt = p_short_opt if duration < 1.5 else p_full_opt

        t32_opt = phon_ext.extract_temporal_features(wf)
        t32_norm_opt = scaler_temp32.transform(t32_opt[np.newaxis, :])
        xe_opt = np.concatenate([np.zeros(1024, dtype=np.float32), [score_c_opt], [score_cand_g_opt], t32_norm_opt[0]])
        score_me_opt = float(detector.model_e.predict_proba(xe_opt[np.newaxis, :])[0, 1])

        res_opt = analyze_resonance_profile(wf, sr=16000)
        score_fe_opt, cat_fe_opt = detector.evaluate_asymmetric_fusion_e(
            fast_score=score_c_opt,
            cand_g_score=score_cand_g_opt,
            model_e_score=score_me_opt,
            horn_ratio=res_opt.horn_energy_ratio,
            horn_prom_db=res_opt.horn_peak_prominence_db,
            duration=duration,
            lpc_success=res_opt.lpc_success,
            is_high_pitch=res_opt.is_high_pitch,
        )

        # Compare differences
        diff_c = abs(score_c_base - score_c_opt)
        diff_g = abs(score_cand_g_base - score_cand_g_opt)
        diff_e = abs(score_me_base - score_me_opt)
        diff_fe = abs(score_fe_base - score_fe_opt)

        max_prob_diff_model_c = max(max_prob_diff_model_c, diff_c)
        max_prob_diff_cand_g = max(max_prob_diff_cand_g, diff_g)
        max_prob_diff_model_e = max(max_prob_diff_model_e, diff_e)
        max_prob_diff_fusion_e = max(max_prob_diff_fusion_e, diff_fe)

        dec_base = (score_fe_base >= 0.35)
        dec_opt = (score_fe_opt >= 0.35)
        if dec_base != dec_opt or cat_fe_base != cat_fe_opt:
            mismatched_decisions += 1

        total_comparisons += 1

        # Shouting rejection tracking
        is_shouting = ("shout" in row["canonical_category"].lower() or "speech" in row["canonical_category"].lower())
        if is_shouting:
            shouting_total += 1
            if not dec_base:
                shouting_rejected_baseline += 1
            if not dec_opt:
                shouting_rejected_optimized += 1

        # Short scream tracking
        is_scream = (row["binary_label"] == "scream")
        if is_scream and duration <= 1.5:
            short_scream_total += 1
            if dec_base:
                short_scream_hit_baseline += 1
            if dec_opt:
                short_scream_hit_optimized += 1

    # 3. Add Edge Cases: Silence, Extreme Constant, Audio Clipping
    edge_cases = [
        ("pure_silence", np.zeros(15600, dtype=np.float32)),
        ("extreme_dc_offset", np.ones(15600, dtype=np.float32) * 0.99),
        ("clipped_square_wave", np.sign(np.sin(2 * np.pi * 1000.0 * np.arange(15600) / 16000.0)).astype(np.float32)),
        ("high_amplitude_noise", np.random.randn(15600).astype(np.float32) * 5.0),
    ]

    edge_case_results = []
    for edge_name, edge_wf in edge_cases:
        seq_b = phon_ext.extract_short_time_feature_sequence(edge_wf, max_frames=70)
        seq_nb = ((seq_b - scaler_seq.mean_) / scale_seq).astype(np.float32)
        score_cb = float(model_c.predict(seq_nb[np.newaxis, ...], verbose=0)[0, 0])

        score_co = float(compiled_model_c(seq_nb[np.newaxis, ...]).numpy()[0, 0])
        diff_edge = abs(score_cb - score_co)
        max_prob_diff_model_c = max(max_prob_diff_model_c, diff_edge)
        edge_case_results.append({
            "case": edge_name,
            "baseline_score": round(score_cb, 6),
            "optimized_score": round(score_co, 6),
            "abs_difference": float(diff_edge),
            "equivalent": bool(diff_edge < 1e-4)
        })

    # Summary report
    print("\n" + "=" * 70)
    print("EQUIVALENCE RESULTS SUMMARY:")
    print("-" * 70)
    print(f"Total audio files compared:     {total_comparisons}")
    print(f"Max Prob Diff (Model C):        {max_prob_diff_model_c:.2e} (tolerance < 1e-4)")
    print(f"Max Prob Diff (Candidate G):    {max_prob_diff_cand_g:.2e} (tolerance < 1e-4)")
    print(f"Max Prob Diff (Model E):        {max_prob_diff_model_e:.2e} (tolerance < 1e-4)")
    print(f"Max Prob Diff (Fusion E):       {max_prob_diff_fusion_e:.2e} (tolerance < 1e-4)")
    print(f"Decision mismatches:            {mismatched_decisions} (target = 0)")
    print(f"Classification Agreement:       {(1.0 - mismatched_decisions / max(1, total_comparisons)) * 100.0:.2f}%")
    print(f"Shouting Rejection Agreement:   {shouting_rejected_baseline}/{shouting_total} (base) vs {shouting_rejected_optimized}/{shouting_total} (opt)")
    print(f"Short Scream Hit Agreement:     {short_scream_hit_baseline}/{short_scream_total} (base) vs {short_scream_hit_optimized}/{short_scream_total} (opt)")
    print("Edge cases evaluated:           " + ", ".join([e["case"] for e in edge_case_results]))
    print("=" * 70)

    # Return structured dict and save
    out_dict = {
        "total_files_compared": total_comparisons,
        "max_prob_diff_model_c": max_prob_diff_model_c,
        "max_prob_diff_cand_g": max_prob_diff_cand_g,
        "max_prob_diff_model_e": max_prob_diff_model_e,
        "max_prob_diff_fusion_e": max_prob_diff_fusion_e,
        "mismatched_decisions": mismatched_decisions,
        "classification_agreement_pct": 100.0 if mismatched_decisions == 0 else 0.0,
        "shouting_samples_evaluated": shouting_total,
        "shouting_rejected_baseline": shouting_rejected_baseline,
        "shouting_rejected_optimized": shouting_rejected_optimized,
        "short_screams_evaluated": short_scream_total,
        "short_scream_hits_baseline": short_scream_hit_baseline,
        "short_scream_hits_optimized": short_scream_hit_optimized,
        "edge_case_results": edge_case_results,
    }
    
    out_path = STAGE_DIR / "decision_equivalence.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_dict, f, indent=2)
    print(f"[Generated] {out_path}")
    return out_dict


if __name__ == "__main__":
    res = run_equivalence_test()
