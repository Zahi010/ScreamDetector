# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Development-Only Short-Event Acoustic Representation Research

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Track C investigated alternative acoustic representations and classification architectures designed to overcome the short-scream blind spot identified in Stage 8.9.61. All experiments were conducted strictly on the unexposed development cohort (`stage_62_development_manifest.csv`, $N=187$, 70 screams, 117 negatives) without touching the exposed evaluation cohort.

Five experimental candidate representations were benchmarked against the frozen C5 baseline:
1. **Baseline C5 Static 1.0s:** Legacy fixed 1.0-second center framing.
2. **Candidate R1 (500 ms Framing):** Shorter 500 ms temporal framing with acoustic tiling.
3. **Candidate R2 (Multi-Resolution Fusion):** Dual-scale STFT representation combining 500 ms and 1000 ms subband peaks.
4. **Candidate R3 (VAD Active Energy Pooling):** Voice Activity Detection (VAD) gating that strips silent padding before filterbank extraction.
5. **Candidate R4 (Acoustic Event Proposal & Peak Centering):** Sliding energy flux detector that dynamically centers the analysis window on the loudest transient burst.
6. **Candidate R5 (Dedicated Short-Event Classifier):** A dedicated 17-dimensional active-feature classifier trained with balanced weights.

### Key Research Findings:
- **Frozen Network Inflexibility:** Representations R1, R2, and R4 yielded $0.0\%$ short-scream recall when fed into the frozen Candidate E1 neural network. Because the network weights were trained strictly on unpadded 1.0-second audio, feeding synthetic tiled representations does not match the network's latent manifold.
- **VAD Gating Efficacy (Candidate R3):** Candidate R3 was the only representation using frozen E1 weights that successfully detected short screams (improving ROC-AUC from 0.7387 to **0.7838**).
- **Dedicated Classifier Breakthrough (Candidate R5):** When a dedicated classifier was trained directly on active VAD features, short-scream recall jumped from $0.0\%$ to **75.00% (6/8)**, overall recall reached **80.00%**, and ROC-AUC reached **0.8593**, while maintaining ultra-low pipeline latency (**6.51 ms P95**).
- **Sample Size Warning:** Because the development set contains only $N=8$ short screams, Candidate R5's performance is strictly an exploratory proof-of-concept (`INSUFFICIENT_DEVELOPMENT_EVIDENCE`).

---

## 2. Experimental Candidate Configurations

```
Incoming Audio Stream
  ├── Candidate R1: Slice 500 ms -> Tile 2x -> C5 Filterbank -> Frozen E1 NN
  ├── Candidate R2: [500 ms Subbands] ⊕ [1000 ms Subbands] -> Peak Fusion -> Frozen E1 NN
  ├── Candidate R3: VAD Gate (Strip Silence) -> Density Tile -> C5 Filterbank -> Frozen E1 NN
  ├── Candidate R4: Energy Flux Proposal (Find Peak 500 ms) -> Center Slice -> Frozen E1 NN
  └── Candidate R5: VAD Active Pooling -> 17-d Vector (11 SB + 6 AC) -> Dedicated Balanced Classifier
```

---

## 3. Development Benchmark Results ($N=187$)

| Candidate Identifier | Threshold ($\theta$) | Overall Recall ($N=70$) | Sustained Recall ($N=62$) | Short Recall ($N=8$) | Hard-Negative FPR ($N=117$) | Precision | F1 Score | ROC-AUC | PR-AUC | Pipeline Latency P95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline C5 Static 1.0s** | 0.6800 | 11.43% (8/70) | 12.90% (8/62) | 0.00% (0/8) | **1.71% (2/117)** | 80.00% | 20.00% | 0.7387 | 0.5821 | 8.67 ms |
| **Candidate R1 (500 ms Framing)** | 0.6800 | 11.43% (8/70) | 12.90% (8/62) | 0.00% (0/8) | **1.71% (2/117)** | 80.00% | 20.00% | 0.6277 | 0.4912 | 8.62 ms |
| **Candidate R2 (Multi-Resolution)**| 0.6800 | 10.00% (7/70) | 11.29% (7/62) | 0.00% (0/8) | **1.71% (2/117)** | 77.78% | 17.72% | 0.6991 | 0.5315 | 17.17 ms |
| **Candidate R3 (VAD Active Pooling)**| 0.6800 | 12.86% (9/70) | 12.90% (8/62) | **12.50% (1/8)** | **1.71% (2/117)** | 81.82% | 22.22% | **0.7838** | 0.6120 | 11.86 ms |
| **Candidate R4 (Event Proposal)** | 0.6800 | 14.29% (10/70) | 16.13% (10/62)| 0.00% (0/8) | 2.56% (3/117) | 76.92% | 24.10% | 0.7374 | 0.5904 | 12.11 ms |
| **Candidate R5 (Dedicated Classifier)**| **0.5000** | **80.00% (56/70)** | **80.65% (50/62)**| **75.00% (6/8)**| 14.53% (17/117) | **76.71%** | **78.32%** | **0.8593** | **0.7885** | **6.51 ms** |

---

## 4. Key Engineering Insights

### 4.1 The Myth of "Free" Representation Adapters
Simply altering acoustic chunk duration (Candidate R1) or tiling slices before the C5 filterbank does not restore detection on a model whose weights were frozen under full-second normalization. The neural network's internal gating layer expects specific phonation statistics ($vocal\_mean$, $vocal\_max$). When these are distorted by artificial tiling, probability outputs remain suppressed.

### 4.2 Why Candidate R5 Succeeds
Candidate R5 abandons the attempt to force short vocalizations through the sustained-scream neural net. Instead, it extracts the 17 raw acoustic features ($11 \text{ C5 subbands} + 6 \text{ phonation statistics}$) from the active VAD region and feeds them to a dedicated classifier trained with balanced class weights.
- It detects **6 out of the 8 short screams** (75.00%).
- It achieves **ROC-AUC of 0.8593**, substantially outperforming all frozen-model candidates.
- Because it operates on low-dimensional summary features, its inference time is under **0.01 ms**, yielding a complete pipeline P95 of **6.51 ms**.

### 4.3 Governance Limitation
Candidate R5 demonstrates the viability of dedicated short-event modeling. However, because only 8 short screams were available in the unexposed development partition, Candidate R5 cannot be considered production-ready. Expanding the legal development pool with calibrated, diverse short screams is the required prerequisite for future stages.

