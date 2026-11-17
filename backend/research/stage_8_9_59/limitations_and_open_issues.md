# Limitations and Open Issues — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

This report documents all known open issues, methodological constraints, and acoustic limitations identified during Stage 8.9.59.

---

## 2. Identified Acoustic & System Limitations

### 2.1 Low-Intensity & Distant Scream Deficit
- **Limitation:** Candidate E1's recall drops sharply on subdued, muffled, or distant screams.
- **Root Cause:** Across the entire 1,732-recording expansion corpus, only 10 clips from 7 source groups represent low-intensity screams, with 0 in the validation partition. The detector has not been trained on low-SNR vocalizations captured at long physical distances (>20 meters).

### 2.2 Temporal Averaging Dilution on Sustained Screams
- **Limitation:** Sustained screams ($\ge 1.0$s) achieve only 76.67% recall (14 false negatives), compared to 94.87% on short screams.
- **Root Cause:** The feature extraction pipeline averages acoustic statistics over the entire recording window. In longer clips, the scream attack (e.g. 0.6s) is followed by several seconds of lower-energy vocal decay, which mathematically depresses window-averaged energy ratios and spectral centroids.

### 2.3 Shouted-Speech Clustering in Two Sessions
- **Limitation:** 10 false positives were observed out of 88 shouted speech clips (11.36% FPR).
- **Root Cause:** 9 of the 10 false alarms (90%) are concentrated in just two specific uploader sessions (`reitanna` Session 3439 and `ericsueiro` Session 2208), where actors produced theatrical shouting with extreme vocal fry and preamplifier soft clipping. The remaining 35 independent shouting source groups generated only 1 false positive across 79 clips (1.27% FPR).

### 2.4 Uploader / Creator Overlap Across Existing Partitions
- **Limitation:** While direct `source_group_id` and parent recording excerpt overlap was strictly zero, 7 creators overlap between Train and Val, and 10 creators overlap between Train and Test.
- **Root Cause:** Splitting was performed using `source_group_id` without grouping higher-level online account / uploader IDs.
- **Resolution:** All future evaluation cohort designs must enforce hierarchical clustering at the creator/uploader level.

### 2.5 Prohibition on Life-Safety Use
- **Limitation:** Under no circumstances may Candidate E1, Candidate B, C5 DSP, or any research prototype be deployed in live life-safety, emergency alerting, or autonomous dispatch environments.

