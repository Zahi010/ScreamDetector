# Limitations & Open Issues — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

This document catalogs the remaining technical limitations, empirical deficits, and open research challenges identified during the final audit closure of Stage 8.9.56 and Stage 8.9.56.1.

In accordance with strict research governance, these limitations are formally documented to guide subsequent authorized research phases without compromising the frozen status of historical evaluations or production baselines.

---

## 2. Technical & Computational Limitations

### 2.1 Subband Filterbank Computational Bottleneck
- **Observed Overhead:** Candidate E1's 11-d Subband Filterbank synthesis consumes **~34 ms (P50)** and **~39-48 ms (P95)** per 1.0-second audio window, accounting for **~85-88%** of total downstream pipeline execution time.
- **Root Cause:** Pure Python / SciPy execution of 6 fourth-order Butterworth bandpass IIR filters using forward-backward zero-phase filtering (`scipy.signal.filtfilt`) followed by temporal frame variance calculations across 98 overlapping frames.
- **Gate 5 Impact:** While Candidate E1 easily passes the original pre-registered model-only Gate 5 ($0.707\text{ ms} \ll 25.0\text{ ms}$), it fails the supplementary complete-pipeline threshold ($46.066\text{ ms} > 25.0\text{ ms}$).
- **Streaming Viability:** Because operational audio window hopping occurs at 975 ms intervals, 46-57 ms execution consumes only $\approx 5.8\%$ of the real-time buffer budget ($\text{RTF} \approx 0.058$). However, edge multi-stream scaling beyond 8 concurrent channels will require DSP acceleration.

### 2.2 Low-Intensity Distress Acoustic Vulnerability
- **Empirical Recall:** On the frozen cohort's authentic low-intensity distress vocalizations, Candidate E1 achieved only **18.18% recall (2 / 11)**, and Candidate B achieved **0.00% recall (0 / 11)**.
- **Acoustic Cause:** Low-SNR screams masked by high-amplitude ambient sound lack distinct formant peaks in standard filterbank representations, falling below classification thresholds.
- **Implication:** Distant or obstructed distress vocalizations represent an unresolved acoustic modeling challenge.

---

## 3. Dataset & Subgroup Gaps

### 3.1 Insufficient Evidence: Mechanically Modulated Whistles ($N=0$)
- The Stage 8.9.55 cohort contains zero isolated referee whistles.
- Consequently, the whistle rejection capability of Candidate B + Intervention D cannot be confirmed on this cohort.
- Status: **INSUFFICIENT EVIDENCE ($N=0$)**. No synthetic recordings may be generated to simulate this subgroup.

### 3.2 Insufficient Evidence: Ultra-Short Distress Vocalizations ($N=0$)
- While short screams between 0.5s and 1.0s are represented ($N=36$), no authentic screams with duration $\le 0.5$ seconds exist in the manifest.
- Status: **INSUFFICIENT EVIDENCE ($N=0$)**.

### 3.3 Consumed Evaluation Cohort Immutability
- The 450 recordings in the Stage 8.9.55 manifest have been fully exposed and inspected across Stages 8.9.55, 8.9.56, and 8.9.56.1.
- Under strict scientific protocol, **this cohort is permanently consumed and retired**.
- It must never be utilized for retraining, hyperparameter optimization, DSP calibration, or threshold tuning.

---

## 4. Acceptance Gate Reality & Prohibition of Production Promotion

| Gate | Target Bound | Candidate E1 | Candidate B | Operational Reality |
|---|---|---|---|---|
| **Gate 1: Overall Recall** | $\ge 96.0\%$ | 72.67% (FAIL) | 55.33% (FAIL) | Substantial deficit (-23.33% for E1) |
| **Gate 2: Hard-Negative FPR** | $\le 5.0\%$ | 6.33% (FAIL) | 6.67% (FAIL) | Above target (+1.33% for E1) |
| **Gate 4: Short-Scream Recall** | $\ge 90.0\%$ | 83.33% (FAIL) | 66.67% (FAIL) | Below target (-6.67% for E1) |
| **Gate 5b: Full-Pipeline Latency** | $\le 25.0\text{ ms}$ | 46.07 ms (FAIL) | 7.54 ms (PASS) | Exceeds target by 21.07 ms for E1 |

**CRITICAL DIRECTIVE:** Neither Candidate E1 nor Candidate B satisfies the research acceptance gates. Under no circumstances may either model be promoted to production or deployed for life-safety or emergency alerting.

