# STAGE 8.9.33 — DUAL-ENCODER ARCHITECTURE, PHONATION FUSION & VALIDATION REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Dual-Objective Optimization, Hard-Negative Discrimination & Independent Validation  
**Operating Mode:** Offline-First Machine Learning Research & Neural Architecture Engineering  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. ARCHITECTURAL DESIGN & MOTIVATION

Single-branch classifiers that operate solely on high-level semantic embeddings (e.g. YAMNet 1024-d) frequently confuse energetic vocalizations like shouting, crowd cheers, and excited speech with screams because their audio event tags share overlapping acoustic semantics. Conversely, rule-based acoustic feature models fail because pitch and LPC tracking break down in extreme vocal conditions (e.g., deterministic pitch tracking fails in $\approx 58.9\%$ of actual screams due to vocal tract turbulence and period doubling).

To solve this, Stage 8.9.33 implemented a **Dual-Encoder Multimodal Architecture** with explicit missing-feature indicator masking and failure-safe fallbacks:

```
                  ┌──────────────────────────────────────────────┐
                  │               Input Audio Frame              │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
       [Path A: Semantic]                             [Path B: Temporal/Acoustic]
       1024-d YAMNet Vector                           6-d Vocal Feats + 6-d Mask
                 │                                               │
                 ▼                                               ▼
     Linear(1024 -> 256)                             Linear(12 -> 64)
     BatchNorm1d + ReLU + Dropout(0.15)              BatchNorm1d + ReLU + Dropout(0.10)
     Linear(256 -> 128)                              Linear(64 -> 32)
     L2 Normalization (z_sem ∈ S^127)                L2 Normalization (z_acoust ∈ S^31)
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         │ Concatenate (160-d)
                                         ▼
                             [Multimodal Fusion Head]
                                 Linear(160 -> 64)
                                 ReLU + Dropout(0.10)
                                 Linear(64 -> 1)
                                         │
                                         ▼
                               Sigmoid Decision Logit
```

---

## 2. MISSING-FEATURE GATING & NUMERICAL SAFEGUARDS

### 2.1 Acoustic Failure Analysis
Empirical measurements across our scream corpus revealed:
- **Pitch Tracking Failures ($F_0$):** In 58.9% of true screams, autocorrelation and YIN algorithms fail to lock onto a deterministic periodic fundamental frequency due to subharmonic bifurcations and chaotic vocal fold vibrations.
- **LPC Instability:** In 45.8% of ultra-high-frequency screams ($F_0 > 1,000\text{ Hz}$), linear predictive coding filter coefficients blow up or produce complex conjugate roots outside the unit circle.

### 2.2 Masked Phonation Projection
To prevent `NaN` or unvoiced zero-values from corrupting gradient updates, Path B incorporates a parallel binary validity mask $m \in \{0, 1\}^6$:
$$m_i = \begin{cases} 1 & \text{if } x_i \text{ is finite, non-NaN, and } x_i > 0 \\ 0 & \text{otherwise} \end{cases}$$
$$x_{\text{safe}} = \text{nan\_to\_num}(x, \text{nan}=0.0)$$
$$\tilde{x} = [x_{\text{safe}} \,\|\, m] \in \mathbb{R}^{12}$$
This guarantees that the acoustic encoder learns to utilize pitch, harmonicity, rolloff, centroid, crest factor, and duration when valid, while learning an alternative unvoiced subharmonic representation when the mask indicates tracker failure.

---

## 3. TRAINING PROTOCOL & LOSS FUNCTION

The Dual-Encoder network was trained end-to-end on the source-group-separated training partition ($N=739$) using a compound loss function:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{BCE}}(y, \hat{y}; w_{\text{pos}}=2.5) + 0.3 \cdot \mathcal{L}_{\text{SupCon}}(z_{\text{sem}}, y; \tau=0.05)$$
- **Optimizer:** AdamW ($\text{lr} = 1.5 \times 10^{-3}$, weight decay $= 10^{-4}$).
- **Learning Rate Schedule:** Cosine annealing over 35 epochs.
- **Batch Size:** 48 samples per batch (class-balanced and source-group disjoint).
- **Validation Early Stopping:** Monitored on the held-out validation cohort ($N=293$).

---

## 4. VALIDATION THRESHOLD SELECTION

Threshold selection was performed exclusively on the validation cohort ($N=293$) to prevent test set data snooping.
Operating thresholds were swept across $\theta \in [0.20, 0.50]$:
- At $\theta = 0.25$: Validation Recall was $84.81\%$, but Validation FPR elevated to $14.95\%$.
- At $\theta = 0.45$: Validation FPR dropped to $7.48\%$, but Validation Recall dropped to $68.35\%$.
- At $\mathbf{\theta^* = 0.35}$: Validation Recall was $75.95\%$, Validation FPR was $10.75\%$, and Shouted-Speech FPR was $8.33\%$, achieving the optimal trade-off criterion:
$$\theta^* = \arg\max_\theta \left(\text{Recall}(\theta) - 1.5 \cdot \text{FPR}(\theta)\right) \implies \mathbf{0.3500}$$

This threshold was **strictly frozen** prior to conducting any test evaluations.

---

## 5. TEST SET RESULTS & GATES AUDIT

Evaluating the frozen Dual-Encoder model against the held-out test cohort ($N=293$):

| Gate Description | Threshold / Constraint | Dual-Encoder Observed | Gate Audit Status |
|---|---|---|---|
| **Gate 1: Overall Scream Recall** | $\ge 96.00\%$ | **84.31%** (86 / 102) | **FAIL** (-11.69%) |
| **Gate 2: Hard-Negative FPR** | $\le 5.00\%$ | **7.85%** (15 / 191) | **FAIL** (+2.85%) |
| **Gate 3: Shouted-Speech FPR** | $\le 15.00\%$ | **8.33%** (4 / 48) | **PASS** (Exceeds target by 6.67%) |
| **Gate 4: Short-Scream Recall** | $\ge 90.00\%$ | **80.00%** (4 / 5)* | **FAIL** (-10.00%) |
| **Gate 5: P95 Inference Latency** | $\le 25.00\text{ ms}$ | **18.57 ms** | **PASS** (6.43 ms margin) |

*\*Note: 80.00% on the $N=5$ test screams $<1.0\text{ s}$ is an insufficient sample size. On the 6-sample forensic diagnostic cohort, recall was 100.00%.*

### 5.1 Key Strengths of the Dual-Encoder
1. **Best Shouted-Speech Discrimination:** Reduced shouted-speech FPR to **8.33%**, vastly outperforming Baseline LR (12.50%) and Weighted LR (18.75%).
2. **Superior Accuracy & F1 Score:** Achieved the highest overall F1 score (**0.8473**) and highest precision (**85.15%**) of any evaluated candidate.
3. **Exceptional Computational Efficiency:** Total neural forward-pass required only **0.26 ms**, contributing to an end-to-end P95 latency of **18.57 ms**.

### 5.2 Why the Dual-Encoder Missed 16 Screams
Detailed forensic examination of the 16 missed positive test recordings revealed:
- **Masking by High-Energy Ambient Noise (9 recordings):** Screams embedded in heavy crowd roar or music playback had attenuated local SNRs ($<3\text{ dB}$).
- **Extreme High-Pitch Phonation (4 recordings):** Screams above $1,100\text{ Hz}$ where harmonic energy concentrated in a single high-frequency formant, causing acoustic branch activations to remain unvoiced.
- **Atypical Vocal Fry / Guttural Screams (3 recordings):** Heavy aperiodic noise components without clear formant structure.
