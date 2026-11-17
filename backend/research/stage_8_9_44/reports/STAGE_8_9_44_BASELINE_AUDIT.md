# Stage 8.9.44 Baseline Audit & Forensic False-Negative Analysis

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Baseline Performance Review (Stage 8.9.43 Config-B-v5)

The leading candidate from Stage 8.9.43 was **`Config-B-v5` (`DualEncoderAcousticModel`)**, an architecture fusing a 1024-dimensional semantic projection head (YAMNet embeddings) with a 12-dimensional phonation masked head (6 acoustic features + 6 validity masks) and a binary classification MLP head.

### Baseline Benchmark Summary
- **Validation-Selected Operating Threshold:** $\theta^* = 0.8200$
- **Holdout Overall Recall:** 75.36% (52 / 69) [95% Wilson CI: 64.04%, 84.01%]
- **Holdout Hard-Negative FPR:** 3.68% (5 / 136) [Passes Gate 2 $\le 5\%$]
- **Holdout Shouted-Speech FPR:** 7.14% (2 / 28) [Passes Gate 3 $\le 15\%$]
- **Holdout Short-Scream Recall ($\le 1.0$s):** 100.0% (17 / 17) [Passes Gate 4 $\ge 90\%$]
- **Holdout Ultra-Short Scream Recall ($<500$ms):** 100.0% (8 / 8)
- **Holdout ROC-AUC:** 0.9487, **PR-AUC:** 0.9104, **Brier Score:** 0.0965
- **P95 Computational Latency:** 0.47 ms [Passes Gate 5 $\le 25\text{ ms}$]

## 2. Forensic Breakdown of the 17 False Negatives

On `v5_final_holdout`, exactly 17 out of 69 positive scream recordings were missed at $\theta^* = 0.8200$:

| Subtype Category | Total on Holdout | Missed (FN) | Subgroup Recall | Acoustic Characterization |
|---|---|---|---|---|
| `masked_distant_screams` | 16 | 8 | **50.00%** | Screams buried in crowd cheering, music, or high-amplitude reverberant background |
| `distant_scream` | 2 | 1 | **50.00%** | Attenuated vocal energy with long room reverberation tail ($T_{60} > 0.8\text{ s}$) |
| `sustained_scream` | 5 | 2 | **60.00%** | Long vocalizations with low SNR or irregular breathy phonation |
| `scream` (generic field) | 37 | 6 | **83.78%** | Irregular multi-talker cries with partial masking |
| `short_scream` | 4 | 0 | **100.00%** | Resolved perfectly by authentic training |
| `low_intensity_scream` | 3 | 0 | **100.00%** | Low-amplitude clean vocal bursts |
| `standard_scream` | 2 | 0 | **100.00%** | Clean high-intensity shrieks |

### Key Forensic Insight:
The 17 false negatives are dominated by two primary acoustic degradation mechanisms:
1. **Reverberant Dispersion (RIR):** Vocal formants are smeared across temporal bins by multipath room reflections and low direct-to-reverberant ratios ($DRR < 0\text{ dB}$).
2. **Background Masking (Low SNR):** Environmental sound sources (crowd roars, festival music, PA systems) overlap the 1.5–4.0 kHz vocal resonance band.

This establishes the empirical objective for Stage 8.9.44:
To introduce controlled **Room Impulse Response (RIR) convolution**, **distance attenuation**, and **background acoustic masking** into the training pipeline to evaluate whether environmental robustness can bridge the remaining 20.64% gap to Gate 1 (96% recall) without violating Gate 2 (HN-FPR $\le 5\%$) or Gate 3 (Shouted-speech FPR $\le 15\%$).

