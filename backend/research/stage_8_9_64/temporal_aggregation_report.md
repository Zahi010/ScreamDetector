# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Temporal Aggregation & Branch-Aware Corroboration Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Track F investigated temporal aggregation strategies to prevent event fragmentation and false-alarm proliferation in continuous rolling-window streaming (50 ms hop stride, 1000 ms sliding context).

We benchmarked seven aggregation mechanisms across the 187 development audio files:
1. `Method Baseline`: Any single window exceeding $\theta = 0.50$ triggers an alarm (logical OR).
2. `Method A (Consecutive Evidence K=2)`: Two consecutive windows $\ge 0.50$ (100 ms sustained progression).
3. `Method B (Bounded EMA)`: Exponential moving average ($\alpha = 0.30$, threshold $\ge 0.45$).
4. `Method C (Peak with Corroboration)`: Peak window $\ge 0.70$ OR ($\ge 0.50$ with adjacent context $\ge 0.45$).
5. `Method D (Event Merging)`: Groups activations with inter-burst intervals $< 200\,\text{ms}$ into a unified event.
6. `Method E (Refractory Holdoff)`: Enforces a $500\,\text{ms}$ lockout following an alarm to prevent duplicate firing.
7. `Method F (Branch-Aware Corroboration + Holdoff)`: Couples branch gating confidence with refractory suppression.

Summary metrics are recorded in [`temporal_aggregation_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/temporal_aggregation_metrics.csv).

---

## 2. Comparative Benchmark Matrix

```
Temporal Aggregation Benchmark Results (N = 187 Rolling Streams)
┌───────────────────────────────────────┬──────────┬──────────┬──────────┬─────────────┬─────────────┬──────────────┬────────────┐
│ Aggregation Method                    │ Recall   │ FPR      │ F1 Score │ Mean Delay  │ P95 Delay   │ Frag. Ratio  │ Total Alms │
├───────────────────────────────────────┼──────────┼──────────┼──────────┼─────────────┼─────────────┼──────────────┼────────────┤
│ Baseline (Any Window >= 0.50)         │ 88.57%   │ 64.96%   │ 0.5962   │ 137.3 ms    │ 657.5 ms    │ 11.85 alarms │ 1,328      │
│ Method A (Consecutive Evidence K=2)   │ 78.57%   │ 34.19%   │ 0.6667   │ 187.4 ms    │ 810.0 ms    │  8.91 alarms │   764      │
│ Method B (Bounded EMA alpha=0.30)     │ 67.14%   │ 29.06%   │ 0.6225   │ 228.4 ms    │ 1000.0 ms   │ 12.60 alarms │   868      │
│ Method C (Peak with Corroboration)    │ 85.71%   │ 54.70%   │ 0.6186   │ 129.4 ms    │ 700.0 ms    │ 11.68 alarms │ 1,170      │
│ Method D (Event Merging < 200ms)      │ 88.57%   │ 64.96%   │ 0.5962   │ 137.3 ms    │ 657.5 ms    │  3.95 events │   397      │
│ Method E (Refractory Holdoff 500ms)   │ 88.57%   │ 64.96%   │ 0.5962   │ 137.3 ms    │ 657.5 ms    │  3.05 events │   285      │
│ Method F (Branch-Aware Corroboration) │ 84.29%   │ 49.57%   │ 0.6310   │ 153.0 ms    │ 770.0 ms    │  2.64 events │   224      │
└───────────────────────────────────────┴──────────┴──────────┴──────────┴─────────────┴─────────────┴──────────────┴────────────┘
```

---

## 3. Analysis of Alarm Dynamics & Latency Trade-offs

### 3.1 Alarm Fragmentation Catastrophe in Baseline
In continuous 50 ms streaming, a single 1.5-second scream generates an average of **11.85 separate window-level threshold crossings**. Without event management, the baseline system floods downstream listeners with over 1,300 redundant alerts, inducing notification storms and rapid operator fatigue.

### 3.2 Event Merging vs Refractory Lockout
- **Method D (Event Merging):** Successfully collapses continuous window triggers into unified acoustic events, cutting fragmentation by **$-66.7\%$** ($11.85 \to 3.95$) with zero loss of recall ($88.57\%$) and zero added delay.
- **Method E (500 ms Refractory Holdoff):** Outperforms simple merging by suppressing echo-like re-triggers during vocal ring-down, reducing fragmentation to **$3.05$** events per target.

### 3.3 False-Alarm Suppression via Method A ($K=2$)
- Requiring two consecutive positive hops ($100\,\text{ms}$) reduces the development FPR by nearly half (**$64.96\% \to 34.19\%$**).
- The trade-off is an increase of $+50.1\,\text{ms}$ in mean detection latency ($137.3\,\text{ms} \to 187.4\,\text{ms}$) and loss of ultra-brief isolated spikes.

### 3.4 Method F (Branch-Aware Corroboration)
- Combines the rapid responsiveness of the sustained branch on unambiguous signals with corroborative filtering on short transients.
- Achieves the lowest event fragmentation ratio (**$2.64$** alarms per event) and total post-alarm count of only $224$ across all test audio streams.

