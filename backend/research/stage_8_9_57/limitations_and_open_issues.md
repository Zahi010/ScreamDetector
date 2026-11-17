# Limitations and Open Issues — Stage 8.9.57

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

Stage 8.9.57 successfully achieved an engineering breakthrough by reducing Candidate E1's digital signal processing (DSP) latency by over 10x (from 34.89 ms down to 5.61 ms P95), bringing complete downstream pipeline latency down to **4.48 - 6.20 ms P95** and clearing the supplementary 25.0 ms pipeline target with substantial headroom.

However, in accordance with scientific rigor and safety governance, this report documents the remaining architectural, environmental, and algorithmic limitations of the system.

---

## 2. Unresolved Scientific & Engineering Limitations

### A. Gate 1 (Overall Scream Recall $\ge 96.0\%$) Remains Unmet
- **Observed Recall:** Candidate E1 achieves **83.84% validation recall** (83/99 screams detected) on `expansion_val`.
- **Underlying Cause:** Reaching $\ge 96.0\%$ overall recall in adverse acoustic environments requires capturing low-intensity, crowd-masked, and distant reverberant vocalizations. Single-channel spectral filtering and spatial averaging cannot reconstruct submerged vocal formants when SNR drops below $-3\text{ dB}$.
- **Status:** Unmet across all candidates (Candidate B achieves 83.84%, Candidate B + Intervention D achieves 82.83%, Candidate E1 achieves 83.84%).

### B. Shouted-Speech False Positives (10.23% FPR)
- **Observed Shouted FPR:** Candidate E1 misclassifies 9 of 88 shouting/speech validation clips as screams (**10.23% FPR**).
- **Acoustic Confounder:** Aggressive cheering, loud stage announcements, and high-effort shouted vocalizations share acoustic roughness, high fundamental frequency ($F_0 > 500\text{ Hz}$), and elevated energy in Subband 4 (2000-3000 Hz).
- **Status:** While comfortably below the $\le 15.0\%$ gate limit, 10.23% FPR remains an operational limitation for quiet festival environments.

### C. Persistent Streaming Filter Phase Distortion (Experiment C2)
- Forward-only Second-Order Sections (`sosfilt`) in Experiment C2 enables real-time persistent filter states across streaming hops, but introduces causal group delay (~10-20 ms envelope lag).
- This phase shift resulted in 2 prediction flips across 311 validation clips (99.36% agreement), causing C2 to be classified as `TRADE-OFF IDENTIFIED — REQUIRES FURTHER RESEARCH`.
- While C5 (zero-phase precomputed `filtfilt`) achieves 100.0% numerical equivalence and 4.48 ms P95, real-time chunked streaming deployments will eventually require either:
  1. Window-overlap margins to allow bidirectional `filtfilt` over small blocks, or
  2. Model re-training directly on causal SOS filtered representations.

### D. Single-Microphone Limitation
- All acoustic representations rely on single-channel monaural audio.
- Direction of arrival (DOA), spatial null-steering against background festival stage speakers, and acoustic beamforming are impossible without multi-microphone hardware arrays.

### E. Operating System & Hardware Jitter
- Benchmarks were conducted on Windows 11 using Python 3.13 on standard x86-64 hardware.
- While P95 latencies are consistently below 6.5 ms, occasional operating system scheduling interrupts (P99/Max) can create transient spikes up to 40 ms during system background activity.
- Dedicated embedded deployment (e.g. Linux RT-PREEMPT, C++ ONNX Runtime) will be necessary for strict hard real-time latency bounds.

---

## 3. Recommended Next Research Milestones (Stage 8.9.58)

1. **C++ / Rust / ONNX DSP Pipeline Port:**
   - Implement the C5 optimized filterbank in C++ or Rust using `pocketfft` / `Eigen` to evaluate whether complete pipeline latency can be pushed below 1.0 ms.
2. **Causal Streaming Retraining Study:**
   - Retrain a dual-head model directly using causal SOS filter states to eliminate the phase distortion discrepancy identified in Experiment C2.
3. **Multi-Channel Acoustic Beamforming Research:**
   - Investigate whether 2- or 4-channel microphone arrays can suppress crowd-masked reverberation and close the gap toward the 96% recall target.

