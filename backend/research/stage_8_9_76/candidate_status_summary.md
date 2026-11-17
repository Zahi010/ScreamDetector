# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate State Machine Audit & Status Summary

**Stage:** 8.9.76  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary

A rigorous state-machine audit was performed across all **67** candidate recordings identified from Freesound.org API discovery. To enforce scientific integrity, candidates advance through 13 discrete lifecycle states, preventing unverified or non-commercial recordings from contaminating research splits.

### State Machine Breakdown:

| State Machine Identifier | Candidate Count | Governance Meaning & Action |
| :--- | :---: | :--- |
| `QUARANTINED` | **41** | Quarantined due to non-commercial license, blacklist match, or concentration cap |
| `ANNOTATION_PENDING` | **26** | Downloaded, hash-verified, and awaiting independent double-blind human labeling |

---

## 2. Quarantine Reason Forensics

| Quarantine Reason | Rejection Count | Legal / Methodological Risk Prevented |
| :--- | :---: | :--- |
| `UPLOADER_CONCENTRATION_CAP_EXCEEDED` | **18** | Prevents cross-cohort leakage, license breach, or single-source clustering. |
| `LEAKAGE_RISK_HISTORICAL_UPLOADER` | **13** | Prevents cross-cohort leakage, license breach, or single-source clustering. |
| `LICENSE_INELIGIBLE_OTHER` | **10** | Prevents cross-cohort leakage, license breach, or single-source clustering. |

---

## 3. Candidate Lifecycle Verification

All **26** active candidates have completed states 1 through 8 (`DISCOVERED` -> `LICENSE_VERIFIED` -> `BLACKLIST_CHECKED` -> `DOWNLOAD_PENDING` -> `DOWNLOADED` -> `FILE_HASH_VERIFIED` -> `PROVENANCE_VERIFIED` -> `ANNOTATION_PENDING`). No candidate skips validation states. Zero candidates are assigned to prospective evaluation prior to human annotation and adjudication.
