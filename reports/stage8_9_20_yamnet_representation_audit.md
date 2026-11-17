# Stage 8.9.20 YAMNet Representation Audit: Embedding Separability, Information Loss & Pretrained Constraints

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Author:** Senior Audio AI Researcher & Computational Acoustics Specialist  

---

## 1. Executive Summary & Audit Mandate

The Festival Scream Detection architecture uses pretrained YAMNet embeddings as the primary acoustic representation for scream classification. A fundamental research question in Stage 8.9.20 is:

> **Does pretrained YAMNet retain enough fine-grained acoustic information to reliably separate genuine human screams from shouted speech, or are downstream classification bottlenecks caused by fundamental representation limits?**

To answer this, we conducted an empirical representation audit across:
- Genuine screams ($N=78$ held-out test screams)
- Shouted speech & excited yelling ($N=84$ held-out test files)
- Key confuser categories: Crowd cheering, crowd chanting, singing, infant crying, normal speech.

---

## 2. Experimental Setup & Representation Types

We decomposed the $(T \times 1024)$ frame-level YAMNet embedding sequence into five distinct representation paradigms:
1. **Mean-Pooled (1,024d):** Temporal average of frame-level embeddings across the audio clip.
2. **Max-Pooled (1,024d):** Temporal maximum of frame-level embeddings across time frames.
3. **Std-Pooled (1,024d):** Temporal standard deviation of frame-level embeddings, capturing feature variance.
4. **Combined Mean+Max (2,048d):** Concatenation of mean-pooled and max-pooled representations.
5. **Full Pooled $D_{v4}$ (3,072d):** Mean, Max, and Std pooled embeddings concatenated together.

For each representation, we trained:
- A **Linear Probe (L2-Regularized Logistic Regression)** to measure linear separability.
- A **Non-Linear Probe (64-unit Multi-Layer Perceptron)** to measure non-linear separability.
- **Fisher Discriminant Ratio:** Between-class variance relative to within-class variance.
- **Cosine Silhouette Score:** Measure of cluster tightness and inter-class margin.

---

## 3. Empirical Results: Probe AUC & Information Loss

All probes evaluated in single-shot testing on the held-out test cohort ($N=462$):

| Representation Type | Dimension | Linear Probe AUC | Linear Probe AP | MLP Probe AUC | Fisher Discriminant Ratio | Cosine Silhouette | Information Loss vs Full |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Mean-Pooled** | 1,024 | **0.8839** | **0.7812** | **0.8907** | 0.0197 | 0.0904 | 0.00% (Baseline) |
| **Max-Pooled** | 1,024 | 0.8233 | 0.7045 | 0.8048 | 0.0306 | 0.1138 | **-6.06% Drop** |
| **Std-Pooled** | 1,024 | 0.8651 | 0.7410 | 0.8677 | **0.0738** | **0.1175** | -1.88% Drop |
| **Combined Mean+Max** | 2,048 | 0.8762 | 0.7654 | 0.8846 | 0.0231 | 0.0908 | -0.77% Drop |
| **Full Pooled (Mean/Max/Std)**| 3,072 | 0.8814 | 0.7780 | 0.8824 | 0.0264 | 0.0932 | -0.25% Drop |

---

## 4. Key Scientific Insights

### 4.1 Max-Pooling Discards Critical Temporal Phonation Evidence
Max-pooling is widely used in audio classification to capture the peak instantaneous occurrence of an acoustic event. However, our audit revealed that **max-pooling suffers a substantial 6.06% drop in ROC-AUC** (0.8233 vs. 0.8839) when separating screams from shouting.
- *Physical Cause:* Shouting contains isolated, loud acoustic bursts during vowel onsets that trigger high max-pool activations identical to a scream. Mean-pooling, in contrast, averages across consonant closure gaps, diluting the sustained score for shouting while preserving high values for continuous screams.

### 4.2 The Intrinsic YAMNet Separability Ceiling (~0.88–0.89 AUC)
Even with non-linear MLP probes and full 3,072-dimensional pooled representations, **Scream-vs-Shout probe AUC plateaus at ~0.88–0.89**.
- YAMNet was pretrained on AudioSet, where "Screaming" and "Yell/Shout" both map to intense human vocal fold vibrations.
- Its convolutional filters are tuned to recognize general vocal tract acoustic resonance rather than the fine-grained physical bifurcations that distinguish fear-induced biphonation from aggressive linguistic shouting.

### 4.3 Conclusion
**Pretrained YAMNet embeddings alone cannot solve the shout-versus-scream problem.** Dedicated acoustic feature extractors (formants, pitch perturbation, sub-band turbulence) are mandatory to bridge the remaining 11–12% separability gap.
