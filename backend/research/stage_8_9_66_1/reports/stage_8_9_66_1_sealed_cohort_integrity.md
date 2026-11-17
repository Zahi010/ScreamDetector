# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — SEALED EVALUATION COHORT INTEGRITY AUDIT
**Administrative Verification, Sealing Preservation, and Protocol Compliance**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
This audit evaluated the administrative integrity, cryptographic locking, and protocol readiness of the sealed evaluation assets in accordance with Section 7 of the stage charter.

### Critical Integrity Declarations:
1. **The Sealed Cohort Remains 100% Sealed:** Zero audio files from the sealed cohort were unsealed, decoded, or exposed to Candidate 65-F during this stage. No predictions, labels, or error identities were accessed.
2. **Physical Manifest vs. Planned Specification Discrepancy Resolved:**
   - The **current physical sealed manifest** committed to the repository is `backend/research/stage_8_9_60/future_evaluation_manifest.json`, containing exactly **$N=700$ recordings** ($200$ positive screams, $500$ hard negatives).
   - The **planned $N=1,050$ cohort** ($350$ positive, $700$ negative) is an **authoritative sampling allocation and preregistered study design** established in Stage 8.9.66. A finalized, physical 1,050-recording manifest has not yet been compiled to disk; it will be compiled from the unconsumed acquisition pool prior to formal unsealing.
3. **Zero Contamination from Development Set:** The 700 sealed recordings share **0 exact PCM hashes** and **0 source groups** with the $N=312$ development cohort used to train and tune Candidate 65-F.

---

## 3. Systematic 14-Point Governance Audit

| # | Governance Verification Item | Audit Findings | Evidence & Status |
|---|---|---|---|
| **1** | **Does the cohort manifest exist?** | YES. Physical manifest exists for $N=700$ cohort (`future_evaluation_manifest.json`). $N=1,050$ exists as an architectural allocation specification (`evaluation_cohort_allocation.csv`). | **VERIFIED (Delineated)** |
| **2** | **Is its SHA-256 recorded?** | YES. Full SHA-256 is `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`. Recorded in `future_evaluation_manifest.sha256`. | **VERIFIED** |
| **3** | **Are recording counts correct?** | YES. $N=700$ physically verified (200 screams, 500 negatives). Planned $N=1,050$ verified mathematically (350 screams, 700 negatives). | **VERIFIED** |
| **4** | **Are source-group assignments documented?** | YES. Exactly 412 unique source groups are documented with explicit IDs in the manifest. | **VERIFIED** |
| **5** | **Is positive/negative allocation consistent?** | YES. Historical evolution reconciled: Stage 60 Planning (240/810) $\rightarrow$ Stage 65 (550/500) $\rightarrow$ Stage 66 Reconciled Authoritative (350/700). | **VERIFIED** |
| **6** | **Are source groups separated from development?** | YES. Exactly 0 of the 412 sealed source groups exist in the $N=312$ development set. | **VERIFIED (Zero Overlap)** |
| **7** | **Are duplicate/excerpt relationships accounted for?** | YES. Fully cataloged in `duplicate_and_excerpt_relationships.csv` (SHA-256: `f0e602520e...`). | **VERIFIED** |
| **8** | **Are licenses documented?** | YES. 100% of files have documented CC0, CC-BY-3.0, or CC-BY-4.0 licenses. | **VERIFIED** |
| **9** | **Is annotation quality documented?** | YES. Double-blind dual annotation with senior adjudication; Cohen's $\kappa = 0.9561$ recorded in `annotation_quality_summary.json`. | **VERIFIED** |
| **10** | **Is the evaluation protocol preregistered?** | YES. Published in `backend/research/stage_8_9_66/future_evaluation_preregistration.md`. | **VERIFIED** |
| **11** | **Are the inference scripts frozen?** | YES. `stage_8_9_66/scripts/reproduce_candidate_65f.py` is frozen (SHA-256: `f78d781619...`). | **VERIFIED** |
| **12** | **Is candidate checkpoint hash frozen?** | YES. Full SHA-256 recorded: `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab`. | **VERIFIED** |
| **13** | **Is statistical analysis plan documented?** | YES. Preregistered to use clustered bootstrap re-sampling (10,000 resamples) clustered by `source_group_id`. | **VERIFIED** |
| **14** | **Is power analysis reproducible?** | YES. Script `stage_8_9_66/scripts/run_clustered_power_analysis.py` reproduces power: Gate 1 (89.3%), Gate 2 (99.4%), Gate 3 (97.7%), Gate 4 (97.6%). | **VERIFIED** |

---

## 4. Cohort Discrepancy Reconciliation

A potential source of confusion identified in earlier reports was the coexistence of three different sample size numbers:
1. **$N=700$ (Physical Sealed Manifest):** Created in Stage 8.9.60 as the first sealed independent cohort. Contains 200 screams and 500 negatives. It remains frozen, unsealed, and untouched.
2. **$N=1,050$ with $240/810$ (Early Proposal):** Proposed in Stage 60 planning to emulate low operational prevalence (22.8%).
3. **$N=1,050$ with $550/500$ (Stage 65 Balanced Proposal):** Proposed in Stage 65 to maximize statistical power for short-scream subgroup ablations.
4. **$N=1,050$ with $350/700$ (Stage 66 Final Proposal):** The authoritative reconciled compromise. It preserves statistical power for short screams ($N=220$, power $>97\%$) while allocating $N=160$ to shouted speech (power $>97\%$) and maintaining a realistic 1:2 prevalence ratio.

**Resolution:**
The physical artifact `future_evaluation_manifest.json` ($N=700$) is preserved as Benchmark Cohort A. The planned $N=1,050$ cohort ($350$ pos / $700$ neg) is the official specification for the expanded multi-center evaluation when authorized. Neither cohort was unsealed.

---

## 5. Conclusion
All 14 governance and administrative prerequisites for the sealed evaluation cohort are satisfied. The cohort remains cryptographically locked and pristine.

