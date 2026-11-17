# Limitations and Open Issues — Stage 8.9.58

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

Stage 8.9.58 fully resolved the two numerical and manifest discrepancies from Stage 8.9.57:
1. Proved mathematically that the $7.81 \times 10^{-3}$ maximum absolute difference on Dimension 9 corresponds to **1.00 ULP** of IEEE 754 single-precision float32 on an unnormalized ratio exceeding $120,942$, with relative error $< 6.46 \times 10^{-8}$ (pure floating-point precision).
2. Reconciled the positive cohort subgroup denominator, proving that the 99 positive screams partition into 39 Short screams (<1.0s) and 60 Sustained screams ($\ge 1.0$s), and that the 80 count in Stage 8.9.57 was a documentation conflation with `target_category == 'scream'`.
3. Validated C5 streaming-state correctness across 10 operational stress scenarios with zero state leakage and zero deadline misses across 1, 2, 4, and 8 concurrent streams.

However, in accordance with scientific transparency and strict safety governance, this report documents the remaining architectural, environmental, and algorithmic limitations of Candidate E1 + C5.

---

## 2. Unresolved Scientific & Engineering Limitations

### A. Gate 1 (Overall Scream Recall $\ge 96.0\%$) Remains Unmet
- **Observed Recall:** Candidate E1 achieves **83.84% validation recall** (83/99 screams detected) on `expansion_val`.
- **Underlying Root Cause:** Reaching $\ge 96.0\%$ overall recall in adverse acoustic festival environments requires capturing low-intensity, crowd-masked, and distant reverberant screams. In the 19 crowd-masked validation recordings, Candidate E1 achieves only **68.42% recall** (13/19 detected). Single-channel spectral filtering and spatial averaging cannot reconstruct submerged vocal formants when SNR drops below $-3\text{ dB}$.
- **Status:** Unmet across all candidates (Candidate B achieves 83.84%, Candidate B + Intervention D achieves 82.83%, Candidate E1 achieves 83.84%).

### B. Shouted-Speech False Positives (10.23% FPR)
- **Observed Shouted FPR:** Candidate E1 misclassifies 9 of 88 shouting/speech validation clips as screams (**10.23% FPR**).
- **Acoustic Confounder:** Aggressive cheering, loud stage announcements, and high-effort shouted vocalizations share acoustic roughness, high fundamental frequency ($F_0 > 500\text{ Hz}$), and elevated energy in Subband 4 (2000-3000 Hz).
- **Status:** While comfortably below the $\le 15.0\%$ gate limit, 10.23% FPR remains an operational limitation for quiet festival environments.

### C. Persistent Causal SOS Filtering (Experiment C2 Trade-off)
- C5 uses zero-phase forward-backward `filtfilt`, which provides mathematical equivalence to the training pipeline but requires the entire 975 ms window to be present in memory.
- Forward-only Second-Order Sections (SOS) filtering evaluated in Experiment C2 enables real-time persistent filter states across streaming hops without recalculating past samples, but introduces causal group delay (~10-20 ms envelope lag).
- This phase shift resulted in 2 prediction flips across 311 validation clips (99.36% agreement), causing C2 to be classified as `TRADE-OFF IDENTIFIED — REQUIRES FURTHER RESEARCH`.
- While C5 achieves 100.0% numerical equivalence and ~6.2 ms P95, real-time chunked streaming deployments will eventually require either:
  1. Window-overlap margins to allow bidirectional `filtfilt` over small blocks, or
  2. Model re-training directly on causal SOS filtered representations.

### D. Single-Microphone Monaural Limitation
- All acoustic representations rely on single-channel monaural audio.
- Direction of arrival (DOA), spatial null-steering against background festival stage speakers, and acoustic beamforming are impossible without multi-microphone hardware arrays.

### E. Python / SciPy Runtime Overhead
- While C5 achieves ~6.2 ms P95 on CPU, it remains implemented in Python using SciPy and PyTorch.
- Operating system scheduling interrupts on Windows 11 can cause transient P99/Max spikes up to ~79 ms under 8 concurrent streams.
- Dedicated embedded deployment (e.g. Linux RT-PREEMPT, C++ ONNX Runtime) will be necessary for strict hard real-time latency bounds.

---

## 3. Recommended Next Research Milestones (Stage 8.9.59)

1. **C++ / Rust / ONNX DSP Pipeline Port:**
   - Implement the C5 optimized filterbank in C++ or Rust using `pocketfft` / `Eigen` to evaluate whether complete pipeline latency can be pushed below 1.0 ms.
2. **Causal Streaming Retraining Study:**
   - Retrain a dual-head model directly using causal SOS filter states to eliminate the phase distortion discrepancy identified in Experiment C2.
3. **Multi-Channel Acoustic Beamforming Research:**
   - Investigate whether 2- or 4-channel microphone arrays can suppress crowd-masked reverberation and close the gap toward the 96% recall target.

