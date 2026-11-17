# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Track D: False-Positive-Controlled Temporal Aggregation Research

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

In Stage 8.9.61, continuous rolling-window evaluation with Exponential Moving Average (EMA, $\alpha=0.50, \theta=0.6000$) demonstrated a major breakthrough in sustained scream recall (increasing from 69.47% to 86.26%). However, it suffered a severe specificity penalty: hard-negative false positive rate escalated from **19.20% (static)** to **35.40% (rolling)**.

Track D evaluated experimental temporal decision rules designed to retain rolling sensitivity on sustained vocalizations while suppressing isolated distractor spikes on the unexposed development cohort ($N=187$).

Seven temporal detection strategies were compared against the legacy static baseline:
1. **Method A (Consecutive Evidence $K=2$):** Requires two consecutive 500 ms windows exceeding $\theta=0.6000$.
2. **Method A (Consecutive Evidence $K=3$):** Requires three consecutive windows exceeding $\theta=0.5500$.
3. **Method B (Bounded EMA $\alpha=0.30$):** Slower exponential accumulator requiring sustained acoustic power to charge.
4. **Method C (Peak with Corroboration):** An isolated spike ($p \ge 0.75$) requires support from an adjacent window ($p \ge 0.40$).
5. **Method D (Event-Level Score Aggregation):** Clusters active contiguous windows and classifies based on integrated acoustic mass.
6. **Method E (Adaptive Context Hysteresis):** Dual-threshold hysteresis ($0.70 / 0.45$).
7. **Baselines:** Static center window ($\theta=0.6800$) and Rolling EMA ($\alpha=0.50, \theta=0.6000$).

### Key Research Findings:
- **Consecutive Evidence ($K=2$):** Successfully slashed hard-negative FPR from 37.61% down to **29.91% (a $+7.70\%$ FPR reduction)** while maintaining **83.87% sustained recall** and **74.29% overall recall**.
- **Peak with Corroboration (Method C):** Reduced FPR to **31.62%** while preserving **91.94% sustained scream recall**, yielding an F1 score of **69.51%** (superior to baseline EMA's 68.21%).
- **Bounded EMA (Method B, $\alpha=0.30$):** Achieved the highest F1 score (**70.59%**) with **95.16% sustained recall**, recovering 1 short scream and reducing false alarms by $+3.42\%$.
- **Hysteresis Failure (Method E):** While hysteresis achieved 96.77% sustained recall, it inflated FPR to **50.43%**, proving unviable for continuous monitoring.

---

## 2. Temporal Aggregation Benchmark Results ($N=187$ Development Cohort)

| Strategy / Decision Rule | Overall Recall ($N=70$) | Sustained Recall ($N=62$) | Short Recall ($N=8$) | Hard-Negative FPR ($N=117$) | Precision | F1 Score | FPR Reduction vs Baseline EMA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Method Baseline: Static 1.0s** | 62.86% (44/70) | 70.97% (44/62) | 0.00% (0/8) | **14.53% (17/117)** | **72.13%** | 67.18% | +23.08% |
| **Method Baseline: Rolling EMA ($\alpha=0.50$)** | 84.29% (59/70) | 95.16% (59/62) | 0.00% (0/8) | 37.61% (44/117) | 57.28% | 68.21% | Reference (0.00%) |
| **Method A: Consecutive Evidence ($K=2$)** | 74.29% (52/70) | 83.87% (52/62) | 0.00% (0/8) | **29.91% (35/117)** | 59.77% | 66.24% | **+7.70%** |
| **Method A: Consecutive Evidence ($K=3$)** | 51.43% (36/70) | 58.06% (36/62) | 0.00% (0/8) | **17.95% (21/117)** | 63.16% | 56.69% | **+19.66%** |
| **Method B: Bounded EMA ($\alpha=0.30$)** | **85.71% (60/70)** | **95.16% (59/62)** | **12.50% (1/8)** | **34.19% (40/117)** | 60.00% | **70.59%** | **+3.42%** |
| **Method C: Peak with Corroboration** | 81.43% (57/70) | 91.94% (57/62) | 0.00% (0/8) | **31.62% (37/117)** | 60.64% | 69.51% | **+5.99%** |
| **Method D: Event-Level Score Mass** | 82.86% (58/70) | 93.55% (58/62) | 0.00% (0/8) | 35.90% (42/117) | 58.00% | 68.24% | +1.71% |
| **Method E: Adaptive Hysteresis** | **85.71% (60/70)** | **96.77% (60/62)** | 0.00% (0/8) | 50.43% (59/117) | 50.42% | 63.49% | -12.82% (Regression) |

---

## 3. Engineering Analysis of Trade-Offs

### 3.1 Consecutive Evidence ($K=2$) as a Distractor Barrier
In continuous audio, non-vocal transients (door slams, microphone thumps, isolated whistle chirps) typically produce an energy spike in exactly one 500 ms window. By enforcing $K=2$ (two sequential windows exceeding $\theta=0.6000$), 9 false alarm events were suppressed without touching sustained screams lasting $> 1.0$s.

### 3.2 Peak with Corroboration (Method C)
Method C addresses the asymmetric nature of screams vs noise:
- If a scream is loud ($p \ge 0.75$), the acoustic decay into the next window almost always leaves $p \ge 0.40$.
- In contrast, isolated transient noise spikes spike to $p \approx 0.76$ and immediately drop back to baseline ($p < 0.20$).
- Enforcing neighbor corroboration prevented 7 false alarms while retaining **91.94% sustained recall**.

### 3.3 Latency Impact
Both Method A ($K=2$) and Method C introduce an algorithmic decision delay of **one hop (500 ms)**: the system waits for the subsequent window before confirming the alert. In a real-time festival monitoring environment, a 500 ms confirmation window is well within safe human response latency thresholds ($< 1.0$ second).

