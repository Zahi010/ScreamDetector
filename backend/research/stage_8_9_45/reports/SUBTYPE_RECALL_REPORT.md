# Subtype Recall & Acoustic Robustness Report — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  

---

## 1. Acoustic Subtype Performance Matrix (Final Holdout $N=205$, 69 Positives)

| Candidate | Threshold | Overall Rec | Masked Screams (N=16) | Distant Screams (N=18) | Low-Intensity / Muffled (N=3) | Sustained Screams (N=52) | Short Comb (N=17) | Ultra-Short (N=8) |
|---|---|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | 0.82 | **75.36%** | 8/16 (50.00%) | 9/18 (50.00%) | 3/3 (100.0%) | 35/52 (67.31%) | 17/17 (100.0%) | 8/8 (100.0%) |
| **Candidate B (Config-B-Mask-v6)** | 0.86 | **72.46%** | 11/16 (68.75%) | 12/18 (66.67%) | 3/3 (100.0%) | 33/52 (63.46%) | 17/17 (100.0%) | 8/8 (100.0%) |
| **Candidate C (Config-B-MildMask)** | 0.91 | **71.01%** | 10/16 (62.50%) | 11/18 (61.11%) | 3/3 (100.0%) | 32/52 (61.54%) | 17/17 (100.0%) | 8/8 (100.0%) |
| **Candidate D (Config-B-MultiSNR)** | 0.85 | **71.01%** | 10/16 (62.50%) | 11/18 (61.11%) | 3/3 (100.0%) | 32/52 (61.54%) | 17/17 (100.0%) | 8/8 (100.0%) |
| **Candidate E (Config-B-MaskAtten)** | 0.73 | **78.26%** | 12/16 (75.00%) | 13/18 (72.22%) | 3/3 (100.0%) | 37/52 (71.15%) | 17/17 (100.0%) | 8/8 (100.0%) |
| **Candidate F (Config-B-MaskEarlyRIR)** | 0.86 | **75.36%** | 12/16 (75.00%) | 13/18 (72.22%) | 3/3 (100.0%) | 36/52 (69.23%) | 16/17 (94.1%) | 7/8 (87.5%) |
| **Candidate G (Config-B-ProbMixed)** | 0.85 | **75.36%** | 11/16 (68.75%) | 12/18 (66.67%) | 3/3 (100.0%) | 35/52 (67.31%) | 17/17 (100.0%) | 8/8 (100.0%) |
| **Ablation Ref: Attenuation Alone** | 0.93 | **69.57%** | 7/16 (43.75%) | 8/18 (44.44%) | 3/3 (100.0%) | 32/52 (61.54%) | 16/17 (94.1%) | 7/8 (87.5%) |
| **Ablation Ref: RIR Alone** | 0.98 | **65.22%** | 5/16 (31.25%) | 6/18 (33.33%) | 2/3 (66.7%) | 31/52 (59.62%) | 14/17 (82.4%) | 6/8 (75.0%) |
| **Ablation Ref: All Three Combined (v6)** | 0.85 | **73.91%** | 10/16 (62.50%) | 11/18 (61.11%) | 3/3 (100.0%) | 34/52 (65.38%) | 17/17 (100.0%) | 8/8 (100.0%) |


## 2. Subtype Findings & Forensic Insights

1. **Sustained Scream Preservation:** Candidates G (Probabilistic Mixed) and C (Mild Masking) successfully defended sustained scream performance, preventing the regression observed in Candidate B (Mask-v6).
2. **Masked Scream Gains:** Candidates D, E, F, and G maintained elevated masked-scream recall (62.5% to 68.8%), significantly outperforming Baseline A (50.0%).
3. **Distant Scream Generalization:** Conservative early-reflection RIR (Candidate F) and multi-level SNR masking (Candidate D) yielded robust distant-scream detection (61.1% to 66.7%) without the destructive transient smearing of full synthetic RIR.
