# STAGE 8.9.34 — JOINT OPTIMIZATION & UNIFIED ARCHITECTURE REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.34 — Temporal Context Modeling, Infant-Cry Discrimination & SNR-Adaptive Scream Detection  
**Operating Mode:** Machine Learning Research & Systems Architecture  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** November 2, 2026  

---

## 1. THE COMBINED TSA-DUALENCODER ARCHITECTURE

Checkpoint 5 investigated whether fusing temporal sequence modeling (Phase 2), infant-cry periodicity suppression (Phase 3), and SNR-adaptive conditioning (Phase 4) into a single unified architecture could simultaneously overcome both failure modes without mutual interference.

```
                    ┌─────────────────────────────────────────────────┐
                    │            Multi-Window Audio Frames            │
                    └────────────────────────┬────────────────────────┘
                                             │
                   ┌─────────────────────────┴────────────────────────┐
                   ▼                                                  ▼
      [Path A: Semantic YAMNet]                           [Path B: Phonation Head]
       Sequence (3 x 1024-d)                               6-d Vocal + 6-d Mask
                   │                                                  │
                   ▼                                                  ▼
     SNR-Conditioned Projector                           Masked Phonation Projector
        Linear(1025 -> 256)                                 Linear(12 -> 64)
        Linear(256 -> 128)                                  Linear(64 -> 32)
                   │                                                  │
                   └─────────────────────────┬────────────────────────┘
                                             │ Concatenation (3 x 160-d)
                                             ▼
                             [Causal GRU Sequence Processor]
                                   GRU(160 -> 64-d)
                                             │
                                             ├────────────────────────┐
                                             ▼                        ▼
                                     [Scream Logit Head]     [Infant-Cry Gate]
                                       Linear(64 -> 1)        Sigmoid(160 -> 1)
                                             │                        │
                                             └───────────┬────────────┘
                                                         │
                                                         ▼
                                       Gated Logit: L * (1 - 0.45 * P_cry)
                                                         │
                                                         ▼
                                             Final Scream Probability
```

---

## 2. JOINT MULTI-TASK LOSS FUNCTION

The unified network was trained end-to-end on the training partition ($N=739$) using a compound multi-task objective:
$$\mathcal{L}_{\text{joint}} = \mathcal{L}_{\text{BCE}}(y, \hat{y}; w_{\text{pos}}=2.5) + 0.20 \cdot \mathcal{L}_{\text{BCE}}(y_{\text{cry}}, \hat{p}_{\text{cry}}) + 0.25 \cdot \mathcal{L}_{\text{SupCon}}(z_{\text{sem}}, y; \tau=0.05)$$
- **Classifier Loss ($\mathcal{L}_{\text{BCE}}$):** Optimized primary binary scream detection.
- **Auxiliary Cry Loss ($\mathcal{L}_{\text{BCE\_cry}}$):** Supervised the auxiliary infant-cry detector to accurately identify rhythmic crying bouts.
- **Contrastive Loss ($\mathcal{L}_{\text{SupCon}}$):** Preserved cluster compactification in the semantic projection space.

---

## 3. INDEPENDENT TEST PERFORMANCE COMPARISON

Evaluating all models on the held-out test cohort ($N=293$) at frozen $\theta^* = 0.35$:

| Architecture Configuration | Scream Recall | Hard-Negative FPR | Shouted-Speech FPR | Infant-Cry FPR | Crowd-Cheer FPR | F1 Score | P95 Latency | Final Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Dual-Encoder Baseline (Stage 8.9.33)** | **84.31%** | 7.85% | **8.33%** | 6.67% | 11.90% | **0.8473** | **18.57 ms** | **REJECTED** |
| **Temporal-Only (Candidate B GRU)** | 79.41% | **6.28%** | **8.33%** | 6.67% | **9.52%** | 0.8308 | 18.72 ms | **REJECTED** |
| **SNR-Adaptive Only** | **90.20%** | 15.18% | 18.75% | 13.33% | 16.67% | 0.8251 | 18.60 ms | **REJECTED** |
| **Combined TSA-DualEncoder (Stage 8.9.34)** | 80.39% | 6.81% | 10.42% | **6.67%** | 11.90% | 0.8325 | 20.07 ms | **REJECTED** |

---

## 4. SCIENTIFIC SYNTHESIS: THE FUNDAMENTAL ML PARETO FRONTIER

The results across Stage 8.9.33 and 8.9.34 demonstrate a **classic machine learning Pareto frontier** between scream sensitivity and hard-negative specificity in complex public audio:

1. **SNR Adaptation Increases Recall but Increases False Alarms:**
   Conditioning on background noise floors successfully elevated scream recall to $90.20\%$ (and $92.16\%$ at $+10\text{ dB}$), but directly doubled the hard-negative false positive rate ($15.18\%$).
2. **Temporal Modeling Suppresses False Alarms but Suppresses Marginal Screams:**
   Causal temporal recurrence effectively suppressed hard negatives (reducing HN-FPR to $6.28\%$, the best in the project's history), but inadvertently filtered out $4.9\%$ of genuine brief or masked screams.
3. **The Joint Outcome:**
   The unified TSA-DualEncoder balanced these forces ($80.39\%$ recall, $6.81\%$ HN-FPR), but could not simultaneously break through both $96\%$ recall and $5\%$ HN-FPR boundaries.
4. **Gate Determination:** Neither Gate 1 nor Gate 2 was satisfied. Final determination remains **REJECTED FOR PRODUCTION — RESEARCH ONLY**.
