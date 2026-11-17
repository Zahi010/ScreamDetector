# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Independent Dataset Acquisition Provenance & License Governance Report

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary

To establish a genuinely independent prospective evaluation cohort without violating licensing rights or contaminating evaluations with historical development data, an automated, authenticated acquisition pipeline was executed against Freesound.org using strict source-group isolation and commercial-intent licensing verification.

### Pipeline Governance Results:
- **API Authentication:** Verified Freesound REST API v2 using secure `.env` credential loading with zero credential leakage.
- **Approved Independent Candidates:** **30 recordings** cataloged across **19 distinct source groups**.
- **Zero Historical Leakage:** **100%** of approved candidates originate from uploaders absent from the 611-creator historical registry.
- **Quarantine Enforcement:** **42 recordings** successfully quarantined (preventing non-commercial licensing infringement and historical uploader reuse).

---

## 2. Commercial-Intent License Policy

| License Classification | Policy Decision | Justification & Legal Constraint |
| :--- | :---: | :--- |
| **CC0 1.0 Universal** | **PERMITTED** | Public domain dedication; unrestricted commercial and research use. |
| **CC BY 3.0 / 4.0** | **PERMITTED** | Permitted with explicit creator attribution and source URL preservation. |
| **CC BY-NC (Non-Commercial)** | **QUARANTINED** | Strictly prohibited to prevent legal cloud on downstream deployment. |
| **CC BY-ND (No Derivatives)** | **QUARANTINED** | Prohibits audio windowing, framing, filtering, or spectrogram transformation. |
| **CC BY-SA (ShareAlike)** | **QUARANTINED** | Viral copyleft restrictions conflict with proprietary production models. |
| **Unknown / Unspecified** | **REJECTED** | Absolute prohibition on unverified or unasserted provenance. |

---

## 3. Approved Candidate Harvest Breakdown

| Target Acoustic Category | Class Role | Approved Clips | Unique Source Groups | Mean Duration (s) |
| :--- | :--- | :---: | :---: | :---: |
| `FESTIVAL_AMBIENT_AND_MUSIC` | HARD_NEGATIVE | **1** | 1 | 16.17s |
| `GASPS_AND_SURPRISE` | HARD_NEGATIVE | **1** | 1 | 0.35s |
| `INFANT_CRY` | HARD_NEGATIVE | **7** | 5 | 5.02s |
| `VOCAL_SCREAM_ADULT_LOW_INTENSITY` | POSITIVE | **9** | 5 | 3.53s |
| `VOCAL_SCREAM_CHILD` | POSITIVE | **12** | 7 | 2.65s |

---

## 4. Quarantine Audit Breakdown

A total of **42** candidate recordings were evaluated and rejected by automated governance filters:

| Quarantine Reason | Rejection Count | Legal / Methodological Risk Prevented |
| :--- | :---: | :--- |
| `LEAKAGE_RISK_HISTORICAL_UPLOADER` | **21** | Prevents cross-cohort leakage, license breach, or single-source clustering. |
| `UPLOADER_CONCENTRATION_CAP_EXCEEDED` | **19** | Prevents cross-cohort leakage, license breach, or single-source clustering. |
| `LICENSE_INELIGIBLE_QUARANTINE` | **2** | Prevents cross-cohort leakage, license breach, or single-source clustering. |

---

## 5. Storage Quota Compliance

All 30 approved prospective candidate recordings are registered as **manifest pointers** with verified metadata. Their total raw PCM audio volume is estimated at **~75.4 MB**, fully compliant with the 500 MB C: drive quota. No raw audio files were downloaded prior to formal annotation protocol and prospective evaluation freezing.
