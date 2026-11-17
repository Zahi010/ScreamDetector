# Dataset Coverage Matrix & Evidence Sufficiency Report — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase F of Stage 8.9.59, a dataset coverage audit was executed across all 11 primary positive and negative acoustic categories in the Stage 8.9.54 expansion corpus ($N=1,732$).

The audit evaluates whether the available evidence base is sufficient to support robust generalization claims or if critical gaps exist that require targeted legal acquisition.

---

## 2. Comprehensive Acoustic Coverage Matrix

| Acoustic Category | Class Type | Total Clips ($N$) | Unique Source Groups | Unique Parents | Train Clips | Val Clips | Test Clips | Duration (Mean) | Commercially Eligible % | Target Min SGs | Evidence Sufficiency Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Short Screams (<1.0s)** | Positive | 224 | 148 | 182 | 142 | 39 | 43 | 0.62s | 100.0% | 50 | **SUFFICIENT FOR EXPLORATORY** |
| └── *Ultra-Short (<0.5s)* | Positive | 48 | 32 | 44 | 26 | 15 | 7 | 0.38s | 100.0% | 30 | **SUFFICIENT FOR EXPLORATORY** |
| **Sustained Screams ($\ge 1.0$s)** | Positive | 380 | 133 | 312 | 261 | 60 | 59 | 2.45s | 100.0% | 80 | **SUFFICIENT FOR EXPLORATORY** |
| **Crowd-Masked / Distant Screams**| Positive | 52 | 26 | 48 | 21 | 19 | 12 | 2.10s | 100.0% | 50 | **UNDERREPRESENTED** |
| **Low-Intensity / Muffled Screams**| Positive | **10** | **7** | **10** | **7** | **0** | **3** | **1.18s** | **100.0%** | **40** | **CRITICALLY INSUFFICIENT** |
| **Shouted Speech** | Negative | 432 | 174 | 380 | 258 | 88 | 86 | 2.85s | 100.0% | 80 | **SUFFICIENT FOR EXPLORATORY** |
| **Cheering & Crowd Chanting** | Negative | 192 | 84 | 165 | 118 | 37 | 37 | 4.10s | 100.0% | 50 | **SUFFICIENT FOR EXPLORATORY** |
| **Referee Whistles & Squeaks** | Negative | 148 | 62 | 124 | 98 | 22 | 28 | 1.45s | 100.0% | 40 | **SUFFICIENT FOR EXPLORATORY** |
| **Infant Crying** | Negative | 94 | 41 | 82 | 52 | 20 | 22 | 3.20s | 100.0% | 30 | **SUFFICIENT FOR EXPLORATORY** |
| **Emergency Sirens & SFX** | Negative | 82 | 38 | 74 | 55 | 9 | 18 | 4.80s | 100.0% | 30 | **SUFFICIENT FOR EXPLORATORY** |
| **General Environmental Noise** | Negative | 180 | 72 | 156 | 104 | 36 | 40 | 12.40s | 100.0% | 50 | **SUFFICIENT FOR EXPLORATORY** |

---

## 3. Identification of Critical Dataset Gaps

### Gap 1: Low-Intensity and Muffled Screams (**CRITICALLY INSUFFICIENT**)
- Across all 1,732 recordings in the corpus, only **10 clips from 7 independent source groups** represent low-intensity or muffled vocalizations.
- In `expansion_val`, exactly **0 recordings** are explicitly tagged as low-intensity.
- **Implication:** The detector cannot be reliably validated on subdued or distant screams. This explains why Candidate E1 fails on distant screams in real-world environments.

### Gap 2: Crowd-Masked Screams (**UNDERREPRESENTED**)
- With only 26 independent source groups across the corpus and 19 in validation, the sample size is inadequate to establish statistically defensible 95% confidence intervals on noisy festival recall.

### Gap 3: Shouting Diversity Deficit
- Although 174 source groups exist in the shouting category, 90% of validation false alarms came from just 2 sessions (`reitanna` and `ericsueiro`). The dataset lacks high-effort shouting recordings from diverse real-world crowds, sporting fans, and outdoor festival attendees.

---

## 4. Preservation & Traceability

Full per-category metrics and source counts are saved in [`dataset_coverage_matrix.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/dataset_coverage_matrix.csv).

