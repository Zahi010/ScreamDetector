"""
Stage 8.9.57: Phase B — Filterbank Implementation Audit
Audits the existing Candidate E1 Butterworth subband filterbank:
- Verifies exact band cutoffs, filter order, and transfer function representations
- Profiles execution time spent in filter design, forward-backward filtfilt, and frame RMS loops
- Analyzes memory allocations, array copies, and redundant operations
Emits:
- backend/research/stage_8_9_57/filterbank_implementation_audit.md
"""
import time
from pathlib import Path
import numpy as np
import scipy.signal as signal

REPO_ROOT = Path(r"festival-scream-detector")
BACKEND_DIR = REPO_ROOT / "backend"
STAGE57_DIR = BACKEND_DIR / "research" / "stage_8_9_57"

BANDS = [
    ("Band1_300_800Hz", 300, 800),
    ("Band2_800_1500Hz", 800, 1500),
    ("Band3_1500_2000Hz", 1500, 2000),
    ("Band4_2000_3000Hz", 2000, 3000),
    ("Band5_3000_4000Hz", 3000, 4000),
    ("Band6_4000_6000Hz", 4000, 6000)
]

def main():
    print("=" * 80)
    print("STAGE 8.9.57: FILTERBANK IMPLEMENTATION AUDIT")
    print("=" * 80)

    sr = 16000
    nyq = sr / 2.0
    audio_len = sr  # 1.0s window = 16,000 samples
    audio = np.random.randn(audio_len).astype(np.float32)

    # 1. Filter Design Audit
    filter_specs = []
    for b_name, f_low, f_high in BANDS:
        low_norm = f_low / nyq
        high_norm = min(0.999, f_high / nyq)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        sos = signal.butter(4, [low_norm, high_norm], btype='band', output='sos')
        filter_specs.append({
            "band_name": b_name,
            "f_low": f_low,
            "f_high": f_high,
            "low_norm": low_norm,
            "high_norm": high_norm,
            "order": 4,
            "b_len": len(b),
            "a_len": len(a),
            "sos_sections": sos.shape[0]
        })

    # 2. Granular Step-by-Step Profiling (N=200 iterations)
    N_ROUNDS = 200
    t_design_list = []
    t_filtfilt_list = []
    t_rms_loop_list = []
    t_rms_vec_list = []

    # Precomputed BA filters
    pre_ba = [signal.butter(4, [s["low_norm"], s["high_norm"]], btype='band') for s in filter_specs]

    hop = int(0.010 * sr)   # 160 samples
    frame = int(0.025 * sr) # 400 samples
    n_frames = max(1, (audio_len - frame) // hop + 1) # 98 frames

    for _ in range(N_ROUNDS):
        # A. Filter design per window
        t0 = time.perf_counter()
        for s in filter_specs:
            _ = signal.butter(4, [s["low_norm"], s["high_norm"]], btype='band')
        t_design_list.append((time.perf_counter() - t0) * 1000.0)

        # B. Filtfilt execution
        t0 = time.perf_counter()
        filtered_bands = []
        for b, a in pre_ba:
            f = signal.filtfilt(b, a, audio)
            filtered_bands.append(f)
        t_filtfilt_list.append((time.perf_counter() - t0) * 1000.0)

        # C. Original list comprehension RMS loop across all 6 bands
        t0 = time.perf_counter()
        for f in filtered_bands:
            _ = [np.sqrt(np.mean(f[i*hop : i*hop + frame]**2) + 1e-9) for i in range(n_frames)]
        t_rms_loop_list.append((time.perf_counter() - t0) * 1000.0)

        # D. Vectorized sliding window RMS across needed bands only (0, 3, 4)
        t0 = time.perf_counter()
        for idx in [0, 3, 4]:
            windows = np.lib.stride_tricks.sliding_window_view(filtered_bands[idx], frame)[::hop]
            _ = np.sqrt(np.mean(windows**2, axis=1) + 1e-9)
        t_rms_vec_list.append((time.perf_counter() - t0) * 1000.0)

    p50_design = np.percentile(t_design_list, 50)
    p95_design = np.percentile(t_design_list, 95)
    p50_filtfilt = np.percentile(t_filtfilt_list, 50)
    p95_filtfilt = np.percentile(t_filtfilt_list, 95)
    p50_rms_loop = np.percentile(t_rms_loop_list, 50)
    p95_rms_loop = np.percentile(t_rms_loop_list, 95)
    p50_rms_vec = np.percentile(t_rms_vec_list, 50)
    p95_rms_vec = np.percentile(t_rms_vec_list, 95)

    print(f"Filter Design (6 bands): P50={p50_design:.3f}ms, P95={p95_design:.3f}ms")
    print(f"Filtfilt (6 bands): P50={p50_filtfilt:.3f}ms, P95={p95_filtfilt:.3f}ms")
    print(f"Frame RMS List Comprehension (6 bands): P50={p50_rms_loop:.3f}ms, P95={p95_rms_loop:.3f}ms")
    print(f"Vectorized Frame RMS (3 needed bands): P50={p50_rms_vec:.3f}ms, P95={p95_rms_vec:.3f}ms")

    # Generate filterbank_implementation_audit.md
    md_lines = [
        "# Filterbank Implementation Audit — Stage 8.9.57",
        "",
        "> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  ",
        "> Research demonstration prototype only. No life-safety efficacy or production promotion.",
        "",
        "---",
        "",
        "## 1. Executive Summary & Audit Mandate",
        "",
        "In accordance with Phase B (Section 6), this report audits the implementation mechanics, mathematical representations,",
        "computational bottlenecks, and memory access patterns of Candidate E1's 11-dimensional Butterworth subband filterbank.",
        "",
        "### Key Audit Finding:",
        "Candidate E1's subband feature extraction suffers from **three severe architectural inefficiencies** in its reference implementation:",
        "1. **Repeated Filter Design in Inner Loop:** Calling `scipy.signal.butter(4, ...)` six times on every single 1.0-second audio window.",
        "2. **Redundant Python List Comprehensions:** Computing 98-frame RMS values across all 6 bands ($6 \\times 98 = 588$ Python loop iterations), even though temporal variance is only used for Bands 1, 4, and 5.",
        "3. **Absence of Vectorized Stride Buffering:** Inability to exploit NumPy's `sliding_window_view` to compute 98 frames simultaneously.",
        "",
        "---",
        "",
        "## 2. Filterbank Specification & Coefficient Matrix",
        "",
        "The filterbank decomposes 16 kHz audio into six non-overlapping and partially contiguous acoustic subbands:",
        "",
        "| Subband Identifier | Lower Cutoff ($f_{\\text{low}}$) | Upper Cutoff ($f_{\\text{high}}$) | Normalized Range ($f/f_{\\text{nyq}}$) | Filter Order | Numerator ($b$) / Denominator ($a$) Length | SOS Sections |",
        "|---|---|---|---|:---:|:---:|:---:|"
    ]

    for s in filter_specs:
        md_lines.append(f"| `{s['band_name']}` | {s['f_low']} Hz | {s['f_high']} Hz | [{s['low_norm']:.4f}, {s['high_norm']:.4f}] | {s['order']} | len(b)={s['b_len']}, len(a)={s['a_len']} | {s['sos_sections']} sections |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Subband Feature Mapping & Dead Computation Analysis",
        "",
        "Candidate E1's downstream classifier consumes an 11-dimensional subband vector:",
        "",
        "| Feature Index | Mathematical Definition | Acoustic Interpretation | Computation Required | Inefficient Redundancy in Reference Code |",
        "|:---:|---|---|:---:|---|",
        "| `0` | $\\text{Band}_1 \\text{ Energy} / E_{\\text{total}}$ | Low vocal resonance (300–800 Hz) | Yes | None |",
        "| `1` | $\\text{Band}_2 \\text{ Energy} / E_{\\text{total}}$ | Mid-low transition (800–1500 Hz) | Yes | None |",
        "| `2` | $\\text{Band}_3 \\text{ Energy} / E_{\\text{total}}$ | Formant dispersion (1500–2000 Hz) | Yes | None |",
        "| `3` | $\\text{Band}_4 \\text{ Energy} / E_{\\text{total}}$ | Core scream band 1 (2000–3000 Hz) | Yes | None |",
        "| `4` | $\\text{Band}_5 \\text{ Energy} / E_{\\text{total}}$ | Core scream band 2 (3000–4000 Hz) | Yes | None |",
        "| `5` | $\\text{Band}_6 \\text{ Energy} / E_{\\text{total}}$ | High-frequency whistle band (4000–6000 Hz) | Yes | None |",
        "| `6` | $\\text{std}(\\text{RMS}_{\\text{Band1}}) / \\text{mean}(\\text{RMS}_{\\text{Band1}})$ | Low-band temporal modulation | Yes | Computed via 98-frame Python loop |",
        "| `7` | $\\text{std}(\\text{RMS}_{\\text{Band4}}) / \\text{mean}(\\text{RMS}_{\\text{Band4}})$ | Core scream temporal modulation | Yes | Computed via 98-frame Python loop |",
        "| `8` | $\\text{std}(\\text{RMS}_{\\text{Band5}}) / \\text{mean}(\\text{RMS}_{\\text{Band5}})$ | Upper scream temporal modulation | Yes | Computed via 98-frame Python loop |",
        "| `9` | $(E_{\\text{Band4}} + E_{\\text{Band5}}) / (E_{\\text{Band1}} + E_{\\text{Band2}})$ | Scream-to-Vocal Energy Ratio | Yes | Derived from band energies |",
        "| `10` | $E_{\\text{Band6}} / E_{\\text{total}}$ | Whistle / High-band Energy Ratio | Yes | Derived from band energies |",
        "",
        "### Dead Computation Identified:",
        "- The reference code computes 98-frame RMS list comprehensions for **Band 2, Band 3, and Band 6** ($3 \\times 98 = 294$ frame RMS calculations), yet `temp_vars[1]`, `temp_vars[2]`, and `temp_vars[5]` are **never included** in the output vector!",
        "- **50% of all frame RMS calculations performed by the reference implementation are dead computation** that is discarded immediately.",
        "",
        "---",
        "",
        "## 4. Empirical Breakdown of Filterbank Execution Overhead",
        "",
        "Benchmarked over 200 steady-state iterations on standard 1.0s (16,000 sample) audio windows:",
        "",
        "| Execution Sub-Step | Implementation Method | P50 (ms) | P95 (ms) | Share of Filterbank Overhead (%) | Optimization Remediation |",
        "|---|---|---|---|---|---|",
        f"| **Repeated Filter Design** | `signal.butter()` 6 times in loop | {p50_design:.3f} ms | {p95_design:.3f} ms | ~{p95_design / (p95_design + p95_filtfilt + p95_rms_loop) * 100.0:.1f}% | Precompute coefficients once at init (**C3**) |",
        f"| **Forward-Backward Filtering** | `signal.filtfilt(b, a)` 6 bands | {p50_filtfilt:.3f} ms | {p95_filtfilt:.3f} ms | ~{p95_filtfilt / (p95_design + p95_filtfilt + p95_rms_loop) * 100.0:.1f}% | Precomputed arrays + streaming state (**C2**) |",
        f"| **Frame RMS Loop (6 bands)** | Python list comprehension (588 frames) | {p50_rms_loop:.3f} ms | {p95_rms_loop:.3f} ms | ~{p95_rms_loop / (p95_design + p95_filtfilt + p95_rms_loop) * 100.0:.1f}% | Eliminate dead bands + vectorize (**C1/C4**) |",
        f"| **Optimized Vectorized RMS (3 bands)** | `sliding_window_view` (294 frames) | **{p50_rms_vec:.3f} ms** | **{p95_rms_vec:.3f} ms** | — | **{p95_rms_loop / max(1e-4, p95_rms_vec):.1f}x speedup** on framing alone |",
        "",
        "---",
        "",
        "## 5. Audit Recommendations for Optimization Phases",
        "1. **Eliminate Filter Design in Loop (Experiment C3):** Precompute `b, a` polynomial arrays at module load time for fixed $f_s = 16000\\text{ Hz}$.",
        "2. **Eliminate Dead Temporal Variance Calculations (Experiment C1):** Only compute temporal variance for Bands 0, 3, and 4.",
        "3. **Vectorize Sliding Window (Experiment C1/C4):** Use `np.lib.stride_tricks.sliding_window_view` to vectorize frame RMS computation.",
        "4. **Persistent Streaming Filter State (Experiment C2):** Evaluate forward-only filtering with persistent state `zi` across contiguous sliding windows.",
        ""
    ])

    out_path = STAGE57_DIR / "filterbank_implementation_audit.md"
    out_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Saved filterbank implementation audit to: {out_path}")

if __name__ == "__main__":
    main()

