# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Authoritative Acceptance-Gate Definition Audit & Dual-Metric Policy — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Status:** COMPLETE — AUTHORITATIVE GATE 4 DEFINITION RE-ESTABLISHED  

---

## 1. Executive Summary & Policy Determination

In Stage 8.9.63, narrative reports described Gate 4 as evaluating "transients $\le 0.50$ seconds," whereas early project specifications, historical benchmark reports (Stages 8.9.40–8.9.62), and evaluation manifests defined Gate 4 as:

$$\mathbf{\text{Gate 4: Short-Scream Recall } \ge 90.00\% \quad (\text{Recordings } < 1.00\text{ second in duration})}$$

A forensic audit of repository documentation, evaluation manifests, and dataset partitions was conducted via `scripts/audit_original_gate_definitions.py`.

### Authoritative Policy Determinations
1. **The authoritative Gate 4 definition requires evaluating all positive screams with duration $< 1.00$ second.**
2. **The narrower $\le 0.50$ second threshold was never formally approved or preregistered as a replacement for Gate 4.** It originated as an internal annotation subcategory (`ultra_short_scream`) to isolate the lower tail of brief acoustic bursts.
3. **To ensure complete governance integrity, Stage 8.9.64 implements a Dual-Metric Reporting Policy:**
   - **Metric 1 (Binding Gate 4):** Original Short-Scream Recall (Duration $< 1.00$ s). Must satisfy $\ge 90.00\%$.
   - **Metric 2 (Diagnostic Subgroup):** Ultra-Short Scream Recall (Duration $\le 0.50$ s). Evaluated as a separate granular diagnostic metric.
4. **No gate substitution is permitted.** Supplementary engineering budgets (e.g. 500 ms pipeline budget) or statistical separation claims ($p < 0.05$) shall never dilute or replace the five binding acceptance gates.

---

## 2. Historical Stage-by-Stage Forensic Ledger

| Stage | Document Audited | Recorded Gate 4 Definition | Population Scope | Gate Determination |
| :--- | :--- | :--- | :--- | :---: |
| **Stage 8.9.40** | `reports/ACCEPTANCE_GATES_REPORT.md` | Short-Scream Recall $\ge 90.0\%$ | Screams $< 1.0$ s ($N=65$) | **PASS** |
| **Stage 8.9.41** | `reports/ACCEPTANCE_GATES_REPORT.md` | Short-Scream Recall $\ge 90.0\%$ | Screams $< 1.0$ s ($N=96$) | **FAIL** (69.79%) |
| **Stage 8.9.47** | `ACCEPTANCE_GATES_AUDIT.md` | Short-Scream Recall $\ge 90.0\%$ | Screams $< 1.0$ s ($N=70$) | **FAIL** (84.29%) |
| **Stage 8.9.54** | `evaluation/acceptance_gate_report.md`| Short-Scream Recall $\ge 90.0\%$ | Screams $< 1.0$ s | **PASS** (94.87%) |
| **Stage 8.9.60** | `acquisition_manifest.csv` | `short_scream` ($<1.0$s) vs `ultra_short_scream` ($\le 0.50$s)| Two distinct annotation labels | Diagnostic |
| **Stage 8.9.61** | `acceptance_gate_report.md` | Short-Scream Recall ($< 1.0$s) $\ge 90.00\%$ | Sealed cohort ($N=69$) | **FAIL** (36.23%) |
| **Stage 8.9.62** | `acceptance_gate_report.md` | Short-Scream Recall ($< 1.0$s) $\ge 90.00\%$ | Sealed cohort ($N=69$) | **FAIL** (36.23%) |
| **Stage 8.9.63** | `original_acceptance_gate_restoration.md` | Short-Scream Recall ($< 1.0$s) $\ge 90.00\%$ | Restored original gate | Binding |

---

## 3. Discrepancy Resolution in Stage 8.9.63 Development Data

Stage 8.9.63 reported a short-scream recall of $98.50\%$ ($131 / 133$) and referred to these as "transients $\le 0.50$ seconds."

The audit of `stage_63_development_manifest.csv` ($N=312$) revealed:
- **Total Positive Screams:** $195$ recordings ($133$ short, $62$ sustained).
- **All 133 short-scream recordings have file duration $< 1.00$ second.**
- Within these 133 files, the annotated vocal scream events all have active burst duration $\le 0.50$ seconds ($r_1 \text{ max} = 0.454$ s, $r_2 \text{ max} = 0.475$ s).
- However, only $51$ recordings have total audio file duration $\le 0.50$ seconds; the remaining $82$ recordings range between $0.50$ s and $0.98$ s.
- In `train_dual_resolution_candidates.py` line 276, the code evaluated:
  `is_short.append(y == 1 and dur < 1.0)`
- Thus, Stage 8.9.63's empirical cross-validation actually measured the **authoritative Gate 4 population (duration $< 1.0$ s)**, but the report narrative loosely described them as "transients $\le 0.50$s."
- This confirms that Stage 8.9.63's $98.50\%$ result applies directly to the authoritative Gate 4 definition ($< 1.0$ s), while ultra-short performance ($\le 0.50$ s) must be separately tabulated.

---

## 4. Authoritative Restoration of All Five Project Acceptance Gates

The project officially operates under the five restored original acceptance gates:

| Gate | Authoritative Metric | Operational Threshold | Evaluation Scope | Rationale |
| :---: | :--- | :---: | :--- | :--- |
| **Gate 1** | **Overall Scream Recall** | **$\ge 96.00\%$** | All positive screams | Mandatory safety-critical sensitivity floor |
| **Gate 2** | **Hard-Negative False Positive Rate** | **$\le 5.00\%$** | Non-scream acoustic nuisance events | Selectivity barrier preventing nuisance alarms |
| **Gate 3** | **Shouted-Speech False Positive Rate** | **$\le 15.00\%$** | Loud speech, shouts, cheers, vocal effort | Acoustic veto preventing speech false alarms |
| **Gate 4** | **Short-Scream Recall ($< 1.0$s duration)** | **$\ge 90.00\%$** | Brief vocal screams ($< 1.00$ s) | Anti-dilution transient sensitivity |
| **Gate 5** | **Model-Only Neural Inference Latency (P95)** | **$\le 25.00$ ms** | Forward pass per window ($\text{batch}=1$) | Real-time edge stream budget |

### Supplementary Diagnostic Ledger (Non-Substitutable)
- **Ultra-Short Recall:** $\text{TP} / \text{Positives}$ on recordings $\le 0.50$ s (diagnostic tracking only).
- **Complete Pipeline P95:** End-to-end latency (DSP + NN + Temporal) $\le 500$ ms audio hop budget (system engineering context only).
- **Statistical Significance:** Paired McNemar $p < 0.05$ with Benjamini-Hochberg FDR control and cluster bootstrap bounds (methodological requirement for comparative claims, but not a replacement for operational gates).

