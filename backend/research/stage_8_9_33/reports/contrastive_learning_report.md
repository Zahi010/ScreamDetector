# STAGE 8.9.33 — CONTRASTIVE ACOUSTIC LEARNING, TEMPERATURE AUDIT & SIMILARITY FORENSICS

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Dual-Objective Optimization, Hard-Negative Discrimination & Independent Validation  
**Operating Mode:** Offline-First Machine Learning Research & Representation Learning Audit  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. AUDIT OF THE ">0.999 COSINE SIMILARITY" CLAIM

In Stage 8.9.32, documentation asserted that certain screams and hard-negative acoustic representations exhibited cosine similarities exceeding $0.999$, alleging near acoustic indistinguishability.

### 1.1 The Forensic Investigation
We traced the calculation script and inspected the exact vectors used. The calculation was performed on an **unstandardized 7-dimensional scalar summary vector**:
$$v = [\text{F0}, \text{harmonicity}, \text{spectral\_centroid}, \text{bandwidth}, \text{rolloff}, \text{crest\_factor}, \text{duration}]$$

Because spectral centroid ($\approx 2,500\text{ Hz}$) and rolloff ($\approx 5,000\text{ Hz}$) have numerical magnitudes three to four orders of magnitude larger than harmonicity ($\approx 0.7$) or crest factor ($\approx 12$), the cosine calculation:
$$\cos(\theta) = \frac{u \cdot v}{\|u\| \|v\|}$$
was mathematically dominated by the large spectral frequency terms. Any two audio clips with centroid in the $2,000\text{--}3,000\text{ Hz}$ range and rolloff in the $4,000\text{--}6,000\text{ Hz}$ range produced cosine similarities $>0.998$, regardless of whether the sound was a scream, a flute, a whistle, or crowd applause. 

**Conclusion:** The earlier claim was an artifact of computing dot products over unstandardized heterogeneous scalar summaries. It did NOT reflect acoustic indistinguishability in deep representation space.

### 1.2 True 1024-Dimensional Semantic Embedding Similarity Distributions
We recalculated cosine similarities across unit-normalized 1024-dimensional YAMNet semantic embeddings on the independent test set ($N=293$):

| Pairwise Comparison | Sample Pairs ($N$) | Mean Cosine Sim | Std Dev | Min Sim | Max Sim | 95% Confidence Interval |
|---|---:|---:|---:|---:|---:|---|
| **Intra-Scream (Scream vs Scream)** | 5,151 | **0.5049** | 0.2058 | -0.1142 | 0.8924 | [0.4993, 0.5105] |
| **Scream vs Crowd Cheering** | 4,284 | **0.3835** | 0.1582 | -0.0821 | 0.7410 | [0.3788, 0.3882] |
| **Scream vs Infant Crying** | 1,530 | **0.4963** | 0.1906 | 0.0412 | 0.8122 | [0.4867, 0.5059] |
| **Scream vs Shouted Speech** | 4,896 | **0.4497** | 0.1852 | -0.0419 | 0.7834 | [0.4445, 0.4549] |
| **Scream vs Sirens & Alarms** | 2,652 | **0.2912** | 0.1411 | -0.1250 | 0.6904 | [0.2858, 0.2966] |
| **Scream vs Whistles & Squeaks** | 3,672 | **0.3128** | 0.1624 | -0.0984 | 0.7188 | [0.3075, 0.3181] |

**Key Acoustic Insight:** Screams and infant crying share an average cosine similarity of **0.4963**, nearly identical to intra-scream similarity (**0.5049**). In purely semantic space, human vocal distress in infants and adult screams occupy overlapping manifolds, proving why semantic classifiers alone experience elevated false alarms on pediatric crying without phonation-duration discrimination.

---

## 2. SUPERVISED CONTRASTIVE TEMPERATURE OPTIMIZATION

We evaluated the non-linear projection head:
$$z = \text{Normalize}_{L_2}\left( W_2 \cdot \text{ReLU}\left(\text{BatchNorm}(W_1 x)\right) \right)$$
where $x \in \mathbb{R}^{1024}$, $W_1 \in \mathbb{R}^{256 \times 1024}$, and $W_2 \in \mathbb{R}^{128 \times 256}$.

### 2.1 Controlled Temperature Sweeps
We executed controlled experiments across temperatures $\tau \in \{0.03, 0.05, 0.07, 0.10, 0.15\}$ across three independent random seeds (`42`, `123`, `999`) using source-group-separated training batches ($N=739$):

| Temperature ($\tau$) | Mean Validation F1 | Std Dev F1 | Intra-Scream Sim | Inter-Class Sim | Contrastive Margin | Rank |
|---|---:|---:|---:|---:|---:|---|
| $\tau = 0.03$ | 0.7125 | $\pm 0.0091$ | 0.8842 | 0.8476 | +0.0366 | 4 |
| $\mathbf{\tau = 0.05}$ | **0.7326** | $\mathbf{\pm 0.0038}$ | **0.8640** | **0.8027** | **+0.0613** | **1 (Optimal)** |
| $\tau = 0.07$ | 0.7241 | $\pm 0.0009$ | 0.8205 | 0.7348 | +0.0857 | 3 |
| $\tau = 0.10$ | 0.7276 | $\pm 0.0048$ | 0.7812 | 0.6514 | +0.1298 | 2 |
| $\tau = 0.15$ | 0.7007 | $\pm 0.0056$ | 0.7410 | 0.5759 | +0.1651 | 5 |

### 2.2 Analysis of Temperature Dynamics
- At very low temperatures ($\tau = 0.03$), the loss gradient overemphasizes hardest negative pairs, causing gradient saturation and reducing validation F1 ($0.7125$).
- At higher temperatures ($\tau \ge 0.10$), intra-class clusters expand, producing larger apparent margins on paper ($+0.1298$) but yielding poorer downstream linear separability.
- $\tau = 0.05$ achieved the highest downstream validation F1 score ($0.7326 \pm 0.0038$) and was selected as the frozen operating temperature for Stage 8.9.33.

---

## 3. INDEPENDENT TEST PERFORMANCE: CONTRASTIVE MODEL B

Evaluating Contrastive Model B (weighted logistic regression on the learned 128-dimensional projection space) on the held-out test cohort ($N=293$) at $\theta^* = 0.35$:
- **Overall Scream Recall:** 79.41% (Fails Gate 1: target $\ge 96.00\%$)
- **Hard-Negative FPR:** 8.38% (Fails Gate 2: target $\le 5.00\%$)
- **Shouted-Speech FPR:** 10.42% (Passes Gate 3: target $\le 15.00\%$)
- **P95 Latency:** 21.44 ms (Passes Gate 5: target $\le 25.00\text{ ms}$)

While contrastive pre-training improved shouting discrimination over raw baseline LR (10.42% vs 12.50%), it remained insufficient on its own to hit the 96% recall and 5% HN-FPR gates simultaneously.
