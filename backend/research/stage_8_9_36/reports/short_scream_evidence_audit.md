# Stage 8.9.36 — Short-Scream Evidence & Sample Adequacy Audit Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Target:** Sample Size Adequacy, Source-Group Independence & Statistical Validity of Gate 4 (Short Screams <1.0s)  
**Data Artifact:** `backend/research/stage_8_9_36/evaluation/short_scream_source_group_analysis.csv`  

---

## 1. Executive Summary & Statistical Verdict

Stage 8.9.35 reported that Candidate D detected **5 out of 5 short screams (<1.0s duration)**, achieving a nominal recall rate of **100.00%** and technically satisfying Gate 4 ($\ge 90.00\%$).

A comprehensive forensic audit of the entire 1,328-recording corpus was conducted to examine the statistical credibility and source diversity of this metric:

### **Statistical Audit Verdict:**
- **SEVERE STATISTICAL UNDER-SAMPLING:** The held-out test cohort contains **only 5 short screams ($N=5$)**.
- **WIDE CONFIDENCE INTERVAL:** While 5/5 screams were detected ($\hat{p} = 100.0\%$), the **95% Wilson Score Confidence Interval spans $[56.55\%, 100.00\%]$**.
- **SCIENTIFIC AUDIT DEDUCTION:** A point estimate of 100% on $N=5$ **cannot scientifically prove** that population recall is $\ge 90\%$. The true population performance could be as low as 56.6% with 95% probability.
- **GATE 4 STATUS:** **CONDITIONALLY INCONCLUSIVE DUE TO INSUFFICIENT STATISTICAL POWER.**

---

## 2. Complete Corpus Duration Breakdown (353 Scream Recordings)

| Duration Bracket | Total Corpus Recordings | Unique Source Groups | Train Partition | Validation Partition | Test Partition | Test Detected | Nominal Test Recall | 95% Wilson Score Confidence Interval | Statistical Evidence Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **< 0.5s (Micro-Screams)** | 1 | 1 | 1 | 0 | **0** | 0 | N/A | N/A | **ZERO TEST SAMPLES** |
| **0.5 – 0.8s (Brief Screams)** | 12 | 10 | 6 | 3 | **3** | 3 | **100.00%** | $[43.85\%, 100.00\%]$ | **CRITICALLY UNDER-SAMPLED ($N=3$)** |
| **0.8 – 1.0s (Short Screams)** | 10 | 7 | 5 | 3 | **2** | 2 | **100.00%** | $[34.24\%, 100.00\%]$ | **CRITICALLY UNDER-SAMPLED ($N=2$)** |
| **Total Short (< 1.0s)** | **23** | **16** | **12** | **6** | **5** | **5** | **100.00%** | **$[56.55\%, 100.00\%]$** | **INSUFFICIENT SAMPLE SIZE ($N=5$)** |
| **1.0 – 1.5s (Intermediate)** | 56 | 28 | 27 | 9 | **20** | 17 | 85.00% | $[63.96\%, 94.76\%]$ | UNDER-SAMPLED ($N < 30$) |
| **> 1.5s (Sustained Screams)** | 274 | 111 | 133 | 64 | **77** | 69 | 89.61% | $[80.82\%, 94.64\%]$ | **ADEQUATE SAMPLE SIZE ($N=77$)** |
| **Total All Screams** | **353** | **125** | **172** | **79** | **102** | **91** | **89.22%** | **$[81.71\%, 93.99\%]$** | AUTHORITATIVE COHORT |

---

## 3. Analysis of the 5 Test Short Screams

All five short screams in the test cohort were inspected for origin, licensing, and acoustic properties:

| Recording ID | Duration | Bracket | Source Group ID | Creator / Uploader | License | Model Probability | Status |
| :--- | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| `v2_fs_169003` | 0.720s | 0.5–0.8s | `stage8_9_reitanna` | Reitanna | CC BY 3.0 | **0.8924** | TP |
| `v2_fs_369003` | 0.650s | 0.5–0.8s | `stage8_9_juskiddink` | juskiddink | CC BY 3.0 | **0.9141** | TP |
| `v2_fs_769001` | 0.580s | 0.5–0.8s | `stage8_9_marionagm90` | marionagm90 | CC0 (Public Domain) | **0.8710** | TP |
| `v2_fs_869001` | 0.840s | 0.8–1.0s | `stage8_9_dream4` | dream4dreamtheater | CC BY 3.0 | **0.7845** | TP |
| `v2_fsd50k_345111` | 0.920s | 0.8–1.0s | `fsd50k_uploader_juliabosque` | juliabosque | CC BY-NC 3.0\* | **0.6521** | TP |

*\*License notice: `v2_fsd50k_345111` carries a Non-Commercial CC BY-NC license; see Section 5 below.*

---

## 4. Duplicate and Crop Forensics

- **Independence Check:** The 5 test recordings originate from 5 distinct uploaders/source groups. None of them are temporal crops or overlapping excerpts of each other.
- **Corpus-Wide Short Scream Concentration:** In the full corpus of 23 short screams, 4 files belong to a single uploader (`reitanna`), and several uploaders contribute 2 crops each (`juskiddink`, `marionagm90`, `juliabosque`, `dream4dreamtheater`).
- **Conclusion:** The test split maintained source-group independence, but the absolute volume of short scream events in the public audio domain is severely constrained.

---

## 5. Statistical Requirements for Future Model Development

To satisfy Gate 4 with genuine scientific confidence (defined as a 95% Wilson lower bound exceeding $80.0\%$ when true recall is $\ge 90\%$):
$$\text{Minimum Required Test Sample Size: } N_{\text{test}} \ge 35 \text{ independent short screams}$$

### **Recommended Legal Acquisition Plan:**
1. **Target Acoustic Domain:** Authentic, unclipped human screams of duration $0.2\text{--}0.9\text{ seconds}$ (startle screams, fear reflex vocalizations, short high-pitch shrieks).
2. **Permissive Licensing Mandate:** Acquire exclusively under **CC0 (Public Domain)** or **CC BY 4.0** licenses.
3. **Prohibited Sources:** Strictly avoid scraping commercial movie sound effects libraries, copyrighted gaming audio, or non-commercial (CC BY-NC) repositories.
4. **Target Volume:** Acquire at least **80–100 new independent short scream recordings**, allowing $\ge 35$ for the held-out test cohort and 45–65 for training/validation.
