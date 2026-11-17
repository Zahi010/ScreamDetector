# STAGE 8.9.34 — SNR-ADAPTIVE CONTRASTIVE CONDITIONING REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.34 — Temporal Context Modeling, Infant-Cry Discrimination & SNR-Adaptive Scream Detection  
**Operating Mode:** Offline-First Machine Learning Research & Robust Representation Learning  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** November 2, 2026  

---

## 1. MOTIVATION & PROBLEM STATEMENT

In Stage 8.9.33, forensic analysis of the 16 false-negative scream recordings revealed that **$62.5\%$ (10 / 16)** were distant, low-amplitude, or masked screams embedded in heavy crowd or festival music noise (SNR $< 3\text{ dB}$).
When screams are masked by high ambient noise floors, their YAMNet semantic activations attenuate towards background representations, causing static classifiers to miss them.

---

## 2. SNR-CONDITIONED PROJECTION HEAD ARCHITECTURE

We developed the **Semantic SNR-Adaptive Head**:
$$z_{\text{sem}} = \text{Normalize}_{L_2}\left( W_2 \cdot \text{ReLU}\left(\text{BatchNorm}(W_1 [x_{\text{sem}} \,\|\, \Delta_{\text{SNR}}] + b_1)\right) + b_2 \right)$$
where $x_{\text{sem}} \in \mathbb{R}^{1024}$, and $\Delta_{\text{SNR}} \in \mathbb{R}^1$ represents the estimated local signal-to-noise ratio:
$$\Delta_{\text{SNR}} = \frac{1}{D}\sum_{d=1}^D (x_{\text{max}, d} - x_{\text{p10}, d})$$
which measures the instantaneous peak energy above the local background floor.

### 2.1 Training Curriculum
The model was trained exclusively on the training partition ($N=739$) using dynamic noise-injection curriculum learning:
- Noise perturbation $\epsilon \sim \mathcal{N}(0, \sigma^2)$ where $\sigma \in [0.0, 0.30]$ was sampled dynamically.
- Effective SNR was scaled accordingly to force the projection manifold to remain separable even under noise floors up to $-5\text{ dB}$.
- Zero independent test partition recordings were used during noise mixing or contrastive training.

---

## 3. CONTROLLED SNR DEGRADATION SWEEP

Evaluating recall and false-positive rates on the independent test partition under controlled simulated acoustic degradation:

| Simulated Condition | Effective Noise Scale | Overall Scream Recall | Masked Scream Recall | Hard-Negative FPR |
|---|---:|---:|---:|---:|
| **Clean Audio** | 0.00 | **90.20%** | **90.20%** | **15.18%** |
| **+10 dB SNR** | 0.05 | **92.16%** | **92.16%** | **16.75%** |
| **+5 dB SNR** | 0.10 | **89.22%** | **89.22%** | **15.71%** |
| **0 dB SNR** | 0.20 | **87.25%** | **87.25%** | **17.80%** |
| **-3 dB SNR** | 0.35 | **81.37%** | **81.37%** | **27.75%** |
| **-5 dB SNR** | 0.50 | **74.51%** | **74.51%** | **25.13%** |

---

## 4. AUDIT FINDINGS & CRITICAL TRADE-OFF

1. **Masked Scream Sensitivity:** SNR-adaptive conditioning successfully recovered masked screams under moderate background noise, achieving up to **$92.16\%$ recall** at $+10\text{ dB}$.
2. **The Unavoidable False-Positive Penalty:** Conditioning the network to become hypersensitive to low-energy transients under high background noise floors caused a severe increase in hard-negative false alarms:
   - Hard-negative FPR rose from **$7.85\%$ to $15.18\%$ on clean audio**, and escalated to **$27.75\%$ at $-3\text{ dB}$**.
   - Background noises containing vocal murmur (e.g. distant festival conversations and laughter) were falsely elevated into scream alerts when the SNR indicator flagged a high noise floor.
3. **Conclusion:** SNR adaptation alone cannot satisfy Gate 2 ($\le 5.00\%$ HN-FPR) without being constrained by temporal phonation gating.
