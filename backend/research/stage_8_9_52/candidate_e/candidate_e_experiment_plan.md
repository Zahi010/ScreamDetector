# Candidate E Experimental Evaluation & Benchmark Plan — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Experimental Objective & Governance Boundaries

Candidate E demonstrated impressive validation results ($100.0\%$ recall, $0.00\%$ HN-FPR on $N=120$), but under strict research governance, **it cannot be promoted or declared to have solved real-world generalization** without an independent evaluation on a newly acquired, untouched independent test cohort.

This document outlines the controlled protocol for evaluating Candidate E against Candidate B and Candidate B + Intervention D once the expanded dataset is assembled.

---

## 2. Experimental Candidates Under Comparison

| Candidate Model | Checkpoint Path | Architecture Type | Operating Threshold | Whistle Filter | Production Promotion Status |
|---|---|---|---|---|---|
| **Candidate B Baseline** | `stage_8_9_44/models/config_b_mask.pt` | Dual-Encoder (Concatenation) | $\theta = 0.8000$ (Frozen) | None | Frozen Research Reference |
| **Candidate B + Interv D** | `stage_8_9_44/models/config_b_mask.pt` | Dual-Encoder + Rejection Layer | $\theta = 0.8000$ (Frozen) | Intervention D Active | Current Reference Standard |
| **Candidate E (Experimental)** | `stage_8_9_51/models/research_exp_candidate.pt` | Dual-Head Cross-Modal Residual Gate | $\theta = 0.4000$ (Val-Tuned) | Standalone / Optional Interv D | Experimental Research Only |

---

## 3. Standardized Evaluation Protocol

1. **Identical Preprocessing:** All candidates must be fed identical audio frames (16 kHz mono, 0.96s window, 100 ms hop).
2. **Untouched Test Cohort:** Generalization must be measured exclusively on a newly acquired, source-group-independent test cohort that was never seen during development, validation, or previous stages.
3. **Threshold Immutability:** Operating thresholds must remain strictly frozen ($\theta = 0.8000$ for Candidate B; $\theta = 0.4000$ for Candidate E). No tuning on the test cohort is permitted.
4. **Mandatory Reporting Metrics:**
   - Overall Recall with 95% Wilson score CI
   - Hard-Negative FPR with 95% Wilson score CI
   - Shouted-Speech FPR with 95% Wilson score CI
   - Short-Scream Recall ($d \le 1.0\text{s}$) with 95% Wilson score CI
   - Subtype recalls: low-intensity, crowd-masked, sustained, distant/reverberant
   - Complete pipeline computational latency: P50, P95, P99, and Max over 2,000 runs
   - Independent source-group counts supporting each metric
5. **Acceptance Criteria:** A candidate is eligible for review only if it simultaneously satisfies all five original acceptance gates on the exact same test cohort.

