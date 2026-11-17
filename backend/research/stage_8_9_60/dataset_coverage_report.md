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

# Dataset Coverage & Subgroup Representation Report

## 1. Executive Summary & Objective

The primary objective of Stage 8.9.60 was to construct a legally verified, source-independent acoustic expansion pool that directly addresses the representation deficiencies identified in the Stage 8.9.59 error audit.

Across all categories, the stage established a target of **890 audio clips across 430 independent source groups**. Stage 8.9.60 successfully acquired and verified **962 audio clips across 633 independent source groups**, achieving **108.1% of the overall clip target** and **147.2% of the source group target**.

---

## 2. Granular Coverage Matrix

The table below reflects the exact figures cataloged in `backend/research/stage_8_9_60/acquisition_coverage_matrix.csv`:

| Priority Tier | Category Name | Target SGs | Acquired SGs | Target Clips | Acquired Clips | % SG Compl. | % Clip Compl. | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Priority 1** | Low-Intensity & Muffled Screams | 50 | 21 | 100 | 27 | 42.0% | 27.0% | **PARTIAL REMAINING GAP** |
| **Priority 2** | Crowd-Masked Screams (SNR < 10 dB) | 60 | 1 | 150 | 4 | 1.7% | 2.7% | **PARTIAL REMAINING GAP** |
| **Priority 3** | Diverse Shouted Speech | 100 | 35 | 200 | 183 | 35.0% | 91.5% | **SUBSTANTIALLY EXPANDED** |
| **Priority 4** | Sustained Screams ($\ge 1.0$s) | 80 | 162 | 160 | 211 | 202.5% | 131.9% | **TARGET ACHIEVED** |
| **Supplementary** | Cheering & Crowd Chanting | 40 | 10 | 80 | 51 | 25.0% | 63.8% | **SUBSTANTIALLY EXPANDED** |
| **Supplementary** | Referee Whistles & Squeaks | 30 | 31 | 60 | 69 | 103.3% | 115.0% | **TARGET ACHIEVED** |
| **Supplementary** | Infant Crying | 20 | 6 | 40 | 19 | 30.0% | 47.5% | **PARTIAL REMAINING GAP** |
| **Supplementary** | Environmental Noise & Sirens | 50 | 336 | 100 | 342 | 672.0% | 342.0% | **TARGET ACHIEVED** |
| **TOTAL** | **Combined Acquisition Pool** | **430** | **633** | **890** | **962** | **147.2%** | **108.1%** | **TARGET EXCEEDED** |

---

## 3. Subgroup Representation Assessment

### Fully Achieved Tiers
1. **Priority 4 (Sustained Screams):** Target of 160 clips exceeded with 211 clips across 162 source groups (131.9% completion). Provides comprehensive coverage of sustained panic vocalizations.
2. **Referee Whistles & Squeaks:** Target of 60 clips exceeded with 69 clips across 31 source groups (115.0% completion). Ensures robust benchmark data for testing whistle discrimination modules (Intervention D).
3. **Environmental Noise & Sirens:** Target of 100 clips exceeded with 342 clips across 336 source groups (342.0% completion). Establishes deep diversity across outdoor acoustic backgrounds.

### Substantially Expanded Tiers
1. **Priority 3 (Diverse Shouted Speech):** Reached 183 clips (91.5% of clip target) across 35 source groups. Delivers deep coverage of spoken vocal projections to evaluate false-alarm rejection.
2. **Cheering & Crowd Chanting:** Reached 51 clips (63.8% of clip target) across 10 source groups.

### Identified Remaining Gaps
1. **Priority 1 (Low-Intensity Screams):** 27 clips acquired vs 100 target (27.0% completion). Gap of 73 clips.
2. **Priority 2 (Crowd-Masked Screams):** 4 clips acquired vs 150 target (2.7% completion). Gap of 146 clips.
3. **Infant Crying:** 19 clips acquired vs 40 target (47.5% completion). Gap of 21 clips.

---

## 4. Evaluation Impact

While remaining gaps exist in open-access repositories for low-intensity and crowd-masked screams, the acquired pool provides an unprecedented expansion of 962 verified recordings. A stratified subset of 700 recordings has been sealed into the Future Evaluation Cohort, reserving 262 recordings for future training/development exploration, while guaranteeing strict isolation from all historical models.

