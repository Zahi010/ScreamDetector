# Stage 8.9.19 Model Comparison Report: Adaptive Temporal Architectures & Gate Benchmarking

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY (Strict Acceptance Gates Enforced)  
**Evaluation Cohort:** Independent Held-Out Test Set ($N=462$, 78 Screams, 384 Hard Negatives)  
**Author:** Audio Machine Learning Researcher & Deep Learning Architect  

---

## 1. Candidate Architecture Overview

Stage 8.9.19 investigated whether an adaptive temporal fusion mechanism could synthesize the high sensitivity and short-scream robustness of Stage 8.9.18 Model D with the shouting rejection power of Stage 8.9.18 Model B. Five distinct adaptive architectures were formulated, trained, and benchmarked:

```
+----------------------------------------------------------------------------------------------------------------+
|                                    STAGE 8.9.19 CANDIDATE ARCHITECTURES                                        |
+----------------------------------------------------------------------------------------------------------------+
| Model A: Calibrated Weighted Fusion                                                                            |
| Linear combination of calibrated probabilities across four distinct acoustic heads with learned positive       |
| simplex weights constrained via Dirichlet-regularized optimization.                                            |
+----------------------------------------------------------------------------------------------------------------+
| Model B: Context-Dependent Gating Network                                                                      |
| A multi-layer perceptron gating mechanism that dynamically allocates head weights conditioned on event        |
| duration, context completeness, temporal confidence, and multi-scale modulation features.                     |
+----------------------------------------------------------------------------------------------------------------+
| Model C: Multi-Scale Hierarchical Routing                                                                      |
| Explicit duration-aware router: Short-scale onset features (<0.75s) bypass long-window constraints;            |
| sustained events (>0.75s) engage the full temporal CNN and consonant closure analyzer.                         |
+----------------------------------------------------------------------------------------------------------------+
| Model D: Cascaded Temporal Architecture                                                                        |
| High-sensitivity candidate trigger followed by a specialized temporal shout-rejection filter equipped with    |
| a brief-scream safety bypass to prevent false pruning of short distress calls.                                 |
+----------------------------------------------------------------------------------------------------------------+
| Model E: Learned Neural Attention Fusion                                                                       |
| 2-layer MLP with residual multi-head attention operating over scale-decomposed temporal representations and    |
| missing-context uncertainty vectors.                                                                           |
+----------------------------------------------------------------------------------------------------------------+
```

---

## 2. Quantitative Evaluation Matrix

Metrics evaluated in single-shot testing on the held-out test cohort ($N=462$) using validation-optimized thresholds:

| Metric | Ref $D_{v4}$ | Ref Model B | Model A (Weighted) | Model B (Gating) | Model C (Routing) | Model D (Cascade) | Model E (Attention) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Operating Threshold ($\theta^*$)** | 0.46 | 0.21 | 0.15 | 0.27 | 0.24 | 0.21 | 0.15 |
| **Event Recall** | 78.21% | 69.23% | 76.92% | 88.46% | **92.31%** | 88.46% | 56.41% |
| **Precision** | 69.32% | 67.50% | 76.92% | 65.09% | 65.45% | 63.30% | **81.48%** |
| **F1-Score** | 0.7349 | 0.6835 | 0.7692 | 0.7500 | **0.7660** | 0.7380 | 0.6667 |
| **ROC-AUC** | 0.9486 | 0.8856 | 0.9582 | 0.9590 | **0.9633** | 0.9408 | 0.9403 |
| **PR-AUC** | 0.7293 | 0.6824 | 0.7365 | 0.7610 | **0.7965** | 0.7238 | 0.7352 |
| **Specificity** | 92.97% | 93.23% | 95.31% | 90.36% | 90.10% | 89.58% | **97.40%** |
| **Hard-Negative FPR** | 7.03% | 6.77% | **4.69%** | 9.64% | 9.90% | 10.42% | **2.60%** |
| **Shouted-Speech FPR** | 20.24% | 10.71% | 15.48% | 20.24% | 21.43% | 23.81% | **8.33%** |
| **Short-Scream Recall** | 92.86% | 85.71% | 85.71% | 92.86% | **100.0%** | **100.0%** | 85.71% |
| **All Short Screams ($\le 1.5$s)** | 81.82% | 86.36% | 81.82% | 95.45% | **100.0%** | **100.0%** | 72.73% |
| **Infant Crying FPR** | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| **Digital Silence FPR** | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| **Brier Score** | 0.0704 | 0.0827 | 0.0711 | 0.0598 | **0.0583** | 0.0653 | 0.0964 |
| **ECE (Calibration)** | 0.0644 | 0.0328 | 0.0694 | 0.0579 | 0.0570 | 0.0707 | 0.0946 |
| **P95 Latency** | 15.2 ms | 16.1 ms | 15.8 ms | 15.8 ms | 15.8 ms | 15.8 ms | 16.2 ms |

---

## 3. Strict Acceptance Gate Evaluation

| Candidate Model | Gate 1: Recall $\ge 96\%$ | Gate 2: HN-FPR $\le 5\%$ | Gate 3: Shout $\le 15\%$ | Gate 4: Short $\ge 90\%$ | Gate 5: Latency $\le 25$ms | Final Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Ref $D_{v4}$ (Stage 8.9.17)** | FAIL (78.2%) | FAIL (7.0%) | FAIL (20.2%) | **PASS (92.9%)** | **PASS (15.2ms)** | `REJECTED — RESEARCH ONLY` |
| **Ref Model B (Stage 8.9.18)** | FAIL (69.2%) | FAIL (6.8%) | **PASS (10.7%)** | FAIL (85.7%) | **PASS (16.1ms)** | `REJECTED — RESEARCH ONLY` |
| **Model A (Weighted Fusion)** | FAIL (76.9%) | **PASS (4.7%)** | FAIL (15.5%) | FAIL (85.7%) | **PASS (15.8ms)** | `REJECTED — RESEARCH ONLY` |
| **Model B (Context Gating)** | FAIL (88.5%) | FAIL (9.6%) | FAIL (20.2%) | **PASS (92.9%)** | **PASS (15.8ms)** | `REJECTED — RESEARCH ONLY` |
| **Model C (Multi-Scale Routing)**| FAIL (92.3%) | FAIL (9.9%) | FAIL (21.4%) | **PASS (100.0%)** | **PASS (15.8ms)** | `REJECTED — RESEARCH ONLY` |
| **Model D (Cascaded Filter)** | FAIL (88.5%) | FAIL (10.4%) | FAIL (23.8%) | **PASS (100.0%)** | **PASS (15.8ms)** | `REJECTED — RESEARCH ONLY` |
| **Model E (Neural Attention)** | FAIL (56.4%) | **PASS (2.6%)** | **PASS (8.3%)** | FAIL (85.7%) | **PASS (16.2ms)** | `REJECTED — RESEARCH ONLY` |

---

## 4. Key Comparative Findings

### 4.1 Sensitivity Frontier: Model C (92.31% Recall, 100% Short Recall)
Model C established the project's highest empirical recall on held-out test data. By recognizing that brief vocalizations ($\le 0.75$s) cannot fulfill the receptive-field requirements of long temporal CNNs, Model C dynamically routes short acoustic events to short-scale onset features and unpooled embeddings. This recovered all 14 short screams in the independent cohort and increased overall recall from 78.2% to 92.31%.

### 4.2 Specificity Frontier: Model E (2.60% HN-FPR, 8.33% Shouting FPR)
Model E proved that non-linear neural attention over multi-scale temporal features can effectively eliminate the vast majority of hard false alarms. Shouted speech FPR fell from 20.24% down to 8.33% (well below the $\le 15.0\%$ gate), and overall hard-negative FPR plummeted to 2.60% (beating the $\le 5.0\%$ gate). However, this high selectivity suppressed sensitivity on ambiguous or reverberant screams, reducing recall to 56.41%.

### 4.3 The Pareto Barrier
No single candidate achieved Pareto-dominance across both sensitivity and specificity. The project is currently constrained by an acoustic frontier:
- Operating in the sensitivity regime ($\ge 92\%$ recall) permits sustained shouted vowels to trigger alerts ($\sim 21\%$ shouting FPR).
- Operating in the specificity regime ($\le 10\%$ shouting FPR) suppresses screams that lack prominent onset dynamics ($\sim 56–69\%$ recall).

Consequently, all Stage 8.9.19 candidate models are strictly designated **`REJECTED — RESEARCH ONLY`**.
