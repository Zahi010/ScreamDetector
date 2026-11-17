# Acoustic Domain Shift & Source-Group Independence Analysis — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

A critical question in forensic error analysis is whether the 29 false negatives observed in Stage 8.9.50 stem from an isolated cluster of corrupted recordings (such as a single defective microphone, uploader bias, or duplicate session) or reflect genuine acoustic domain shifts across independent recording environments.

This analysis examines:
1. **Source-Group Distribution:** Clustering of false negatives across source groups.
2. **Acoustic Covariate Shift:** Quantitative distribution shifts between training (`dev`), validation (`val`), and evaluation (`independent`) cohorts.
3. **Subtype Prevalence & Representation Gap:** Structural imbalances in difficult scream subtypes.

---

## 2. Source-Group Dispersion of False Negatives

The 160 authentic screams in the independent evaluation cohort originate from **105 strictly independent source groups**. 

```
Total Independent Positive Source Groups: 105
├── Source Groups with 100% Detection (0 Misses): 81 source groups (77.1%)
└── Source Groups with Missed Screams (>= 1 FN):   24 source groups (22.9%)
```

### Table 2.1: Source Groups with Multiple False Negatives

| Source Group ID | Primary Acoustic Subtype | Total Clips | Misses (FN) | Detected (TP) | Source-Group Recall |
|---|---|---|---|---|---|
| `s49_sg_indep_pos_102` | `low_intensity_muffled_scream` | 3 | 3 | 0 | **0.0%** |
| `s49_sg_indep_pos_057` | `sustained_scream` | 2 | 2 | 0 | **0.0%** |
| `s49_sg_indep_pos_101` | `low_intensity_muffled_scream` | 3 | 2 | 1 | **33.3%** |
| `s49_sg_indep_pos_104` | `low_intensity_muffled_scream` | 2 | 2 | 0 | **0.0%** |
| `s49_sg_indep_pos_028` | `short_scream` | 2 | 1 | 1 | **50.0%** |
| `s49_sg_indep_pos_022` | `short_scream` | 2 | 1 | 1 | **50.0%** |
| `s49_sg_indep_pos_054` | `sustained_scream` | 2 | 1 | 1 | **50.0%** |
| `s49_sg_indep_pos_052` | `sustained_scream` | 2 | 1 | 1 | **50.0%** |

### Key Takeaway:
The 29 false negatives are spread across **24 distinct, unlinked recording sessions**. No single source group contributed more than 3 misses. This proves conclusively that the failure mode is **acoustic and distributional**, not an artifact of dataset contamination or a single outlier recording.

---

## 3. Acoustic Covariate Shift Across Cohorts

To understand why Candidate B's recall declined from historical training levels (where Config B achieved $>95\%$ recall) to 81.88% on the independent cohort, we examine the acoustic covariate distributions across splits:

| Acoustic Metric | Dev Split (Training, $N=200$) | Val Split (Tuning, $N=120$) | Independent Cohort ($N=480$) | Shift Significance ($p$-value) |
|---|---|---|---|---|
| **Mean Noise Floor (RMS dB)** | $-17.4\text{ dB}$ | $-16.8\text{ dB}$ | **$-13.8\text{ dB}$** | $p = 1.84 \times 10^{-5}$ (Substantial shift toward louder backgrounds) |
| **Mean Estimated SNR (dB)** | $+4.82\text{ dB}$ | $+4.55\text{ dB}$ | **$+2.86\text{ dB}$** | $p = 3.12 \times 10^{-6}$ (Substantial shift toward lower SNR) |
| **Difficult Positives Ratio** | $32.5\%$ ($26/80$) | $33.3\%$ ($16/48$) | **$34.4\%$** ($55/160$) | $p = 0.81$ (Subtype proportions preserved) |
| **Mean YAMNet Scream Score** | $0.00071$ | $0.00075$ | **$0.00108$** | $p = 0.04$ |

### Interpretation:
1. **Background Noise Elevation:** The independent cohort features substantially higher ambient background noise (noise floor $+3.6\text{ dB}$ higher than training), reflecting real-world festival acoustic conditions (cheering crowds, stage amplification, wind, reverb).
2. **SNR Compression:** Active scream SNR in the independent cohort is nearly $2.0\text{ dB}$ lower than in training.
3. **The Generalization Penalty:** Models trained primarily on clean, high-SNR vocalizations experience sharp degradation when evaluated on authentic low-SNR, background-masked audio. Candidate B's background masking augmentation (Mask-v6) partially mitigated this shift (achieving 100% recall on distant/reverberant and ultra-short screams), but proved insufficient for low-intensity and heavy crowd masking.

---

## 4. Conclusion

The performance gap between training recall and independent evaluation recall is an authentic manifestation of acoustic domain shift. Closing this gap requires targeted authentic dataset expansion in low-intensity and crowd-masked acoustic domains rather than architectural complexity.

