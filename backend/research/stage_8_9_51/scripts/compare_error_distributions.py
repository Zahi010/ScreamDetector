"""
Stage 8.9.51: Workstream C — Comparative Error Pattern & Feature Distribution Analysis
Computes statistical comparisons between the 29 False Negatives and 131 True Positives
across acoustic, spectral, temporal, and model features.
Emits statistical tables, Cohen's d effect sizes, Mann-Whitney U tests, Welch's t-tests,
and outputs data for FEATURE_DISTRIBUTION_ANALYSIS.md and DOMAIN_SHIFT_ANALYSIS.md.
"""
import sys
import math
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats

REPO_ROOT = Path(r"c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE51_DIR = BACKEND_DIR / "research" / "stage_8_9_51"

def cohen_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    if dof <= 0:
        return 0.0, (0.0, 0.0)
    vx, vy = np.var(x, ddof=1), np.var(y, ddof=1)
    pooled_std = np.sqrt(((nx - 1) * vx + (ny - 1) * vy) / dof)
    if pooled_std < 1e-9:
        return 0.0, (0.0, 0.0)
    d = (np.mean(x) - np.mean(y)) / pooled_std
    # 95% CI for Cohen's d (Hedges & Olkin approximation)
    se_d = np.sqrt((nx + ny) / (nx * ny) + (d**2) / (2 * (nx + ny)))
    ci_low = d - 1.96 * se_d
    ci_high = d + 1.96 * se_d
    return float(d), (float(ci_low), float(ci_high))

def main():
    print("=" * 80)
    print("STAGE 8.9.51: WORKSTREAM C FEATURE DISTRIBUTION & ERROR ANALYSIS")
    print("=" * 80)
    
    in_csv = STAGE51_DIR / "results" / "ALL_AUTHENTIC_POSITIVES_FORENSICS.csv"
    if not in_csv.exists():
        raise FileNotFoundError(f"Missing {in_csv}")
        
    df = pd.read_csv(in_csv)
    print(f"Loaded {len(df)} authentic positive records.")
    
    tp_df = df[df["is_false_negative"] == 0]
    fn_df = df[df["is_false_negative"] == 1]
    
    n_tp = len(tp_df)
    n_fn = len(fn_df)
    print(f"True Positives (TP): {n_tp}")
    print(f"False Negatives (FN): {n_fn}")
    
    features = [
        ("candidate_b_prob", "Candidate B Probability", "prob"),
        ("model_logit", "Candidate B Raw Logit", "logit"),
        ("duration_sec", "Total Audio Duration (s)", "s"),
        ("vocal_event_dur_sec", "Active Vocal Duration (s)", "s"),
        ("rms_amp", "RMS Amplitude", "linear"),
        ("peak_amp", "Peak Amplitude", "linear"),
        ("crest_factor_db", "Crest Factor (dB)", "dB"),
        ("dyn_range_db", "Dynamic Range (dB)", "dB"),
        ("snr_db", "Estimated SNR (dB)", "dB"),
        ("noise_floor_db", "Noise Floor (dB)", "dB"),
        ("silence_ratio", "Silence Ratio", "ratio"),
        ("spectral_centroid_hz", "Spectral Centroid (Hz)", "Hz"),
        ("spectral_bandwidth_hz", "Spectral Bandwidth (Hz)", "Hz"),
        ("spectral_rolloff_hz", "Spectral Rolloff 85% (Hz)", "Hz"),
        ("spectral_flatness", "Spectral Flatness", "ratio"),
        ("zcr", "Zero Crossing Rate", "rate"),
        ("low_e_ratio", "Low-Frequency Energy (<1kHz)", "ratio"),
        ("mid_e_ratio", "Mid-Frequency Energy (1-4kHz)", "ratio"),
        ("high_e_ratio", "High-Frequency Energy (>4kHz)", "ratio"),
        ("vocal_band_ratio", "Vocal Formant Band (300-1800Hz)", "ratio"),
        ("whistle_band_ratio", "Whistle Band (2.5-3.8kHz)", "ratio"),
        ("env_cv", "Amplitude Envelope CV", "ratio"),
        ("attack_time_ms", "Attack Time (ms)", "ms"),
        ("decay_time_ms", "Decay Time (ms)", "ms"),
        ("temporal_persistence", "Temporal Persistence", "ratio"),
        ("padding_ratio", "Window Padding Ratio", "ratio"),
        ("alignment_offset_ms", "Window Alignment Offset (ms)", "ms"),
        ("acoust_vocal_max", "YAMNet Vocal Frame Max", "score"),
        ("acoust_vocal_mean", "YAMNet Vocal Frame Mean", "score"),
        ("acoust_crowd_max", "YAMNet Crowd Frame Max", "score"),
        ("acoust_crowd_mean", "YAMNet Crowd Frame Mean", "score"),
        ("acoust_scream_max", "YAMNet Scream Frame Max", "score"),
        ("acoust_scream_mean", "YAMNet Scream Frame Mean", "score"),
        ("subband_scream_ratio", "Subband Scream-to-Vocal Ratio", "ratio"),
        ("z_sem_norm", "Semantic Projection L2 Norm", "norm"),
        ("z_acoust_norm", "Acoustic Projection L2 Norm", "norm"),
    ]
    
    records = []
    
    for col, name, unit in features:
        tp_vals = tp_df[col].dropna().values
        fn_vals = fn_df[col].dropna().values
        
        tp_mean, tp_std = float(np.mean(tp_vals)), float(np.std(tp_vals, ddof=1))
        tp_med = float(np.median(tp_vals))
        tp_iqr = float(np.percentile(tp_vals, 75) - np.percentile(tp_vals, 25))
        
        fn_mean, fn_std = float(np.mean(fn_vals)), float(np.std(fn_vals, ddof=1))
        fn_med = float(np.median(fn_vals))
        fn_iqr = float(np.percentile(fn_vals, 75) - np.percentile(fn_vals, 25))
        
        # Welch's t-test
        t_stat, p_welch = stats.ttest_ind(fn_vals, tp_vals, equal_var=False)
        
        # Mann-Whitney U test
        u_stat, p_mwu = stats.mannwhitneyu(fn_vals, tp_vals, alternative='two-sided')
        rank_biserial = 1.0 - (2.0 * u_stat) / (len(fn_vals) * len(tp_vals))
        
        # Cohen's d (FN vs TP)
        d_val, (d_low, d_high) = cohen_d(fn_vals, tp_vals)
        
        records.append({
            "feature_id": col,
            "feature_name": name,
            "unit": unit,
            "tp_mean": tp_mean,
            "tp_std": tp_std,
            "tp_median": tp_med,
            "tp_iqr": tp_iqr,
            "fn_mean": fn_mean,
            "fn_std": fn_std,
            "fn_median": fn_med,
            "fn_iqr": fn_iqr,
            "welch_t_stat": float(t_stat),
            "p_welch": float(p_welch),
            "mann_whitney_u": float(u_stat),
            "p_mwu": float(p_mwu),
            "rank_biserial": float(rank_biserial),
            "cohens_d": float(d_val),
            "cohens_d_ci_low": float(d_low),
            "cohens_d_ci_high": float(d_high)
        })
        
    res_df = pd.DataFrame(records)
    out_table = STAGE51_DIR / "results" / "FEATURE_DISTRIBUTION_STATISTICS.csv"
    res_df.to_csv(out_table, index=False)
    print(f"Saved feature distribution statistics to: {out_table}")
    
    # Sort by absolute effect size |Cohen's d|
    res_df["abs_d"] = res_df["cohens_d"].abs()
    top_effects = res_df.sort_values("abs_d", ascending=False).head(15)
    print("\nTop 15 Features by Effect Size (FN vs TP):")
    for _, r in top_effects.iterrows():
        print(f"  {r['feature_name']:<35} | d = {r['cohens_d']:+6.2f} (95% CI: [{r['cohens_d_ci_low']:+6.2f}, {r['cohens_d_ci_high']:+6.2f}]) | p_mwu = {r['p_mwu']:.2e}")
        
    # Analyze Subtype Breakdown
    print("\nSubtype Distribution and Recall:")
    subtype_summary = df.groupby("acoustic_subtype").agg(
        total=("file_id", "count"),
        detected=("candidate_b_pred", "sum"),
        missed=("is_false_negative", "sum")
    ).reset_index()
    subtype_summary["recall_pct"] = (subtype_summary["detected"] / subtype_summary["total"]) * 100.0
    print(subtype_summary.to_string(index=False))
    
    # Analyze Source-Group Independence and Clustering
    print("\nSource Group Clustering Analysis:")
    sg_counts = df.groupby(["source_group_id", "acoustic_subtype"]).agg(
        total=("file_id", "count"),
        misses=("is_false_negative", "sum")
    ).reset_index()
    sg_with_misses = sg_counts[sg_counts["misses"] > 0].sort_values("misses", ascending=False)
    print(f"Total Source Groups in Positive Cohort: {df['source_group_id'].nunique()}")
    print(f"Source Groups containing FNs: {sg_with_misses['source_group_id'].nunique()}")
    print(sg_with_misses.head(10).to_string(index=False))

if __name__ == "__main__":
    main()

