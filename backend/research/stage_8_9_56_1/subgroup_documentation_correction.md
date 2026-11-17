# Subgroup Documentation Correction & Reconciliation — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Audit Mandate

Phase G (Section 10) mandates the strict preservation and formal certification of the corrected acoustic subgroup counts and performance metrics established during Stage 8.9.56.

A documentation discrepancy in Stage 8.9.55 Section 4 summary prose cited secondary subtype counts of Low-Intensity screams ($N=35$) and Muffled screams ($N=73$). Stage 8.9.56 forensically audited the underlying data artifacts (`subgroup_evaluation.md` and `frozen_test_manifest.json`) and proved that the authentic recorded counts are **$N=11$ for Low-Intensity** and **$N=94$ for Muffled screams**.

This document reaffirms the corrected counts, catalogs the verified performance metrics across all 11 acoustic subgroups, and confirms the `INSUFFICIENT EVIDENCE` designations.

---

## 2. Definitive Acoustic Subgroup Performance Table

The evaluation cohort comprises 450 total recordings (150 authentic screams, 300 hard negatives) across 246 source groups. All subgroup counts are derived directly from `frozen_test_manifest.json`:

| Acoustic Subgroup | Clip Count ($N$) | Source Groups | Candidate E1 Detected / Total | Candidate E1 Rate | Candidate B Detected / Total | Candidate B Rate | Delta ($\text{E1} - \text{B}$) | Audit & Evidence Finding |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Short Screams (<1.0s)** | **36** | 17 | 30 / 36 | **83.33%** | 24 / 36 | **66.67%** | **+16.67%** | Gate 4 Evaluation Target |
| **Sustained Screams ($\ge 1.0$s)** | **114** | 71 | 79 / 114 | **69.30%** | 59 / 114 | **51.75%** | **+17.54%** | Primary Duration Subgroup |
| **Low-Intensity Screams** | **11** | 8 | 2 / 11 | **18.18%** | 0 / 11 | **0.00%** | **+18.18%** | **Corrected Count (Was Prose $N=35$)** |
| **Muffled / Obstructed Screams** | **94** | 56 | 72 / 94 | **76.60%** | 53 / 94 | **56.38%** | **+20.21%** | **Corrected Count (Was Prose $N=73$)** |
| **Shouted Speech** | **60** | 39 | 4 / 60 | **6.67% FPR** | 3 / 60 | **5.00% FPR** | **+1.67%** | Gate 3 Evaluation Target |
| **Crowd Cheering / Noise** | **50** | 40 | 0 / 50 | **0.00% FPR** | 2 / 50 | **4.00% FPR** | **-4.00%** | Hard Negative Subgroup |
| **Infant / Child Crying** | **50** | 37 | 4 / 50 | **8.00% FPR** | 2 / 50 | **4.00% FPR** | **+4.00%** | Hard Negative Subgroup |
| **Sirens & Emergency Alarms** | **35** | 34 | 2 / 35 | **5.71% FPR** | 3 / 35 | **8.57% FPR** | **-2.86%** | Hard Negative Subgroup |
| **Music, Brass & Singing** | **35** | 28 | 4 / 35 | **11.43% FPR** | 8 / 35 | **22.86% FPR** | **-11.43%** | Hard Negative Subgroup |
| **Ordinary / Conversational Speech**| **100** | 63 | 7 / 100 | **7.00% FPR** | 4 / 100 | **4.00% FPR** | **+3.00%** | Hard Negative Subgroup |
| **Mechanically Modulated Whistles** | **0** | 0 | — | — | — | — | — | **INSUFFICIENT EVIDENCE ($N=0$)** |
| **Ultra-Short Screams ($\le 0.5$s)** | **0** | 0 | — | — | — | — | — | **INSUFFICIENT EVIDENCE ($N=0$)** |

---

## 3. Detailed Forensic Origin of the Low-Intensity and Muffled Prose Discrepancy

### 3.1 The Contradiction
- In Stage 8.9.55 Section 4 text, the author wrote:
  > *"Low-Intensity screams ($N=35$) achieved low recall, whereas Muffled screams ($N=73$) performed strongly."*
- However, querying `frozen_test_manifest.json` by subtype tag yields:
  - Clips tagged with `'low_intensity'`: exactly **11 clips**.
  - Clips tagged with `'muffled'`: exactly **94 clips**.
  - Candidate E1 correct on low-intensity: exactly 2 clips ($18.18\%$).
  - Candidate E1 correct on muffled: exactly 72 clips ($76.60\%$).

### 3.2 Provenance of the Prose Numbers
During the curation of Stage 8.9.55, an early preliminary candidate query considered 35 candidate low-intensity clips and 73 candidate muffled clips. When the final curation pipeline applied strict multi-source quarantine (filtering out all 2,213 historical exclusions), the filtered manifest ended with 11 low-intensity and 94 muffled clips. The author inadvertently retained the preliminary draft counts in the Section 4 prose summary.

### 3.3 Confirmation
The underlying manifest, feature arrays, and prediction CSVs (`candidate_e1_predictions.csv`, `candidate_b_predictions.csv`) have **always contained $N=11$ and $N=94$**. All calculations, evaluations, and tests in Stage 8.9.56 and Stage 8.9.56.1 use these verified counts. The incorrect $N=35$ and $N=73$ figures must never be reintroduced.

---

## 4. Insufficient Evidence Subgroups

1. **Mechanically Modulated Whistles ($N=0$):**
   - The Stage 8.9.55 independent cohort was curated from general festival and environmental acoustic archives (FSD50K, AudioSet, Freesound) and did not contain isolated referee whistles.
   - Therefore, whistle rejection by Candidate B + Intervention D cannot be empirically assessed on this cohort.
   - Status: **INSUFFICIENT EVIDENCE ($N=0$)**. No synthetic whistle data may be generated to fill this gap.
2. **Ultra-Short Screams $\le 0.5$ Seconds ($N=0$):**
   - While short screams between 0.5s and 1.0s are represented ($N=36$), no authentic screams with duration $\le 0.5$ seconds exist in the frozen manifest.
   - Status: **INSUFFICIENT EVIDENCE ($N=0$)**.

