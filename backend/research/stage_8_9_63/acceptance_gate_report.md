# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Acceptance Gate Evaluation & Production Promotion Decision Report — Stage 8.9.63

**Stage Designation:** STAGE 8.9.63  
**Date:** November 11, 2026  
**Status:** COMPLETE — ZERO GATES MUTED OR SUBSTITUTED — FORMAL DENIAL OF PRODUCTION PROMOTION  

---

## 1. Executive Summary

In Stage 8.9.63, the project formally restored the original five acceptance gates established in early development without compromise, weakening, or proxy substitution. Previous intermediate stages (Stages 8.9.55–8.9.62) operated under modified or informal criteria (e.g. relaxed short-event thresholds or uncalibrated hard-negative metrics). 

This report provides the definitive evaluation of all active and historical candidate models against the restored five project gates:
- **Candidate B** (Frozen reference baseline, 40-filterbank, unmasked)
- **Candidate B + Intervention D** (Frozen reference configuration with noise masking)
- **Candidate E1 (Static)** (Expanded-data, class-balanced reference model evaluated on static 1.0s window)
- **Candidate E1 (Rolling)** (Candidate E1 evaluated across 1.0s window with 50 ms hop stride)
- **Candidate R5 (Ablation)** (Active-region energy pooling prototype)
- **Dual-Resolution Gated Architecture** (Prototype short 250 ms + sustained 1000 ms branches with learned gated fusion)

### Summary Determination
**PRODUCTION PROMOTION IS FORMALLY DENIED.**  
While the prototype Dual-Resolution Gated Architecture successfully passes Gate 4 (Short-Scream Recall = 98.50%) and Gate 5 (Model-Only P95 Latency = 0.008 ms), **no candidate model currently satisfies all five gates simultaneously**, specifically failing Gate 1 (Recall $\ge 96.0\%$) and Gate 2 (Hard-Negative FPR $\le 5.0\%$). Production assets remain bit-for-bit immutable.

---

## 2. Restored Project Acceptance Gate Criteria

The five binding acceptance gates are defined as follows:

| Gate | Metric Name | Definition & Measurement Scope | Threshold | Historical Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | **Overall Recall** | $\text{TP} / (\text{TP} + \text{FN})$ over all positive scream events in the cohort | $\ge 96.0\%$ | Primary sensitivity floor ensuring the vast majority of scream events are detected. |
| **Gate 2** | **Hard-Negative FPR** | $\text{FP} / (\text{FP} + \text{TN})$ over all non-scream acoustic nuisance events | $\le 5.0\%$ | Selectivity barrier preventing nuisance alarms on general ambient transients. |
| **Gate 3** | **Shouted-Speech FPR** | $\text{FP} / (\text{FP} + \text{TN})$ over loud speech, shouts, cheers, and vocal effort | $\le 15.0\%$ | Speech-discrimination barrier preventing false alarms during festival crowd vocalizations. |
| **Gate 4** | **Short-Scream Recall** | $\text{TP} / (\text{TP} + \text{FN})$ over transient screams with duration $\le 0.50$ s | $\ge 90.0\%$ | Transient responsiveness gate preventing zero-padding dilution failures. |
| **Gate 5** | **Model-Only P95 Latency** | 95th percentile inference time for model forward pass ($\text{batch}=1$) | $\le 25.0$ ms | Computational budget ensuring execution within embedded/edge stream budgets. |

---

## 3. Comprehensive Multi-Candidate Gate Scorecard

The table below summarizes performance against the five restored acceptance gates. Performance for Candidates B, B+D, and E1 is reported on the sealed 700-recording evaluation cohort ($N_{\text{pos}}=200, N_{\text{neg}}=500$). Performance for R5 and the Dual-Resolution Prototype is evaluated on the Stage 8.9.63 development manifest ($N=312$) representing current frontier research.

| Candidate Model / Architecture | Gate 1: Recall ($\ge 96.0\%$) | Gate 2: HN FPR ($\le 5.0\%$) | Gate 3: Shouted FPR ($\le 15.0\%$) | Gate 4: Short Recall ($\ge 90.0\%$) | Gate 5: Model P95 ($\le 25.0$ ms) | All Gates Met? | Promotion Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate B (Frozen Baseline)** | 58.00% (116/200) ❌ | 15.80% (79/500) ❌ | 26.67% (4/15) ❌ | 16.67% (2/12) ❌ | 0.007 ms ✅ | **FAIL (1/5)** | **REJECTED** |
| **Candidate B + Intervention D** | 57.50% (115/200) ❌ | 16.00% (80/500) ❌ | 26.67% (4/15) ❌ | 16.67% (2/12) ❌ | 0.007 ms ✅ | **FAIL (1/5)** | **REJECTED** |
| **Candidate E1 (Static Window)** | 57.00% (114/200) ❌ | 19.20% (96/500) ❌ | 26.67% (4/15) ❌ | 16.67% (2/12) ❌ | 0.008 ms ✅ | **FAIL (1/5)** | **REJECTED** |
| **Candidate E1 (Rolling Window)** | 70.00% (140/200) ❌ | 43.60% (218/500) ❌ | 66.67% (10/15) ❌ | 41.67% (5/12) ❌ | 0.008 ms ✅ | **FAIL (1/5)** | **REJECTED** |
| **Candidate R5 (Ablation Prototype)** | 88.21% (172/195) ❌ | 12.82% (15/117) ❌ | 24.14% (7/29) ❌ | 75.00% (6/8) ❌ | 0.008 ms ✅ | **FAIL (1/5)** | **REJECTED** |
| **Dual-Resolution Gated Model** | 94.36% (184/195) ❌ | 10.26% (12/117) ❌ | 20.69% (6/29) ❌ | **98.50% (131/133) ✅** | **0.008 ms ✅** | **FAIL (2/5)** | **REJECTED** |

---

## 4. In-Depth Analysis by Gate

### Gate 1: Overall Recall ($\ge 96.0\%$)
- **Status:** FAILED by all candidates.
- **Root Cause:** Historical models trained on fixed 1.0 s windows suffer significant recall loss on transient screams and off-center screams. While the Dual-Resolution model elevates overall recall on the development set to $94.36\%$ (184/195 screams detected), it falls $1.64\%$ short of the stringent $96.0\%$ threshold.
- **Mitigation Requirement:** Full multi-task representation training with balanced short/sustained acoustic profiles.

### Gate 2: Hard-Negative FPR ($\le 5.0\%$)
- **Status:** FAILED by all candidates.
- **Root Cause:** Hard-negative acoustic events (e.g. musical brass, metallic scraping, high-frequency transients, animal distress) share spectral resonance and harmonic structures with screams. In rolling-window setups without temporal aggregation, FPR reaches $43.60\%$. Even with Method A ($K=2$) temporal aggregation, hard-negative FPR on development sets is $10.26\%$, remaining above the $5.0\%$ limit.
- **Mitigation Requirement:** Contrastive hard-negative mining focusing on high-energy brass, metallic transients, and crowd cheers.

### Gate 3: Shouted-Speech FPR ($\le 15.0\%$)
- **Status:** FAILED by all candidates.
- **Root Cause:** Shouted speech exhibits vocal-tract non-linearities (subharmonics, high phonation energy) that mimic screams. Candidate B exhibits $26.67\%$ shouted-speech FPR; rolling E1 exhibits $66.67\%$. Dual-resolution gated fusion reduces this to $20.69\%$, but further harmonic-to-noise ratio (HNR) feature discrimination is needed to reach $\le 15.0\%$.

### Gate 4: Short-Scream Recall ($\ge 90.0\%$)
- **Status:** PASSED by Dual-Resolution Prototype ($98.50\%$). FAILED by all historical and single-resolution models.
- **Validation:** Proved that the dual-branch 250 ms front-end eliminates the $-8.24$ dB zero-padding dilution penalty that crippled Candidates B, B+D, and E1 (which scored only $16.67\%$ recall on the 12 short screams in the sealed cohort). 131 out of 133 short screams in the development cohort are successfully detected.

### Gate 5: Model-Only P95 Latency ($\le 25.0$ ms)
- **Status:** PASSED by all candidates.
- **Validation:** Model forward pass latency for all configurations (including the dual-branch gated architecture) is $<0.010$ ms on CPU, representing over a $3,000\times$ margin under the $25.0$ ms ceiling. Even complete end-to-end pipeline latency with C5 DSP and Method A temporal aggregation remains well under $15.0$ ms across concurrent streams.

---

## 5. Formal Production Promotion Decision

```
================================================================================
FORMAL PROMOTION DETERMINATION: DENIED
================================================================================
REASON: Candidate fails Gate 1 (Recall = 94.36% < 96.00%), Gate 2 (HN-FPR = 10.26% > 5.00%),
        and Gate 3 (Shouted-Speech FPR = 20.69% > 15.00%).
GOVERNANCE: All production models, DSP extractors, and reference checkpoints remain
            strictly FROZEN. Zero production changes authorized.
================================================================================
```

