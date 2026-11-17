# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recordings and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Temporal Aggregation Comparison Report: Development Cohort Analysis

## 1. Executive Summary

In Stage 8.9.61 Track A, five distinct temporal score aggregation strategies were evaluated on the 187 development recordings ($N=187$: 70 positive screams, 117 hard negatives, across 180 source groups). The goal was to establish how 500 ms rolling hops interact with temporal smoothing to solve Candidate E1's sustained scream decay without generating unacceptable false-positive inflation on continuous audio.

### Key Experimental Findings:
1. **Sustained Vocalization Gain:** Stepping a 1.0s window in 500 ms hops boosts sustained scream recall ($\ge 1.0$s duration) to **95.16% – 96.77%**, compared to 62.86% – 72.86% under static non-overlapping windowing.
2. **The Cumulative False Alarm Dilemma:** Under raw independent window decisions (Strategy A), false-negative suppression comes at the cost of cumulative false positives: on continuous multi-second negative recordings, FPR reaches **50.43%**.
3. **Persistence vs. Sensitivity Trade-off:** Requiring 2 consecutive positive hops (Strategy B) reduces FPR down to **28.21%**, but cuts overall recall from 85.71% to 68.57% by penalizing transient screams.
4. **Optimal Trade-off via Rolling EMA (Strategy D):** Exponential moving average aggregation ($\alpha = 0.50, \theta = 0.6000$) preserves **84.29% overall recall** (and **95.16% sustained recall**) while suppressing FPR to **37.61%**, achieving the highest overall development F1-score of **68.21%**.

---

## 2. Granular Comparative Results on Development Cohort

The table below summarizes performance across the 187 eligible development recordings:

| Strategy Designation | Aggregation Formula & Threshold | Overall Recall | Sustained Recall | Short Recall | Hard-Neg FPR | Precision | F1-Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Strategy A: Independent** | $p_t \ge 0.6800$ (Any window) | 85.71% (60/70) | 96.77% (60/62) | 0.00% (0/8) | 50.43% (59/117) | 50.42% | 63.49% |
| **Strategy B: Persistence** | $K=2$ consecutive $p \ge 0.6800$ | 68.57% (48/70) | 77.42% (48/62) | 0.00% (0/8) | 28.21% (33/117) | 59.26% | 63.58% |
| **Strategy C: Hysteresis** | $\theta_{high}=0.68, \theta_{low}=0.40$ | 85.71% (60/70) | 96.77% (60/62) | 0.00% (0/8) | 50.43% (59/117) | 50.42% | 63.49% |
| **Strategy D: Rolling EMA** | $\alpha=0.50, z_t \ge 0.6000$ | **84.29% (59/70)** | **95.16% (59/62)** | **0.00% (0/8)** | **37.61% (44/117)** | **57.28%** | **68.21%** |
| **Strategy E: Max Window** | $W=2, \max(p) \ge 0.6800$ | 85.71% (60/70) | 96.77% (60/62) | 0.00% (0/8) | 50.43% (59/117) | 50.42% | 63.49% |
| *Baseline Static Center* | Single 1.0s window, $\theta=0.68$ | 62.86% (44/70) | 67.74% (42/62) | 25.00% (2/8) | 14.53% (17/117) | 72.13% | 67.18% |

---

## 3. In-Depth Mechanism Analysis

### Why Strategy D (EMA) Outperforms Strategy A & B:
- In Strategy A, a single aberrant 500 ms frame containing an acoustic transient (e.g. mic bump or sudden shout onset) immediately produces a false positive for the entire recording.
- In Strategy D, $z_t = 0.50 p_t + 0.50 z_{t-1}$. An isolated transient spike ($p_t = 0.72$, $z_{t-1} = 0.05$) yields $z_t = 0.385$, safely below the 0.6000 threshold.
- Conversely, sustained screams produce multiple consecutive elevated windows ($p_{t-1}=0.85, p_t=0.88$), quickly driving $z_t \approx 0.865$, reliably crossing the 0.6000 alert threshold.

---

## 4. Conclusion and Freeze Recommendation

Based on these empirical findings, **Strategy D (Rolling EMA, $\alpha=0.50, \theta=0.6000$)** was selected as the frozen configuration for Track B independent evaluation. All recording-level development predictions are preserved in `backend/research/stage_8_9_61/rolling_window_development_predictions.csv`.

