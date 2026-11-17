# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.65 — Authoritative Five-Gate Compliance Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Gate 3 Restoration

This report formally reinstates the authoritative Five Research Acceptance Gates, replacing the incorrect "Paired Statistical Superiority" proxy introduced in Stage 8.9.64 with the true Gate 3: **Shouted-Speech False Positive Rate ($\le 15.0\%$)**.

The automated gate evaluation was executed via [`original_gate_scorecard.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/scripts/original_gate_scorecard.py).

---

## 2. Five-Gate Authoritative Compliance Matrix

```
Authoritative Acceptance Gate Evaluation (Baseline Dual-Resolution on Development N=312)
┌────────┬──────────────────────────────────────┬──────────┬──────────────┬──────────────┬──────────────────┬────────────┐
│ Gate   │ Metric Name                          │ Bound    │ Observed     │ Denominator  │ 95% Wilson CI    │ Status     │
├────────┼──────────────────────────────────────┼──────────┼──────────────┼──────────────┼──────────────────┼────────────┤
│ Gate 1 │ Overall Scream Recall                │ >= 96.0% │ 94.36%       │ 184 / 195    │ [90.2%, 96.8%]   │ FAIL       │
│ Gate 2 │ Hard-Negative FPR                    │ <= 5.0%  │ 21.37%       │ 25 / 117     │ [14.9%, 29.6%]   │ FAIL       │
│ Gate 3 │ Shouted-Speech FPR                   │ <= 15.0% │ 100.00%      │ 5 / 5        │ [56.5%, 100.0%]  │ FAIL       │
│ Gate 4 │ Short-Scream Recall (< 1.00s dur)    │ >= 90.0% │ 98.50%       │ 131 / 133    │ [94.7%, 99.6%]   │ PASS       │
│ Gate 5 │ Model-Only Inference Latency P95     │ <= 25 ms │ 0.807 ms     │ 1 Stream     │ N/A              │ PASS       │
│        │                                      │ <= 25 ms │ 0.929 ms     │ 8 Streams    │ N/A              │ PASS       │
└────────┴──────────────────────────────────────┴──────────┴──────────────┴──────────────┴──────────────────┴────────────┘

Diagnostic Subgroups (Informational Only):
- Ultra-Short Screams (<=0.50s Duration): 100.00% (51 / 51)
- Sustained Screams (>=1.00s Duration):    85.48% (53 / 62)
```

---

## 3. Governance Determination

> [!CAUTION]
> **GOVERNANCE RULING: ZERO PRODUCTION PROMOTION.**
> 
> The Baseline Dual-Resolution model fails Gate 1 ($94.36\% < 96.0\%$), Gate 2 ($21.37\% > 5.0\%$), and Gate 3 ($100.0\% > 15.0\%$).
> Production assets remain strictly frozen bit-for-bit.

