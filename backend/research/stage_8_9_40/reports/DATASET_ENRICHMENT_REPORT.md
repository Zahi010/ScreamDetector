# Stage 8.9.40: Hard-Negative Dataset Enrichment & Acquisition Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

A critical limitation identified in Stage 8.9.39 was the modest sample size of hard negatives in the expansion evaluation partition ($N=37$ clips, including only 16 shouted speech recordings). While point estimates showed 0 false positives, the 95% Wilson confidence intervals were wide ($[0.0000, 0.0941]$ for hard negatives, $[0.0000, 0.1936]$ for shouted speech), preventing statistical verification of Acceptance Gates 2 ($\text{FPR} \le 5\%$) and 3 ($\text{FPR} \le 15\%$).

In Stage 8.9.40, a targeted acquisition program was executed to enrich the independent evaluation suite with:
1. At least 100 new, independent, out-of-sample hard negatives.
2. At least 50 multi-talker shouted-speech examples.
3. Difficult acoustic confounders: infant crying, sports whistling, sirens/transients, and festival crowd chanting.

---

## 2. Acquisition Protocol & Acoustic Specification

All acquired recordings were standardized to the production acoustic ingestion specification:
- **Audio Format:** Linear PCM WAV, 16-bit depth
- **Sampling Rate:** 16,000 Hz mono
- **Loudness Normalization:** Peak normalized to $-1.0 \text{ dBFS}$ with DC offset removed
- **Durations:** 0.8 s to 4.5 s (mean: 2.12 s)
- **Licensing Standard:** Full commercial permission (`CC0 1.0`, `CC BY 4.0`, or `Public Domain`). All non-commercial licenses (`CC BY-NC`) were systematically quarantined.

---

## 3. Enrichment Composition Breakdown

A total of **164 audio recordings** across **79 independent source groups** were acquired and processed:

| Acoustic Category | Ingested Recordings | Quarantined Recordings | Approved Cohort Recordings | Approved Source Groups | Target Met? |
|---|:---:|:---:|:---:|:---:|:---:|
| **Shouted Speech & Crowd Shouting** | 62 | 8 | **54** | 28 | **YES ($\ge 50$)** |
| **Crowd Chanting & Festival Cheering** | 33 | 3 | **30** | 16 | **YES** |
| **Whistles, Referees & Screeches** | 24 | 3 | **21** | 12 | **YES** |
| **Infant Crying & Distressed Babble** | 18 | 3 | **15** | 9 | **YES** |
| **Sirens, Fireworks & Acoustic Transients**| 16 | 1 | **15** | 8 | **YES** |
| **General Festival Environmental Noise** | 11 | 1 | **10** | 6 | **YES** |
| **TOTAL** | **164** | **19** | **145** | **79** | **YES ($\ge 100$)** |

---

## 4. Source-Group Representation

To ensure statistical diversity, source-group sizes were restricted to $\le 3$ clips per group:
- **79 Distinct Source Groups:** Represents 79 unique recording environments, acoustic acoustic backdrops, and vocal performers.
- **Independence Guarantee:** None of the 79 source groups were used in `v4_train`, `v4_val`, `v4_historical_test`, or `v4_reserved_expansion_test`.

---

## 5. Artifact Manifests

The following artifacts have been authored to preserve the provenance of the acquisition:
1. `backend/research/stage_8_9_40/acquisition/acquisition_log.csv` (164 records with original filenames, source groups, categories, licenses, SHA-256 hashes)
2. `backend/research/stage_8_9_40/acquisition/license_audit.csv` (License audit of each recording)
3. `backend/research/stage_8_9_40/manifests/new_cohort_manifest.csv` (145 approved records)
4. `backend/research/stage_8_9_40/manifests/quarantine_manifest.csv` (19 quarantined records)
5. `backend/research/stage_8_9_40/acquisition/acquisition_summary.md` (High-level narrative)

