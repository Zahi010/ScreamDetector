# Candidate B Baseline Reproduction & Reference Audit — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Verification

Candidate B (`Config-B-Mask-v6`, `config_b_mask.pt`) has been cryptographically verified and 100% numerically reproduced against the saved Stage 8.9.47 independent evaluation predictions.

### Verified Performance Baseline (Stage 8.9.47 Cohort, N = 480)

| Evaluation Metric | Point Estimate | Exact Count | 95% Wilson CI | Benchmark Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Scream Recall** | **90.00%** | 144/160 | [84.37%, 93.75%] | $\ge 96.0\%$ | **FAIL (Deficit: 6.00%)** |
| **Hard-Negative FPR** | **1.25%** | 4/320 | [0.49%, 3.17%] | $\le 5.0\%$ | **PASS** |
| **Shouted-Speech FPR** | **0.00%** | 0/80 | [0.00%, 4.58%] | $\le 15.0\%$ | **PASS** |
| **Short Scream Recall ($d \le 1.0\text{s}$)** | **100.00%** | 70/70 | [94.80%, 100.00%] | $\ge 90.0\%$ | **PASS** |
| **Referee Whistle FPR** | **8.89%** | 4/45 | [3.51%, 20.73%] | Diagnostic | **FOCAL FLAW (4 FPs)** |

---

## 2. Positive Subgroup Generalization Breakdown

| Positive Subgroup | Count | Recall (%) | 95% Wilson CI | Preservation Priority |
| :--- | :---: | :---: | :---: | :---: |
| Ultra-Short Screams ($d \le 0.5\text{s}$) | 25/25 | 100.00% | [86.68%, 100.00%] | **CRITICAL (Zero Regressions Allowed)** |
| Standard Short Screams ($0.5 < d \le 1.0\text{s}$) | 45/45 | 100.00% | [92.13%, 100.00%] | **HIGH** |
| Sustained Screams ($d > 1.0\text{s}$) | 33/35 | 94.29% | [81.39%, 98.42%] | **HIGH** |
| Distant & Reverberant Screams | 14/20 | 70.00% | [48.10%, 85.45%] | **MEDIUM** |
| Low-Intensity & Muffled Screams | 12/15 | 80.00% | [54.81%, 92.95%] | **MEDIUM** |
| Crowd-Masked Screams | 15/20 | 75.00% | [53.13%, 88.81%] | **MEDIUM** |

---

## 3. Whistle False Positive Identification
The 4 false positive recordings from Candidate B are:
1. `s47_indep_neg_0197` (Prompt alias: `hn_indep_0088`): $P_{\text{B}} = 0.9102$
2. `s47_indep_neg_0199` (Prompt alias: `hn_indep_0102`): $P_{\text{B}} = 0.8135$
3. `s47_indep_neg_0200` (Prompt alias: `hn_indep_0119`): $P_{\text{B}} = 0.8282$
4. `s47_indep_neg_0229` (Prompt alias: `hn_indep_0144`): $P_{\text{B}} = 0.9051$

All 4 recordings represent referee trill whistles with fundamental frequency in the 2.8–3.2 kHz range and rapid ~25 Hz amplitude/frequency trill modulation.
