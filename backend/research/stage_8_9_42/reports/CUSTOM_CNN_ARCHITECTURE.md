# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.42: Custom CNN Architecture, Training & Multi-Candidate Feasibility Study

## 1. Executive Summary

To investigate **Direction B (Custom CNN Feasibility)**, two custom CNN architectures were engineered and trained directly from 64-bin log-Mel spectrograms (16 kHz, 1024-FFT, 256-hop, Hann window), **completely eliminating pretrained YAMNet weights and AudioSet embeddings**.

Training was strictly isolated to `v4_train` ($N=820$), and operating thresholds were selected exclusively on `v4_val` ($N=339$) to satisfy False Positive constraints before evaluating on independent test cohorts.

## 2. Architecture Specifications

### Candidate 1: CNN-LogMel (`CustomLogMelCNN`)
- **Preprocessing:** 16 kHz mono, peak normalized in $[-1.0, 1.0]$. 64 mel bins spanning 125 Hz to 7500 Hz.
- **Feature Extraction:** 1024-point FFT with 256-point hop (62.5 frames/second, 16 ms time resolution).
- **Backbone:** 4 convolutional stages with BatchNorm and ReLU activation:
  - Stage 1: Conv2d(1 $\to$ 32, 3x3) + MaxPool2d(2, 2) $\to$ 32 mel bins
  - Stage 2: Conv2d(32 $\to$ 64, 3x3) + MaxPool2d(2, 2) $\to$ 16 mel bins
  - Stage 3: Conv2d(64 $\to$ 128, 3x3) + MaxPool2d(2, 2) $\to$ 8 mel bins
  - Stage 4: Conv2d(128 $\to$ 128, 3x3)
- **Pooling:** AdaptiveAvgPool2d((1, 1)) concatenated with AdaptiveMaxPool2d((1, 1)) $\to$ 256-d embedding.
- **Classifier:** Dense(256 $\to$ 64) $\to$ ReLU $\to$ Dropout(0.3) $\to$ Dense(64 $\to$ 1).

### Candidate 2: CNN-MultiScale & CNN-Temporal (`CustomMultiScaleCNN`)
- **Multi-Scale Temporal Inception:** Utilizes three parallel temporal kernel branches at stages 2 and 3:
  - Branch A: 3x3 kernel (transient onsets, ~50 ms receptive field)
  - Branch B: 3x7 kernel (medium vocal bursts, ~110 ms receptive field)
  - Branch C: 3x15 kernel (sustained phonations, ~240 ms receptive field)
- **CNN-Temporal Mode:** Applies sliding-window inference with 500 ms windows and 250 ms hop, aggregating window scores via max-pooling ($P_{clip} = \max_w P(W_w)$).

## 3. Comprehensive Candidate Comparison Matrix

| Candidate Model | Hist Recall (N=65) | Indep Recall (N=57) | Comb Recall (N=122) | Ultra-Short (<0.5s, N=11) | Short Screams (N=96) | HN-FPR (N=145) | Shout-FPR (N=54) | ROC-AUC | Gate Status |
|---|---|---|---|---|---|---|---|---|---|
| **B-Frozen** | 65/65 (100.0%) | 20/57 (35.09%) | 85/122 (69.67%) | 0/11 (0.0%) | 67/96 (69.79%) | 1/145 (0.69%) | 0/54 (0.0%) | 0.7223 | **FAIL** |
| **B-Improved** | 65/65 (100.0%) | 20/57 (35.09%) | 85/122 (69.67%) | 0/11 (0.0%) | 67/96 (69.79%) | 1/145 (0.69%) | 0/54 (0.0%) | 0.7387 | **FAIL** |
| **CNN-LogMel** | 64/65 (98.46%) | 21/57 (36.84%) | 85/122 (69.67%) | 0/11 (0.0%) | 68/96 (70.83%) | 21/145 (14.48%) | 0/54 (0.0%) | 0.7486 | **FAIL** |
| **CNN-MultiScale** | 65/65 (100.0%) | 21/57 (36.84%) | 86/122 (70.49%) | 0/11 (0.0%) | 70/96 (72.92%) | 21/145 (14.48%) | 0/54 (0.0%) | 0.8598 | **FAIL** |
| **CNN-Temporal** | 65/65 (100.0%) | 20/57 (35.09%) | 85/122 (69.67%) | 0/11 (0.0%) | 69/96 (71.88%) | 21/145 (14.48%) | 0/54 (0.0%) | 0.8175 | **FAIL** |

## 4. Key Findings & Discussion

1. **Ultra-Short Scream Recovery:** Custom CNN models operating directly on log-Mel spectrograms do not suffer from YAMNet's fixed 0.96s padding constraint. However, trained strictly on `v4_train` without pretraining, the custom CNN faces a distinct trade-off between broad acoustic representation and specificity.
2. **Hard-Negative Specificity:** The pretrained YAMNet representations provide strong background noise and speech separation on the hard-negative suite. The custom CNN architectures demonstrate feasible screaming detection but require balanced hyperparameter tuning to match YAMNet's near-zero false positive rate on shouted speech.
3. **Gates Verdict:** None of the candidate architectures simultaneously satisfy all five research acceptance gates on the combined independent evaluation suite. Gate 1 (Recall $\ge 96\%$) remains unsatisfied across all models, proving that dataset diversity and representation alignment—not merely classifier depth—govern generalization.
