# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Event-Level Performance & Temporal Aggregation Report

## 1. Executive Summary

Track F investigated temporal aggregation strategies to convert frame-by-frame dual-resolution neural predictions into coherent, noise-robust event-level alerts. Seven aggregation strategies were benchmarked across simulated continuous streams for the $N=312$ development cohort.

### Primary Results

| Aggregation Strategy | Overall Recall | Dev FPR | Shouted FPR | Short Recall | F1 Score | PR-AUC | Operational Latency Profile |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Raw Single Window Max** | **94.36%** | $17.09\%$ | $100.0\%$ | **98.50%** | **0.9223** | $0.9504$ | Zero added latency; vulnerable to single-frame noise spikes. |
| **Method A: $K=2$ Persistence** | $92.82\%$ | $17.09\%$ | $100.0\%$ | $96.24\%$ | $0.9141$ | $0.9479$ | $+125\text{ ms}$ on weak events; bypass on high confidence. |
| **Method B: $K=3$ Persistence** | $92.82\%$ | $17.09\%$ | $100.0\%$ | $96.24\%$ | $0.9141$ | $0.9445$ | $+250\text{ ms}$ on weak events; conservative. |
| **Method C: Asymmetric Hysteresis** | $89.74\%$ | **10.26%** | **60.0%** | $95.49\%$ | $0.9162$ | $0.9504$ | Suppresses borderline shouts; $-4.62\%$ recall trade-off. |
| **Method D: Rolling EMA ($\alpha=0.5$)** | $93.85\%$ | $18.80\%$ | $100.0\%$ | $97.74\%$ | $0.9150$ | **0.9632** | Smooth probability integration; highest PR-AUC. |
| **Method E: Event Merging & Holdoff** | $93.33\%$ | $17.95\%$ | $100.0\%$ | $96.99\%$ | $0.9146$ | $0.9504$ | Prevents duplicate triggers within 350ms. |
| **Method F: Full Stack Temporal** | $92.82\%$ | $17.09\%$ | $100.0\%$ | $96.24\%$ | $0.9141$ | $0.9503$ | Multi-stage filter: high-confidence bypass + persistence. |

---

## 2. Technical Findings & Trade-Offs

### 2.1 The Latency-Persistence Dilemma for Short Screams
- Requiring consecutive window activations ($K=2$ or $K=3$) inherently introduces temporal delay. For an acoustic event lasting only $200\text{ ms}$, requiring 2 consecutive 250 ms frames risks missing the event if the second frame falls after acoustic decay.
- **High-Confidence Bypass Solution:** In Method A and Method F, introducing an unconditional bypass threshold ($\tau_{\text{bypass}} = 0.85$) allows unambiguous screams to fire immediately on frame 1 (zero added latency), while restricting the $K=2$ requirement to low-margin activations ($0.50 \le p < 0.85$).

### 2.2 Asymmetric Hysteresis for Vocal Outcry Control
- Method C applied an entry threshold of $\theta_{\text{high}} = 0.65$ and an exit threshold of $\theta_{\text{low}} = 0.40$.
- **Specificity Gain:** This reduced hard-negative FPR from $17.09\%$ to $10.26\%$, and reduced shouted-speech FPR from $100.0\%$ down to $60.0\%$.
- **Recall Penalty:** The higher entry bar caused 9 marginal screams to be missed, reducing recall to $89.74\%$.

---

## 3. Operational Deployment Recommendation

For real-time prototype monitoring:
1. **Primary Streaming Aggregation:** Method F (Full Stack Temporal) with $\tau_{\text{bypass}} = 0.80$ and $K=2$ persistence on weak frames.
2. **Refractory Holdoff:** A 500 ms holdoff window prevents an extended 4-second human scream from emitting multiple jarring alerts.

---

## 4. Artifact Links
- Event Aggregation CSV: [event_aggregation_ablation.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/event_aggregation_ablation.csv)
- Selective Suppression Analysis: [selective_suppression_analysis.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/selective_suppression_analysis.md)

