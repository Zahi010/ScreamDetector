# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# INDEPENDENT EVALUATION READINESS DECISION REPORT
**Formal Governance Determination on Candidate 65-F and Dual-Resolution Architectures**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Authoritative Readiness Verdict

```
========================================================================================
                      FORMAL GOVERNANCE READINESS VERDICT:
                    NOT READY FOR INDEPENDENT EVALUATION
========================================================================================
```

---

## 3. Executive Decision Rationale

Stage 8.9.66 was chartered as an **evaluation-readiness stage**, designed to determine whether any current model candidate satisfies the necessary prerequisites to justify conducting an independent evaluation on an unsealed cohort.

A thorough, reproducible empirical audit established that:
1. **Candidate 65-F is the clear front-runner among all research candidates**, achieving an F1 score of **0.9534**, short-scream recall of **98.50%** (and **96.51%** on the full 401 cohort), and neural P95 latency of **0.918 ms**.
2. **However, Candidate 65-F fails three of the five mandatory acceptance gates** on the standardized development cohort ($N=312$):
   - **Gate 1 (Overall Recall):** Observed **94.36%** vs. Mandatory Target **$\ge 96.00\%$** (Deficit: **-1.64%**; 184/195 vs 188/195).
   - **Gate 2 (Dev Hard-Negative FPR):** Observed **5.98%** vs. Mandatory Target **$\le 5.00\%$** (Excess: **+0.98%**; 7/117 vs 5/117).
   - **Gate 3 (Shouted-Speech FPR):** Observed **20.00%** vs. Mandatory Target **$\le 15.00\%$** (Excess: **+5.00%**; 1/5 vs 0/5).
3. **Rigorous Scientific Governance Prohibits Premature Cohort Unsealing:**
   - Proceeding to an independent evaluation on a sealed cohort when the candidate already fails 3 of 5 gates on the development cohort would waste the sealed evaluation dataset.
   - Declaring "Readiness" based on optimism or hand-waving would violate scientific integrity.
   - Therefore, the only scientifically honest, methodologically sound verdict is **NOT READY FOR INDEPENDENT EVALUATION**.

---

## 4. Gate Scorecard Summary

| Gate | Criterion | Threshold | Candidate 65-F Value | Delta to Target | Gate Status |
|---|---|---|---|---|---|
| **Gate 1** | Overall Recall | $\ge 96.00\%$ | 94.36% (184/195) | -1.64% | **FAIL** |
| **Gate 2** | Hard-Negative FPR | $\le 5.00\%$ | 5.98% (7/117) | +0.98% | **FAIL** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.00\%$ | 20.00% (1/5) | +5.00% | **FAIL** |
| **Gate 4** | Short-Scream Recall ($<1.00$s) | $\ge 90.00\%$ | 98.50% (131/133) | +8.50% | **PASS** |
| **Gate 5** | Neural Model Latency (P95) | $\le 25.00$ ms | 0.918 ms | -24.082 ms | **PASS** |

---

## 5. Required Engineering Actions to Achieve Readiness

Before an independent evaluation can be scheduled, future research stages must accomplish the following remediation milestones:
1. **Sustained-Branch Feature Refinement:**
   - Candidate 65-F's 11 false negatives are all sustained screams masked by background acoustics.
   - Enhance the sustained branch by incorporating multi-window pooling or harmonic-to-formant tracking to recover at least 4 of these 11 screams, lifting recall to $\ge 96.41\%$.
2. **Selective Tone Filtering Calibration:**
   - Calibrate the narrow-band whistle and transient suppression filters against the newly cataloged **462 hard-negative expansion files**, eliminating at least 2 of the 7 development false alarms to lower FPR to $\le 4.27\%$.
3. **Shouted-Speech Training Integration:**
   - Leverage the **529-recording shouted-speech dataset** assembled in Track D to calibrate vocal formant discrimination, bringing shouted-speech FPR strictly $\le 15.00\%$.
4. **Preregistration Readiness Check:**
   - Once all 5 gates pass on the development cohort, rerun the preregistration verification suite and transition to formal evaluation.

