# Streaming Filter State Report — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Architectural Evaluation

Experiment C2 investigated persistent streaming filter states (`E1_DSP_C2_STREAMING_FILTER_STATE`) for Candidate E1.
In offline windowed processing, `scipy.signal.filtfilt` processes audio forward and backward with zero phase distortion, but requires
padding transients at the edges and cannot maintain state across streaming hops without recalculating past samples.

Experiment C2 introduced forward-only Second-Order Sections (SOS) filtering using `scipy.signal.sosfilt` with persistent `zi` state vectors.

---

## 2. Latency Performance Profile

- **Continuous Streaming Mode:** P50 = 1.478 ms | P95 = **2.440 ms** | Max = 4.456 ms.
- **Windowed Mode with Explicit Reset:** P50 = 3.888 ms | P95 = **5.490 ms** | Max = 6.320 ms.
- **Speedup vs Baseline:** ~15.9x faster than original Candidate E1 baseline.

---

## 3. Boundary Transients & Cross-Stream Isolation

### A. Reset API Verification
- `StreamingFilterbankC2` implements an explicit `reset()` method.
- Calling `reset()` zeroes the filter state vectors (`zi`), guaranteeing that subsequent audio inputs begin with zero initial conditions.
- Automated verification confirmed that consecutive calls with `reset()` between identical inputs yield an identical feature vector with **maximum absolute difference = 0.0**.

### B. Cross-Clip Contamination Prevention
- In batch processing or independent stream switching, failure to call `reset()` causes state carry-over from preceding clips.
- For independent audio file evaluation, `reset()` must be invoked between clips.

### C. Phase Distortion & Numerical Equivalence
- Unlike zero-phase `filtfilt`, forward-only `sosfilt` introduces causal group delay (phase distortion).
- This results in small numerical discrepancies compared to the frozen Candidate E1 training features (evaluated in Phase E).
- In contrast, Experiment C5 retains zero-phase `filtfilt` while achieving **3.30 ms P95**, preserving bit-for-bit mathematical equivalence with zero causal delay.

---

## 4. Conclusion & Recommendation

- Experiment C2 demonstrates the computational viability of persistent SOS filtering for ultra-low-latency real-time streaming.
- However, because Experiment C5 already achieves **3.30 ms P95** with **exact zero-phase numerical equivalence**, C5 is preferred as the primary optimized DSP implementation for Candidate E1.
