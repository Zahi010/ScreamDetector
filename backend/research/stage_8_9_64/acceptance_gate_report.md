# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Formal Acceptance Gate Scorecard & Promotion Evaluation

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Formal Promotion Determination

This scorecard evaluates the Dual-Resolution Gated Architecture and false-positive suppression mechanisms investigated in Stage 8.9.64 against the authoritative Five Research Acceptance Gates.

> [!CAUTION]
> **FORMAL GOVERNANCE RULING: ZERO PRODUCTION PROMOTION.**
> Production promotion is **CATEGORICALLY DENIED**.
> 
> While Gate 4 (Short-Scream Recall = 98.50%) and Gate 5 (Model-Only Latency P95 = 0.81 ms) pass decisively, Gate 1 (Overall Recall = 94.36% < 96.0%) and Gate 2 (FPR = 21.37% > 5.0% on baseline; 4.27% on Variant 6 at the cost of overall recall) fail to satisfy requirements concurrently.
> 
> Baseline production assets, weights, feature extractors, and reference configurations remain **STRICTLY FROZEN BIT-FOR-BIT**.

---

## 2. Acceptance Gate Scorecard

```
Authoritative Five Research Acceptance Gates Scorecard
┌──────────────────────────────────────┬──────────┬──────────────────────┬──────────────────────┬────────────┐
│ Acceptance Gate                      │ Standard │ Baseline Dual-Res    │ Variant 6 Full Stack │ Final Gate │
│                                      │          │ (Development N=312)  │ (Development N=312)  │ Status     │
├──────────────────────────────────────┼──────────┼──────────────────────┼──────────────────────┼────────────┤
│ Gate 1: Overall Recall               │ >= 96.0% │ 94.36% [90.9%, 97.4%]│ 87.69%               │ FAILED     │
│ Gate 2: False Positive Rate (FPR)    │ <= 5.0%  │ 21.37% [14.1%, 29.0%]│  4.27%               │ FAILED *   │
│ Gate 3: Paired Statistical Super.    │ p < 0.01 │ p < 0.0001 on short  │ Inconclusive overall │ FAILED     │
│ Gate 4: Short-Scream Recall (<1.0s)  │ >= 90.0% │ 98.50% [96.0%, 100%] │ 94.74%               │ PASSED     │
│   * Diagnostic Ultra-Short (<=0.50s) │ Inform.  │ 100.00% (51/51)      │ 98.04% (50/51)       │ (PASSED)   │
│ Gate 5: Model-Only Latency P95       │ <= 25 ms │  0.81 ms (1 stream)  │  0.81 ms (1 stream)  │ PASSED     │
│                                      │          │  0.93 ms (8 streams) │  0.93 ms (8 streams) │ PASSED     │
└──────────────────────────────────────┴──────────┴──────────────────────┴──────────────────────┴────────────┘
* Note: While Variant 6 achieves Gate 2 FPR (4.27%), it causes overall recall to fall to 87.69%, failing Gate 1.
```

---

## 3. Detailed Audit by Gate

### Gate 1: Overall Recall ($\ge 96.0\%$) — FAILED
- **Baseline Result:** $94.36\%$ ($184/195$), with 95% Clustered Bootstrap Confidence Interval of $[90.86\%, 97.40\%]$. Because the point estimate and lower confidence bound are below $96.0\%$, Gate 1 fails.
- **Root Cause:** Missed positives ($FN = 11$) primarily involve muffled or low-amplitude vocal screams embedded in high environmental noise floors.

### Gate 2: False Positive Rate ($\le 5.0\%$) — FAILED (CONCURRENT PASS UNMET)
- **Baseline Result:** $21.37\%$ ($25/117$) raw development FPR (Clustered 95% CI: $[14.06\%, 28.97\%]$).
- **Suppression Result:** Variant 6 successfully drives FPR down to $4.27\%$ ($5/117$), satisfying the Gate 2 threshold in isolation. However, this suppression suppresses borderline sustained scream frames, pulling Gate 1 recall down to $87.69\%$. The model does not achieve simultaneous Gate 1 and Gate 2 compliance.

### Gate 3: Paired Statistical Superiority ($p < 0.01$) — FAILED
- Dual-resolution shows overwhelming statistical superiority over Candidate E1 specifically for short screams ($98.50\%$ vs $12.50\%$, McNemar paired test $p < 10^{-15}$). However, on full-length screams and hard negatives, Candidate E1 maintains lower FPR ($1.8\%$ vs $21.4\%$). Net superiority across all dimensions is not demonstrated.

### Gate 4: Short-Scream Recall ($\ge 90.0\%$ on Screams $< 1.00\,\text{s}$) — PASSED
- **Authoritative Definition:** Evaluated strictly on all positive screams with total clip duration $< 1.00$s ($N=133$).
- **Performance:** **$98.50\%$** ($131/133$), with a 95% Clustered Bootstrap Confidence Interval of **$[96.03\%, 100.00\%]$**.
- **Ultra-Short Diagnostic Subgroup:** On ultra-brief active bursts ($\le 0.50$s, $N=51$), recall is **$100.00\%$** ($51/51$).
- Gate 4 is fulfilled beyond doubt.

### Gate 5: Model-Only Forward Pass Latency P95 ($\le 25.0\,\text{ms}$) — PASSED
- **Performance:**
  - 1 Stream: P95 = **$0.807\,\text{ms}$** (Safety margin: $96.8\%$)
  - 8 Concurrent Streams: P95 = **$0.929\,\text{ms}$** (Safety margin: $96.3\%$)
- Complete end-to-end streaming latency (DSP + Model + Method F aggregation) is **$11.456\,\text{ms}$** (1 stream) and **$83.094\,\text{ms}$** (8 streams), well within the $500\,\text{ms}$ streaming budget.

---

## 4. Production Asset Integrity Certification

All 18 protected baseline assets verified bit-for-bit with zero drift:
- Production weights, checkpoints, DSP pipelines, and evaluation manifests remain 100% identical to baseline hashes.
- Promotion is formally vetoed.

