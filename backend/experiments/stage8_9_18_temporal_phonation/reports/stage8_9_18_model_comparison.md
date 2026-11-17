# Stage 8.9.18 Model Comparison Report: Candidate Architectures & Gate Benchmarking

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Evaluation Cohort:** Independent Held-Out Test Set ($N=462$, 78 Screams, 384 Hard Negatives)  
**Author:** Audio Machine Learning Researcher & Deep Learning Engineer  

---

## 1. Candidate Architecture Overview

Five distinct model paradigms were developed and benchmarked to evaluate whether temporal acoustic modelling can resolve the shout-vs-scream false-positive challenge while preserving high recall:

```
+-------------------------------------------------------------------------------------------------------+
|                                    STAGE 8.9.18 CANDIDATE ARCHITECTURES                              |
+-------------------------------------------------------------------------------------------------------+
|  Model A: Handcrafted Temporal Baseline                                                               |
|  Audio -> 32 Temporal Features (Phonation + Turbulence + Energy + Flux) -> L2 Scaled LogReg          |
+-------------------------------------------------------------------------------------------------------+
|  Model B: Temporal 1D Dilated CNN                                                                     |
|  Audio -> (70, 16) Time-Frequency Tensor -> 3 Dilated Conv1D Layers -> GAP + GMP -> Sigmoid (~5.2k p) |
+-------------------------------------------------------------------------------------------------------+
|  Model C: YAMNet Temporal Sequence Model                                                              |
|  Audio -> Unpooled YAMNet Frame Sequence (T, 1024) -> Mean + Max + Std + Delta Velocity (5,120d)      |
+-------------------------------------------------------------------------------------------------------+
|  Model D: Hybrid Fusion Classifier                                                                    |
|  Audio -> [D_v4 Embeddings (3,080d) + 32 Temporal Features + CNN Prob] -> Calibrated Ensemble (3,112d)|
+-------------------------------------------------------------------------------------------------------+
```

---

## 2. Quantitative Evaluation Matrix

Metrics were computed in single-shot evaluation on the held-out test cohort ($N=462$) using thresholds selected on the validation split ($N=373$).

| Metric | Ref $D_{v4}$ | Model A | Model B | Model C | Model D (Hybrid) | Ablation E1 | Ablation E2 | Ablation E3 | Ablation E5 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Operating Threshold ($\theta$)** | 0.43 | 0.53 | 0.36 | 0.49 | 0.37 | 0.44 | 0.42 | 0.35 | 0.53 |
| **Event Recall** | 87.18% | 62.82% | 67.95% | 82.05% | **88.46%** | 87.18% | 87.18% | 87.18% | 62.82% |
| **Precision** | 68.69% | 59.76% | 67.09% | 71.91% | 70.41% | 70.83% | 70.10% | 65.38% | 59.76% |
| **F1-Score** | 0.7684 | 0.6125 | 0.6752 | 0.7665 | **0.7841** | 0.7816 | 0.7771 | 0.7473 | 0.6125 |
| **ROC-AUC** | 0.9515 | 0.9079 | 0.9056 | 0.9478 | **0.9538** | 0.9501 | 0.9510 | 0.9412 | 0.9079 |
| **PR-AUC** | 0.7407 | 0.6061 | 0.5891 | 0.7389 | **0.7424** | 0.7395 | 0.7401 | 0.7188 | 0.6061 |
| **Specificity** | 91.93% | 91.41% | 93.23% | 93.49% | **92.45%** | 92.71% | 92.45% | 90.62% | 91.41% |
| **Hard-Negative FPR** | 8.07% | 8.59% | **6.77%** | **6.51%** | 7.55% | 7.29% | 7.55% | 9.38% | 8.59% |
| **Shouted-Speech FPR** | 20.24% | **13.10%** | **10.71%** | 19.05% | 21.43% | 21.43% | 21.43% | 25.00% | **13.10%** |
| **Short-Scream Recall** | **92.86%** | 85.71% | 78.57% | **92.86%** | **92.86%** | **92.86%** | **92.86%** | **92.86%** | 85.71% |
| **Infant Crying FPR** | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| **Digital Silence FPR** | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| **Brier Score** | 0.0715 | 0.0954 | 0.0982 | 0.0732 | **0.0698** | 0.0712 | 0.0720 | 0.0765 | 0.0954 |
| **ECE (Calibration)** | 0.0523 | 0.0641 | 0.0712 | 0.0540 | **0.0489** | 0.0518 | 0.0524 | 0.0581 | 0.0641 |
| **P95 Latency** | 15.2 ms | 14.8 ms | 16.1 ms | 15.6 ms | 15.2 ms | 15.1 ms | 15.1 ms | 15.1 ms | 14.8 ms |

---

## 3. Strict Acceptance Gate Evaluation

| Candidate Model | Gate 1: Recall $\ge 96\%$ | Gate 2: HN-FPR $\le 5\%$ | Gate 3: Shout $\le 15\%$ | Gate 4: Short $\ge 90\%$ | Gate 5: Latency $\le 25$ms | Final Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Ref $D_{v4}$ (Stage 8.9.17)** | FAIL (87.2%) | FAIL (8.1%) | FAIL (20.2%) | **PASS (92.9%)** | **PASS (15.2ms)** | `REJECTED — RESEARCH ONLY` |
| **Model A (Temporal Baseline)** | FAIL (62.8%) | FAIL (8.6%) | **PASS (13.1%)** | FAIL (85.7%) | **PASS (14.8ms)** | `REJECTED — RESEARCH ONLY` |
| **Model B (1D Dilated CNN)** | FAIL (68.0%) | FAIL (6.8%) | **PASS (10.7%)** | FAIL (78.6%) | **PASS (16.1ms)** | `REJECTED — RESEARCH ONLY` |
| **Model C (YAMNet Sequence)** | FAIL (82.1%) | FAIL (6.5%) | FAIL (19.0%) | **PASS (92.9%)** | **PASS (15.6ms)** | `REJECTED — RESEARCH ONLY` |
| **Model D (Hybrid Fusion)** | FAIL (88.5%) | FAIL (7.6%) | FAIL (21.4%) | **PASS (92.9%)** | **PASS (15.2ms)** | `REJECTED — RESEARCH ONLY` |
| **Ablation E1 (No Phonation)** | FAIL (87.2%) | FAIL (7.3%) | FAIL (21.4%) | **PASS (92.9%)** | **PASS (15.1ms)** | `REJECTED — RESEARCH ONLY` |
| **Ablation E3 (No Energy Mod)** | FAIL (87.2%) | FAIL (9.4%) | FAIL (25.0%) | **PASS (92.9%)** | **PASS (15.1ms)** | `REJECTED — RESEARCH ONLY` |
| **Ablation E5 (Temporal Alone)**| FAIL (62.8%) | FAIL (8.6%) | **PASS (13.1%)** | FAIL (85.7%) | **PASS (14.8ms)** | `REJECTED — RESEARCH ONLY` |

---

## 4. Architectural Analysis & Trade-Offs

### 4.1 The Shouted-Speech Breakthrough: Model B (1D Dilated CNN)
Model B demonstrated that **temporal convolutional modelling over short-time feature sequences is fundamentally superior to static pooled embeddings for rejecting speech-like syllables**.
- Conv1D with dilation factors ($d=1, 2, 4$) explicitly captures the rhythmic modulation frequency of speech ($3–5$ Hz syllabic cadence).
- When human subjects shout, consonants create acoustic closure boundaries where RMS energy drops and zero-crossing rate spikes. Model B detected these recurring patterns, reducing shouted-speech false alarms from **17 down to 9** (10.71% FPR).
- However, Model B suffered a significant recall penalty (67.95%), because distant or masked screams that lacked clear temporal boundaries failed to trigger the required sequence activation.

### 4.2 The Short-Scream Dilemma
A critical trade-off was uncovered between sequence windowing and short-scream detection:
- The independent test set contains 14 short screams ($\le 1.5$s, with 5 screams $<0.75$s).
- Standalone temporal sequence models (Model B) achieved only **78.57%** short-scream recall (missing 3 out of 14 short screams). In sub-second audio bursts, there are insufficient time frames to populate the dilated receptive field (70 frames = 2.24s).
- Static pooled models (Ref $D_{v4}$ and Model D) easily detect short screams (**92.86%**, 13/14 detected) because max-pooling across time extracts the peak burst regardless of event duration.

### 4.3 Why Hybrid Model D Improved Recall But Failed Gate 3
Model D attempted to combine the best of both worlds by stacking $D_{v4}$ embeddings, 32 handcrafted temporal features, and the Model B sequence probability:
- **Gain:** Event recall increased from 87.18% to **88.46%**, and F1-score reached a project-high **0.7841**.
- **Limitation:** In the 3,112-dimensional feature space, the 3,080 YAMNet embedding dimensions dominated the regularized linear decision space. Consequently, shouting false alarms remained high (21.43%).

---

## 5. Visualizations

See the generated comparison figure:
![Model Performance Comparison](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/reports/figures/temporal_model_performance_comparison.png)
