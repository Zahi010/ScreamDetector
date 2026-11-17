# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Track A: Development-Only Evaluation & Aggregation Strategy Benchmark

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Track A of Stage 8.9.61 evaluated experimental rolling-window temporal aggregation strategies exclusively on the unexposed development manifest ($N=187$ recordings, 180 source groups). The goal of this track was to investigate whether a sliding 1.0-second analysis window advancing in 500 ms hops (50% overlap) could eliminate transient scream omissions caused by rigid static center-window alignment, while preserving streaming real-time capability and maintaining bounded false-positive rates.

Under strict governance protocols, the evaluation cohort ($N=700$) remained cryptographically sealed and completely inaccessible throughout all Track A experiments. Five temporal aggregation strategies were benchmarked using the frozen Candidate E1 neural network weights (`candidate_e_v954_weighted.pt`) and C5 combined DSP filterbank.

Based on multi-criteria optimization on development data, **Strategy D (Rolling Exponential Moving Average, $\alpha=0.50, \theta=0.6000$)** was selected as the frozen experimental candidate (`E1_ROLLING_C5_STRATEGY_D`) for preregistered independent evaluation.

---

## 2. Development Cohort Composition and Governance

The development manifest was derived from the Stage 8.9.60 acquisition pool after strictly excluding all 700 evaluation recordings and quarantining 75 sister-excerpt recordings that shared source groups or parent recordings with the sealed cohort:

| Cohort Property | Value | Notes |
| :--- | :--- | :--- |
| **Total Development Recordings** | 187 | Unique acoustic files |
| **Unique Source Groups** | 180 | High source diversity ($180 / 187 = 96.3\%$) |
| **Positive Class (Screams)** | 70 | 62 sustained ($\ge 1.0$s), 8 short ($< 1.0$s) |
| **Negative Class (Hard Negatives)** | 117 | Shouted speech (40), cheering (18), whistles (16), environmental (43) |
| **Shared Source Groups with Sealed Cohort** | 0 | Strictly 0 overlap verified by automated audit |
| **Shared Parent Excerpts with Sealed Cohort** | 0 | Strictly 0 overlap verified by duplicate audit |
| **Manifest SHA-256 Digest** | `bdf27fdf...` | Sealed in `rolling_window_development_manifest.csv` |

---

## 3. Evaluated Temporal Aggregation Strategies

Each strategy processes sequential 1.0-second analysis windows $w_t = [t \cdot H, t \cdot H + W]$ where $W = 16,000$ samples (1.0 s) and $H = 8,000$ samples (0.5 s hop). For a recording of duration $T$, this produces $M = \max(1, \lfloor (T - W)/H \rfloor + 1)$ neural network probabilities $\{p_1, p_2, \dots, p_M\}$.

The five benchmarked strategies operate as follows:

1. **Strategy A (Max Pooling):**
   $$p_{\text{event}} = \max_{1 \le t \le M} p_t, \quad \hat{y} = \mathbb{I}(p_{\text{event}} \ge 0.6800)$$
   *Hypothesis:* Maximizes sensitivity by triggering on any single high-confidence window. Highly vulnerable to isolated transient noise spikes.

2. **Strategy B (Persistence / Multi-Window Confirmation, $K=2$):**
   $$\hat{y} = \mathbb{I}\left(\sum_{t=1}^{M-1} \mathbb{I}(p_t \ge 0.65 \land p_{t+1} \ge 0.65) \ge 1\right)$$
   *Hypothesis:* Suppresses isolated single-window false alarms (e.g. sharp whistles, transient coughs) by requiring two consecutive windows exceeding threshold.

3. **Strategy C (Dual-Threshold Hysteresis):**
   State transitions to `ACTIVE` when $p_t \ge 0.7000$, and remains active until $p_t < 0.4500$.
   *Hypothesis:* Smooths decision boundaries, preventing rapid flapping around the operating threshold.

4. **Strategy D (Rolling Exponential Moving Average, EMA):**
   $$S_0 = p_1, \quad S_t = \alpha p_t + (1 - \alpha) S_{t-1} \quad (\alpha = 0.50), \quad \hat{y} = \mathbb{I}(\max_t S_t \ge 0.6000)$$
   *Hypothesis:* Provides continuous temporal smoothing with a 500 ms exponential decay memory, bridging momentary acoustic dips during sustained vocalizations while resisting single-hop noise spikes.

5. **Strategy E (Static Center Window — Baseline Control):**
   $$p_{\text{static}} = p_{\text{center}}, \quad \hat{y} = \mathbb{I}(p_{\text{static}} \ge 0.6800)$$
   *Control:* The legacy single 1.0-second center-window extraction used in Stage 8.9.54 and Stage 8.9.55.

---

## 4. Benchmark Results on Development Cohort ($N=187$)

| Strategy ID | Decision Rule | Overall Recall ($N=70$) | Sustained Recall ($N=62$) | Short Recall ($N=8$) | Hard-Negative FPR ($N=117$) | Precision | F1 Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Strategy A** | Max Pooling ($\theta=0.68$) | 87.14% (61/70) | 98.39% (61/62) | 0.00% (0/8) | 47.86% (56/117) | 52.14% | 65.24% |
| **Strategy B** | Persistence ($K=2, \theta=0.65$) | 75.71% (53/70) | 85.48% (53/62) | 0.00% (0/8) | 26.50% (31/117) | 63.10% | 68.83% |
| **Strategy C** | Hysteresis ($0.70 / 0.45$) | 82.86% (58/70) | 93.55% (58/62) | 0.00% (0/8) | 34.19% (40/117) | 59.18% | 69.05% |
| **Strategy D** | **Rolling EMA ($\alpha=0.5, \theta=0.60$)** | **84.29% (59/70)** | **95.16% (59/62)** | **0.00% (0/8)** | **37.61% (44/117)** | **57.28%** | **68.21%** |
| **Strategy E** | Static Center Window ($\theta=0.68$) | 61.43% (43/70) | 70.97% (44/62) | 0.00% (0/8) | 17.09% (20/117) | 68.25% | 64.66% |

---

## 5. Comparative Trade-off Analysis

### 5.1 Sensitivity Gain on Sustained Screams
Static center-window sampling severely handicapped scream detection when the scream onset occurred away from the exact middle of the recording. Strategy D increased sustained scream recall from 70.97% to 95.16% (+24.19 percentage points on development data). By advancing every 500 ms, the analysis window captures the peak acoustic energy of screams regardless of where they start in the audio segment.

### 5.2 Specificity and False-Positive Inflation
Rolling-window evaluation tests multiple windows per recording (average $4.2$ windows per 3.0s file), which naturally inflates the cumulative recording-level false positive rate:
- Static baseline: 17.09% FPR ($20/117$).
- Strategy D: 37.61% FPR ($44/117$).
- Strategy A: 47.86% FPR ($56/117$).

Strategy D reduced false positives compared to Max Pooling (37.61% vs 47.86%, saving 12 false alarms) while retaining 95.16% sustained recall.

### 5.3 Short-Scream Limitation ($< 1.0$s)
All five strategies failed to detect any of the 8 short screams in the development cohort ($0.0\%$ recall). Because the neural network was trained on 1.0-second mel-filterbank vectors, zero-padding a short vocalization (e.g. 300–600 ms) distorts the spectral energy distribution, diluting the subband features. Solving short-scream detection requires architectural changes (e.g. multi-scale receptive fields or dedicated short-window models) rather than window hopping alone.

---

## 6. Selection Rationale for Candidate Freeze

Strategy D was selected as the designated experimental configuration for the following reasons:
1. **Sustained Vocalization Capture:** Achieved $>95\%$ recall on sustained distress vocalizations on development data.
2. **State Simplicity and Determinism:** EMA maintains a single scalar state variable $S_t$, eliminating complex buffer queues or lookahead delays.
3. **Subband Feature Compatibility:** Operates directly on C5 combined filterbanks without retraining neural network weights.
4. **Streaming Suitability:** Emits an updated smoothed score every 500 ms with bounded memory and zero latency overhang.

The parameters $\alpha = 0.50$ and $\theta = 0.6000$ were frozen in `rolling_window_candidate_freeze.json` prior to unsealing the evaluation cohort.

