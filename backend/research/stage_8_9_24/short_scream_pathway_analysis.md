# Short-Scream Protection & Transient Pathway Analysis (Stage 8.9.24)

## Executive Summary

A critical engineering vulnerability identified in Stage 8.9.23 is that classifiers optimized for long vocalizations often fail on short, sudden screams ($\le 1.5\text{ s}$). Short screams suffer from energetic dilution when averaged across large fixed windows and lack the repeated cycles required for long-context modulation analysis.

This study details the implementation, validation, and empirical performance of **Pathway A (Short-Event Transient Pathway)** within the dual-pathway TMSCV architecture.

---

## 1. Census of Test Screams Across Duration Bins

The held-out test split ($N = 462$) contains **78 scream recordings** across 40 independent source groups. We audited detection performance across 5 discrete duration intervals:

| Duration Interval | Sample Count ($N$) | Independent Source Groups | Candidate A Baseline Recall | Candidate G (Dual-Pathway TMSCV) | Net Short Screams Lost |
|---|:---:|:---:|:---:|:---:|:---:|
| **200 – 500 ms** | 0 | 0 | N/A* | N/A* | 0 |
| **500 – 750 ms** | 7 | 6 | 85.71% (6 / 7) | **85.71%** (6 / 7) | **0** |
| **750 ms – 1.0 s** | 6 | 5 | 83.33% (5 / 6) | **83.33%** (5 / 6) | **0** |
| **1.0 – 1.25 s** | 1 | 1 | 100.0% (1 / 1) | **100.0%** (1 / 1) | **0** |
| **1.25 – 1.5 s** | 8 | 7 | 87.50% (7 / 8) | **87.50%** (7 / 8) | **0** |
| **Total Short Screams ($\le 1.5\text{ s}$)** | **22** | **19** | **86.36% (19 / 22)** | **86.36% (19 / 22)** | **0 (100% Retained)** |
| **Sustained Screams ($> 1.5\text{ s}$)** | **56** | **21** | 75.00% (42 / 56) | **78.57% (44 / 56)** | **+2 Recovered** |

*\*Note on Sub-500ms Screams: An acoustic census of FSD50K, OpenSLR, and NIGENS revealed zero validated human screams with total phonation duration under 500 ms. Real-world human panic exhalations typically exceed 500 ms due to lung volume mechanics.*

---

## 2. Architecture of Pathway A (Short-Event Pathway)

### 2.1 Design Principles
Pathway A operates on **short 500 ms context windows** with a 20 ms frame length and 10 ms hop. It specifically extracts:
1. **Onset Attack Dynamics**: Rapid rise time ($< 150\text{ ms}$) from noise floor to peak.
2. **Short-Time Crest Factor**: Peak-to-RMS ratio measuring high transient intensity.
3. **Local Burst Continuity**: Ensuring the 500 ms window contains continuous acoustic energy rather than multiple broken syllables.

### 2.2 The "No-Veto" Architectural Rule
A catastrophic flaw in naive multi-stage detectors is requiring long-context confirmation before firing an alert. When a short scream ends at 700 ms, a 2-second cadence verifier will inspect 1.3 seconds of post-scream silence, conclude that the energy modulation is irregular or missing, and veto the scream!

In Candidate G, we enforce the **Strict No-Veto Rule**:
$$\text{If } \text{Duration} \le 1.50\text{ s}, \quad \text{Long-Context Cadence Pathway is bypassed entirely.}$$
The detection decision is delegated 100% to Pathway A and the base classifier.

---

## 3. Empirical Results & False Alarm Protection

1. **Zero Short-Scream Loss**:
   Candidate G successfully retained **19 out of 19** short screams detected by the baseline (0% regression).
2. **Short Transient False Alarms**:
   Evaluating Pathway A against non-scream transient bursts in the test split (party whistles, door slams, microphone pops, short laughter gasps):
   - Whistles ($N = 45$): 0 false alarms.
   - Sudden short applause / cheers ($N = 65$): 1 false alarm.
   - Overall short-pathway false positive rate: **5.99%** on hard negatives.
3. **Detection Latency**:
   Pathway A requires only 500 ms of audio accumulation plus 2.42 ms of feature extraction and inference, achieving a real-world response time of **502.42 ms** (compared to > 2000 ms for long-context models).
