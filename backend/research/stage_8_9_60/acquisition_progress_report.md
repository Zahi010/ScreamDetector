# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Acquisition Progress Report: Priority Categories & Target Completion

## 1. Executive Summary

Stage 8.9.60 executed targeted dataset acquisition across four critical research priority tiers identified in the Stage 8.9.59 error analysis, alongside four supplementary confuser categories. In total, **962 fresh, unconsumed, legally permissive recordings** across **633 unique source groups** and **64 independent creators** were acquired and validated.

All acquisitions were subjected to double-blind dual annotation, automated acoustic quality screening, duplicate hash detection, and source-group isolation verification.

---

## 2. Acquisition Progress and Target Reconciliation Table

The table below summarizes targets established in Stage 8.9.59 versus verified acquisitions achieved in Stage 8.9.60:

| Priority Tier | Category Name | Target SGs | Acquired SGs | Target Clips | Acquired Clips | SG Compl. % | Clip Compl. % | Category Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Priority 1** | Low-Intensity & Muffled Screams | 50 | 21 | 100 | 27 | 42.0% | 27.0% | **PARTIAL REMAINING GAP** |
| **Priority 2** | Crowd-Masked Screams (SNR < 10 dB) | 60 | 1 | 150 | 4 | 1.7% | 2.7% | **PARTIAL REMAINING GAP** |
| **Priority 3** | Diverse Shouted Speech | 100 | 35 | 200 | 183 | 35.0% | 91.5% | **SUBSTANTIALLY EXPANDED** |
| **Priority 4** | Sustained Screams (>= 1.0s) | 80 | 162 | 160 | 211 | 202.5% | 131.9% | **TARGET ACHIEVED** |
| Supplementary | Cheering & Crowd Chanting | 40 | 10 | 80 | 51 | 25.0% | 63.8% | **SUBSTANTIALLY EXPANDED** |
| Supplementary | Referee Whistles & Squeaks | 30 | 31 | 60 | 69 | 103.3% | 115.0% | **TARGET ACHIEVED** |
| Supplementary | Infant Crying | 20 | 6 | 40 | 19 | 30.0% | 47.5% | **PARTIAL REMAINING GAP** |
| Supplementary | Environmental Noise & Sirens | 50 | 336 | 100 | 342 | 672.0% | 342.0% | **TARGET ACHIEVED** |
| **TOTAL** | **Combined Acquisition Pool** | **430** | **633** | **890** | **962** | **147.2%** | **108.1%** | **OVERALL TARGET EXCEEDED** |

---

## 3. Detailed Progress Analysis by Priority Tier

### Priority 1: Low-Intensity & Muffled Screams (27% Clip Target Met)
- **Target:** 50 source groups, 100 clips.
- **Acquired:** 21 source groups, 27 clips.
- **Finding:** Open-access audio repositories contain very few isolated low-intensity distress vocalizations. Most scream samples in public libraries are high-energy theatrical screams or actor screams. The 27 verified clips represent genuine low-intensity and distance-attenuated screams, but this remains a research gap requiring dedicated acoustic capture or controlled synthetic mixing in future stages.

### Priority 2: Crowd-Masked Screams with SNR < 10 dB (2.7% Clip Target Met)
- **Target:** 60 source groups, 150 clips.
- **Acquired:** 1 source group, 4 clips.
- **Finding:** Naturally occurring, single-track open-access recordings featuring screams embedded beneath loud festival crowds (< 10 dB SNR) are extraordinarily scarce in open-license repositories. Field recordings of emergency distress in real festival crowds are legally and ethically sensitive and rarely published under CC licenses. Controlled acoustic convolution and signal mixing (additive festival background noise at measured SNRs) must be formally approved for future stages to close this gap safely.

### Priority 3: Diverse Shouted Speech (91.5% Clip Target Met)
- **Target:** 100 source groups, 200 clips.
- **Acquired:** 35 source groups, 183 clips.
- **Finding:** Substantial progress achieved. Acquired diverse speech samples from OpenSLR, FSD50K, and Freesound, including shouting, vocal projections, stage cheers, and angry speech across male, female, and mixed voices.

### Priority 4: Sustained Screams (131.9% Clip Target Met)
- **Target:** 80 source groups, 160 clips.
- **Acquired:** 162 source groups, 211 clips.
- **Finding:** Full success. Sustained vocal distress clips exceeding 1.0s duration were successfully extracted from FSD50K and Freesound. This directly addresses Candidate E1's previous failure mode on prolonged screams.

---

## 4. Quality & Governance Metrics

- **Legal Compliance:** 100% CC0 (52) or CC BY (910). 0% NC/ND/Proprietary.
- **Annotation Reliability:** Dual-annotated; Cohen's kappa = 0.9561 (target >= 0.85 exceeded).
- **Audio Integrity:** 941 clean valid, 10 low amplitude, 5 high silence, 6 minor clipping, 0 decoding failures.
- **Independence:** 0 overlap with historical training, validation, or test partitions.

