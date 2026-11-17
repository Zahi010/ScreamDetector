# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.65 — Authoritative Five-Gate Definition & Governance Correction Audit

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Governance Correction

In Stage 8.9.64, narrative scorecards erroneously listed "Paired Statistical Superiority ($p < 0.01$)" as Acceptance Gate 3. 

This audit formally corrects this documentation error and reaffirms the historical project governance established across Stages 8.9.40 through 8.9.63:
- **Paired statistical superiority is supplementary research evidence**, not an acceptance gate.
- **The true, authoritative Gate 3 is Shouted-Speech False Positive Rate ($\le 15.0\%$)**, designed to protect against false alarms triggered by loud festival vocalizations.
- **Gate 4 requires Short-Scream Recall $\ge 90.0\%$ on all screams with total duration $< 1.00$ second.** Ultra-short screams ($\le 0.50$s) remain a separate diagnostic subgroup and must never substitute for Gate 4.

---

## 2. Authoritative Five Acceptance Gates Matrix

```
Original Five Research Acceptance Gates Specification
┌────────┬──────────────────────────────────────┬──────────┬──────────────┬────────────────────────────────────────────────────────┐
│ Gate   │ Standard Metric Name                 │ Bound    │ Denominator  │ Operational & Scientific Purpose                       │
├────────┼──────────────────────────────────────┼──────────┼──────────────┼────────────────────────────────────────────────────────┤
│ Gate 1 │ Overall Scream Recall                │ >= 96.0% │ N_pos = 195  │ Emergency life-safety acoustic sensitivity baseline     │
│ Gate 2 │ Hard-Negative False Positive Rate    │ <= 5.0%  │ N_neg = 117  │ Bounded false alarm rate on complex acoustic backgrounds│
│ Gate 3 │ Shouted-Speech False Positive Rate   │ <= 15.0% │ N_shout = 5  │ Speech discrimination barrier against festival shouts  │
│ Gate 4 │ Short-Scream Recall (< 1.00s dur)    │ >= 90.0% │ N_short = 133│ Protection against rapid, fleeting panic bursts        │
│ Gate 5 │ Model-Only Inference Latency P95     │ <= 25 ms │ Per stream   │ Neural computation budget for real-time edge streaming │
└────────┴──────────────────────────────────────┴──────────┴──────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Policy on Proxy Metrics & Metric Integrity

1. **No Proxy Substitution:** Evaluating active burst length in place of annotated clip duration, or substituting ultra-short recall ($\le 0.50$s) for Gate 4 ($< 1.00$s), is strictly prohibited.
2. **Denominators Must Be Preserved:** Gate 1 ($N=195$), Gate 2 ($N=117$), and Gate 4 ($N=133$) denominators on the development cohort are fixed. Scores computed on truncated or filtered subsets will be rejected by [`original_gate_scorecard.py`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/scripts/original_gate_scorecard.py).
3. **No Gate Deletion or Redefinition:** All five gates must be reported concurrently for every evaluated candidate.

