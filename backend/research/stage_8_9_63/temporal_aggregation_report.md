# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — False-Positive-Controlled Temporal Aggregation Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Objective

In Stage 8.9.61 and Stage 8.9.62, rolling-window DSP improved sustained scream recall from $58.0\%$ to $70.0\%$, but caused a catastrophic surge in false positive rate (from $19.20\%$ to $35.40\%$, generating 81 additional false alarms on non-scream noise).

Stage 8.9.63 investigated event-level temporal aggregation mechanisms across streaming audio buffers ($50$ ms hop, $1000$ ms window) using [`scripts/run_temporal_aggregation_experiments.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/scripts/run_temporal_aggregation_experiments.py).

---

## 2. Comparative Evaluation Matrix

| Aggregation Method | Operational Logic | Sustained Recall ($N=62$) | Short Recall ($N=8$) | Overall Recall ($N=70$) | Hard-Neg FPR ($N=117$) | F1 Score | Mean Delay (ms) | Raw Triggers | Post Triggers | Duplicates Suppressed |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Any Window)** | Trigger if any 50ms window $\ge 0.50$ | **$98.39\%$** | $12.50\%$ | **$88.57\%$** | $64.96\%$ | $59.62\%$ | $137.3$ ms | 735 | 735 | 0 |
| **Method A (Consecutive $K=2$)**| Require 2 consecutive windows $\ge 0.50$ ($100$ms sustained) | $88.71\%$ | $0.00\%$ | $78.57\%$ | **$34.19\%$** | **$66.67\%$** | $187.4$ ms | 735 | 490 | **245** |
| **Method B (Bounded EMA)** | $\alpha = 0.30, \theta_{\text{ema}} = 0.45$ | $75.81\%$ | $0.00\%$ | $67.14\%$ | **$29.06\%$** | $62.25\%$ | $228.4$ ms | 735 | 592 | 143 |
| **Method C (Corroborated Peak)**| Peak $\ge 0.70$ OR ($2\times \ge 0.45$ in 200ms) | $96.77\%$ | $0.00\%$ | $85.71\%$ | $54.70\%$ | $61.86\%$ | $129.4$ ms | 735 | 701 | 34 |
| **Method D (Event Merging)** | Group contiguous active hops ($<200$ms gap) | $98.39\%$ | $12.50\%$ | $88.57\%$ | $64.96\%$ | $59.62\%$ | $137.3$ ms | 735 | **245** | **490** |
| **Method E (Refractory Holdoff)**| $500$ ms post-trigger lockout | $98.39\%$ | $12.50\%$ | $88.57\%$ | $64.96\%$ | $59.62\%$ | $137.3$ ms | 735 | **189** | **546** |

---

## 3. Key Technical Findings

1. **Method A (Consecutive Evidence $K=2$) Achieves Optimal Discrimination:**
   - Requiring 2 consecutive windows exceeding threshold reduces the recording-level FPR from **$64.96\%$ to $34.19\%$** (a massive **$-30.77\%$ reduction** in false positive files).
   - Sustained scream recall is preserved at **$88.71\%$**, yielding the highest overall F1 score (**$66.67\%$**).
   - Timing implication: Method A introduces an intentional, bounded detection delay of exactly one hop ($+50.0$ ms), bringing mean alert latency to $187.4$ ms, which remains well within safety guidelines.
2. **Method D & E Eliminate Duplicate Alert Storms:**
   - While Refractory Holdoff (Method E) does not change recording-level binary classification (because the first false alarm still fires), it suppresses **$74.3\%$ of repeat alarm spam** (reducing raw triggers from 735 to 189).
   - In deployment, Method E prevents sirens and alarms from generating dozens of repetitive event dispatches.
3. **The Short-Scream Vulnerability in Rolling Temporal Filters:**
   - Both Method A and Method B zero out short-scream recall ($0.00\%$) because transient screams ($< 0.3$s) fail to sustain energy across two consecutive 50 ms window hops.
   - This proves that **temporal aggregation alone cannot solve short-scream detection** and reinforces the necessity of the **Track D Dual-Resolution Architecture**, where the short branch processes transients before temporal aggregation is applied.

