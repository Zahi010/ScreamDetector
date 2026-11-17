# Environmental Acoustic Augmentation Comparative Study — Stage 8.9.44

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Executive Summary

Stage 8.9.44 conducted a controlled, systematic investigation comparing five training conditions using the `DualEncoderAcousticModel` on `v5_train` ($N=1,198$):

- **Condition A (Baseline):** Authentic `v5_train` data only (`Config-B-v5-baseline`).
- **Condition B (RIR):** Authentic + Room Impulse Response convolution (`Config-B-RIR`).
- **Condition C (Attenuation):** Authentic + Distance attenuation & air absorption (`Config-B-Atten`).
- **Condition D (Masking):** Authentic + Background crowd/environmental noise masking (`Config-B-Mask`).
- **Condition E (Combined):** Authentic + Combined environmental pipeline (`Config-B-EnvCombined`).

All candidates were calibrated strictly on `v5_validation` ($N=309$) to enforce hard-negative $\text{FPR} \le 5.0\%$, and evaluated on the independent sealed `v5_final_holdout` benchmark ($N=205$: 69 screams, 136 negatives).

---

## 2. Comparative Benchmark Matrix (Final Holdout, $N=205$)

| Evaluation Dimension | Condition A (Baseline) | Condition B (RIR) | Condition C (Atten) | Condition D (Mask) | Condition E (Combined) |
|---|---|---|---|---|---|
| **Calibrated Threshold $\theta^*$** | **0.8200** | 0.9800 | 0.9300 | 0.8600 | 0.8500 |
| **Overall Recall** | **75.36% (52/69)** | 65.22% (45/69) | 69.57% (48/69) | 72.46% (50/69) | 73.91% (51/69) |
| **95% Wilson CI** | [64.04%, 84.01%] | [53.45%, 75.38%] | [57.92%, 79.15%] | [60.95%, 81.61%] | [62.49%, 82.81%] |
| **Hard-Negative FPR** | **3.68%** | **2.94%** | **3.68%** | **4.41%** | **3.68%** |
| **Shouted-Speech FPR** | **7.14%** | 10.71% | 14.29% | **7.14%** | **7.14%** |
| **Short-Scream Recall ($\le 1.0$s)**| **100.0% (17/17)** | 88.24% (15/17) | **94.12% (16/17)** | **100.0% (17/17)** | **100.0% (17/17)** |
| **Ultra-Short Recall ($<0.5$s)** | **100.0% (8/8)** | 75.0% (6/8) | 87.5% (7/8) | **100.0% (8/8)** | **100.0% (8/8)** |
| **Distant / Reverberant ($N=18$)** | 50.00% (9/18) | 33.33% (6/18) | 44.44% (8/18) | **66.67% (12/18)** | **61.11% (11/18)** |
| **Masked Screams ($N=16$)** | 50.00% (8/16) | 31.25% (5/16) | 43.75% (7/16) | **68.75% (11/16)** | **62.50% (10/16)** |
| **Clean / Standard Screams** | **100.0%** | 100.0% | 100.0% | **100.0%** | **100.0%** |
| **ROC-AUC** | 0.9487 | 0.9514 | 0.9433 | **0.9531** | 0.9514 |
| **PR-AUC** | 0.9104 | 0.9021 | 0.9015 | **0.9182** | 0.9145 |
| **Brier Score** | **0.0965** | 0.1284 | 0.1082 | 0.0994 | 0.1012 |
| **P95 Latency** | **0.539 ms** | 0.586 ms | **0.503 ms** | 0.530 ms | 0.541 ms |

---

## 3. Detailed Subgroup Findings

### 3.1 Background Masking (Condition D): Specific Benefit
Condition D demonstrated the most compelling targeted gains of any experimental condition:
- **Distant / Reverberant Screams:** Recall increased from **50.00% (9/18) to 66.67% (12/18)** (+16.67% gain, 3 additional distant screams recovered).
- **Masked Screams:** Recall increased from **50.00% (8/16) to 68.75% (11/16)** (+18.75% gain, 3 additional masked screams recovered).
- **ROC-AUC & PR-AUC:** Achieved the highest discrimination metrics of any candidate on the holdout benchmark (ROC-AUC = 0.9531, PR-AUC = 0.9182).
- **False-Positive Control:** Hard-negative FPR remained safely below the 5% gate at 4.41%, and shouted-speech FPR matched baseline at 7.14%.

### 3.2 Combined Environmental Pipeline (Condition E): Balanced Robustness
Condition E integrated RIR, distance attenuation, and background masking simultaneously:
- Distant scream recall reached **61.11% (11/18)** (+11.11% over baseline).
- Masked scream recall reached **62.50% (10/16)** (+12.50% over baseline).
- Maintained a lower hard-negative FPR than Condition D (3.68% vs. 4.41%).
- Preserved perfect short-scream recall (17/17, 100.0%).

### 3.3 Attenuation Augmentation (Condition C): Borderline Shouted Speech Risk
Condition C simulated physical distance falloff and high-frequency atmospheric absorption:
- Achieved the highest development-test recall (81.48%), but holdout recall dropped to 69.57%.
- Shouted-speech FPR rose sharply to **14.29%**, dangerously close to the Gate 3 failure threshold (15.0%).
- Air-absorption low-pass filtering makes screams sound darker and more speech-like, narrowing the acoustic boundary between distant screams and nearby aggressive shouting.

---

## 4. Five Research Acceptance Gates Audit

| Candidate | Gate 1 (Recall $\ge 96\%$) | Gate 2 (HN-FPR $\le 5\%$) | Gate 3 (Shout-FPR $\le 15\%$) | Gate 4 (Short Rec $\ge 90\%$) | Gate 5 (P95 $\le 25\text{ ms}$) | Overall Gates Passed |
|---|---|---|---|---|---|---|
| **Condition A (Baseline)** | **FAIL (75.36%)** | **PASS (3.68%)** | **PASS (7.14%)** | **PASS (100.0%)** | **PASS (0.54 ms)** | 4 of 5 |
| **Condition B (RIR)** | **FAIL (65.22%)** | **PASS (2.94%)** | **PASS (10.71%)** | **FAIL (88.24%)** | **PASS (0.59 ms)** | 3 of 5 |
| **Condition C (Atten)** | **FAIL (69.57%)** | **PASS (3.68%)** | **PASS (14.29%)** | **PASS (94.12%)** | **PASS (0.50 ms)** | 4 of 5 |
| **Condition D (Mask)** | **FAIL (72.46%)** | **PASS (4.41%)** | **PASS (7.14%)** | **PASS (100.0%)** | **PASS (0.53 ms)** | 4 of 5 |
| **Condition E (Combined)** | **FAIL (73.91%)** | **PASS (3.68%)** | **PASS (7.14%)** | **PASS (100.0%)** | **PASS (0.54 ms)** | 4 of 5 |

---

## 5. Synthesis & Scientific Conclusion

1. **Gate 1 Remains Unmet:** Despite targeted gains on distant and masked screams, **no candidate satisfied Gate 1 (Overall recall $\ge 96.0\%$)**. Overall recall on the sealed holdout benchmark is capped at 75.36% (baseline) and 73.91% (combined environmental). The upper bound of the 95% Wilson confidence interval reaches at most 84.01%, conclusively failing Gate 1.
2. **Specific Acoustic Benefit Confirmed:** Background masking (Condition D) and combined environmental modeling (Condition E) specifically benefited distant screams (+16.7% recall) and noise-masked screams (+18.8% recall) without causing false alarm collapse.
3. **Primary Recommendation:** Retain Condition D (Background Masking) and Condition E (Combined Environmental Pipeline) as validated augmentation components for future research, while keeping the production baseline strictly frozen.

