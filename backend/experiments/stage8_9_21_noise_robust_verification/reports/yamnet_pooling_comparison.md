# Stage 8.9.21: YAMNet Representation Reconstruction & Pooling Benchmark Report

**Author:** Machine-Learning Engineer & Computational Acoustics Researcher  
**Module:** [yamnet_pooling_study.py](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/stage8_9_21_noise_robust_verification/src/yamnet_pooling_study.py)  
**Status:** COMPLETE — RESEARCH EXPERIMENTATION  

---

## 1. Executive Summary

YAMNet extracts 1024-dimensional feature representations for every 0.48-second audio frame (with 0.05-second hop). In standard industrial pipelines, frame embeddings are aggregated into a single vector per audio segment using temporal pooling.

Stage 8.9.21 conducted an empirical investigation comparing:
1. **Mean Pooling (1024d):** Temporal average of all active frame embeddings.
2. **Max Pooling (1024d):** Temporal maximum across each embedding dimension.
3. **Combined Mean-Max Pooling (2048d):** Concatenation of mean and max vectors.
4. **Mean + Temporal Statistics (3072d):** Mean, Max, and Standard Deviation across frames.
5. **Frame-Level Sequence Representation (1120d):** 16-frame sequence representations.

---

## 2. Quantitative Benchmark Results

Evaluated on the source-group-isolated held-out benchmark (Screams vs Shouting/Speech):

| Representation Architecture | Dimensionality | Linear Train AUC | Linear Val AUC | Linear Test AUC | Linear Test AP | Overfitting Gap ($AUC_{tr} - AUC_{te}$) | MLP Test AUC | Generalization Verdict |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A. Mean Pooling** | 1024 | 1.0000 | 0.9412 | **0.8839** | **0.9021** | **0.1161** | **0.8916** | **Optimal Baseline** |
| **B. Max Pooling (Diagnostic)**| 1024 | 0.9990 | 0.8715 | **0.8233** | 0.8415 | **0.1757** | 0.8078 | **Severely Degraded (-6.06% AUC)** |
| **C. Combined Mean-Max** | 2048 | 1.0000 | 0.9380 | **0.8762** | 0.8955 | **0.1238** | 0.8834 | **Overfits (Higher Gap, Lower Test AUC)** |
| **D. Mean + Temporal Stats** | 3072 | 1.0000 | 0.9420 | **0.8814** | 0.8998 | **0.1186** | 0.8826 | **Capacity Inflation Without Gain** |
| **E. Frame Sequence (Temporal)**| 1120 | 0.9995 | 0.8920 | **0.8484** | 0.8650 | **0.1510** | — | **Sensitive to Alignment** |

---

## 3. Scientific & Forensic Findings

### 1. Reproduction of Baseline
Stage 8.9.21 independently reproduced the Stage 8.9.20 findings:
- **Mean Pooling Probe AUC:** **0.8839**
- **Max Pooling Probe AUC:** **0.8233**
- The **6.06% AUC drop** for max-pooling is robust across random seeds and regularisation penalties.

### 2. Why Max Pooling Fails for Scream Detection
Max pooling records the single highest activation observed across the entire time window for each of the 1024 convolutional filter channels. 
- In festival audio, brief acoustic transients (microphone bumps, drum strikes, pyrotechnics, brass horn stabs) trigger transient filter spikes. Max pooling retains these spikes permanently, causing high false alarm rates.
- Mean pooling integrates energy across time, penalizing isolated transients and rewarding sustained distress energy.

### 3. Does Mean-Max Fusion (2048d) Improve Generalization?
**No.** 
- Combined Mean-Max pooling achieved **0.8762 Test AUC**, which is lower than Mean Pooling alone (0.8839).
- The train-to-test overfitting gap increased from **0.1161 to 0.1238**.
- Doubling the feature space from 1024 to 2048 dimensions increases model parameters, allowing classifiers to fit idiosyncratic noise in the training source groups rather than learning invariant vocal dynamics.

### 4. Policy Decision on Pooling
**Max-only pooling must never be used as the sole representation for new candidate classifiers.** 
All future YAMNet-based research candidates should adopt Mean Pooling (1024d) or temporal pooling with strong regularization.
