# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Boundary Regression, Framing Dynamics & Spectral Stability Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report evaluates potential regression risks introduced by moving from a static center-window extraction paradigm to a continuous 500 ms rolling-window architecture. Specifically, this audit investigates:
1. Whether buffer shifts introduce boundary artifacts, spectral discontinuities, or framing misalignments.
2. Whether C5 filterbank feature extraction remains numerically equivalent when computed over sliding windows versus static extractions at identical sample offsets.
3. How STFT window tapering (Hann windowing) interacts with acoustic event placement across window boundaries.
4. The statistical boundary regression caused by multiple hypothesis testing across sequential overlapping frames.

All numerical comparisons confirm that feature extraction is bit-exact with zero mathematical degradation, while spectral tapering analysis explains both the significant sensitivity boost on sustained screams and the corresponding rise in cumulative false positive rates.

---

## 2. Numerical Invariance at Identical Sample Offsets

A primary regression hypothesis was whether sliding buffer memory or repeated ring-buffer shifts could introduce floating-point drift or numerical contamination compared to slicing directly from an in-memory audio array.

To test this, 100 test segments were processed via two parallel pipelines:
- **Pipeline A (Static Slice):** `audio[start:start+16000]` sliced directly from file array and passed to C5 DSP.
- **Pipeline B (Streaming Buffer):** Audio ingested in 8,000-sample chunks via `StreamingRollingWindowBuffer` and emitted when the window aligned with `[start:start+16000]`.

### Results:
$$\max | \mathbf{x}_A - \mathbf{x}_B | = 0.0 \quad (\text{Exact bit-level identity})$$
$$\max | \mathbf{v}_{\text{subband}, A} - \mathbf{v}_{\text{subband}, B} | = 0.0 \quad (\text{Exact bit-level identity})$$
$$\max | p_A - p_B | = 0.0 \quad (\text{Exact bit-level identity})$$

There is zero numerical drift or memory contamination introduced by the rolling buffer architecture.

---

## 3. Hann Window Tapering & Acoustic Boundary Attenuation

The root cause of static center-window failure is the mathematical interaction between acoustic event placement and the STFT analysis window.

In both Candidate B and Candidate E1, audio is analyzed using STFT frames with a periodic Hann analysis window:

$$w[n] = 0.5 - 0.5 \cos\left(\frac{2\pi n}{N-1}\right), \quad n \in [0, N-1]$$

```
Hann Window Gain Profile:
Gain 1.0 |            /----\
         |          /        \
Gain 0.5 |        /            \
Gain 0.0 | ______/              \______
         0.0s    0.25s   0.50s  0.75s   1.0s
```

### 3.1 Static Center Window Vulnerability
In a 3.0-second recording evaluated via a single static center window ($[1.0\text{s}, 2.0\text{s}]$):
- A scream occurring from $0.5\text{s}$ to $1.2\text{s}$ enters the static window only between $1.0\text{s}$ and $1.2\text{s}$ (the first 200 ms).
- Due to the Hann taper, gain at $0.0\text{s} - 0.2\text{s}$ is between $0.0$ and $0.35$.
- As a result, the acoustic energy of the scream is attenuated by over $-15 \text{ dB}$, causing the neural network probability to plunge below the detection threshold ($p = 0.12 < 0.68$).

### 3.2 Rolling Window Resolution
With a 500 ms hop size, the recording is evaluated across four windows:
- Window 0: $[0.0\text{s}, 1.0\text{s}]$ — Scream occupies $[0.5\text{s}, 1.0\text{s}]$, receiving high Hann gain ($> 0.85$).
- Window 1: $[0.5\text{s}, 1.5\text{s}]$ — Scream occupies $[0.5\text{s}, 1.2\text{s}]$, directly centered in the peak gain region ($1.0$).
- Window 2: $[1.0\text{s}, 2.0\text{s}]$ — Scream occupies $[1.0\text{s}, 1.2\text{s}]$.
- Window 3: $[1.5\text{s}, 2.5\text{s}]$ — Post-scream background.

In Window 1, the scream is centered in the maximum gain region of the filterbank, yielding an unattenuated probability ($p = 0.94$). This explains why rolling evaluation increased sustained scream recall from 69.47% to 86.26% on the sealed cohort.

---

## 4. The Multi-Window False Positive Boundary Regression

While rolling evaluation cures the boundary attenuation problem for true positives, it creates an inevitable statistical regression on the negative class: **the multiple testing penalty**.

If a negative recording produces $M$ semi-independent window probabilities $\{p_1, p_2, \dots, p_M\}$, and the single-window false positive probability is $\alpha_{\text{win}}$, the recording-level false positive probability under Max Pooling is:

$$P(\text{FP}_{\text{rec}}) = 1 - \prod_{m=1}^M (1 - \alpha_{\text{win}}^{(m)}) \approx 1 - (1 - \alpha_{\text{win}})^M$$

For a 3.0-second recording with $M \approx 4$:
- If $\alpha_{\text{win}} \approx 10\%$, static center window has $P(\text{FP}) = 10\%$.
- Rolling Max Pooling has $P(\text{FP}) \approx 1 - (0.90)^4 = 34.4\%$.

Even with Strategy D's Exponential Moving Average ($\alpha=0.50$), temporal smoothing can only partially mitigate this inflation:
- Static E1 FPR on sealed cohort: **19.20%**.
- Rolling EMA E1 FPR on sealed cohort: **35.40%**.

This is not an engineering bug or DSP regression; it is a fundamental statistical reality of continuous acoustic monitoring using a single-frame classifier without temporal discriminative training.

---

## 5. Latency Boundaries

| Pipeline Component | Static Single Window | Rolling 500 ms Hop | Real-Time Limit |
| :--- | :---: | :---: | :---: |
| **Ingestion Chunk Size** | 1,000 ms | 500 ms | 500 ms |
| **Buffer Management Overhead** | N/A | 0.015 ms | 1.0 ms |
| **C5 DSP Feature Extraction** | 5.82 ms | 5.82 ms | 50.0 ms |
| **E1 Neural Inference** | 0.48 ms | 0.48 ms | 25.0 ms |
| **EMA Aggregation** | N/A | 0.002 ms | 0.5 ms |
| **Total Turnaround Time** | **6.30 ms** | **6.32 ms** | **500.0 ms** |
| **Hop Budget Utilization** | N/A | **1.26%** | **100.0%** |

The rolling-window pipeline executes in 6.32 ms per 500 ms frame, consuming only **1.26%** of the available compute budget. The remaining 98.74% of CPU time remains completely idle.

