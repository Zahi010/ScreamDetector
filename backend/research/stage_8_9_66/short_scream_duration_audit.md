# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# SHORT-SCREAM DURATION BAND AUDIT REPORT
**Acoustic Sensitivity and Recall Stability Across Sub-Second Duration Strata**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Duration Band Taxonomy
Historically, single-resolution models (Candidate E1) failed on screams shorter than 0.75s due to temporal averaging over 1,000 ms sliding windows.
To verify that the dual-resolution architecture eliminates this failure mode, the 401 screams were stratified into two critical duration bands:
1. **Ultra-Short Screams ($\le 0.500$s):** 119 recordings (minimum duration: 0.224s).
2. **Short Screams (0.501s to 1.000s):** 282 recordings.

---

## 3. Stratified Recall Across Duration Bands

| Duration Band | Duration Range | Total Clips | Candidate 65-F Detections | Recall (%) | Gate 4 Requirement ($\ge 90\%$) |
|---|---|---|---|---|---|
| **Ultra-Short** | 0.224s – 0.500s | 119 | 118 | **99.16%** | **PASS (+8.41% margin)** |
| **Standard Short** | 0.501s – 0.999s | 282 | 269 | **95.39%** | **PASS (+5.64% margin)** |
| **Combined Short Cohort** | 0.224s – 0.999s | 401 | 387 | **96.51%** | **PASS (+6.51% margin)** |

---

## 4. Acoustic Mechanism Behind Ultra-Short Robustness
In ultra-short events ($\le 0.50$s), the 250 ms short branch captures virtually the entire acoustic envelope of the scream.
Tiling this 250 ms slice 4 times reconstructs a quasi-stationary 16,000-sample buffer where C5 DSP subband filters and phonation statistics operate at peak SNR without background noise dilution.
Furthermore, Candidate 65-F's high-confidence bypass ($p \ge 0.80$) and branch agreement check prevent downstream filters from attenuating these sudden vocal transients.
