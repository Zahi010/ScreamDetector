# STAGE 8.9.34 — FINAL INDEPENDENT EVALUATION & CANDIDATE ACCEPTANCE AUDIT

**Project:** Festival Scream Detector  
**Stage:** 8.9.34 — Temporal Context Modeling, Infant-Cry Discrimination & SNR-Adaptive Scream Detection  
**Operating Mode:** Offline-First Machine Learning Research & Validation Audit  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Partition:** Authoritative Independent Held-Out Test Partition ($N=293$, 102 Screams, 191 Hard Negatives across 111 Source Groups)  
**Operating Threshold:** Validation-Frozen Operating Threshold $\theta^* = 0.3500$  
**Audit Date:** November 2, 2026  

---

## 1. PREDEFINED ACCEPTANCE GATES

Every candidate model must simultaneously satisfy all five predefined acceptance gates on the exact same held-out test cohort ($N=293$):
1. **Gate 1 — Overall Scream Recall:** $\ge 96.00\%$
2. **Gate 2 — Hard-Negative False-Positive Rate (HN-FPR):** $\le 5.00\%$
3. **Gate 3 — Shouted-Speech False-Positive Rate (Shout-FPR):** $\le 15.00\%$
4. **Gate 4 — Short-Scream Recall ($< 1.0\text{ s}$):** $\ge 90.00\%$
5. **Gate 5 — Computational P95 Latency:** $\le 25.00\text{ ms}$ per 100 ms audio hop

---

## 2. OFFICIAL CANDIDATE ACCEPTANCE MATRIX

| Candidate Model | Recall ($\ge 96\%$) | HN-FPR ($\le 5\%$) | Shout-FPR ($\le 15\%$) | Short Recall ($\ge 90\%$) | P95 Latency ($\le 25\text{ ms}$) | Final Determination |
|---|---:|---:|---:|---:|---:|---|
| **Dual-Encoder Baseline (8.9.33)** | 84.31% [FAIL] | 7.85% [FAIL] | 8.33% [PASS] | 80.00% [FAIL]* | 18.57 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Candidate B (Causal GRU)** | 79.41% [FAIL] | 6.28% [FAIL] | 8.33% [PASS] | 80.00% [FAIL]* | 18.72 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Candidate C (Causal TCN)** | 78.43% [FAIL] | 6.28% [FAIL] | 8.33% [PASS] | 80.00% [FAIL]* | 18.84 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Candidate D (Gated Aggregator)** | 80.39% [FAIL] | 6.81% [FAIL] | 8.33% [PASS] | 80.00% [FAIL]* | 18.64 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |
| **Combined TSA-DualEncoder (8.9.34)** | 80.39% [FAIL] | 6.81% [FAIL] | 10.42% [PASS] | 80.00% [FAIL]* | 20.07 ms [PASS] | **REJECTED FOR PRODUCTION — RESEARCH ONLY** |

*\*Note on Short Recall: Evaluated on test set screams $<1.0\text{ s}$ ($N=5$, 4 detected = 80.00%, marked INSUFFICIENT SAMPLE SIZE). On the historical 6-sample forensic diagnostic cohort, recovery was 6/6 (100.00%).*

---

## 3. COMPREHENSIVE PERFORMANCE COMPARISON

Detailed classification and ranking metrics on the $N=293$ held-out test partition at $\theta^* = 0.35$:

| Metric | Dual-Encoder Baseline | Candidate B (GRU) | Candidate C (TCN) | Candidate D (Gated) | Combined TSA-DualEncoder |
|---|---:|---:|---:|---:|---:|
| **Recall (Sensitivity)** | **84.31%** | 79.41% | 78.43% | 80.39% | 80.39% |
| **Specificity** | 92.15% | **93.72%** | **93.72%** | 93.19% | 93.19% |
| **Precision** | 85.15% | **87.10%** | **86.96%** | 86.32% | 86.32% |
| **F1 Score** | **0.8473** | 0.8308 | 0.8247 | 0.8325 | 0.8325 |
| **Accuracy** | 89.42% | 88.74% | 88.40% | **88.74%** | **88.74%** |
| **Hard-Negative FPR** | 7.85% | **6.28%** | **6.28%** | 6.81% | 6.81% |
| **Shouted-Speech FPR** | **8.33%** | **8.33%** | **8.33%** | **8.33%** | 10.42% |
| **Crowd-Cheering FPR** | 11.90% | **9.52%** | **9.52%** | 11.90% | 11.90% |
| **Infant-Crying FPR** | **6.67%** | **6.67%** | **6.67%** | **6.67%** | **6.67%** |
| **ROC-AUC** | **0.9283** | 0.9024 | 0.8985 | 0.9015 | 0.9015 |
| **PR-AUC** | **0.8717** | 0.8425 | 0.8390 | 0.8410 | 0.8410 |
| **P95 Latency** | **18.57 ms** | 18.72 ms | 18.84 ms | 18.64 ms | 20.07 ms |

---

## 4. SCIENTIFIC AUDIT DETERMINATION

In strict compliance with validation audit rules:
1. All five metrics for each row originate from that exact candidate model.
2. All metrics were evaluated on the exact same authoritative independent test cohort ($N=293$).
3. Operating threshold ($\theta^* = 0.3500$) was frozen on validation data prior to test evaluation.
4. No gate was weakened.

Because no candidate simultaneously satisfied all five gates:
### **FINAL STATUS: REJECTED FOR PRODUCTION — RESEARCH ONLY.**

Production model weights, configuration, threshold (`0.3500`), and metadata remain strictly frozen.
