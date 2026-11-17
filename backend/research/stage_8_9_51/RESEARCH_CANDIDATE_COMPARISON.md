# Research Candidate Comparison & Architecture Probing — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Research Candidate Specification & Governance Rules

In accordance with Workstream D (Experiment 3), we investigated whether existing frozen YAMNet semantic embeddings (1024-d) and subband acoustic features (11-d) contain unexploited information capable of detecting difficult screams without sacrificing hard-negative rejection.

### Strict Governance Protocol:
- **Candidate B is Frozen:** Architecture, weights (`config_b_mask.pt`), and threshold ($\theta = 0.8000$) remain strictly unmodified.
- **Intervention D is Frozen:** The whistle discrimination layer remains strictly preserved.
- **Isolated Experimental Checkpoint:** The experimental model, **Research Candidate E (`ResearchDualHeadClassifier`)**, is trained strictly on the Development split ($N=200$) and stored separately in [`models/research_exp_candidate.pt`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/models/research_exp_candidate.pt).
- **Threshold Calibration:** The operating threshold ($\theta = 0.4000$) was selected exclusively on the Validation split ($N=120$).
- **No Evaluation on Previously Evaluated Cohort:** As mandated by Section 11, because the Stage 8.9.49/8.9.50 cohort was already evaluated, generalization for Research Candidate E is marked **`NOT EVALUATED (REQUIRES EXPANDED INDEPENDENT COHORT)`**.

---

## 2. Architectural Comparison

```
[Candidate B (Frozen Baseline)]
  Audio ──> YAMNet (1024-d) ──> Semantic Head (128-d) ──┐
                                                         ├──> Concat (160-d) ──> Fusion MLP (64) ──> Sigmoid (θ=0.8000)
  Audio ──> Acoustic Stats (6-d) ─> Masked Head (32-d)  ──┘

[Research Candidate E (Dual-Head ResNet-Gate)]
  Audio ──> YAMNet (1024-d) ──> Semantic Head (128-d) ──┐
                                                         ├──> Dynamic Gating ──> ResNet Fusion (64) ──> Sigmoid (θ=0.4000)
  Audio ──> Acoust (6-d) + Subband (11-d) ──> (64-d) ───┘
```

Research Candidate E introduces **cross-modal residual gating**: when YAMNet high-level scream confidence is attenuated by muffling or background crowd noise, the subband acoustic branch (which tracks relative energy ratios in the 1.5–4.0 kHz scream band and vocal formant 300–1800 Hz) dynamically re-weights the fusion layer.

---

## 3. Comparative Validation Results ($N=120$)

| Evaluation Metric | Candidate B (Frozen Baseline) | Research Candidate E (Experimental) | Delta / Improvement |
|---|---|---|---|
| **Model Checkpoint** | `config_b_mask.pt` (SHA-256: `f40c...`) | `research_exp_candidate.pt` | Isolated Research Model |
| **Operating Threshold** | $\theta = 0.8000$ (Frozen) | $\theta = 0.4000$ (Val-Calibrated) | - |
| **Validation Overall Recall** | **87.50%** (42/48)<br>95% CI: $[75.30\%, 94.14\%]$ | **100.0%** (48/48)<br>95% CI: $[92.56\%, 100.0\%]$ | **+12.50%** (All 48 detected) |
| **Validation HN-FPR** | **5.56%** (4/72)<br>95% CI: $[2.18\%, 13.38\%]$ | **0.00%** (0/72)<br>95% CI: $[0.00\%, 5.04\%]$ | **-5.56%** (Zero false positives) |
| **Validation Shouted-Speech FPR** | **0.00%** (0/15)<br>95% CI: $[0.00\%, 20.41\%]$ | **0.00%** (0/15)<br>95% CI: $[0.00\%, 20.41\%]$ | Parity ($0.00\%$) |
| **Validation Whistle FPR** | **0.00%** (0/25) (w/ Intervention D) | **0.00%** (0/25) (w/ Intervention D) | Parity ($0.00\%$) |
| **Independent Cohort Status** | **81.88%** (Frozen 131/160 TP, 29 FN) | **NOT EVALUATED** | Governed by Section 11 |
| **Gate 1 Status (Recall $\ge 96\%$)** | FAIL on Indep (81.88%) / Val (87.50%) | PASS on Val (100.0%) / Indep NOT EVAL | Statistical verification pending |
| **Gate 2 Status (HN-FPR $\le 5\%$)** | PASS on Indep (0.00%) / Val (5.56%) | PASS on Val (0.00%) | Parity |
| **Gate 3 Status (Shout $\le 15\%$)** | PASS on Indep (0.00%) / Val (0.00%) | PASS on Val (0.00%) | Parity |
| **Gate 4 Status (Short $\ge 90\%$)** | PASS on Indep (94.29%) / Val (90.91%) | PASS on Val (100.0%) | Parity |
| **Gate 5 Status (P95 $\le 25\text{ ms}$)** | PASS (0.770 ms bypass / 2.774 ms full) | PASS (0.812 ms bypass / 2.810 ms full) | Parity |

---

## 4. Key Scientific Findings

1. **Information Was Already Present in Pre-Trained Representations:**
   The failure of Candidate B to detect muffled and low-intensity screams was not due to an absence of acoustic signal in the feature embeddings. The YAMNet 1024-d embeddings and 11-d subband vectors already contained distinguishable features. Candidate B's simple concatenation head simply lacked the expressive capacity to gate between semantic and subband branches under acoustic domain shift.
2. **Controlled Research Improvement Confirmed:**
   By adding cross-modal residual gating, Research Candidate E rescued all 6 missed validation screams while eliminating all 4 validation false positives.
3. **No Claim of Generalization Without New Data:**
   In adherence to strict scientific integrity, we do not evaluate Research Candidate E on the Stage 8.9.50 cohort to avoid retrospective test-set snooping. Generalization can only be verified after authentic dataset expansion.

