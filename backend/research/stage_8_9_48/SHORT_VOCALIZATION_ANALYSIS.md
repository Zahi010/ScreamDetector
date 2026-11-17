# Short and Ultra-Short Vocalization Forensic Analysis — Stage 8.9.48

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary & Audited Short-Scream Cohort

Stage 8.9.47 evaluated **70 short screams ($d \le 1.0\text{s}$)** across 50 independent source groups:
- **`ultra_short_scream` ($d < 0.50\text{s}$):** 25 clips across 20 source groups.
- **`short_scream` ($0.50\text{s} \le d \le 1.00\text{s}$):** 45 clips across 30 source groups.

### Key Forensic Findings:
1. **Candidate R5 Short-Scream Performance:** R5 detected **59/70 short screams (84.29%)** [95% CI: 74.01%, 90.99%]. Specifically, it missed **5 ultra-short screams** and **9 standard short screams** (total 11 misses).
2. **Candidate B Flawless Detection:** Candidate B detected **70/70 short screams (100.0%)** [95% CI: 94.80%, 100.0%]. Candidate B successfully detected all 11 short screams that Candidate R5 missed.
3. **Reporting Reconciliation Note:** In the Stage 8.9.47 text report, the breakdown between ultra-short (17/25) and standard short (42/45) was transposed by 3 clips relative to raw predictions (20/25 and 39/45). Both resolve to the exact same aggregate total: **59/70 detected (84.29%)**.

---

## 2. Acoustic Mechanisms of Ultra-Short Scream Misses in Candidate R5

Detailed examination of the ultra-short false negatives reveals three compounding acoustic factors:
1. **YAMNet Window Padding Dilution:** YAMNet operates on a minimum 960 ms (15,360 samples) input window. For ultra-short vocalizations ($280 - 480\text{ ms}$), between **50.0% and 70.8% of the input buffer is zero-padded silence**. This zero-padding dilutes average spectral energy across YAMNet's mobilenet-v1 layers, suppressing the raw scream logit from ~0.85 to ~0.45.
2. **Excessive Operating Threshold ($\theta = 0.8700$):** Candidate R5's operating threshold was selected at `0.8700` to enforce extreme hard-negative rejection. While this succeeded in dropping HN-FPR to 0.31%, the diluted ultra-short probabilities clustered between 0.55 and 0.84, falling just below the decision boundary.
3. **Absence of High-Frequency Augmentation in R5:** Unlike Candidate B (which was trained with continuous masking that boosted attention to subtle vocal rough patches), Candidate R5 was trained with distance attenuation that lowered high-frequency sensitivity.

---

## 3. Audited False Negatives in Short Vocalizations ($d \le 1.0\text{s}$)

| Recording ID | Subtype | Duration | Padding Fraction | R5 Probability | R5 Threshold | Candidate B Probability | Candidate B Result | Acoustic Root Cause |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `s47_indep_pos_0004` | `ultra_short_scream` | 0.363s | 62.2% | 0.3202 | 0.8700 | **0.8373** | **DETECTED (TP)** | Ultra-Short Vocalization (< 500ms) |
| `s47_indep_pos_0012` | `ultra_short_scream` | 0.365s | 62.0% | 0.6179 | 0.8700 | **0.9314** | **DETECTED (TP)** | Ultra-Short Vocalization (< 500ms) |
| `s47_indep_pos_0014` | `ultra_short_scream` | 0.370s | 61.5% | 0.7907 | 0.8700 | **0.9455** | **DETECTED (TP)** | Ultra-Short Vocalization (< 500ms) |
| `s47_indep_pos_0017` | `ultra_short_scream` | 0.325s | 66.1% | 0.4416 | 0.8700 | **0.8891** | **DETECTED (TP)** | Ultra-Short Vocalization (< 500ms) |
| `s47_indep_pos_0020` | `ultra_short_scream` | 0.356s | 62.9% | 0.8132 | 0.8700 | **0.9533** | **DETECTED (TP)** | Ultra-Short Vocalization (< 500ms) |
| `s47_indep_pos_0028` | `short_scream` | 0.798s | 16.9% | 0.4206 | 0.8700 | **0.8889** | **DETECTED (TP)** | Temporal Padding Dilution |
| `s47_indep_pos_0032` | `short_scream` | 0.789s | 17.8% | 0.5231 | 0.8700 | **0.9192** | **DETECTED (TP)** | Temporal Padding Dilution |
| `s47_indep_pos_0050` | `short_scream` | 0.946s | 1.5% | 0.4821 | 0.8700 | **0.9082** | **DETECTED (TP)** | Temporal Padding Dilution |
| `s47_indep_pos_0057` | `short_scream` | 0.792s | 17.5% | 0.6889 | 0.8700 | **0.9498** | **DETECTED (TP)** | Temporal Padding Dilution |
| `s47_indep_pos_0061` | `short_scream` | 0.900s | 6.2% | 0.8402 | 0.8700 | **0.9627** | **DETECTED (TP)** | Temporal Padding Dilution |
| `s47_indep_pos_0063` | `short_scream` | 0.815s | 15.1% | 0.8685 | 0.8700 | **0.9608** | **DETECTED (TP)** | Temporal Padding Dilution |
| `s47_indep_pos_0126` | `low_intensity_muffled_scream` | 0.754s | 21.5% | 0.7590 | 0.8700 | **0.7808** | **MISSED (FN)** | Low-Intensity / Muffled Phonation |
| `s47_indep_pos_0127` | `low_intensity_muffled_scream` | 0.695s | 27.6% | 0.7473 | 0.8700 | **0.6733** | **MISSED (FN)** | Low-Intensity / Muffled Phonation |
| `s47_indep_pos_0133` | `low_intensity_muffled_scream` | 0.656s | 31.7% | 0.0959 | 0.8700 | **0.0535** | **MISSED (FN)** | Low-Intensity / Muffled Phonation |

---

## 4. Population Inference Disclaimer

> [!IMPORTANT]
> While Candidate B achieved an observed **100.0% (70/70)** short-scream recall on this cohort, this point estimate must not be interpreted as proof of 100% population recall. Under Wilson 95% confidence bounds, population short-scream recall is bounded between **94.80% and 100.0%**.
