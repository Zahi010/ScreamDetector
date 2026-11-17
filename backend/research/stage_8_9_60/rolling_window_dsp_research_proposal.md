# Rolling-Window DSP Research Proposal — Stage 8.9.60

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary & Research Context

Stage 8.9.59's forensic investigation of Candidate E1's 16 false negatives established that **sustained screams ($\ge 1.0$s) underperform short screams (76.67% recall vs 94.87%)**. Forensic analysis showed that this is primarily driven by **global window temporal averaging**: when an audio buffer of 2.0s to 4.0s contains a transient scream burst (e.g. 0.6s) followed by a decaying vocal release or room reverberation, computing statistical averages across the full buffer dilutes the peak scream-to-low energy ratio and depresses the mean spectral centroid.

This document outlines a controlled research proposal to investigate a **500 ms rolling-hop aggregation architecture** in a future experimental stage.

**In strict compliance with Stage 8.9.60 governance, the C5 implementation (`c5_combined.py`) remains completely frozen. No model training, threshold tuning, or code modifications are authorized or executed in this stage.**

---

## 2. Technical Evaluation of Current vs Proposed Architecture

```
Current Buffer Averaging vs Proposed Rolling-Window Aggregation:
========================================================================================
CURRENT (C5 Buffer Averaging):
[--- Scream Attack (0.6s) ---][------------- Vocal Decay / Silence (2.4s) -------------]
|                                                                                      |
+-------------------------- FULL BUFFER (3.0s) AVERAGE --------------------------------+
==> High energy burst diluted by 80% trailing silence; scream-to-low ratio depressed.

PROPOSED (500 ms Rolling-Hop with Max-Pooling Aggregation):
[ Hop 1 (0.5s) ][ Hop 2 (0.5s) ][ Hop 3 (0.5s) ][ Hop 4 (0.5s) ][ Hop 5 (0.5s) ][ Hop 6 (0.5s) ]
|   Attack     ||    Peak      ||    Decay     ||   Silence    ||   Silence    ||   Silence    |
|   p = 0.82   ||   p = 0.94   ||   p = 0.55   ||   p = 0.02   ||   p = 0.01   ||   p = 0.01   |
+--------------------------------------------------------------------------------------+
==> Buffer Aggregation: max(p_i) = 0.94 ==> DETECTED!
========================================================================================
```

### Detailed Design Elements:

1. **Current Configuration:** C5 currently processes contiguous audio buffers (typically 975 ms to 2,000 ms) and computes a single global 18-dimensional feature vector per buffer (6 phonation features, 9 subband energies/ratios, 3 temporal covariance metrics).
2. **Proposed 500 ms Rolling Hop:** The audio stream is decomposed into overlapping 500 ms sub-windows advanced by a 250 ms hop step. Features are computed independently per 500 ms window.
3. **Temporal Resolution Impact:** Improves temporal onset precision from $\sim 1000\text{ ms}$ down to $250\text{ ms}$, ensuring transient shrieks within longer clips are captured at peak acoustic energy density.
4. **Feature Dimensionality & Model Compatibility:** Individual sub-window feature dimension remains strictly 18 features, ensuring 100% mathematical compatibility with existing trained linear heads or MLP classifiers.
5. **Computational Overhead:** A 2.0-second clip requires 7 overlapping hops instead of 1 global extraction. In Stage 8.9.58, C5 per-hop inference was measured at $0.72\text{ ms}$. Processing 7 hops requires $\approx 5.04\text{ ms}$, comfortably within the 25.0 ms real-time latency ceiling.
6. **Temporal Aggregation Alternatives:**
   - *Option A: Max-Pooling Aggregation:* $p_{\text{clip}} = \max_i p_i$. Maximizes recall on transient screams embedded in noise; slightly elevates false-positive vulnerability on single transient clicks.
   - *Option B: Persistent 2-Hop Hysteresis:* Requires $p_i \ge \theta$ across 2 consecutive hops ($>250\text{ ms}$). Highly effective at rejecting impulse clicks while preserving screams lasting $\ge 500\text{ ms}$.
   - *Option C: Exponential Moving Average (EMA):* Smoothes probabilities over time with decay parameter $\alpha = 0.6$.
7. **False-Positive Risks:** Shorter windows have higher instantaneous variance. Transient door slams or dropped objects could trigger isolated false alarms under pure max-pooling, mandating persistent multi-hop hysteresis.
8. **Required Validation & Evaluation Governance:** Any rolling-window DSP variant must be developed in an isolated experimental directory (`backend/research/stage_8_9_61/dsp_rolling/`), benchmarked against the frozen C5 baseline on identical validation audio, and subjected to a full numerical stability and latency audit before authorization.

