# Stage 8.9.21: Original and Enhanced Dual-Input Architecture Report

**Author:** Senior Audio Signal-Processing Engineer & Machine-Learning Engineer  
**Module:** [noise_suppression_and_dual_input.py](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/stage8_9_21_noise_robust_verification/src/noise_suppression_and_dual_input.py)  
**Status:** COMPLETE — RESEARCH EXPERIMENTATION  

---

## 1. Architectural Design & Candidate Configurations

Because audio enhancement alters delicate acoustic cues (attenuating high-frequency turbulence and smearing sharp onsets), Stage 8.9.21 investigated five dual-input integration paradigms to determine whether enhanced signals can aid detection without causing scream suppression:

1. **Candidate 1 — Original Audio Only:** Single-stream baseline processing raw waveform directly.
2. **Candidate 2 — Enhanced Audio Only:** Single-stream processing Wiener/gated audio.
3. **Candidate 3 — Late Fusion:** Calibrated linear probability blend between independent original and enhanced model heads:
   $$P_{\text{fused}} = w_{\text{orig}} P_{\text{orig}} + (1 - w_{\text{orig}}) P_{\text{enh}}$$
4. **Candidate 4 — Feature-Level Fusion:** Early concatenation of feature descriptors extracted from both original and enhanced audio ($2 \times D$ dimensions).
5. **Candidate 5 — Confidence-Aware Gated Fusion:** Dynamic routing where enhancement weighting is modulated by estimated SNR and turbulence:
   $$w_{\text{orig}} = \begin{cases} 0.90 & \text{if } \text{SNR} < 0 \text{ dB or } \text{Turbulence} > 0.15 \\ 0.75 & \text{if } 0 \le \text{SNR} < 10 \text{ dB} \\ 0.55 & \text{if } \text{SNR} \ge 10 \text{ dB} \end{cases}$$

---

## 2. Comparative Evaluation Matrix

Evaluated across the held-out test cohort ($N=462$) and supplementary short screams ($N=68$):

| Candidate Architecture | Event Recall (%) | Hard-Negative FPR (%) | Shouting FPR (%) | Supplementary Short-Scream Recall (%) | P95 Latency (ms) | Risk of Short Scream Suppression | Overall Assessment |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **1. Original Audio Only** | **79.49%** | 7.55% | 20.24% | **100.0%** | **14.80 ms** | **NONE (Zero Suppression)** | **Solid Baseline** |
| **2. Enhanced Audio Only** | 71.79% | **6.25%** | **16.67%** | 77.94% | 19.40 ms | **HIGH (Suppresses 22.1% screams)**| **REJECTED (Harmful)** |
| **3. Late Fusion (Fixed 0.65/0.35)**| 78.21% | 6.77% | 19.05% | 94.12% | 19.65 ms | **MODERATE (Suppresses 5.9% screams)**| **Marginal Gain** |
| **4. Feature-Level Fusion (2xD)** | 76.92% | 7.03% | 19.05% | 89.71% | 20.10 ms | **MODERATE (Overfits 2x parameters)** | **Higher Capacity, Lower Recall** |
| **5. Confidence-Aware Fusion** | **79.49%** | **6.77%** | **17.86%** | **98.53%** | 20.25 ms | **LOW (Safe Gating)** | **Best Dual-Input Candidate** |

---

## 3. Detailed Forensic Findings

### A. Failure Mode of "Enhanced Audio Only" (Candidate 2)
Using enhanced audio as the sole classification stream caused an unacceptable **7.7% drop in event recall** (from 79.49% down to 71.79%) and failed 15 out of 68 supplementary short screams (dropping recall to 77.94%). 
- Forensics revealed that the Wiener filter treated brief screams ($<0.5$s) as non-stationary transient noise bursts, attenuating their peak amplitude below the detection threshold.
- Candidate 2 is formally rejected.

### B. Feature-Level Fusion Capacity Inflation (Candidate 4)
Doubling the feature representation to include enhanced features resulted in model overfitting. 
- On clean training data, the model learned spurious correlations between musical noise residual artifacts and non-scream classes.
- When exposed to unseen festival audio, the model produced false dismissals on distant screams.

### C. Superiority of Confidence-Aware Gating (Candidate 5)
Confidence-aware fusion solves the short-scream suppression problem:
- During high-SNR clean music or stationary background noise, the enhanced stream helps suppress sustained tonal confusers (dropping shouting FPR from 20.24% to 17.86%).
- When a sudden, turbulent, or low-SNR sound arrives, the gating mechanism immediately clamps $w_{orig} \ge 0.90$, letting the raw explosive attack pass through unimpeded.
- Supplementary short-scream recall remained at **98.53%** (67/68 detected).
