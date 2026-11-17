# Source-Group Cluster Bootstrap Report — Stage 8.9.50

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Methodology & Sampling Architecture

To rigorously account for correlation among recordings originating from the same audio capture session, device, or acoustic setting, cluster bootstrap was performed at the `source_group_id` level ($B = 2,000$ iterations, fixed random seed 42):
- **Number of Resamples:** 2,000.
- **Cluster Level:** `source_group_id` (220 unique clusters across 480 clips).
- **Sampling Unit:** Entire source-group cluster drawn with replacement, keeping all associated clips intact.

---

## 2. Paired Metric Comparison (Baseline vs Intervention D)

| Metric Comparison | Candidate B Baseline | Candidate B + Intervention D | Paired Difference ($\Delta = \text{D} - \text{Base}$) | 95% Bootstrap Percentile CI | Paired McNemar $p$-value | Significance Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Overall Scream Recall** | 81.90% | 81.90% | **+0.00%** | [+0.00%, +0.00%] | $p = 1.0000$ | **Identical (Zero Recall Loss)** |
| **Hard-Negative FPR** | 0.31% | 0.31% | **+0.00%** | [+0.00%, +0.00%] | $p = 1.0000$ | **Preserved Ultra-Low Level** |
| **Referee Whistle FPR** | 0.00% | 0.00% | **+0.00%** | [+0.00%, +0.00%] | $p = 1.0000$ | **Complete Rejection Maintained** |
| **Macro F1 Score** | 89.70% | 89.70% | **+0.00%** | [+0.00%, +0.00%] | — | **Preserved Classification Balance** |

---

## 3. Cluster Bootstrap Audit Conclusion
- The cluster bootstrap demonstrates that Candidate B + Intervention D maintains **exact paired parity with Candidate B baseline on authentic screams** across all 2,000 resamples.
- No intra-cluster degradation was observed, confirming robust positive-class preservation.
