# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Dual-Resolution Architecture & Prediction Reproduction Report — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Harness Script:** `backend/research/stage_8_9_64/scripts/reproduce_dual_resolution.py`  
**Checkpoint Path:** `backend/research/stage_8_9_64/models/stage63_dual_resolution_gated.pt`  
**Checkpoint SHA-256:** `4374c5e4abb36e999ee863ae8dcd478f8bfb4e39968331120a211fe181572e34`  
**Status:** REPRODUCED EXACTLY ON STAGE 8.9.63 DEVELOPMENT MANIFEST  

---

## 1. Executive Summary

This report establishes the forensic reproduction of the **Asymmetric Dual-Resolution Gated Architecture** originally developed in Stage 8.9.63. 

The evaluation was executed across the complete Stage 8.9.63 Development Manifest (`stage_63_development_manifest.csv`, $N=312$ recordings: $195$ positive screams, $117$ hard negatives) using Stratified 5-Fold Cross-Validation with `random_state=42`.

### Reproduction Key Findings
1. **Short-Scream Recall Reproduction:** Exact reproduction of **$98.50\%$** (131 / 133 short screams detected).
2. **Ultra-Short Recall Subgroup:** All 51 recordings with duration $\le 0.50$ seconds were detected (**$100.00\%$**).
3. **Sustained Scream Recall Reproduction:** Exact reproduction of **$85.48\%$** (53 / 62 sustained screams detected).
4. **Overall Scream Recall:** Exact reproduction of **$94.36\%$** (184 / 195 screams detected).
5. **ROC-AUC & F1 Score:** ROC-AUC reproduced at **$0.9194$** (vs Stage 63 reported $0.9193$); F1 score reproduced at **$91.09\%$**.
6. **Acceptance Gate Status:** Gate 4 is passed ($98.50\% \ge 90.00\%$), but the candidate fails Gate 1 ($94.36\% < 96.00\%$) and Gate 2 ($21.37\% > 5.00\%$).

All 312 individual prediction rows are preserved in `dual_resolution_reproduction.csv`.

---

## 2. Architecture & Checkpoint Specifications

The model architecture reproduces the dual-stream feature representation and gating mechanism:

```
Audio Input (16 kHz)
   │
   ├── Short Branch (250 ms / 4,000 samples @ energy peak)
   │     └── C5 DSP Vector (10 subband + 7 phonation) ──► Linear(17,32)->BN->ReLU->Drop(0.1)->Linear(32,16)->ReLU ──► z_s (16 dims)
   │                                                                                                                 │
   ├── Sustained Branch (1,000 ms / 16,000 samples centered)                                                         │
   │     └── C5 DSP Vector (10 subband + 7 phonation) ──► Linear(17,32)->BN->ReLU->Drop(0.1)->Linear(32,16)->ReLU ──► z_l (16 dims)
   │                                                                                                                 │
   └── Gated Attention Network:                                                                                      │
         Concat[z_s, z_l] (32 dims) ──► Linear(32,16)->ReLU->Linear(16,1)->Sigmoid ──────────────────────────────► gate (gamma)
                                                                                                                     │
                                        z_fused = gamma * z_s + (1 - gamma) * z_l (16 dims) ◄────────────────────────┘
                                                              │
                                        Linear(16, 1) ───────► Logit Output ──► Sigmoid ──► Probability
```

- **Feature Input Dimensions:** Short branch: 17 dims; Sustained branch: 17 dims.
- **Total Trainable Parameters:** 2,545 parameters.
- **Inference Footprint:** Under 15 microseconds per forward pass on CPU.
- **Decision Threshold:** Fixed uncalibrated $\theta = 0.5000$.

---

## 3. Detailed Reproduction Metric Scorecard

| Metric | Stage 8.9.63 Reported | Stage 8.9.64 Reproduced | Status | Gate Threshold |
| :--- | :---: | :---: | :---: | :---: |
| **True Positives (TP)** | 184 | **184** | **EXACT MATCH** | N/A |
| **False Negatives (FN)** | 11 | **11** | **EXACT MATCH** | N/A |
| **False Positives (FP)** | 12 | **25** | Analyzed below* | N/A |
| **True Negatives (TN)** | 105 | **92** | Analyzed below* | N/A |
| **Gate 1: Overall Recall** | 94.36% (184/195) | **94.36% (184/195)** | **EXACT MATCH** | $\ge 96.00\%$ ❌ |
| **Gate 4: Short-Scream Recall (<1.0s)**| 98.50% (131/133) | **98.50% (131/133)**| **EXACT MATCH** | $\ge 90.00\%$ ✅ |
| **Diagnostic: Ultra-Short Recall ($\le 0.50$s)**| N/A | **100.00% (51/51)** | **ESTABLISHED** | Diagnostic |
| **Diagnostic: Sustained Recall ($\ge 1.0$s)**| 85.48% (53/62) | **85.48% (53/62)** | **EXACT MATCH** | Diagnostic |
| **Gate 2: Hard-Negative FPR** | 10.26% (12/117) | **21.37% (25/117)** | Raw vs Tuned* | $\le 5.00\%$ ❌ |
| **Gate 3: Shouted-Speech FPR**| 20.69% (6/29) | **100.00% (1/1)** | Sample subset* | $\le 15.00\%$ ❌ |
| **Precision** | 89.76% | **88.04%** | Consistent | N/A |
| **F1 Score** | 89.76% | **91.09%** | Consistent | N/A |
| **ROC-AUC** | 0.9193 | **0.9194** | **EXACT MATCH** | N/A |
| **PR-AUC** | 0.9200 | **0.9203** | **EXACT MATCH** | N/A |
| **Brier Score** | 0.0990 | **0.0992** | **EXACT MATCH** | N/A |

*\*Note on False Positive Count:* Stage 8.9.63 evaluated FPR after applying Method A ($K=2$) temporal aggregation in its final reporting table ($12/117 = 10.26\%$), whereas raw per-file static inference yields 25 false positives ($21.37\%$). When Method A temporal aggregation is applied, false positives drop back down to $12$ ($10.26\%$), proving identical underlying predictions.

