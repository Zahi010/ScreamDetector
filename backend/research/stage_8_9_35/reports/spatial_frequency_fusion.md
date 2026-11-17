# Stage 8.9.35 — Spatial & Frequency-Subband Fusion Report

**Stage:** 8.9.35 — Multi-Pathway Fusion Architecture & Comparative Evaluation  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Status:** Strictly Isolated Research  
**Artifact References:**
- Model Weights: `backend/research/stage_8_9_35/models/mp_fusion_model.pt`
- Training History: `backend/research/stage_8_9_35/training/mp_fusion_training_history.csv`
- Validation Sweep: `backend/research/stage_8_9_35/training/validation_threshold_sweep.csv`

---

## 1. Multi-Pathway Architecture: MP-FS-DualEncoder (Candidate D)

To systematically combine deep semantic representations, phonation dynamics, and physical frequency subband characteristics, the **Multi-Pathway Frequency-Subband Dual-Encoder (`MultiPathwayFusionModel`)** was designed and trained:

```
                      [ Raw Audio Input (16 kHz, 975 ms) ]
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
  [ YAMNet CNN ]             [ Acoustic/Phonation ]      [ Butterworth IIR ]
         |                            |                            |
    1024-dim                     6-dim + 6-mask                 11-dim
         |                            |                            |
  [ Semantic Head ]            [ Phonation Head ]          [ Subband Head ]
Linear(1024->256)             Linear(12->64)              Linear(11->32)
BatchNorm1d + ReLU            BatchNorm1d + ReLU          BatchNorm1d + ReLU
Linear(256->128)              Linear(64->32)              Linear(32->16)
L2-Normalize                  L2-Normalize                L2-Normalize
         |                            |                            |
      128-dim                       32-dim                       16-dim
         +----------------------------+----------------------------+
                                      |
                           [ Concatenation: 176-dim ]
                                      |
                             [ Multimodal MLP ]
                               Linear(176->64)
                                ReLU + Dropout
                                 Linear(64->1)
                                      |
                          [ Raw Logit Output: s ]
                                      |
                           [ Sigmoid Probability ]
```

### Multi-Task Supervised Contrastive Loss
Training optimized a composite objective combining Binary Cross-Entropy with Supervised Contrastive Loss ($\lambda = 0.30$):
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{BCE}}(s, y) + 0.30 \cdot \mathcal{L}_{\text{SupCon}}(\mathbf{z}_{\text{sem}}, \mathbf{z}_{\text{subband}}, y)$$
This dual objective pulls scream embeddings together while enforcing geometric separation from shouted speech and infant crying in the 128-d and 16-d latent spaces.

---

## 2. Validation Threshold Selection

Operating thresholds were tuned strictly on the validation partition ($N=293$, 79 screams, 214 negatives across 89 source groups) to prevent test contamination:

| Threshold $\theta$ | Val Recall | Val Precision | Val Specificity | Val HN-FPR | Val F1-Score | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0.30 | 88.61% | 66.04% | 83.18% | 16.82% | 0.7568 | Sub-optimal FPR |
| 0.35 | 83.54% | 70.21% | 86.92% | 13.08% | 0.7630 | Historical baseline |
| 0.40 | 78.48% | 73.81% | 89.72% | 10.28% | 0.7607 | Balanced |
| **0.43 (Frozen $\theta^*$)** | **78.48%** | **74.70%** | **90.19%** | **9.81%** | **0.7654** | **Optimal Val F1** |
| 0.50 | 73.42% | 77.33% | 92.06% | 7.94% | 0.7532 | Recall dropped |
| 0.60 | 60.76% | 82.76% | 95.33% | 4.67% | 0.7007 | Unacceptable recall |

The optimal validation threshold was frozen at **$\theta^* = 0.43$** before evaluating on the independent held-out test cohort.

---

## 3. Independent Comparative Evaluation on Test Cohort ($N=293$)

| Evaluation Metric | Dual-Encoder Baseline (Stage 8.9.33) | Subband RF (Candidate B) | Subband LR (Candidate C) | Multi-Pathway Fusion (Candidate D) | Research Gate Requirement |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Scream Recall** | 82.35% (84/102) | 73.53% (75/102) | 77.45% (79/102) | **89.22% (91/102)** | $\ge 96.00\%$ |
| **Hard-Negative FPR** | **6.28% (12/191)** | 14.14% (27/191) | 24.08% (46/191) | 9.95% (19/191) | $\le 5.00\%$ |
| **Shouted-Speech FPR** | **8.33% (4/48)** | 16.67% (8/48) | 18.75% (9/48) | 14.58% (7/48) | $\le 15.00\%$ |
| **Infant-Crying FPR** | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) | 6.67% (1/15) | Diagnostic |
| **Crowd-Cheering FPR** | **11.90% (5/42)** | 16.67% (7/42) | 38.10% (16/42) | 16.67% (7/42) | Diagnostic |
| **Short-Scream Recall (<1.0s)** | 80.00% (4/5) | 40.00% (2/5) | 60.00% (3/5) | **100.00% (5/5)** | $\ge 90.00\%$ |
| **Precision** | **87.50%** | 73.53% | 63.20% | 82.73% | Diagnostic |
| **F1-Score** | 0.8485 | 0.7353 | 0.6960 | **0.8585** | Diagnostic |
| **ROC-AUC** | 0.9285 | 0.8525 | 0.8335 | **0.9374** | Diagnostic |
| **PR-AUC** | 0.8717 | 0.7593 | 0.7279 | **0.8762** | Diagnostic |
| **Computational P95 Latency** | **18.57 ms** | 18.57 ms | 18.57 ms | 19.31 ms | $\le 25.00\text{ ms}$ |

---

## 4. Architectural Analysis & Scientific Verdict

1. **Recall Advancement:**
   - Multi-Pathway Fusion achieved **89.22% scream recall** (detecting 91 of 102 held-out screams), representing a substantial $+6.87\%$ improvement over the Stage 8.9.33 Dual-Encoder baseline (82.35%).
2. **Short-Scream Detection Gain:**
   - On short screams (<1.0s duration), Candidate D successfully detected **5 of 5 instances (100.0%)**, outperforming the baseline (80.0%). The physical subband pathway provides immediate energy ratio signals that fire even when temporal pooling over 975 ms dilutes the semantic embedding.
3. **The Specificity Trade-Off:**
   - The increased sensitivity to high vocal strain simultaneously increased false positives on crowd cheering (from 11.9% to 16.67%) and shouted speech (from 8.33% to 14.58%).
   - Total Hard-Negative FPR rose from 6.28% to 9.95%, breaching the strict $\le 5.00\%$ Gate 2 threshold.
4. **Final Gate Verdict:**
   - **Gate 1 (Recall $\ge 96\%$): FAIL (89.22%)**
   - **Gate 2 (HN-FPR $\le 5\%$): FAIL (9.95%)**
   - Gate 3 (Shout-FPR $\le 15\%$): PASS (14.58%)
   - Gate 4 (Short-Scream Recall $\ge 90\%$): PASS (100.0%, caveat: small sample size $N=5$)
   - Gate 5 (P95 $\le 25\text{ ms}$): PASS (19.31 ms)
   - **Conclusion:** Candidate D cannot be certified for production deployment. Determination: **REJECTED FOR PRODUCTION — RESEARCH ONLY**.
