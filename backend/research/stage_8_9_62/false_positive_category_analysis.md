# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — False-Positive Category Analysis & Acoustic Distractor Profiling ($N=500$)

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Continuous streaming acoustic monitoring is severely vulnerable to non-target distractors. In Stage 8.9.61, rolling-window aggregation inflated hard-negative false positive rate to **35.40% (177/500)** across the exposed evaluation cohort.

This report presents a forensic category-by-category audit of all 500 hard negatives across four model configurations:
1. Candidate E1 Static C5
2. Candidate B Baseline
3. Candidate B + Intervention D
4. Candidate E1 Rolling EMA

---

## 2. Hard-Negative Distractor Category Breakdown

| Distractor Category | Sample Size ($N$) | Unique Source Groups | Candidate E1 Static FPR | Candidate B Baseline FPR | Candidate B + Interv. D FPR | Candidate E1 Rolling EMA FPR | Statistical Evidence Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **All Hard Negatives** | **500** | **296** | 19.20% (96/500) | 15.80% (79/500) | **14.80% (74/500)** | 35.40% (177/500) | `ROBUST_EVIDENCE` |
| **Priority 3: Shouted Speech** | 150 | 34 | 22.67% (34/150) | **14.00% (21/150)** | **14.00% (21/150)** | 30.67% (46/150) | `ROBUST_EVIDENCE` |
| **Referee Whistles & Squeaks** | 60 | 30 | 23.33% (14/60) | 10.00% (6/60) | **1.67% (1/60)** | 25.00% (15/60) | `ROBUST_EVIDENCE` |
| **Cheering & Crowd Chants** | 50 | 10 | **32.00% (16/50)** | 36.00% (18/50) | 36.00% (18/50) | 58.00% (29/50) | `ROBUST_EVIDENCE` |
| **Infant Crying** | 19 | 6 | 10.53% (2/19) | **5.26% (1/19)** | **5.26% (1/19)** | 31.58% (6/19) | `LIMITED_SAMPLE_SIZE` |
| **Environmental Noise & Sirens** | 221 | 221 | **13.57% (30/221)**| 14.93% (33/221) | 14.93% (33/221) | 36.65% (81/221) | `ROBUST_EVIDENCE` |

---

## 3. Acoustic Vulnerability Analysis by Distractor Category

### 3.1 Cheering and Stadium Crowd Chanting (Highest Error Rate: 58.00%)
- **Acoustic Overlap:** High-volume stadium cheering exhibits high fundamental pitch ($F_0 > 600$ Hz), chaotic subharmonics, and elevated acoustic roughness that directly mimic panic shrieks.
- **Rolling Exposure:** In continuous cheering recordings, acoustic energy remains elevated across several seconds. Rolling EMA easily charges above $\theta=0.6000$, resulting in false alarms on **29 out of 50 cheering files (58.00%)**.
- **Remediation Requirement:** Pure spectral filterbanks cannot separate happy cheering from terrified screaming. Semantic speech/non-speech classifiers or phonetic rejection layers are mandatory.

### 3.2 Shouted Speech & Aggressive Shouts (Gate 3 Focus)
- **Candidate B Superiority:** Candidate B Baseline achieved **14.00% FPR** on shouted speech, comfortably meeting Gate 3 ($\le 15.00\%$). In contrast, Candidate E1 Static failed at **22.67%**, and Rolling E1 failed at **30.67%**.
- **Acoustic Driver:** Candidate B's dual-encoder masking architecture penalizes formant structures with prominent lower harmonic voicing, distinguishing spoken vowels from open-mouth distress screams.

### 3.3 Referee Whistles and The Efficacy of Intervention D
- **Neural Net Vulnerability:** Pure data-driven neural nets misclassify 23% to 25% of referee whistles because whistles concentrate intense acoustic power in the 2.5–4.0 kHz scream band.
- **Intervention D Triumph:** Intervention D's deterministic spectral purity and harmonic ratio guardrail eliminated 5 out of 6 whistle false positives for Candidate B, slashing whistle FPR down to **1.67% (1/60)**.
- **Takeaway:** Hybrid DSP discriminators are essential to protect deep neural classifiers against narrowband physical acoustics.

### 3.4 Environmental Noise and Sirens
- On static evaluation, both models perform well ($13.57\% - 14.93\%$).
- Under rolling evaluation, persistent industrial sirens, squealing brakes, and metal scraping trigger multiple windows, elevating environmental FPR to **36.65%**.

