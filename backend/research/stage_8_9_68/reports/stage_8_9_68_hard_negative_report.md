# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
# Stage 8.9.68 — Hard-Negative Rejection & Multi-Class Specificity Report

**Stage:** 8.9.68 — SNR-Adaptive Roughness Calibration, Recall Recovery & Multi-Class Generalization  
**Cohort Evaluated:** Stage 54 Validation Cohort — Non-Shouting Hard Negatives ($N=124$, 66 Source Groups)  
**Target Criterion:** Acceptance Gate 2 (Hard-Negative FPR $\le 5.0\%$)  
**Safety Notice:** Experimental acoustic prototype. Not certified for life-safety alerting, emergency dispatch, or security response.

---

## 1. Executive Summary

Hard-negative audio classes—including crowd cheering, synthesizer sweeps, referee whistles, baby crying, and festival sound effects—frequently possess high acoustic energy in the 1–4 kHz frequency bands that trigger false alarms in simplistic scream detectors. In Stage 8.9.66, Candidate 65-F failed catastrophically with a **59.68% Hard-Negative FPR (74/124)**.

Stage 8.9.67 reduced this to 8.87% (11/124). In Stage 8.9.68, Candidate 68-D achieves a new project record low of **7.26% Hard-Negative FPR (9/124)**, an 18.2% relative false alarm reduction over Candidate 67-D.

While this represents substantial architectural progress, Gate 2 requires an FPR of $\le 5.0\%$ ($\le 6$ false alarms out of 124). Consequently, Candidate 68-D **FAILS Gate 2**.

---

## 2. Multi-Candidate Historical Trajectory

| Model Candidate | Operating Threshold | Hard-Negative FPs | Hard-Negative TNs | Hard-Negative FPR | Gate 2 Target | Gate 2 Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate 65-F** | 0.4800 | 74 | 50 | 59.68% | $\le 5.0\%$ | **CATASTROPHIC FAIL** |
| **Candidate 67-D** | 0.5200 | 11 | 113 | 8.87% | $\le 5.0\%$ | **FAIL (Significant Improvement)** |
| **Candidate 68-A (No Veto)** | 0.5200 | 12 | 112 | 9.68% | $\le 5.0\%$ | **FAIL** |
| **Candidate 68-B (Roughness Only)** | 0.5200 | 6 | 118 | 4.84% | $\le 5.0\%$ | **PASS (Destroys Recall: 37%)** |
| **Candidate 68-D (Champion)** | **0.4900** | **9** | **115** | **7.26%** | $\le 5.0\%$ | **FAIL (Best in Project History)** |

---

## 3. Subcategory Breakdown of Hard Negatives ($N=124$)

Candidate 68-D's performance across the 5 non-shouting hard negative categories:

| Target Category | Total Clips ($N=124$) | Candidate 65-F FPs | Candidate 67-D FPs | Candidate 68-D FPs | Candidate 68-D Category FPR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Crowd Chants & Cheering** | 37 | 24 (64.9%) | 4 (10.8%) | 3 (8.1%) | **8.11%** |
| **General Environmental Noise** | 36 | 19 (52.8%) | 5 (13.9%) | 4 (11.1%) | **11.11%** |
| **Whistles & Squeaks** | 22 | 16 (72.7%) | 0 (0.0%) | 0 (0.0%) | **0.00% (Perfect Rejection)** |
| **Infant Crying** | 20 | 11 (55.0%) | 2 (10.0%) | 2 (10.0%) | **10.00%** |
| **Sirens, Fireworks & SFX** | 9 | 4 (44.4%) | 0 (0.0%) | 0 (0.0%) | **0.00% (Perfect Rejection)** |
| **Total Cohort** | **124** | **74 (59.7%)** | **11 (8.87%)** | **9 (7.26%)** | **7.26%** |

---

## 4. Acoustic Breakdown of Residual 9 False Positives

The 9 residual false positives under Candidate 68-D were audited recording-by-recording:

1. **Crowd Cheering / Chants (3 FPs):**
   - High-energy stadium roar with harmonic whistling (`crowd_screaming_stadium_02`). The collective unison roar contains non-linear acoustic turbulence that mimics distress acoustics.
2. **General Environmental (4 FPs):**
   - Metal scraping and industrial machinery squeal (`fs_369001`, `fsd50k_194821`). High frequency friction with erratic modulation generates flux and roughness above the veto thresholds.
3. **Infant Crying (2 FPs):**
   - High-distress baby wailing (`infant_colic_scream_04`). Severe colic cries possess genuine non-linear vocal fold desynchronization that biologically overlaps with adult panic screams.

---

## 5. Summary & Gap to Gate 2 Compliance

To achieve Gate 2 ($\le 5.0\%$, $\le 6$ false alarms), exactly 3 additional false positives must be eliminated:
- Discriminating infant colic cries from adult screams will require fundamental frequency ($F_0$) envelope tracking ($F_0 > 500\text{ Hz}$ sustained glide) or age-specific vocal tract length modeling ($VTL$).
- Machinery squeals can be suppressed with harmonic comb filtering.

---

## 6. Artifact Links

- Predictions CSV: [candidate_68_val_predictions.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/candidate_68_val_predictions.csv)
- Scorecard Report: [stage_8_9_68_five_gate_scorecard.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_five_gate_scorecard.md)
- Shouted Speech Report: [stage_8_9_68_shouted_speech_report.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_68/reports/stage_8_9_68_shouted_speech_report.md)

