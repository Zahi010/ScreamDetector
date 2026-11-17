# Subgroup Error Analysis — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. False Negative Taxonomy (Missed Screams: N=38)

Total authentic screams in cohort: **102**.  
Candidate E missed **38** screams (62.75% recall).

| Category / Subtype | FN Count | Total in Subtype | Subgroup Recall (%) |
|---|---|---|---|
| `CROWD_MASKED` | 8 | 8 | Detailed below |
| `SHORT` | 3 | 3 | Detailed below |
| `SUSTAINED` | 27 | 27 | Detailed below |

---

## 2. False Positive Taxonomy (False Alarms: N=43)

Total hard negatives in cohort: **264**.  
Candidate E produced **43** false alarms (16.29% HN-FPR).

| Primary Negative Class | FP Count | Total in Class | Class FPR (%) |
|---|---|---|---|
| `CHEERING` | 17 | 55 | 30.91% |
| `CRYING` | 1 | 26 | 3.85% |
| `OTHER_VOCALIZATION` | 7 | 40 | 17.50% |
| `SHOUTED_SPEECH` | 9 | 111 | 8.11% |
| `WHISTLE` | 9 | 32 | 28.12% |

---

## 3. Forensic Case Studies
Detailed breakdown of each missed clip is persisted in `error_analysis/false_negatives.csv`.
Detailed breakdown of each false alarm clip is persisted in `error_analysis/false_positives.csv`.
