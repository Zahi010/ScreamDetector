# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Future Evaluation Cohort Preregistration & Governance Plan

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Governance & Anti-Leakage Protocol

To preserve evaluation integrity and prevent benchmark degradation, the $N = 1,050$ evaluation cohort will adhere to strict preregistration governance:

```
Preregistration Protocol Lifecycle:
[Target Acquisition] ──► [Legal & Lic. Audit] ──► [Double-Blind Annot.] ──► [SHA-256 Vault Freeze] ──► [Post-Freeze Eval]
   (>=600 groups)          (CC0/CC-BY only)        (Dual Raters, k>=0.85)     (Zero Dev Access)          (Frozen Checkpoint)
```

### 1.1 Five Invariant Rules of Preregistration:
1. **Zero Exposure During Optimization:** No candidate model, feature selection script, threshold tuner, or suppression hyperparameter may touch, inspect, or train on the $1,050$ cohort before the evaluation freeze.
2. **Permanent Quarantine Hashing:** The dataset manifest, PCM audio hashes, and cluster metadata must be committed to git alongside a signed SHA-256 digest prior to evaluation execution.
3. **Bit-Level Partition Isolation:** Zero audio file, waveform slice, or recording session from the development cohort ($N=312$), short-scream expansion manifest ($N=401$), or historical evaluation sets may enter the unexposed evaluation cohort.
4. **Mandatory Cluster Cap:** No single creator, uploader, or physical recording session may contribute more than $3$ recordings ($m \le 3$).
5. **Dual Metric Reporting:** Gate 4 must be evaluated exclusively against its authoritative definition ($\text{duration} < 1.00\,\text{s}$), with ultra-short ($\le 0.50\,\text{s}$) reported separately as an internal diagnostic subgroup.

---

## 2. Evaluation Cohort Composition & Acceptance Criteria

```
Pre-registered Evaluation Specifications (Target N = 1,050)
┌──────────────────────────────────────┬───────────────────┬────────────────────────────────────────────────────────┐
│ Acceptance Gate                      │ Threshold         │ Statistical Certification Requirement                  │
├──────────────────────────────────────┼───────────────────┼────────────────────────────────────────────────────────┤
│ Gate 1: Overall Recall               │ >= 96.0%          │ Lower bound of 95% Clustered Bootstrap CI >= 95.0%     │
│ Gate 2: False Positive Rate (FPR)    │ <= 5.0%           │ Upper bound of 95% Clustered Bootstrap CI <= 5.0%      │
│ Gate 3: Paired Statistical Superior. │ p < 0.01          │ Paired cluster bootstrap vs baseline Candidate E1      │
│ Gate 4: Short-Scream Recall (<1.0s)  │ >= 90.0%          │ Lower bound of 95% Clustered Bootstrap CI >= 88.0%     │
│ Gate 5: Model-Only Latency P95       │ <= 25.0 ms        │ P95 forward pass across 1, 2, 4, 8 concurrent streams  │
└──────────────────────────────────────┴───────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Discrepancy Prevention & Protocol Closure

Any deviation between observed results and preregistered gate definitions will trigger an immediate forensic audit. In particular, proxy substitution (e.g. evaluating active burst length in lieu of total clip duration) is strictly forbidden.

