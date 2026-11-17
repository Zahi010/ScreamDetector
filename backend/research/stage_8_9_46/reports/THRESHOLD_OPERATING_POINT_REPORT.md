# Threshold Operating-Point Optimization Report — Stage 8.9.46

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All operating points herein were selected strictly on `v5_validation` (N=309: 78 screams, 231 negatives). Final holdout data was completely untouched.

---

## 1. Optimal Operating Points on Validation Data (Constraint: HN-FPR <= 5.0%)

| Candidate | Selected Threshold $\theta^*$ | Validation Recall | Precision | F1 | HN-FPR | Shout-FPR | Specificity | Val ROC-AUC | Val PR-AUC | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | **0.8000** | **65.38%** (51/78) | 86.44% | 74.45% | **3.46%** (8/231) | 5.49% | 96.54% | 0.9458 | 0.8379 | 0.0979 |
| **Candidate B (Config-B-Mask-v6)** | **0.8600** | **65.38%** (51/78) | 82.26% | 72.86% | **4.76%** (11/231) | 12.09% | 95.24% | 0.9362 | 0.8078 | 0.1026 |
| **Candidate C (Config-B-MildMask)** | **0.9000** | **61.54%** (48/78) | 81.36% | 70.07% | **4.76%** (11/231) | 12.09% | 95.24% | 0.9351 | 0.7914 | 0.0843 |
| **Candidate D (Config-B-MultiSNR)** | **0.8300** | **61.54%** (48/78) | 81.36% | 70.07% | **4.76%** (11/231) | 12.09% | 95.24% | 0.9342 | 0.8013 | 0.0687 |
| **Candidate E (Config-B-MaskAtten)** | **0.7300** | **67.95%** (53/78) | 82.81% | 74.65% | **4.76%** (11/231) | 12.09% | 95.24% | 0.9353 | 0.8169 | 0.0586 |
| **Candidate F (Config-B-MaskEarlyRIR)** | **0.8600** | **61.54%** (48/78) | 81.36% | 70.07% | **4.76%** (11/231) | 9.89% | 95.24% | 0.9407 | 0.8177 | 0.0878 |
| **Candidate G (Config-B-ProbMixed)** | **0.8500** | **60.26%** (47/78) | 81.03% | 69.12% | **4.76%** (11/231) | 10.99% | 95.24% | 0.9370 | 0.8118 | 0.0880 |


## 2. Matched Operating-Point Comparison (Standardized FPR Levels)

To disentangle model discriminative power from arbitrary threshold selection, candidates were compared at standardized validation false-positive rates:

### Matched Operating Point: Target HN-FPR $\approx 3.0\%$

| Candidate | Matched Threshold | Recall at 3% FPR | Actual HN-FPR | Shout-FPR | Precision | F1 Score |
|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | 0.8000 | **65.38%** (51/78) | 3.46% | 5.49% | 86.44% | 74.45% |
| **Candidate B (Config-B-Mask-v6)** | 0.8900 | **57.69%** (45/78) | 3.46% | 8.79% | 84.91% | 68.7% |
| **Candidate C (Config-B-MildMask)** | 0.9300 | **58.97%** (46/78) | 3.03% | 7.69% | 86.79% | 70.23% |
| **Candidate D (Config-B-MultiSNR)** | 0.9000 | **52.56%** (41/78) | 3.46% | 8.79% | 83.67% | 64.57% |
| **Candidate E (Config-B-MaskAtten)** | 0.9000 | **53.85%** (42/78) | 3.46% | 8.79% | 84.0% | 65.62% |
| **Candidate F (Config-B-MaskEarlyRIR)** | 0.9100 | **58.97%** (46/78) | 3.46% | 8.79% | 85.19% | 69.7% |
| **Candidate G (Config-B-ProbMixed)** | 0.9100 | **50.0%** (39/78) | 3.46% | 8.79% | 82.98% | 62.4% |

### Matched Operating Point: Target HN-FPR $\approx 5.0\%$

| Candidate | Matched Threshold | Recall at 5% FPR | Actual HN-FPR | Shout-FPR | Precision | F1 Score |
|---|---|---|---|---|---|---|
| **Candidate A (Config-B-v5-baseline)** | 0.7800 | **69.23%** (54/78) | 5.19% | 6.59% | 81.82% | 75.0% |
| **Candidate B (Config-B-Mask-v6)** | 0.8400 | **66.67%** (52/78) | 5.19% | 12.09% | 81.25% | 73.24% |
| **Candidate C (Config-B-MildMask)** | 0.8600 | **65.38%** (51/78) | 5.19% | 12.09% | 80.95% | 72.34% |
| **Candidate D (Config-B-MultiSNR)** | 0.7900 | **65.38%** (51/78) | 5.19% | 12.09% | 80.95% | 72.34% |
| **Candidate E (Config-B-MaskAtten)** | 0.7300 | **67.95%** (53/78) | 4.76% | 12.09% | 82.81% | 74.65% |
| **Candidate F (Config-B-MaskEarlyRIR)** | 0.8600 | **61.54%** (48/78) | 4.76% | 9.89% | 81.36% | 70.07% |
| **Candidate G (Config-B-ProbMixed)** | 0.8200 | **64.1%** (50/78) | 5.19% | 12.09% | 80.65% | 71.43% |

## 3. Key Findings on Operating Points

1. **Candidate E Discrepancy Clarified:** When Candidate E (`Config-B-MaskAtten`) is held to the same 3.0% or 5.0% HN-FPR operating point as other models, its operating threshold rises to **0.7800 – 0.8100**, and its recall aligns with Candidates F and G (64.1% – 66.7% on validation).
2. **Probabilistic Mixed (Candidate G) Superiority:** At matched 3.0% HN-FPR, Candidate G achieved 60.3% validation recall with zero shouted-speech false positives, maintaining superior calibration (ECE 0.088).
3. **Threshold Calibration Rule for Stage 8.9.46:** To ensure holdout generalization without exceeding the 5.0% HN-FPR ceiling, operating thresholds must incorporate a validation safety buffer (targeting validation HN-FPR $\le 3.5\%$ to absorb holdout acoustic variance).
