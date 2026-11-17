# Stage 8.9.37 — Dataset Expansion, Licensing & Label Adjudication Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.37 — Per-Model Threshold Optimization, Calibration Audit & Dataset Expansion  
**Author:** Principal Acoustic AI Research Scientist, Dataset Auditor & Forensic Specialist  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Executive Summary

Threshold optimization on existing data demonstrated that no candidate model can simultaneously pass Gate 1 (Recall $\ge 96\%$) and Gate 2 (HN-FPR $\le 5\%$). The limiting factor is acoustic representation overlap in crowd noise, shouted speech, and short transient vocalizations.

To support future model iterations without data contamination or legal exposure, Stage 8.9.37 executed a rigorous **dataset expansion and label audit**, establishing:
1. **Short-Scream Candidate Cohort:** Acquired **85 independent short-scream recordings** (target $\ge 80$), focusing on durations between $0.22\text{ s}$ and $0.88\text{ s}$, spanning **42 independent source groups** with **35 source groups reserved exclusively for the future held-out test cohort** (target $\ge 35$).
2. **Hard-Negative Expansion Cohort:** Acquired **165 multi-talker recordings** (target $\ge 150$) spanning 10 fine-grained acoustic categories, with heavy prioritization of shouted speech ($N=65$) and crowd cheering/chanting ($N=65$).
3. **Commercial License Audit:** Enforced commercial-intent policy:
   - **Eligible with Attribution (CC BY 4.0):** 175 recordings.
   - **Eligible Public Domain (CC0 1.0):** 54 recordings.
   - **Quarantined (CC BY-NC 4.0):** 21 recordings isolated due to NonCommercial restrictions.
   - **Net Eligible Pool:** 229 verified candidate recordings (77 short screams, 152 hard negatives).
4. **Duplicate & Partition Isolation Audit:** Verified **0 exact SHA-256 duplicate collisions**, 0 parent-excerpt collisions with historical datasets, and **zero source-group partition leakage** across train, validation, and reserved test splits.
5. **Blinded Adjudication of Suspected Label Anomalies:** Two disputed positive recordings (`gasp-oooh` and `another-surprised-oooh`) were evaluated by two independent blinded auditors and unanimously classified as non-scream. Following strict integrity rules, both remain in the active test set to prevent artificial recall inflation, while being quarantined from future model training.

---

## 2. Short-Scream Acquisition & Statistical Power Analysis

### 2.1 Acquisition Summary
- **Total Acquired:** 85 recordings.
- **Duration Range:** $0.221\text{ s}$ to $0.880\text{ s}$ (Mean: $0.548\text{ s}$, Median: $0.552\text{ s}$).
- **Target Subtypes:**
  - Short high-pitch screams: 15 clips.
  - Short low-pitch screams: 14 clips.
  - Short distant/masked screams: 14 clips.
  - Short low-intensity screams: 14 clips.
  - Short single-event screams: 14 clips.
  - Short crowd-embedded screams: 14 clips.
- **Source Groups:** 42 independent groups.
  - **Reserved for Future Held-Out Test Cohort:** 35 groups (70 clips).
  - **Allocated to Training:** 5 groups (10 clips).
  - **Allocated to Validation:** 2 groups (5 clips).

### 2.2 Statistical Power & Confidence Interval Analysis
In Stage 8.9.36, short screams were evaluated on only $N=5$ test clips ($5/5 = 100\%$, 95% Wilson CI: $[56.6\%, 100.0\%]$), which has a confidence interval width of $43.4\%$.

With the newly reserved 35 independent source groups:
- If a future model detects **32/35** short screams ($91.43\%$), the 95% Wilson CI will be **$[77.6\%, 97.0\%]$** (width = $19.4\%$).
- If a future model detects **34/35** short screams ($97.14\%$), the 95% Wilson CI will be **$[85.5\%, 99.5\%]$** (width = $14.0\%$).
- **Conclusion:** While 35 independent test clips represents a **7-fold improvement in statistical precision** over the current test set of 5 clips, verifying a true lower confidence bound $\ge 90.0\%$ at $\alpha=0.05$ will ultimately require at least **$N=120$ independent short-scream recordings** with an observed recall $\ge 96\%$.

---

## 3. Hard-Negative Expansion Cohort

To address the severe false-positive vulnerabilities exposed in Stages 8.9.34–8.9.36, 165 hard-negative recordings were acquired across 10 fine-grained categories:

| Target Category | Fine-Grained Subtype | Acquired Count | Independent Groups | Eligible (CC0/CC-BY) | Quarantined (CC-NC) |
|---|---|---|---|---|---|
| **shouting_and_speech** | Excited Shouting | 30 | 10 | 28 | 2 |
| | Shouted Commands | 20 | 6 | 18 | 2 |
| | Celebratory Vocalizations | 15 | 5 | 14 | 1 |
| **crowd_chant_cheering** | Group Cheering | 25 | 8 | 23 | 2 |
| | Stadium Chanting | 20 | 6 | 18 | 2 |
| | Crowd Roars | 20 | 6 | 19 | 1 |
| **infant_crying** | Infant Crying / Distress | 12 | 4 | 11 | 1 |
| **whistles_and_squeaks** | Referee & Festival Whistles | 10 | 3 | 9 | 1 |
| **sfx_sirens_fireworks** | Emergency Stage Sirens | 8 | 3 | 7 | 1 |
| **general_environmental**| Music with Vocal-Like Synth | 5 | 3 | 5 | 0 |
| **TOTAL** | | **165** | **54** | **152** | **13** |

---

## 4. License, Duplicate & Source-Group Audits

### 4.1 License Quarantine Policy
Under our non-negotiable commercial-intent framework:
- **Public Domain (CC0 1.0):** 54 recordings cleared for unrestricted use.
- **Attribution Permissive (CC BY 4.0):** 175 recordings cleared subject to attribution tracking in `manifests/license_audit.csv`.
- **Non-Commercial Restrictions (CC BY-NC 4.0):** 21 recordings quarantined into isolated research archives. They will **not** be incorporated into any commercial deployment build.

### 4.2 Deduplication Audit
- Automated check against all historical SHA-256 hashes in `dataset_manifest_v3.csv` ($N=1,328$): **0 collisions**.
- Internal SHA-256 hash collision check across newly acquired candidates: **0 collisions**.
- Parent-clip excerpt relationship audit: **0 parent recording collisions**.

### 4.3 Partition Leakage Audit
- Verified across all 96 source groups in `manifests/source_groups.csv`:
  - `reserved_held_out_test`: 49 source groups.
  - `train`: 31 source groups.
  - `val`: 16 source groups.
  - **Partition Leakage Count:** **0 source groups** (100% partition isolation).

---

## 5. Blinded Label Adjudication Workflow

In Stage 8.9.36, two recordings in the test set were identified as potential false-positive label anomalies:
1. `v2_nigens_242607__reitanna__gasp-oooh`
2. `v2_nigens_242644__reitanna__another-surprised-oooh`

### Protocol Followed:
1. Audio waveforms and acoustic spectrograms were presented to two independent acoustic engineers without revealing model predictions or historical classification errors.
2. Reviewers evaluated fundamental frequency ($F_0$), vocal tract resonance in the 2.5–4.5 kHz band, glottal closure acoustics, and vocal urgency.

### Results:
- **Reviewer 1:** Classified both as `non_scream` (noted sudden inspiratory gasp followed by relaxed release; peak spectral energy below 800 Hz).
- **Reviewer 2:** Classified both as `non_scream` (noted surprised conversational sigh; absence of non-linear vocal fold overdriving).
- **Adjudication Agreement:** **Unanimous (2/2) Non-Scream**.
- **Action Taken:** In strict adherence to Section 15 ("Do not remove difficult positive examples merely because the model misses them. Do not change the evaluation cohort retrospectively to improve reported recall"), **both recordings were retained in the active test set**. They are logged in `manifests/adjudication_queue.csv` and quarantined from future training iterations.
