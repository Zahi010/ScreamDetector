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

# Rolling-Window DSP Architecture Specification & Temporal Aggregation Design

## 1. System Motivation & Architectural Distinction

In Stage 8.9.59 error analysis, Candidate E1 exhibited two temporal failure modes when evaluated under static, non-overlapping windowing:
1. **Sustained Vocalization Vulnerability:** Prolonged screams ($\ge 1.0$s duration) often experienced score decay across temporal frames in static evaluation because background adaptation and feature normalization attenuated the vocal energy tail.
2. **Boundary Truncation:** Distress vocalizations spanning the boundary between two adjacent non-overlapping blocks suffered from split spectral energy, causing both windows to fall below the detection threshold.

To resolve these issues without altering Candidate E1's frozen neural network weights or retuning its input feature dimensions, Stage 8.9.61 investigates an experimental **Rolling-Window DSP Streaming Wrapper** using a 500 ms hop size.

### Mandatory Conceptual Distinctions:
- **Audio Window Duration ($W_{audio} = 1.0\text{ s}$ / 16,000 samples):** The continuous chunk of uncompressed audio consumed by C5 DSP and the semantic feature extractor.
- **Hop Duration ($H_{audio} = 0.5\text{ s}$ / 8,000 samples):** The cadence at which new audio enters the system and a new inference step is triggered.
- **Feature-Frame Duration ($W_{frame} = 25\text{ ms}$, $H_{frame} = 10\text{ ms}$):** The internal STFT frame and hop sizes utilized within C5 DSP for sliding RMS and spectral subband extraction.
- **Temporal Aggregation Interval ($T_{agg} = 1.0\text{ to } 2.5\text{ s}$):** The rolling history of discrete window scores $(p_t, p_{t-1}, \dots)$ evaluated by downstream temporal aggregation logic.

---

## 2. Buffer Management & Signal Flow Architecture

```
Incoming Stream (16 kHz Float32 Mono)
       │
       ▼ [Chunks of 8,000 samples / 500 ms]
┌────────────────────────────────────────────────────────┐
│  Rolling Ring Buffer (Capacity: 16,000 samples / 1.0 s) │
│  ┌─────────────────────────┬─────────────────────────┐  │
│  │    T - 500 ms (Old)     │    T (New 500 ms Hop)   │  │
│  └─────────────────────────┴─────────────────────────┘  │
└────────────────────────────────────────────────────────┘
       │  50% Window Overlap (8,000 samples shared)
       ▼
┌────────────────────────────────────────────────────────┐
│  Frozen C5 Combined DSP Feature Extraction Pipeline    │
│  ├── 11-d Subband Filterbank (Precomputed Butter)      │
│  ├── 6-d Phonation Statistics & RMS Framing            │
│  └── 1024-d Semantic Projection (Pretrained YAMNet)    │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  Frozen Candidate E1 Dual-Branch Neural Classifier     │
│  Logits -> Sigmoid Activation -> Probability p_t        │
└────────────────────────────────────────────────────────┘
       │
       ▼ [Triggered every 500 ms]
┌────────────────────────────────────────────────────────┐
│  Experimental Temporal Aggregation Engine               │
│  (Strategies A, B, C, D, E)                             │
└────────────────────────────────────────────────────────┘
       │
       ▼
  Alert Event Decision & Confidence Tracking
```

---

## 3. Granular Design Components

### A. Existing C5 Input Window & Model Compatibility
- Candidate E1 expects four fixed-dimension input tensors:
  - `t_sem`: $(1, 1024)$ semantic embedding.
  - `t_ac`: $(1, 6)$ acoustic phonation statistics.
  - `t_m`: $(1, 6)$ acoustic feature mask.
  - `t_sb`: $(1, 11)$ subband energy vector.
- **Model Compatibility Invariant:** The neural network weights in `candidate_e_v954_weighted.pt` cannot process variable-length inputs. Therefore, every rolling inference step feeds an exact 1.0-second (16,000 samples) window into C5 DSP. A 500 ms hop does *not* shrink the model window; it doubles the evaluation cadence by stepping 500 ms across the continuous ring buffer.

### B. Buffer Initialization and Boundary Handling
1. **Recording Start (Zero Padding):** When a new stream or recording begins, the ring buffer contains 8,000 samples of zero-padding in the first half and the initial 8,000 audio samples in the second half.
2. **Partial Final Window:** If a continuous recording terminates with fewer than 8,000 remaining samples, the partial buffer is zero-padded to reach the 16,000-sample requirement for clean execution.
3. **Recording Boundary Reset:** Between independent recordings or when stream disconnection occurs, the ring buffer and all temporal aggregation states (hysteresis, persistence counters) are completely purged to prevent state leakage.

### C. Computational Overhead and Budget
- Original C5 DSP execution time: **6.20 ms P95**.
- Candidate E1 neural network forward pass: **1.48 ms P95**.
- Total downstream pipeline execution: **7.68 ms P95**.
- In a 500 ms hop architecture, an inference step executes every 500 ms.
- **CPU Utilization Budget:** The entire inference cycle consumes:
  $$\frac{7.68\text{ ms}}{500.0\text{ ms}} = 1.54\% \text{ of available real-time single-core budget}$$
  This provides a $>64\times$ real-time headroom factor, guaranteeing that multi-stream concurrent execution can be supported on low-power hardware without deadline misses.

---

## 4. Five Experimental Temporal Aggregation Strategies

Stage 8.9.61 investigates five strictly separated aggregation strategies evaluated exclusively on development data:

### Strategy A: Independent Window Decisions (Baseline Reference)
- Each 500 ms window produces an independent score $p_t$.
- Decision: $\hat{y}_t = \mathbb{I}(p_t \ge \theta_{E1})$, where $\theta_{E1} = 0.6800$.
- No temporal smoothing or cross-window memory.

### Strategy B: Consecutive-Window Persistence
- Requires $K$ consecutive positive windows before an alert is asserted:
  $$\hat{y}_t = \prod_{i=0}^{K-1} \mathbb{I}(p_{t-i} \ge \theta_{E1})$$
- For $K=2$, an alert requires elevated scream probability across at least two consecutive 500 ms hops ($\ge 1.0$s duration). Suppresses isolated transient impulses and whistle squeaks.

### Strategy C: Dual-Threshold Hysteresis
- Employs separate entry ($\theta_{high}$) and exit ($\theta_{low}$) thresholds:
  - If $S_{t-1} = 0$: $S_t = \mathbb{I}(p_t \ge \theta_{high})$.
  - If $S_{t-1} = 1$: $S_t = \mathbb{I}(p_t \ge \theta_{low})$.
- Experimental parameter selection: $\theta_{high} \in [0.60, 0.70]$, $\theta_{low} \in [0.35, 0.45]$. Prevents rapid alert chattering on undulating sustained screams.

### Strategy D: Rolling Exponential Probability Aggregation
- Smoothed probability score $z_t$:
  $$z_t = \alpha p_t + (1 - \alpha) z_{t-1}$$
  where $\alpha \in [0.4, 0.7]$.
- Decision: $\hat{y}_t = \mathbb{I}(z_t \ge \theta_{EMA})$.

### Strategy E: Bounded Maximum-Window Aggregation
- Maximum score across a sliding window of recent hops:
  $$z_t = \max(p_t, p_{t-1}, \dots, p_{t-W+1})$$
  with $W = 2$ or $W = 3$.
- Decision: $\hat{y}_t = \mathbb{I}(z_t \ge \theta_{max})$.
- *Evaluation Requirement:* Explicitly measure impact on false-alarm rate, as maximum aggregation is prone to elevating false positives if transient noise bursts occur.

