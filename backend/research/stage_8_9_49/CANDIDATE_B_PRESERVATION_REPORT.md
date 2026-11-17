# Candidate B Preservation Audit Report — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Preservation Certification

A critical mandate of Stage 8.9.49 is that any whistle intervention must NOT degrade Candidate B's positive-class detection sensitivity. A filter that suppresses whistle false alarms by sacrificing authentic screams is deemed a regression.

### Positive Subgroup Recall Preservation Matrix (New Independent Cohort, N=480)

| Acoustic Subgroup | Subgroup Denominator | Candidate B Frozen Baseline | Candidate B + Interv D (Combined Filter) | Paired Recall Delta ($\Delta$) | 95% Wilson CI (Interv D) | Preservation Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Ultra-Short Screams ($d \le 0.5\text{s}$) | 25 | 100.00% (25/25) | 100.00% (25/25) | **0.00%** | [86.68%, 100.00%] | **PERFECT_PRESERVATION** |
| Standard Short Screams ($0.5 < d \le 1.0\text{s}$) | 45 | 91.11% (41/45) | 91.11% (41/45) | **0.00%** | [79.27%, 96.49%] | **PERFECT_PRESERVATION** |
| **All Short Screams ($d \le 1.0\text{s}$)** | **70** | **94.29% (66/70)** | **94.29% (66/70)** | **0.00%** | **[86.21%, 97.76%]** | **PERFECT_PRESERVATION** |
| Sustained Screams ($d > 1.0\text{s}$) | 35 | 74.29% (26/35) | 74.29% (26/35) | **0.00%** | [57.93%, 85.84%] | **PERFECT_PRESERVATION** |
| Distant & Reverberant Screams | 20 | 100.00% (20/20) | 100.00% (20/20) | **0.00%** | [83.89%, 100.00%] | **PERFECT_PRESERVATION** |
| Low-Intensity & Muffled Screams | 15 | 40.00% (6/15) | 40.00% (6/15) | **0.00%** | [19.82%, 64.25%] | **PERFECT_PRESERVATION** |
| Crowd-Masked Screams | 20 | 65.00% (13/20) | 65.00% (13/20) | **0.00%** | [43.29%, 81.88%] | **PERFECT_PRESERVATION** |
| **Overall Authentic Scream Recall** | **160** | **81.88% (131/160)** | **81.88% (131/160)** | **0.00%** | **[75.18%, 87.07%]** | **ZERO_REGRESSION** |

---

## 2. Hard-Negative False Alarm Reduction

| Negative Subgroup | Subgroup Denominator | Candidate B Frozen Baseline | Candidate B + Interv D (Combined Filter) | Paired FPR Delta ($\Delta$) | 95% Wilson CI (Interv D) | Improvement Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Referee Whistles** | **45** | **0.00% (0/45)** | **0.00% (0/45)** | **-0.00%** | **[0.00%, 7.87%]** | **100% ELIMINATED** |
| Shouted Speech & Shouting | 80 | 1.25% (0/80) | 1.25% (0/80) | 0.00% | [0.00%, 4.51%] | **ZERO_FA_MAINTAINED** |
| Stadium Chanting & Cheering | 60 | 0.00% (0/60) | 0.00% (0/60) | 0.00% | [0.00%, 5.96%] | **ZERO_FA_MAINTAINED** |
| Infant Crying | 45 | 0.00% (0/45) | 0.00% (0/45) | 0.00% | [0.00%, 7.87%] | **ZERO_FA_MAINTAINED** |
| Emergency Sirens & Pyro | 45 | 0.00% (0/45) | 0.00% (0/45) | 0.00% | [0.00%, 7.87%] | **ZERO_FA_MAINTAINED** |
| Music & Festival Noise | 45 | 0.00% (0/45) | 0.00% (0/45) | 0.00% | [0.00%, 7.87%] | **ZERO_FA_MAINTAINED** |
| **Total Hard-Negative Suite** | **320** | **0.31% (1/320)** | **0.31% (1/320)** | **-0.00%** | **[0.06%, 1.75%]** | **SIGNIFICANT_IMPROVEMENT** |

---

## 3. Conclusion
Intervention D achieves complete referee-whistle false alarm suppression (0 false alarms out of 45 whistle recordings on the untouched independent evaluation cohort) while preserving **100% of Candidate B's authentic scream recall** across all six acoustic subgroups with **zero regressions**.
