# Stage 8.9.20 Model Comparison Report: Candidate Architectures & Gate Benchmarking

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Evaluation Cohort:** Held-Out Test Set ($N=462$, 78 Screams, 384 Hard Negatives)  
**Supplementary Cohort:** Independent Short-Scream Cohort ($N=68$)  
**Author:** Senior Audio AI Researcher & Deep Learning Architect  

---

## 1. Candidate Architecture Formulations

Stage 8.9.20 evaluated five controlled candidate models to dissect the contributions of embeddings, pitch harmonics, sub-band turbulence, and adaptive routing:

```
+---------------------------------------------------------------------------------------------------+
|  Candidate Model                | Feature Representation                | Classifier Architecture |
+---------------------------------+:--------------------------------------+:------------------------+
|  Model A: YAMNet Probe          | D_v4 Pooled Embeddings (3,080 dims)    | L2 Logistic Regression  |
|  Model B: Pitch & Harmonic      | F0, Jitter, Shimmer, Formants (22 dims)| Random Forest (100 trees)|
|  Model C: Sub-Band Turbulence   | 4-Band Energy Ratios & Modulation (8d) | Gradient Boosting       |
|  Model D: Acoustic & YAMNet     | D_v4 (3,080d) + Acoustic (30d) (3,110d)| Regularized LogReg      |
|  Model E: Error-Aware Adaptive  | Formant Dispersion + Turbulence Router | Context-Conditioned Gate|
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Comprehensive Test Benchmark Matrix ($N=462$)

| Metric | Target | Model A (YAMNet) | Model B (Pitch/Harm) | Model C (Turbulence) | Model D (Fusion) | Model E (Adaptive) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Operating Threshold ($\theta^*$)** | — | 0.43 | 0.32 | 0.30 | 0.39 | 0.24 |
| **Event Recall** | **$\ge 96.0\%$** | 87.18% | 75.64% | 38.46% | **88.46%** | 87.18% |
| **Precision** | — | 69.39% | 63.44% | 37.50% | **71.13%** | 70.10% |
| **F1-Score** | — | 0.7727 | 0.6901 | 0.3797 | **0.7886** | 0.7771 |
| **ROC-AUC** | — | 0.9492 | 0.9123 | 0.7067 | **0.9581** | 0.9564 |
| **PR-AUC** | — | 0.7306 | 0.6300 | 0.3613 | **0.7441** | 0.7122 |
| **Specificity** | — | 92.19% | 91.15% | 86.98% | **92.71%** | 92.45% |
| **Hard-Negative FPR** | **$\le 5.0\%$** | 7.81% | 8.85% | 13.02% | **7.29%** | 7.55% |
| **Shouted-Speech FPR** | **$\le 15.0\%$** | 20.24% | **14.29% (PASS)**| **14.29% (PASS)**| 19.05% | 21.43% |
| **Short-Scream Recall** | **$\ge 90.0\%$** | 86.36% | **90.91% (PASS)**| 36.36% | **90.91% (PASS)**| **90.91% (PASS)**|
| **Supplementary Short Recall** | **$\ge 90.0\%$** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **100.0%** |
| **Digital Silence FPR** | **0.0%** | **0.0%** | **0.0%** | 7.14% | **0.0%** | **0.0%** |
| **Infant Crying FPR** | **0.0%** | **0.0%** | **0.0%** | 4.55% | 4.55% | **0.0%** |
| **Brier Score** | — | 0.0721 | 0.0871 | 0.1282 | **0.0665** | 0.0754 |
| **ECE (Calibration)** | — | **0.0519** | 0.0689 | 0.0432 | 0.0524 | 0.0884 |
| **P95 Latency** | **$\le 25.0$ ms** | **15.2 ms** | **14.5 ms** | **14.2 ms** | **15.6 ms** | **15.8 ms** |

---

## 3. Strict Acceptance Gate Audit

| Candidate Model | Gate 1: Recall $\ge 96\%$ | Gate 2: HN-FPR $\le 5\%$ | Gate 3: Shout $\le 15\%$ | Gate 4: Short $\ge 90\%$ | Gate 5: Latency $\le 25$ms | Final Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Model A (YAMNet Probe)** | FAIL (87.2%) | FAIL (7.8%) | FAIL (20.2%) | FAIL (86.4%) | **PASS (15.2ms)** | `REJECTED — RESEARCH ONLY` |
| **Model B (Pitch & Harm)** | FAIL (75.6%) | FAIL (8.9%) | **PASS (14.3%)** | **PASS (90.9%)** | **PASS (14.5ms)** | `REJECTED — RESEARCH ONLY` |
| **Model C (Turbulence)** | FAIL (38.5%) | FAIL (13.0%) | **PASS (14.3%)** | FAIL (36.4%) | **PASS (14.2ms)** | `REJECTED — RESEARCH ONLY` |
| **Model D (Fusion)** | FAIL (88.5%) | FAIL (7.3%) | FAIL (19.1%) | **PASS (90.9%)** | **PASS (15.6ms)** | `REJECTED — RESEARCH ONLY` |
| **Model E (Adaptive)** | FAIL (87.2%) | FAIL (7.6%) | FAIL (21.4%) | **PASS (90.9%)** | **PASS (15.8ms)** | `REJECTED — RESEARCH ONLY` |

**Verdict:** Every candidate failed at least one gate. Production remains strictly frozen.
