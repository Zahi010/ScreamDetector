# STAGE 8.9.30.2 — AUDIT & DENOMINATOR RECONCILIATION REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.2  
**Date:** November 2, 2026  
**Auditor:** Senior ML Evaluation Reviewer  

---

## 1. RESOLUTION OF THE CRITICAL DENOMINATOR DISCREPANCY

In Stage 8.9.30.1, a surface discrepancy appeared between the Executive Summary (stating **67 hard negatives**) and the Category Confusion Matrix (summing to **98 negatives** with **55 false alarms** and **56.12% FPR**).

### Definitive Mathematical & Forensic Proof:
1. **The Original 67 Negatives:**
   - In Stage 8.9.30, the negative cohort consisted of 67 recordings from NIGENS (clean speech, reverberant speech, baby crying, and siren/alarms).
   - The production classifier triggered 30 false alarms on these 67 files:
     $$\text{FPR} = \frac{30}{67} = 44.78\%$$
2. **The 31 Mislabeled Positive Recordings:**
   - Stage 8.9.30.1 discovered that 31 files originally admitted with `ground_truth = 1` were NOT screams (28 stadium cheering, 2 shouted commands, 1 barking/guitar).
   - In Stage 8.9.30, **25 of these 31 files had triggered the classifier** with scores $\ge 0.3500$.
   - In Stage 8.9.30, those 25 predictions were erroneously counted as **25 True Positives** (Hits).
   - When audited and reclassified to their true ground truth (`GT = 0`), those 25 predictions became **25 False Alarms**!
3. **The Audited 98 Negatives:**
   - Combining the original 67 negatives with the 31 reclassified non-scream files gives:
     $$\text{Total Negatives} = 67 + 31 = 98$$
     $$\text{Total False Alarms} = 30 + 25 = 55$$
     $$\text{Audited FPR} = \frac{55}{98} = 56.12\%$$
4. **The Quarantined Clean Cohort (173 Files):**
   - If the 31 mislabeled files are quarantined (excluded from evaluation entirely rather than evaluated as hard negatives), the clean dataset consists of:
     - 106 Genuine Screams (89 Hits / 17 Misses = **83.96% Recall**)
     - 67 Clean Hard Negatives (30 False Alarms / 37 True Negatives = **44.78% FPR**)

| Evaluation Cohort | Positives | Hits | Recall (%) | Negatives | False Alarms | FPR (%) | Total Recordings |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Stage 8.9.30 Reported** | 137 | 114 | 83.21% | 67 | 30 | 44.78% | 204 |
| **Stage 8.9.30.1 Audited Total** | 106 | 89 | 83.96% | 98 | 55 | 56.12% | 204 |
| **Quarantined Clean Cohort** | 106 | 89 | 83.96% | 67 | 30 | 44.78% | 173 |
| **Reclassified Mislabeled Subset** | 0 | 0 | N/A | 31 | 25 | 80.65% | 31 |

---

## 2. SOURCE INDEPENDENCE RECONCILIATION

- Stage 8.9.30 reported 49 source groups due to a metadata grouping bug in `evaluate_and_audit.py` that assigned 76 Freesound files to `fs_user_freesound_user` and 56 NIGENS files to `nigens_zenodo`.
- Stage 8.9.30.1 and 8.9.30.2 resolved the underlying audio provenance to **81 unique uploaders** and **87 reconciled session clusters**.
- The 106 genuine screams originate from **49 independent source groups**.
- Multiple multi-clip recording sessions exist (e.g., `WelvynZPorterSamples` 6 takes, `julius_galla` 8 takes, `MrFossy` 4 takes, `todorrobot` 9 takes), confirming that recording count must never be equated with independent speaker count.
