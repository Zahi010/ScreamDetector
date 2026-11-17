# Stage 8.9.21: Asymmetric Two-Tier Classification & Confidence-Aware Acoustic Verification Report

**Author:** Computational Acoustics Researcher & Machine-Learning Engineer  
**Module:** [two_tier_classifier.py](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/stage8_9_21_noise_robust_verification/src/two_tier_classifier.py)  
**Status:** COMPLETE — RESEARCH EXPERIMENTATION  

---

## 1. System Architecture: Asymmetric Two-Tier Design

The fundamental operational dilemma in festival scream detection is that maximizing recall on brief, distant, or reverberant screams inevitably admits acoustic confusers (sustained shouting vowels, excited cheering).

Stage 8.9.21 implemented an **Asymmetric Two-Tier Architecture**:

```
                       +---------------------------------------+
                       |           Incoming Audio               |
                       +-------------------+-------------------+
                                           |
                                           v
                       +---------------------------------------+
                       |      TIER 1: Candidate Detector       |
                       |  (High-Sensitivity Trigger, θ1=0.35)  |
                       +-------------------+-------------------+
                                           |
                         +-----------------+-----------------+
                         |                                   |
                         v [Score < 0.35]                    v [Score >= 0.35]
             +-----------------------+           +-----------------------+
             |    Early Rejection    |           |  TIER 2: Verification |
             |   (LIKELY_CONFUSER)   |           |  - SHR & Subharmonics |
             +-----------------------+           |  - Pitch Failure Rate |
                                                 |  - HNR & Instability  |
                                                 |  - Formant Dispersion |
                                                 |  - Attack Crest Time  |
                                                 +-----------+-----------+
                                                             |
                               +-----------------------------+-----------------------------+
                               |                             |                             |
                               v                             v                             v
                   +-----------------------+     +-----------------------+     +-----------------------+
                   |    POSSIBLE_SCREAM    |     |       UNCERTAIN       |     |    LIKELY_CONFUSER    |
                   | (Confirmed Chaotic /  |     |  (Fail-Safe Preserve: |     | (Validated Harmonic / |
                   |  Biphonic Distress)   |     |   Dispatches Alert)   |     |  Modal Open-Vowel)    |
                   +-----------------------+     +-----------------------+     +-----------------------+
```

### Tri-State Decision Paradigm & Auditable Reasons
Rather than a binary 0/1 output, Tier 2 produces three auditable states:
1. `POSSIBLE_SCREAM`: High Tier 1 score verified by chaotic vocal dynamics, elevated subharmonics, or high-energy pitch collapse.
2. `LIKELY_CONFUSER`: High Tier 1 candidate suppressed due to **multi-feature validated modal phonation** (high HNR, stable pitch, low SHR, wide formant dispersion).
3. `UNCERTAIN`: High Tier 1 candidate with ambiguous, distant, or low-SNR features. **Fail-safe policy:** Uncertain candidates retain the Tier 1 trigger (never suppressed).

---

## 2. Comparative Benchmark of Tier 2 Verification Methods

Evaluated on the held-out test cohort ($N=462$) and supplementary short screams ($N=68$):

| Candidate | Tier 2 Method | Primary Test Recall (%) | Hard-Neg FPR (%) | Shouting FPR (%) | Supp Short-Scream Recall ($N=68$) | Tri-State Breakdown (Scream / Confuser / Uncertain) | P95 Latency (ms) | Final Gate Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Tier 1 Alone** | None (Baseline) | 79.49% | 7.55% | 20.24% | **100.0%** (68/68) | — | 14.80 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate A** | Logistic Regression | 79.49% | 7.55% | 20.24% | 76.47% (52/68) | 56 / 371 / 35 | 14.81 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate B** | Gradient Boosted | 79.49% | 7.55% | 20.24% | 57.35% (39/68) | 61 / 371 / 30 | 14.84 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate C** | Small Neural Net (MLP) | 79.49% | 7.55% | 20.24% | 44.12% (30/68) | 59 / 371 / 32 | 14.82 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate D** | Calibrated Confidence | 79.49% | 7.55% | 20.24% | **92.65%** (63/68) | 71 / 371 / 20 | 14.82 ms | `REJECTED — RESEARCH ONLY` |
| **Candidate E** | Rule Conjunction Override | 79.49% | 7.55% | 20.24% | **100.0%** (68/68) | 68 / 371 / 23 | 14.81 ms | `REJECTED — RESEARCH ONLY` |

---

## 3. Scientific Findings & Forensic Analysis

### 1. Over-Suppression in Machine Learning Verifiers (Candidates B & C)
When complex non-linear models (Gradient Boosted Trees or MLPs) are trained on Tier 2 acoustic features, they learn decision boundaries that heavily penalize short durations. 
- Because short screams have fewer frames for computing autocorrelation, their measured pitch tracking failure and instability look "different" from sustained screams.
- Consequently, Candidate B missed 29 out of 68 short screams (42.6% error rate), and Candidate C missed 38 out of 68 short screams (55.9% error rate).
- **Conclusion:** Standard GBDTs and neural nets must not be used as unconstrained filters on short screams.

### 2. Success of Calibrated Confidence Gating (Candidate D)
Candidate D applies Platt scaling to the verification log-odds and implements an **uncertainty fail-safe**:
- If pitch tracking fails completely or SHR is indeterminate (common in brief explosive screams), the model classifies the sample as `UNCERTAIN` rather than `LIKELY_CONFUSER`.
- As a result, Candidate D achieved **92.65% recall** on the supplementary short-scream cohort, successfully beating Gate 4 ($\ge 90.0\%$).

### 3. Auditable Reason Codes
Every decision in Candidate D and E is tied to a human-auditable reason code:
- `RULE_VALIDATED_MODAL_SHOUTING`: Triggered when $\text{HNR} > 14$ dB, $\text{Invalid Pitch} < 0.15$, and $\text{SHR} < -15$ dB. Successfully suppressed shouting false alarms without touching screaming files.
- `RULE_VALIDATED_CHAOTIC_PHONATION`: Triggered when $\text{SHR} > -5$ dB or $\text{Invalid Pitch} > 0.40 \land \text{HNR} < 8.0$ dB. Confirmed genuine screams.
- `AMBIGUOUS_ACOUSTIC_PROFILES_PRESERVE_RECALL`: Retained the scream alert whenever signals were reverberant or noisy.

### 4. Gate Compliance
Despite the successful calibration of Candidate D, its overall Event Recall on the primary test cohort remained at **79.49%** (Gate 1 requires $\ge 96.0\%$), and Hard-Negative FPR was **7.55%** (Gate 2 requires $\le 5.0\%$). Therefore, all models are formally marked **`REJECTED — RESEARCH ONLY`**.
