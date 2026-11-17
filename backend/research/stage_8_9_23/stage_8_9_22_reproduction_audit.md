# Stage 8.9.22 Independent Reproduction Audit & Discrepancy Investigation

## Executive Summary

This audit independently reproduces the experimental claims, metrics, and implementation behaviors reported in the **Stage 8.9.22 Completion Report** (`backend/experiments/stage8_9_22_sddfr/reports/stage_8_9_22_completion_report.md`). 

The audit was conducted strictly against the frozen primary test split ($N = 462$) and the supplementary short-scream validation set ($N = 68$) using exact saved predictions, audio files, and reconstructed feature manifests.

### Summary of Audit Verdicts

| Metric / Claim | Reported in Stage 8.9.22 | Independently Audited Value | Reproduction Verdict | Root Cause of Discrepancy (if any) |
|---|---|---|---|---|
| **Overall Primary Scream Recall** | 78.21% (61 / 78) | **78.21%** (61 / 78) | **VERIFIED** | Exact parity across all 78 positive test recordings. |
| **Primary Short-Scream Recall** | 86.36% (19 / 22) | **86.36%** (19 / 22) | **VERIFIED** | Exact parity across the 22 short screams in test split. |
| **Supplementary Short-Scream Recall** | 95.59% (65 / 68) | **95.59%** (65 / 68) | **VERIFIED** | Re-evaluated on isolated supplementary set; 65/68 detected. |
| **P95 Real-time Latency** | 16.40 ms | **16.40 ms** | **VERIFIED** | Wall-clock latency benchmark confirmed (< 25 ms gate). |
| **Hard-Negative FPR (Overall)** | 5.21% (20 / 384) | **7.03%** (27 / 384) | **DISCREPANCY** | Stage 8.9.22 calculated hard-negative FPR by excluding 7 supposed Tier 2 shouting suppressions ($20 / 384 = 5.208\% \approx 5.21\%$). On held-out test data, Tier 2 suppressed 0 shouting samples. |
| **Shouting False Positive Rate** | 11.90% (10 / 42 claimed) | **20.24%** (17 / 84) | **CRITICAL DISCREPANCY** | **Denominator & Suppression Error**: The test set contains **84 shouting samples**, not 42. Furthermore, Tier 2 suppressed **0 of 17** triggers on held-out test data. $10 / 84 = 11.9047\%$, revealing that the author divided a hypothesized 10 remaining FPs by 84 while mislabeling the denominator as 42. |
| **Tier 2 Shouting False Alarm Suppression** | 7 of 17 suppressed (41.2%) | **0 of 17 suppressed** (0.0%) | **UNREPRODUCED ON TEST** | All 17 Tier 1 shouting triggers exhibited $p_2 \ge 0.40$ or triggered chaotic phonation safeguards (`he_pitch_fail > 0.35`), bypassing suppression on held-out test split. |
| **Identical Candidate Metrics** | 8 candidates produced identical 78.21% / 5.21% | **Identical Binary Decisions Explained** | **VERIFIED PHENOMENON** | Probabilities drifted by 0.01–0.05, but zero examples crossed the decision threshold (0.35) or Tier 2 bypass (0.40). |

---

## 1. Experimental Setup and Dataset Manifests

### 1.1 Evaluated Dataset Splits
The evaluation was executed across the ground-truth partitioned datasets without any data leakage or synthetic corruption:

1. **Primary Held-Out Test Split ($N = 462$)**:
   - Manifest: `backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.json`
   - Split: `split == "test"`
   - Total Positives ($y = 1$): **78 scream recordings**
     - Sustained screams: 41
     - Standard screams: 15
     - Short screams ($\le 1.0$ s): **22**
   - Total Negatives ($y = 0$): **384 recordings**
     - Shouting / Excited Speech (`canonical_category == "SHOUTING_EXCITED_SPEECH"`): **84 recordings**
     - Acoustic Confusers & Hard Negatives: **300 recordings** (cheering, crowd noise, whistling, laughter, music, mechanical transients)
   - Independent Source Groups: **142 isolated clusters** (Zero source-level overlap with training or validation).

2. **Supplementary Short-Scream Dataset ($N = 68$)**:
   - Positives only ($y = 1$), duration $\le 1.0$ s, sourced from FSD50K and OpenSLR.
   - Evaluated as a separate benchmark. 65 / 68 detected (95.59%).

---

## 2. Forensic Investigation of the Shouting Metric Discrepancy

### 2.1 The 11.90% vs 20.24% Mathematical Proof
The Stage 8.9.22 report asserted:
> *"Shouting FPR reduced from 20.24% (17/84) to 11.90% (10/42) via Tier 2 Acoustic Suppression."*

A mathematical contradiction exists in that statement:
$$\frac{10}{42} = 0.23809 \quad (23.81\%)$$
$$\frac{10}{84} = 0.119047 \quad (11.90\%)$$

The arithmetic reveals the exact origin of the error:
1. The author took the true denominator of the shouting test set ($N_{\text{shout}} = 84$).
2. The author hypothesized or observed on an exploratory validation slice that 7 shouting false alarms could be suppressed, leaving $17 - 7 = 10$ remaining false alarms.
3. The author computed $\frac{10}{84} = 11.9047\%$.
4. In authoring the markdown text, the author wrote "10/42", mistakenly halving 84 to 42, while printing the percentage computed from $\frac{10}{84}$.

### 2.2 Why Tier 2 Suppressed 0 Shouting False Alarms on the Test Split
In `backend/experiments/stage8_9_22_sddfr/src/sddfr_classifier.py`, the Tier 2 verifier logic is:
```python
is_confirmed_chaotic_scream = (
    (p2 >= 0.40) or 
    (he_pitch_fail > 0.35) or 
    (shr_db > -6.0)
)
if is_confirmed_chaotic_scream:
    verifier_decision = "POSSIBLE_SCREAM"
    verifier_reason = "TIER2_CONFIRMED_CHAOTIC_OR_BIPHONIC_DISTRESS"
    final_pred = 1
```

Forensic extraction of all 17 shouting false positives in `backend/research/stage_8_9_23/remaining_shouting_fp_analysis.csv` revealed:
- **15 out of 17** shouting false alarms had Tier 2 acoustic probability $p_2 \ge 0.40$ (e.g., `v2_fsd50k_220823` had $p_2 = 0.9986$; `v2_fsd50k_432875` had $p_2 = 0.9335$).
- **17 out of 17** shouting false alarms exhibited high glottal vocal strain where `high_energy_pitch_failure == 1.0` (exceeding the 0.35 safeguard).
- Because every single one of the 17 shouting triggers met the chaotic distress bypass condition, the Tier 2 verifier outputted `POSSIBLE_SCREAM` with reason `TIER2_CONFIRMED_CHAOTIC_OR_BIPHONIC_DISTRESS`.
- **Result:** Exactly 0 false alarms were suppressed on the test split. The true Shouting FPR on the frozen held-out test split is **20.24%** (17/84).

---

## 3. Investigation of Identical Candidate Metrics

A major puzzle in Stage 8.9.22 was that Candidates 1 through 8 produced identical aggregate metrics:
- Overall Recall: 78.21%
- Shouting FPR: 20.24% (Tier 1)
- Short-scream Recall: 86.36%

### 3.1 Per-Record Comparison Analysis
Using `backend/research/stage_8_9_23/candidate_prediction_comparison.csv` ($N = 3,696$ rows across 8 candidates $\times$ 462 test samples), we conducted a pairwise diff of raw probabilities, feature weights, and binary decisions.

Key findings:
1. **Dynamic Routing Is Actively Executed**:
   The feature router is NOT broken or dead code. Across the test recordings:
   - High-SNR tonal screams received $w_{\text{yamnet}} \approx 0.70$, $w_{\text{spec}} \approx 0.12$, $w_{\text{pitch}} \approx 0.10$.
   - Low-SNR masked screams received $w_{\text{yamnet}} \approx 0.85$, $w_{\text{spec}} \approx 0.05$, $w_{\text{pitch}} \approx 0.02$.
   - Intermediate probability $p_2$ varied between candidates by up to $\pm 0.048$.
2. **Backbone Dominance**:
   The base YAMNet logistic regression model outputs probabilities with extreme margins (either $< 0.15$ or $> 0.70$). Because YAMNet weight $w_{\text{yamnet}} \ge 0.70$ under all conditions, acoustic feature weighting shifted scores by only $\pm 0.03$, which was insufficient to move any sample across the fixed decision boundary of $\tau = 0.3500$.
3. **Identical Binary Decisions**:
   Of the 462 test samples, exactly 0 samples flipped from positive to negative or negative to positive across Candidates 1 through 8.

---

## 4. Audit Conclusions & Recommendations

1. **Reproducibility Status**:
   - Primary scream recall (78.21%), short-scream recall (86.36%), and P95 latency (16.40 ms) are **100% verified and reproducible**.
   - The reported shouting FPR of 11.90% is **unreproduced on the held-out test split**; the true value is **20.24%**.
   - The Tier 2 verifier did not suppress shouting false alarms on held-out test data because real shouting vocal fold strain mimics glottal turbulence.
2. **Implications for Candidate 8**:
   Candidate 8 violates the project engineering target for Shouting FPR ($\le 15.0\%$) with an actual rate of $20.24\%$. It must remain **REJECTED — RESEARCH ONLY**.
