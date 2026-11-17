# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Source Diversity, Uploader Concentration & Acoustic Independence Report

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary

An empirical diversity and clustering evaluation was performed across all historical datasets in the repository. Concentration metrics, including the Herfindahl-Hirschman Index (HHI) and top-N uploader share, were computed to diagnose why previous models failed to generalize across unseen source groups.

### Key Concentration Findings:
- **Uploader Herfindahl-Hirschman Index (HHI):** **2070.01** (indicates moderate-to-high concentration in critical subcategories).
- **Top-1 Uploader Concentration:** `unknown_creator` contributes **1625 clips (43.99%)** of the entire repository.
- **Top-5 Uploader Concentration:** Accounts for **2328 clips (63.02%)**.
- **Top-10 Uploader Concentration:** Accounts for **2541 clips (68.79%)**.
- **Diagnostic Impact:** In Stage 64 short screams, 61% of clips originated from a single uploader session. In Stage 74 shouted speech, 61.5% of false alarms originated from `reitanna`. This severe source clumping created an illusion of high recall while failing on unseen speakers.

---

## 2. Top-20 Historical Creator Concentration Table

| Rank | Creator / Uploader | Total Clips | Share of Dataset (%) | Cumulative Share (%) | Primary Category Focus |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 1 | `unknown_creator` | 1625 | 43.99% | 43.99% | `general` |
| 2 | `unknown_freesound_creator` | 354 | 9.58% | 53.57% | `unknown` |
| 3 | `AcousticResearch_Lab` | 153 | 4.14% | 57.72% | `unknown` |
| 4 | `artist_s49_dev_` | 101 | 2.73% | 60.45% | `short_scream` |
| 5 | `v2_creator_v2_fsd50` | 95 | 2.57% | 63.02% | `unknown` |
| 6 | `artist_s49_val_` | 63 | 1.71% | 64.73% | `short_scream` |
| 7 | `bulldozia` | 44 | 1.19% | 65.92% | `shouting_and_speech` |
| 8 | `artist_s43_pos_` | 37 | 1.00% | 66.92% | `short_scream` |
| 9 | `v2_creator_v3_fsd50` | 35 | 0.95% | 67.87% | `unknown` |
| 10 | `artist_supp_sho` | 34 | 0.92% | 68.79% | `short_scream` |
| 11 | `Reitanna` | 32 | 0.87% | 69.65% | `shouting_and_speech` |
| 12 | `Corsica_S` | 29 | 0.79% | 70.44% | `shouting_and_speech` |
| 13 | `toiletrolltube` | 20 | 0.54% | 70.98% | `general_environmental` |
| 14 | `11linda` | 18 | 0.49% | 71.47% | `shouting_and_speech` |
| 15 | `dobroide` | 17 | 0.46% | 71.93% | `shouting_and_speech` |
| 16 | `artist_v3_fsd50` | 16 | 0.43% | 72.36% | `short_scream` |
| 17 | `davidkyoku` | 14 | 0.38% | 72.74% | `general_environmental` |
| 18 | `Ephemeral_Rift` | 14 | 0.38% | 73.12% | `shouting_and_speech` |
| 19 | `Robinhood76` | 10 | 0.27% | 73.39% | `shouting_and_speech` |
| 20 | `Festival Scream Detector Synthetic Sound Lab` | 9 | 0.24% | 73.63% | `general_environmental` |

---

## 3. Mandatory Source Diversity Mandates for Stage 8.9.75 Acquisition

1. **Strict Per-Source Quota:** No single uploader, creator, or recording session may contribute more than **5.0%** of any evaluation cohort.
2. **Minimum Source-Group Threshold:** A prospective cohort of 700 clips must contain a minimum of **350 distinct source groups** (ratio >= 0.50).
3. **Cross-Uploader Verification:** Hard-negative categories (shouted speech, infant cries, whistles) must be drawn from at least 40 independent creators each.
