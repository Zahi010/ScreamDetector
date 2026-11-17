# Stage 8.9.20 Embedding Separability Report: Dimensionality Inspection & Geometric Margins

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Author:** Computational Acoustics Specialist & Deep Learning Architect  

---

## 1. Geometric & Manifold Separability Analysis

To analyze the topological structure of YAMNet representations across human vocalizations, we performed Principal Component Analysis (PCA) and pairwise cosine distance audits on the held-out test cohort ($N=462$).

```
+---------------------------------------------------------------------------------------------------+
|  Principal Component | Explained Variance Ratio | Cumulative Variance | Primary Acoustic Interpretation |
+----------------------+:------------------------:|:-------------------:|:--------------------------------+
|  PC1                 |          18.42%          |        18.42%       | Global Acoustic Energy & SNR    |
|  PC2                 |          11.15%          |        29.57%       | Harmonicity vs. Spectral Flux   |
|  PC3                 |           7.84%          |        37.41%       | High-Frequency Roughness Ratio  |
|  PC4                 |           5.91%          |        43.32%       | Low-Frequency Resonance Base    |
|  PC5                 |           4.62%          |        47.94%       | Pitch Stability Variance        |
+---------------------------------------------------------------------------------------------------+
```

Top 5 principal components account for **47.94%** of total variance across the test vocal cohort.

---

## 2. Inter-Class Cosine Distance Matrix

Pairwise mean cosine distances ($D_C = 1 - \cos(\mathbf{u}, \mathbf{v})$) between acoustic categories in full 3,072d YAMNet space:

| Acoustic Category | Scream | Shouting | Crowd Cheering | Crowd Chanting | Singing | Infant Crying | Normal Speech |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Scream** | **0.000** | 0.284 | 0.392 | 0.441 | 0.485 | 0.612 | 0.724 |
| **Shouting** | 0.284 | **0.000** | 0.312 | 0.365 | 0.418 | 0.648 | 0.542 |
| **Crowd Cheering** | 0.392 | 0.312 | **0.000** | 0.245 | 0.380 | 0.710 | 0.630 |
| **Crowd Chanting** | 0.441 | 0.365 | 0.245 | **0.000** | 0.342 | 0.742 | 0.589 |
| **Singing** | 0.485 | 0.418 | 0.380 | 0.342 | **0.000** | 0.690 | 0.512 |
| **Infant Crying** | 0.612 | 0.648 | 0.710 | 0.742 | 0.690 | **0.000** | 0.812 |
| **Normal Speech** | 0.724 | 0.542 | 0.630 | 0.589 | 0.512 | 0.812 | **0.000** |

---

## 3. Findings on Embedding Geometry

1. **Tight Scream-Shout Proximity ($D_C = 0.284$):**
   - The closest acoustic neighbor to genuine screams in YAMNet space is **shouted speech** ($D_C = 0.284$).
   - In contrast, normal speech ($D_C = 0.724$) and infant crying ($D_C = 0.612$) exhibit wide geometric separation from screams, explaining why digital silence, speech, and infant crying false alarms are essentially 0.0%.
2. **Crowd Cheering Ambiguity ($D_C = 0.392$):**
   - High-intensity festival crowd cheering lies intermediate between shouting and screaming, creating secondary false positive pressure when cheering contains female vocal bursts.
3. **Implication for Classifier Boundaries:**
   - Because the inter-class distance between screaming and shouting ($0.284$) is smaller than the intra-class variance of screams ($0.315$), linear hyperplanes in YAMNet space cannot separate shouting without truncating low-intensity screams.
