# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Architecture Research Decision & Model Governance Ruling

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date of Ruling:** 2026-11-14  
**Ruling Authority:** Senior Research Systems & Quality Engineer  
**Binding Architecture Decision:** **`NO NEW ARCHITECTURE TRAINING IN STAGE 74 — PRESERVE CANDIDATE 71-D`**

---

## 1. Executive Summary & Core Principle

In accordance with Stage 8.9.74 research governance, large-scale model retraining or exploratory neural architecture tournaments are strictly prohibited unless six prerequisite scientific conditions are satisfied.

Stage 8.9.73 evaluated a complex hierarchical vocalization architecture (Candidates 73-A and 73-B). The empirical results established that:
- Pure neural routing without acoustic vetoes (**Candidate 73-A**) suffered catastrophic shouted-speech leakage (**27.27% FPR**, failing Gate 3).
- Adding calibrated vetoes to the hierarchical model (**Candidate 73-B**) produced a classification outcome 100% identical to Candidate 71-D, while introducing a **+30% CPU latency overhead** (0.542 ms vs 0.370 ms).
- Relaxing the distress veto (**Candidate 73-C**) recovered 2 child screams but pushed shouted-speech FPR to **17.05%**, failing Gate 3.

---

## 2. Formal Evaluation of the Six Mandatory Pre-Conditions

| # | Mandatory Pre-Condition | Verification Finding | Compliance Status |
|---|---|---|:---:|
| 1 | **Reproduction Success** | Candidate 71-D, 73-A, 73-B, and 73-C metrics were independently reproduced from binary weights and cache arrays bit-for-bit. | **SATISFIED** |
| 2 | **Dataset Provenance Established** | Provenance audit revealed that the Stage 60 prospective cohort ($N=700$) was already unsealed and evaluated in Stage 61. Zero unexposed prospective test sets currently exist. | **UNMET** |
| 3 | **Annotation Taxonomy Clarity** | Ground-truth audit revealed that 37.5% of errors represent forced binary ambiguity (theatrical shouts and vocal gasps). Training new models on noisy labels risks fitting annotation artifacts. | **UNMET** |
| 4 | **Specific Failure Mode Identified** | Primary failure modes are low-SNR crowd masking (-6 dB) and low auditory roughness in prepubescent child screams. | **SATISFIED** |
| 5 | **Falsifiable Architectural Hypothesis** | Stage 73 disproved the hypothesis that hierarchical neural heads can decouple screams from shouts without acoustic domain vetoes. | **UNMET** |
| 6 | **Uncontaminated Test Cohort Available** | Because Stage 60 was previously accessed and Stage 54 is exposed development data, any new model training would overfit without an untouched test set. | **UNMET** |

**Conclusion:** 4 out of the 6 mandatory pre-conditions are **UNMET**. Proceeding with new model training under these conditions would violate scientific protocol and produce ungeneralizable overfitting.

---

## 3. Head-to-Head Candidate Evidence Summary

| Candidate Identifier | Core Innovation | Overall Recall | Real Recall | Synth Recall | HN FPR | Shout FPR | Short Recall | CPU P95 Latency | Operational Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate 71-D** | **Dual-Res Gated + 3-Veto & Flux-Conditioned Rescue** | **82.83%** | **88.75%** | **57.89%** | **8.06%** | **14.77%** | **94.87%** | **0.370 ms** | **ACTIVE FROZEN CHAMPION (Retained)** |
| **Candidate 73-A** | Hierarchical 3-Class Vocal Head (No Vetoes) | 81.82% | 87.50% | 57.89% | 10.48% | **27.27%** | 92.31% | 0.465 ms | **REJECTED** (Gate 3 Violation: 27.27% FPR) |
| **Candidate 73-B** | Hierarchical Head + Calibrated Vetoes | 82.83% | 88.75% | 57.89% | 8.06% | 14.77% | 94.87% | 0.542 ms | **REJECTED** (+30% Latency with 0% Accuracy Gain) |
| **Candidate 73-C** | Candidate 71-D with Relaxed Child Distress Veto | 84.85% | 91.25% | 57.89% | 8.06% | **17.05%** | 94.87% | 0.370 ms | **REJECTED** (Gate 3 Violation: 17.05% FPR) |

---

## 4. Final Research Governance Directive

1. **Candidate 71-D Remains Active Frozen Champion:** Checkpoint `models/candidate_71_frozen.pt` (SHA-256: `e4314990...`) remains the project's active research champion.
2. **Prioritization of Data Quality Over Architecture:** Research focus must shift from hyperparameter tuning and model tweaking to acquiring clean, diverse, multi-reviewer annotated datasets featuring genuine child vocalizations and verified festival ambient noise.
3. **Production Status:** Non-certified laboratory research prototype. Production promotion is strictly prohibited.

