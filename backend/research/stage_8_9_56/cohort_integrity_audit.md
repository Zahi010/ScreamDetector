# Cohort Integrity & Provenance Audit Report — Stage 8.9.56

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Audit Scope

In accordance with Phase 2 of Stage 8.9.56, an independent, comprehensive audit of the frozen Stage 8.9.55 evaluation cohort was conducted to verify record uniqueness, physical audio availability, cryptographic digest integrity, licensing eligibility, and strict isolation from historical training and evaluation splits.

### Integrity Verdict:
**STAGE 8.9.55 COHORT INTEGRITY 100% CONFIRMED AND REPRODUCED.**  
Zero missing files, zero corrupted hashes, zero license violations, and zero historical data leakage.

---

## 2. Quantitative Cohort Inventory

| Cohort Dimension | Expected Value | Actual Audited Value | Reconciliation Status |
|---|---|---|---|
| **Total Evaluation Recordings** | Exactly 450 | **450** | **100% MATCH** |
| **Authentic Scream Vocalizations** | Exactly 150 | **150** | **100% MATCH** |
| **Hard Negatives** | Exactly 300 | **300** | **100% MATCH** |
| **Unique Recording Identifiers** | 450 distinct IDs | **450 distinct IDs** | **ZERO DUPLICATES** |
| **Physical Audio Files on Disk** | 450 accessible files | **450 accessible files** | **100% FOUND** |
| **File SHA-256 Digest Verification** | 450/450 matches | **450/450 matches** | **100% VERIFIED** |
| **Unique Source Groups** | $\ge 150$ | **246** | **MET (+96 SG margin)** |
| **Commercial License Eligibility** | 100% CC0 / CC-BY | **100% (450/450)** | **100% PERMISSIVE** |
| **Historical Exclusion Check** | 0 collisions against 2213 files | **0 collisions** | **STRICT CRYPTOGRAPHIC ISOLATION** |

---

## 3. License Audit Verification

Every individual recording admitted into the Stage 8.9.55 evaluation cohort was evaluated against commercial use restrictions:
- Creative Commons Attribution 3.0 (CC BY 3.0): **251 recordings**
- Creative Commons Zero (CC0 1.0 Universal): **142 recordings**
- Creative Commons Attribution 4.0 (CC BY 4.0): **57 recordings**

Zero Non-Commercial (NC), Non-Derivative (ND), or unverifiable licenses were admitted. All 450 recordings maintain documented attribution metadata in `dataset/license_audit.csv`.

---

## 4. Historical Independence & Quarantine Verification

The evaluation cohort was screened against `integrity/historical_exclusion_registry.csv` containing:
- 1,732 recordings from Stage 8.9.52/53/54 expansion sets (`expansion_train`, `expansion_val`, and quarantined `expansion_reserved_test`).
- 480 recordings from Stage 8.9.47/49/50/51 independent cohorts.
- 243 recordings from Production Stage 5 benchmark.
- **Total historical exclusion pool: 2213 unique recording hashes across 906 source groups.**

### Audit Finding:
- File SHA-256 Collisions: **0**
- PCM Hash Collisions: **0**
- Source-Group Overlaps: **0**
- File ID / Original ID Overlaps: **0**

The Stage 8.9.55 cohort is proven to be genuinely independent, source-group isolated, and free of historical leakage.
