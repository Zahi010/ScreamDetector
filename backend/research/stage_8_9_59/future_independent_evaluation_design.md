# Future Independent Evaluation Design — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase H of Stage 8.9.59, a blueprint was authored for a future independent, source-quarantined evaluation cohort.

**No new evaluation cohort was acquired or evaluated in this stage.** This report defines the mandatory structural criteria, sample-size calculations, stratification matrix, and quarantine safeguards required before any future evaluation may be conducted.

---

## 2. Mandatory Structural Independence Requirements

To prevent evaluation leakage and ensure reproducibility, any future evaluation cohort must fulfill 6 core criteria:

1. **Complete Source-Group & Creator Independence:** Zero overlap in `source_group_id`, `parent_recording_id`, or `creator_uploader` with `expansion_train`, `expansion_val`, or any previously consumed historical test cohort (Stages 8.9.47, 8.9.53, 8.9.55).
2. **Zero Derivative / Crop Overlap:** No cropped excerpts, reverberated variants, pitch-shifted copies, or synthetic derivatives of training files may appear in the evaluation cohort.
3. **Verified Commercial License:** 100% of audio clips must possess verified CC0, Public Domain, or CC BY licensing.
4. **Independent Dual-Reviewer Provenance:** Ground-truth labels must be independently assigned by at least two human annotators (inter-annotator Cohen's $\kappa \ge 0.85$). All borderline or ambiguous recordings (e.g. low-effort gasps) must be quarantined into an explicit exploratory bucket.
5. **Pre-Evaluation Cryptographic Freeze:** The evaluation manifest and audio files must be frozen, SHA-256 hashed, and sealed prior to executing any candidate inference.
6. **No Test-Set Tuning:** The evaluation cohort must be evaluated exactly once per research cycle. Model retraining, threshold sweeping, or hyperparameter selection on the test cohort is strictly forbidden.

---

## 3. Sample-Size Rationale & Statistical Power Formulation

Sample size requirements were computed to achieve a 95% confidence interval half-width (margin of error $E$) for each of the Five Project Acceptance Gates, accounting for source-group clustering:

$$N_{\text{indep}} = \frac{Z_{\alpha/2}^2 \cdot p (1 - p)}{E^2}, \quad \text{DEFF} = 1 + (m - 1)\rho, \quad N_{\text{clustered}} = N_{\text{indep}} \cdot \text{DEFF}$$

Where:
- $Z_{\alpha/2} = 1.96$ for 95% confidence.
- $p$ = target gate metric (e.g., $0.96$ for Recall, $0.05$ for Hard-Negative FPR).
- $m$ = average recordings per source group cluster ($m \approx 1.5 - 2.5$).
- $\rho$ = intraclass correlation coefficient ($\text{ICC} \approx 0.15 - 0.25$).
- $\text{DEFF}$ = Design Effect due to source clustering ($\text{DEFF} \approx 1.15 - 1.38$).

---

## 4. Stratified Sample Size & Source Group Target Matrix

| Evaluation Gate / Subgroup | Target Rate ($p$) | Margin of Error ($E$) | Clustered Total Recordings ($N$) | Min. Independent Source Groups (Strong Claim) | Exploratory Min. Source Groups |
|---|:---:|:---:|:---:|:---:|:---:|
| **Gate 1: Overall Scream Recall** | $\ge 96.0\%$ | $\pm 3.0\%$ | **200 Recordings** | **120 SGs** | **60 SGs** |
| ├── *Short Screams (<1.0s)* | $\ge 90.0\%$ | $\pm 5.0\%$ | 80 Recordings | 55 SGs | 30 SGs |
| ├── *Sustained Screams ($\ge 1.0$s)* | $\ge 90.0\%$ | $\pm 5.0\%$ | 120 Recordings | 65 SGs | 35 SGs |
| └── *Crowd-Masked Screams* | $\ge 85.0\%$ | $\pm 7.0\%$ | 60 Recordings | 40 SGs | 20 SGs |
| **Gate 2: All Hard Negatives** | $\le 5.0\%$ | $\pm 2.0\%$ | **500 Recordings** | **250 SGs** | **125 SGs** |
| ├── *Gate 3: Shouted Speech* | $\le 15.0\%$ | $\pm 5.0\%$ | 250 Recordings | 130 SGs | 65 SGs |
| ├── *Crowd Cheering / Chanting* | $\le 5.0\%$ | $\pm 3.0\%$ | 100 Recordings | 60 SGs | 30 SGs |
| ├── *Referee Whistles & Squeaks* | $\le 2.0\%$ | $\pm 2.0\%$ | 60 Recordings | 40 SGs | 20 SGs |
| └── *Infant Crying & Sirens* | $\le 5.0\%$ | $\pm 4.0\%$ | 90 Recordings | 50 SGs | 25 SGs |
| **Grand Total Recommended Cohort** | — | — | **700 Recordings** | **370 SGs** | **185 SGs** |

---

## 5. Preservation & Traceability

Full statistical calculations across all target gates are saved in [`future_evaluation_requirements.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/future_evaluation_requirements.csv).

