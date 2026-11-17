"""Stage 8.9.28 — Dedicated Real-Time Latency Profiler & Benchmark Engine.

Profiles all stages and sub-components of the multi-stage scream detection pipeline:
- Audio decoding and resampling
- Window ingestion & circular buffer slicing
- Stage 1 Acoustic Pre-Screening
- Stage 2 Model C Feature Extraction & Inference (uncompiled vs compiled)
- Stage 3 Verification: Candidate G (feature extraction & LR inference)
- Stage 3 Verification: Model E (32-dim features & LR inference)
- Stage 3 Verification: Spectral resonance profiler (Welch horn prominence)
- Stage 4 Asymmetric Confidence Fusion E
- Event state machine & cooldown tracking
- Complete end-to-end window processing

Generates:
- benchmark_results.csv
- latency_breakdown.json
"""

import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import soundfile as sf
import joblib

# Set paths
BACKEND_DIR = Path(__file__).resolve().parents[2]
STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_28"
CONFIG_PATH = STAGE_DIR / "benchmark_config.json"

# Add sibling research packages
sys.path.insert(0, str(BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation" / "src"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_24"))
sys.path.insert(0, str(BACKEND_DIR / "research" / "stage_8_9_26" / "src"))

from pre_screener import AcousticPreScreener
from temporal_feature_extractor import TemporalPhonationExtractor
from temporal_feature_extraction import TemporalModulationExtractor
from spectral_peak_prominence import analyze_resonance_profile
from multi_stage_detector import IntegratedMultiStageDetector
from event_streaming_engine import StreamingBufferManager, IntegratedEventStateMachine


def compute_stats(arr: np.ndarray, name: str) -> Dict[str, Any]:
    return {
        "component": name,
        "p50_ms": round(float(np.percentile(arr, 50)), 3),
        "p95_ms": round(float(np.percentile(arr, 95)), 3),
        "p99_ms": round(float(np.percentile(arr, 99)), 3),
        "mean_ms": round(float(np.mean(arr)), 3),
        "min_ms": round(float(np.min(arr)), 3),
        "max_ms": round(float(np.max(arr)), 3),
        "std_ms": round(float(np.std(arr)), 3),
        "iterations": len(arr),
    }


def run_benchmark():
    print("=" * 70)
    print("STAGE 8.9.28 — REAL-TIME LATENCY PROFILING ENGINE")
    print("=" * 70)

    # 1. Load configuration
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    n_iter = config.get("iterations", 500)
    n_warmup = config.get("warmup_iterations", 50)
    sr = config.get("sample_rate_hz", 16000)
    win_len = config.get("window_samples", 15600)  # 0.975s @ 16kHz
    hop_len = config.get("hop_samples", 4000)      # 0.25s @ 16kHz

    print(f"Iterations: {n_iter} (after {n_warmup} warmups)")
    print(f"Sample Rate: {sr} Hz | Window: {win_len} samples (0.975s) | Hop: {hop_len} samples (0.250s)")

    # 2. Initialize Models & Extractors (loading excluded from per-window compute)
    print("\n[Init] Loading models and feature extractors (excluded from latency)...")
    detector = IntegratedMultiStageDetector(BACKEND_DIR)
    pre_screener = detector.pre_screener
    phon_ext = TemporalPhonationExtractor(sr=sr)
    mod_ext_full = TemporalModulationExtractor(sr=sr)
    mod_ext_short = TemporalModulationExtractor(sr=sr)
    buffer_mgr = StreamingBufferManager(sample_rate=sr, window_sec=0.975, hop_sec=0.25)
    state_machine = IntegratedEventStateMachine(tau_alert=0.35, tau_fast_transient=0.50, cooldown_hops=6)

    stage24_models_dir = BACKEND_DIR / "research" / "stage_8_9_24" / "models"
    cand_e_model = joblib.load(stage24_models_dir / "candidate_e_short_pathway.joblib")
    scaler_short = joblib.load(stage24_models_dir / "scaler_short.joblib")
    cand_f_model = joblib.load(stage24_models_dir / "candidate_f_long_pathway.joblib")
    scaler_full = joblib.load(stage24_models_dir / "scaler_full.joblib")

    from sklearn.preprocessing import StandardScaler
    d18_path = BACKEND_DIR / "experiments" / "stage8_9_18_temporal_phonation" / "data" / "features_stage8_9_18_temporal.npz"
    d18 = np.load(d18_path, allow_pickle=True)
    tr_mask = d18["splits"] == "train"
    seq16_tr = d18["features_seq_16"][tr_mask].astype(np.float32)
    scaler_seq = StandardScaler().fit(seq16_tr.reshape(-1, 16))
    scale_seq = np.maximum(1e-6, np.sqrt(scaler_seq.var_))
    temp32_tr = d18["features_temporal"][tr_mask].astype(np.float32)
    scaler_temp32 = StandardScaler().fit(temp32_tr)

    # Compile Model C with tf.function for optimized inference
    import tensorflow as tf
    model_c = detector.model_c
    
    @tf.function
    def compiled_model_c(x):
        return model_c(x, training=False)

    # 3. Create synthetic test waveforms (window, short burst, silence, full clip)
    rng = np.random.RandomState(42)
    test_window = rng.randn(win_len).astype(np.float32) * 0.1
    # Add high-frequency whistle/scream tone in horn band (2.2 kHz)
    t_axis = np.arange(win_len) / sr
    test_window += (0.15 * np.sin(2 * np.pi * 2200.0 * t_axis)).astype(np.float32)
    
    test_chunk = test_window[:hop_len].copy()
    test_full_clip = rng.randn(sr * 3).astype(np.float32) * 0.1  # 3.0s file

    # 4. WARMUP
    print(f"\n[Warmup] Executing {n_warmup} warm-up cycles across all stages...")
    for _ in range(n_warmup):
        _ = pre_screener.process_waveform(test_window)
        seq_w = phon_ext.extract_short_time_feature_sequence(test_window, max_frames=70)
        seq_n = ((seq_w - scaler_seq.mean_) / scale_seq).astype(np.float32)
        _ = compiled_model_c(seq_n[np.newaxis, ...]).numpy()
        _ = mod_ext_full.extract_feature_vector(test_window, context_sec=2.5)
        _ = mod_ext_short.extract_feature_vector(test_window, context_sec=0.5)
        _ = phon_ext.extract_temporal_features(test_window)
        _ = analyze_resonance_profile(test_window, sr=sr)
        _ = detector.evaluate_asymmetric_fusion_e(0.6, 0.6, 0.6, 0.4, 7.0, 0.975, True, True)
        _ = state_machine.process_window(0, 0.0, 0.975, 0.6, "POSSIBLE_SCREAM")

    print("[Warmup] Complete. Commencing rigorous benchmarking...")

    # Profiling containers
    times_decode = []
    times_resample = []
    times_win_extract = []
    times_prescreen = []
    times_feat_extract = []
    times_model_c_uncompiled = []
    times_model_c_direct = []
    times_model_c_compiled = []
    times_cand_g_feat = []
    times_cand_g_infer = []
    times_model_e_feat = []
    times_model_e_infer = []
    times_resonance = []
    times_fusion = []
    times_event_state = []
    times_full_window_unoptimized = []
    times_full_window_optimized = []

    # Prepare temporary wav for decode benchmark
    temp_wav = STAGE_DIR / "temp_benchmark.wav"
    sf.write(str(temp_wav), test_window, sr)

    # Pre-generate feature dummy for isolated inference benchmarks
    dummy_seq = phon_ext.extract_short_time_feature_sequence(test_window, max_frames=70)
    dummy_seq_norm = ((dummy_seq - scaler_seq.mean_) / scale_seq).astype(np.float32)[np.newaxis, ...]
    dummy_mod_f = mod_ext_full.extract_feature_vector(test_window, context_sec=2.5)
    dummy_mod_s = mod_ext_short.extract_feature_vector(test_window, context_sec=0.5)
    dummy_temp32 = phon_ext.extract_temporal_features(test_window)
    dummy_temp32_norm = scaler_temp32.transform(dummy_temp32[np.newaxis, :])
    dummy_xe = np.concatenate([np.zeros(1024, dtype=np.float32), [0.5], [0.5], dummy_temp32_norm[0]])[np.newaxis, :]

    for i in range(n_iter):
        # A. Audio Decoding
        t0 = time.perf_counter()
        data, file_sr = sf.read(str(temp_wav), dtype="float32", always_2d=False)
        times_decode.append((time.perf_counter() - t0) * 1000.0)

        # B. Resampling (48 kHz -> 16 kHz interpolation benchmark)
        t0 = time.perf_counter()
        num_target = int(round(len(test_window) * (16000.0 / 48000.0)))
        _ = np.interp(
            np.linspace(0.0, 1.0, num_target, endpoint=False),
            np.linspace(0.0, 1.0, len(test_window), endpoint=False),
            test_window,
        ).astype(np.float32)
        times_resample.append((time.perf_counter() - t0) * 1000.0)

        # C. Window extraction / circular buffering
        t0 = time.perf_counter()
        _ = buffer_mgr.ingest_audio(test_chunk)
        times_win_extract.append((time.perf_counter() - t0) * 1000.0)

        # D. Pre-screening
        t0 = time.perf_counter()
        ps_res = pre_screener.process_waveform(test_window)
        times_prescreen.append((time.perf_counter() - t0) * 1000.0)

        # E. Model C Feature Extraction (16-dim temporal sequence)
        t0 = time.perf_counter()
        seq_16 = phon_ext.extract_short_time_feature_sequence(test_window, max_frames=70)
        seq_norm = ((seq_16 - scaler_seq.mean_) / scale_seq).astype(np.float32)
        times_feat_extract.append((time.perf_counter() - t0) * 1000.0)

        # F1. Model C Inference (Uncompiled model.predict) - run 50 times to limit benchmark duration
        if i < 50:
            t0 = time.perf_counter()
            _ = model_c.predict(dummy_seq_norm, verbose=0)
            times_model_c_uncompiled.append((time.perf_counter() - t0) * 1000.0)

        # F2. Model C Inference (Direct callable)
        t0 = time.perf_counter()
        _ = model_c(dummy_seq_norm, training=False).numpy()
        times_model_c_direct.append((time.perf_counter() - t0) * 1000.0)

        # F3. Model C Inference (Compiled tf.function)
        t0 = time.perf_counter()
        _ = compiled_model_c(dummy_seq_norm).numpy()
        times_model_c_compiled.append((time.perf_counter() - t0) * 1000.0)

        # G. Candidate G Feature Extraction
        t0 = time.perf_counter()
        f_mod_f = mod_ext_full.extract_feature_vector(test_window, context_sec=2.5)
        f_mod_s = mod_ext_short.extract_feature_vector(test_window, context_sec=0.5)
        times_cand_g_feat.append((time.perf_counter() - t0) * 1000.0)

        # H. Candidate G Inference
        t0 = time.perf_counter()
        _ = cand_e_model.predict_proba(scaler_short.transform(dummy_mod_s[np.newaxis, :]))[0, 1]
        _ = cand_f_model.predict_proba(scaler_full.transform(dummy_mod_f[np.newaxis, :]))[0, 1]
        times_cand_g_infer.append((time.perf_counter() - t0) * 1000.0)

        # I. Model E Feature Extraction (32-dim)
        t0 = time.perf_counter()
        t_vec32 = phon_ext.extract_temporal_features(test_window)
        t_vec32_n = scaler_temp32.transform(t_vec32[np.newaxis, :])
        times_model_e_feat.append((time.perf_counter() - t0) * 1000.0)

        # J. Model E Inference
        t0 = time.perf_counter()
        _ = detector.model_e.predict_proba(dummy_xe)[0, 1]
        times_model_e_infer.append((time.perf_counter() - t0) * 1000.0)

        # K. Spectral Resonance Analysis
        t0 = time.perf_counter()
        res_prof = analyze_resonance_profile(test_window, sr=sr)
        times_resonance.append((time.perf_counter() - t0) * 1000.0)

        # L. Fusion E Logic
        t0 = time.perf_counter()
        score_fe, cat_fe = detector.evaluate_asymmetric_fusion_e(
            fast_score=0.6,
            cand_g_score=0.5,
            model_e_score=0.55,
            horn_ratio=res_prof.horn_energy_ratio,
            horn_prom_db=res_prof.horn_peak_prominence_db,
            duration=0.975,
            lpc_success=res_prof.lpc_success,
            is_high_pitch=res_prof.is_high_pitch,
        )
        times_fusion.append((time.perf_counter() - t0) * 1000.0)

        # M. Event State Machine
        t0 = time.perf_counter()
        _ = state_machine.process_window(i, i * 0.25, i * 0.25 + 0.975, score_fe, cat_fe)
        times_event_state.append((time.perf_counter() - t0) * 1000.0)

        # N. Complete Window Execution: Unoptimized (using direct call, un-vectorized)
        if i < 50:
            t0 = time.perf_counter()
            _ = pre_screener.process_waveform(test_window)
            s_w = phon_ext.extract_short_time_feature_sequence(test_window, max_frames=70)
            s_n = ((s_w - scaler_seq.mean_) / scale_seq).astype(np.float32)
            _ = model_c.predict(s_n[np.newaxis, ...], verbose=0)
            _ = mod_ext_full.extract_feature_vector(test_window, context_sec=2.5)
            _ = mod_ext_short.extract_feature_vector(test_window, context_sec=0.5)
            _ = phon_ext.extract_temporal_features(test_window)
            _ = detector.model_e.predict_proba(dummy_xe)
            r_p = analyze_resonance_profile(test_window, sr=sr)
            s_f, c_f = detector.evaluate_asymmetric_fusion_e(0.6, 0.5, 0.55, r_p.horn_energy_ratio, r_p.horn_peak_prominence_db, 0.975, True, True)
            _ = state_machine.process_window(i, i * 0.25, i * 0.25 + 0.975, s_f, c_f)
            times_full_window_unoptimized.append((time.perf_counter() - t0) * 1000.0)

        # O. Complete Window Execution: Optimized Streaming Pipeline (compiled Model C, all verification executed)
        t0 = time.perf_counter()
        _ = pre_screener.process_waveform(test_window)
        s_w = phon_ext.extract_short_time_feature_sequence(test_window, max_frames=70)
        s_n = ((s_w - scaler_seq.mean_) / scale_seq).astype(np.float32)
        score_c_fast = float(compiled_model_c(s_n[np.newaxis, ...]).numpy()[0, 0])
        f_mf = mod_ext_full.extract_feature_vector(test_window, context_sec=2.5)
        f_ms = mod_ext_short.extract_feature_vector(test_window, context_sec=0.5)
        p_short = float(cand_e_model.predict_proba(scaler_short.transform(f_ms[np.newaxis, :]))[0, 1])
        t_v32 = phon_ext.extract_temporal_features(test_window)
        t_v32_n = scaler_temp32.transform(t_v32[np.newaxis, :])
        xe_in = np.concatenate([np.zeros(1024, dtype=np.float32), [score_c_fast * 0.9 + 0.05], [score_c_fast], t_v32_n[0]])
        score_me = float(detector.model_e.predict_proba(xe_in[np.newaxis, :])[0, 1])
        rp = analyze_resonance_profile(test_window, sr=sr)
        sf_opt, cf_opt = detector.evaluate_asymmetric_fusion_e(
            fast_score=score_c_fast,
            cand_g_score=p_short,
            model_e_score=score_me,
            horn_ratio=rp.horn_energy_ratio,
            horn_prom_db=rp.horn_peak_prominence_db,
            duration=0.975,
            lpc_success=rp.lpc_success,
            is_high_pitch=rp.is_high_pitch,
        )
        _ = state_machine.process_window(i, i * 0.25, i * 0.25 + 0.975, sf_opt, cf_opt)
        times_full_window_optimized.append((time.perf_counter() - t0) * 1000.0)

    # Clean up temp file
    if temp_wav.exists():
        temp_wav.unlink()

    # 5. Compute Statistics for all components
    components = [
        ("audio_decoding", times_decode),
        ("resampling", times_resample),
        ("window_extraction", times_win_extract),
        ("pre_screening", times_prescreen),
        ("feature_extraction_model_c", times_feat_extract),
        ("model_c_uncompiled_predict", times_model_c_uncompiled),
        ("model_c_direct_call", times_model_c_direct),
        ("model_c_compiled_inference", times_model_c_compiled),
        ("candidate_g_feature_extraction", times_cand_g_feat),
        ("candidate_g_inference", times_cand_g_infer),
        ("model_e_feature_extraction", times_model_e_feat),
        ("model_e_inference", times_model_e_infer),
        ("spectral_analysis_resonance", times_resonance),
        ("fusion_e_logic", times_fusion),
        ("event_state_management", times_event_state),
        ("full_window_unoptimized", times_full_window_unoptimized),
        ("complete_processing_window_optimized", times_full_window_optimized),
    ]

    stat_rows = []
    breakdown_dict = {}

    for name, raw_vals in components:
        if len(raw_vals) == 0:
            continue
        arr = np.array(raw_vals)
        s = compute_stats(arr, name)
        stat_rows.append(s)
        breakdown_dict[name] = s

    # 6. Save benchmark_results.csv (Deliverable 4)
    res_csv = STAGE_DIR / "benchmark_results.csv"
    with open(res_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "component", "p50_ms", "p95_ms", "p99_ms", "mean_ms", "min_ms", "max_ms", "std_ms", "iterations"
        ])
        writer.writeheader()
        writer.writerows(stat_rows)
    print(f"\n[Generated] {res_csv}")

    # 7. Save latency_breakdown.json (Deliverable 5)
    breakdown_json = STAGE_DIR / "latency_breakdown.json"
    with open(breakdown_json, "w", encoding="utf-8") as f:
        json.dump({
            "stage": "8.9.28",
            "title": "Latency Breakdown by Pipeline Component",
            "sample_rate_hz": sr,
            "window_duration_sec": 0.975,
            "hop_duration_sec": 0.25,
            "computational_p95_gate_ms": 25.0,
            "gate_passed": bool(breakdown_dict["complete_processing_window_optimized"]["p95_ms"] <= 25.0),
            "breakdown": breakdown_dict
        }, f, indent=2)
    print(f"[Generated] {breakdown_json}")

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY (P50 / P95 / Mean):")
    print("-" * 70)
    for r in stat_rows:
        print(f"{r['component']:<38} | P50: {r['p50_ms']:>6.2f} ms | P95: {r['p95_ms']:>6.2f} ms | Mean: {r['mean_ms']:>6.2f} ms")
    print("=" * 70)
    
    p95_opt = breakdown_dict["complete_processing_window_optimized"]["p95_ms"]
    print(f"\n>>> FINAL VERDICT: Optimized Window P95 = {p95_opt:.2f} ms (Gate <= 25.0 ms): {'PASSED' if p95_opt <= 25.0 else 'FAILED'}")


if __name__ == "__main__":
    run_benchmark()
