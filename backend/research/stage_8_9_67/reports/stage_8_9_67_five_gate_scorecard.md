# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 FIVE-GATE SCORECARD: Formal Acceptance Matrix, Compliance Verification & Authoritative Verdict

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Executive Summary & Authoritative Verdict

Stage 8.9.67 evaluates research candidates against the project's five mandatory acceptance gates. These criteria govern whether an acoustic model candidate may be considered for prospective unsealed evaluation and operational staging.

### Formal Stage Verdict
**`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**

- **Gate 1 (Overall Scream Recall):** **FAILED** (73.74% observed vs. $\ge 96.00\%$ target).
- **Gate 2 (Diverse Hard-Negative FPR):** **FAILED** (8.87% observed vs. $\le 5.00\%$ target).
- **Gate 3 (Shouted-Speech FPR):** **PASSED** (13.64% observed vs. $\le 15.00\%$ target).
- **Gate 4 (Short-Scream Recall):** **PASSED** (92.31% observed vs. $\ge 90.00\%$ target).
- **Gate 5 (Model-Only P95 Latency):** **PASSED** (0.397 ms observed vs. $\le 25.00$ ms target).

**Conclusion:** Production promotion remains **STRICTLY PROHIBITED**. Unsealing of the Stage 60 sealed evaluation cohort ($N=700$) remains **FROZEN**. Candidate 67-D is retained strictly as an active research artifact and engineering demonstration prototype.

---

## 2. Five-Gate Master Scorecard Table

Evaluation performed on the independent Stage 54 validation cohort ($N=311$ across 138 source groups: 99 screams, 88 shouted speech, 124 diverse hard negatives).

| Gate Identifier | Description | Mathematical Criteria | Target | Candidate 65-F (Ref) | Candidate 67-D (Champion) | Margin to Target | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Gate 1** | Overall Scream Recall | $\frac{\text{TP}}{\text{TP} + \text{FN}}$ | $\ge 96.00\%$ | 86.87% (86/99) | **73.74% (73/99)** | $-22.26\%$ | **FAIL** |
| **Gate 2** | Hard-Negative FPR | $\frac{\text{FP}_{\text{neg}}}{\text{FP}_{\text{neg}} + \text{TN}_{\text{neg}}}$ | $\le 5.00\%$ | 59.68% (74/124) | **8.87% (11/124)** | $+3.87\%$ | **FAIL** |
| **Gate 3** | Shouted-Speech FPR | $\frac{\text{FP}_{\text{shout}}}{\text{FP}_{\text{shout}} + \text{TN}_{\text{shout}}}$ | $\le 15.00\%$ | 48.86% (43/88) | **13.64% (12/88)** | $-1.36\%$ | **PASS** |
| **Gate 4** | Short-Scream Recall ($T < 1.0$s) | $\frac{\text{TP}_{\text{short}}}{\text{TP}_{\text{short}} + \text{FN}_{\text{short}}}$ | $\ge 90.00\%$ | 97.44% (38/39) | **92.31% (36/39)** | $+2.31\%$ | **PASS** |
| **Gate 5** | Model-Only P95 Latency | $\text{Percentile}_{95}(\Delta t_{\text{model}})$ | $\le 25.0\,\text{ms}$ | 0.812 ms | **0.397 ms** | $-24.60\,\text{ms}$ | **PASS** |

---

## 3. Deep-Dive Compliance Analysis by Gate

### Gate 1: Overall Scream Recall ($\ge 96.00\%$) — FAIL
- **Result:** 73.74% (73 detected out of 99 screams).
- **Analysis:** Candidate 67-D misses Gate 1 by 22.26 percentage points. The strict roughness gating ($R \ge 0.015$) necessary to suppress shouted speech rejected distant, low-SNR, and reverberant screams where background noise filled envelope modulations.
- **Remediation Plan:** Implement local SNR-normalized roughness scaling and an intermediate 500 ms branch in Stage 8.9.68 to recover distant screams without reopening shouting vulnerabilities.

### Gate 2: Diverse Hard-Negative FPR ($\le 5.00\%$) — FAIL
- **Result:** 8.87% (11 false alarms out of 124 non-scream clips).
- **Analysis:** While Candidate 67-D achieved an impressive 85.1% relative reduction in false positives compared to Candidate 65-F (which had 74 false alarms), 11 clips still triggered detection. The remaining triggers are concentrated in emergency sirens (4), brass overblowing (3), whistles (2), and intense chaotic laughter (2).
- **Remediation Plan:** Integrate cepstral peak prominence (CPP) and deterministic pitch trajectory tracking in Stage 8.9.68 to separate mechanical sirens and musical instruments from turbulent vocal distress.

### Gate 3: Shouted-Speech FPR ($\le 15.00\%$) — PASS
- **Result:** 13.64% (12 false alarms out of 88 shouted clips).
- **Analysis:** Gate 3 was the core focus of Stage 8.9.67. Candidate 65-F failed catastrophically at 48.86%. Candidate 67-D successfully brought this down to 13.64%, comfortably clearing the 15.00% ceiling.
- **Significance:** This marks the first time an acoustic architecture in this project has passed Gate 3 on an independent source-group partition.

### Gate 4: Short-Scream Recall ($< 1.0$s) ($\ge 90.00\%$) — PASS
- **Result:** 92.31% (36 detected out of 39 short screams).
- **Analysis:** The 250 ms short-event branch prevented temporal dilution, maintaining high sensitivity to abrupt startle shrieks and sudden vocal yelps.
- **Significance:** Gate 4 compliance was preserved despite the addition of aggressive false-positive suppression filters.

### Gate 5: Model-Only P95 Latency ($\le 25.0$ ms) — PASS
- **Result:** 0.397 ms.
- **Analysis:** Candidate 67-D's lightweight MLP architecture (9,985 parameters) processes a 39-dimensional feature vector in under 400 microseconds on a standard CPU, operating at 63x faster than the 25.0 ms ceiling.
- **Significance:** Guarantees zero latency bottleneck in real-time streaming pipelines.

---

## 4. Governance & Safety Restrictions

Because Gate 1 and Gate 2 failed:
1. **Production Assets Protected:** Production models (`scream_classifier.joblib`) remain strictly frozen.
2. **Sealed Cohort Remains Locked:** The Stage 60 sealed cohort ($N=700$, hash `9dfa4ced...`) will not be unsealed.
3. **No Promotion Permitted:** Candidate 67-D is classified as an experimental research candidate only.
4. **Research Demonstration Only:** Live web dashboard integration is strictly for internal engineering evaluation and peer review.

