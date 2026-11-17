# STAGE 8.9.32 BASELINE INVENTORY & RESEARCH RECOVERY
## Historical Models, Multi-Resolution Candidates, and Production Reference State

**Project:** Festival Scream Detector  
**Stage:** 8.9.32  
**Operating Mode:** Isolated Research Only  
**Production Status:** STRICTLY FROZEN (Decision Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date:** November 2, 2026

---

## 1. Production Reference Baseline (Strictly Frozen)

| Property | Value / Location |
|---|---|
| Model Classifier File | `backend/models/scream_classifier.joblib` |
| SHA-256 Hash | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` |
| Metadata File | `backend/models/model_metadata.json` |
| SHA-256 Hash | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` |
| Test Predictions File | `backend/reports/test_predictions.csv` |
| SHA-256 Hash | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` |
| Stage 5 Test Evaluation | `backend/reports/stage5_test_evaluation.md` |
| SHA-256 Hash | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` |
| Production Classifier Architecture | L2-regularized Logistic Regression ($C=1.0$) trained on 1024-dim mean-pooled YAMNet embeddings |
| Production Operational Threshold | **0.3500** (Frozen) |

---

## 2. Research Models Recovered from Stages 8.9.28 – 8.9.31

### 2.1 Model C (1D Temporal CNN)
- **Artifact Location:** `backend/research/stage_8_9_28/`
- **Architecture:** 1D Convolutional Neural Network (Conv1D + MaxPool + Dense + Dropout)
- **Input Dimension:** 70 frames $\times$ 16-dim temporal phonation features (F0, harmonic ratio, formant peaks, LPC residual energy)
- **Nominal Temporal Context:** 975 ms analysis window ($15,600\text{ samples}$ at $16\text{ kHz}$)
- **Role:** Evaluates phonation dynamics, harmonic stability, and high-energy spectral transitions.
- **Identified Failure Mode:** Highly vulnerable to zero-padding dilution when residual audio $< 975\text{ ms}$. Raw scores collapse toward $0.0076 - 0.0125$ on short recordings.

### 2.2 Candidate G (Micro-Resolution Burst Detector)
- **Architecture:** Logistic Regression on acoustic modulation & prominence features
- **Input Features:** `horn_prom_db`, `horn_ratio`, `temporal_entropy`, `crest_factor`, energy envelope peak-to-RMS ratio
- **Nominal Temporal Context:** 375 ms micro-resolution window ($6,000\text{ samples}$ at $16\text{ kHz}$ with 100 ms hop)
- **Role:** High-sensitivity detection of brief, sharp screams ($200 - 800\text{ ms}$).
- **Strengths:** 100% sensitivity ($6/6$) on short screams.
- **Weaknesses:** Higher false-positive rates on crowd cheering and excited high-pitched speech if unconstrained.

### 2.3 Model E (Multimodal 1058-dim Classifier)
- **Architecture:** Ensemble classifier trained on concatenated 1024-dim YAMNet embeddings and 34-dim acoustic profile vector.
- **Nominal Temporal Context:** 975 ms macro-resolution window.
- **Role:** Primary context-level classifier in Stage 8.9.28 and 8.9.29.

---

## 3. Stage 8.9.31 Multi-Resolution Fusion Baseline Reference

| Candidate | Name | Mathematical Formulation / Decision Rule | Stage 8.9.31 Short Scream Recall | Stage 8.9.31 Hard Negative FPR |
|---|---|---|---|---|
| **Candidate A** | Macro-Only Baseline | Historical Asymmetric Fusion E on 975 ms macro window | 16.67% (1/6) | 56.12% (55/98) |
| **Candidate B** | Candidate G Dominant | $\max(\text{Micro\_G}, \text{Macro\_Score})$ if $\text{Micro\_G} \ge 0.35$ | 100.00% (6/6) | 65.31% (64/98) |
| **Candidate C** | Duration-Aware Asymmetric | $w_G = 1.0 - 0.5 \cdot \min(1.0, \frac{\text{valid\_dur}}{0.975})$; $w_C = 0.5 \cdot \min(1.0, \frac{\text{valid\_dur}}{0.975})$ | **66.67% (4/6)** | 58.16% (57/98) |
| **Candidate D** | Dual-Resolution Max | $\max(\text{Micro\_Score}, \text{Macro\_Score})$ | 66.67% (4/6) | 61.22% (60/98) |
| **Candidate E** | Padding-Aware Fusion | $w_C = 0.5 \cdot (1.0 - \text{pad\_ratio})$; renormalizes component weights | **66.67% (4/6)** | 58.16% (57/98) |
| **Candidate F** | Conservative Branch Agreement | Requires both micro and macro branches $\ge 0.30$ to confirm detection | 33.33% (2/6) | **48.98% (48/98)** |

---

## 4. Problem Statement for Stage 8.9.32

Stage 8.9.31 proved that streaming buffer correction and dual-resolution processing resolve window underflow and quadruple short-scream recall. However, **acoustic classification errors on crowd cheering ($78.6\% - 82.1\%$) and infant crying ($85.7\%$) remain unacceptable**. 

Stage 8.9.32 targets the root cause: representation overlap in the underlying acoustic features. This will be addressed through dataset reconciliation, hard-negative mining, and contrastive representation learning evaluated against supervised baselines.
