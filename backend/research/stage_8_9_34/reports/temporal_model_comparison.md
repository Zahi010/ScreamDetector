# STAGE 8.9.34 — MULTI-WINDOW TEMPORAL CONTEXT MODELING REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.34 — Temporal Context Modeling, Infant-Cry Discrimination & SNR-Adaptive Scream Detection  
**Operating Mode:** Offline-First Machine Learning Research & Sequence Modeling  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** November 2, 2026  

---

## 1. INVESTIGATION & ARCHITECTURAL CANDIDATES

Stage 8.9.34 investigated whether multi-window temporal modeling could overcome frame-level acoustic confusion between screams, infant crying, and crowd cheering.
All temporal models were implemented using **causal processing** to ensure streaming viability (at step $t$, the model only accesses frames $\le t$, with zero future-frame lookahead).

### 1.1 Evaluated Temporal Aggregator Architectures
- **Baseline A (Stage 8.9.33 Dual-Encoder):** Static single-frame evaluation (1 frame = 975 ms).
- **Candidate B (Causal GRU):** A single-layer Gated Recurrent Unit (160 input dim, 64 hidden dim) processing a 3-window temporal evolution sequence $[f_{\text{p10}}, f_{\text{mean}}, f_{\text{max}}]$ representing baseline noise floor, central tendency, and peak burst.
- **Candidate C (Causal TCN):** A 2-block Temporal Convolutional Network with causal left-padding, kernel size 2, dilations $[1, 2]$, and residual skip connections.
- **Candidate D (Lightweight Gated Aggregator):** Gated Linear Unit (GLU) performing non-linear feature gating over temporal average pool.

---

## 2. INDEPENDENT TEST EVALUATION ($N=293$)

Evaluating each temporal architecture on the held-out test cohort ($N=293$, 102 screams, 191 hard negatives) at $\theta^* = 0.35$:

| Architecture | Scream Recall | Hard-Negative FPR | Shouted-Speech FPR | Infant-Cry FPR | Crowd-Cheer FPR | F1 Score | P95 Latency | Gate Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Dual-Encoder Baseline (8.9.33)** | **84.31%** | 7.85% | 8.33% | 6.67% | 11.90% | **0.8473** | 18.57 ms | **REJECTED** |
| **Candidate B (Causal GRU)** | 79.41% | **6.28%** | 8.33% | 6.67% | **9.52%** | 0.8308 | 18.72 ms | **REJECTED** |
| **Candidate C (Causal TCN)** | 78.43% | **6.28%** | 8.33% | 6.67% | **9.52%** | 0.8247 | 18.84 ms | **REJECTED** |
| **Candidate D (Gated Aggregator)**| 80.39% | 6.81% | 8.33% | 6.67% | 11.90% | 0.8325 | 18.64 ms | **REJECTED** |

---

## 3. AUDIT FINDINGS: TEMPORAL TRADE-OFFS

1. **Hard-Negative FPR Reduction:** Temporal context modeling successfully lowered the aggregate hard-negative FPR from **7.85%** to **6.28%** in Candidate B (GRU) and Candidate C (TCN).
2. **Cheering False Alarm Suppression:** Crowd cheering false alarms dropped from 11.90% to 9.52% because rhythmic clapping and stadium chanting were filtered by causal sequence recurrence.
3. **The Temporal Trade-Off Penalty:** Introducing multi-window temporal causal constraints resulted in a **$4\text{--}6\%$ drop in overall scream recall** (from 84.31% down to 79.41% in GRU and 78.43% in TCN). Masked, low-energy, and brief screams that triggered marginal frame activations were suppressed by the temporal filter because they lacked extended sequential energy continuity.
4. **Computational Efficiency:** All temporal aggregators added $<0.30\text{ ms}$ to neural forward passes, maintaining P95 latency well within the 25 ms gate ($18.6\text{--}18.8\text{ ms}$).
