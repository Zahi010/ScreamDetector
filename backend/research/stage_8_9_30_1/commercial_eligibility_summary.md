# STAGE 8.9.30.1 — LICENSING & COMMERCIAL ELIGIBILITY AUDIT SUMMARY

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.1  
**Operating Mode:** Legal Provenance & Intellectual Property Audit  
**Date:** November 2, 2026  
**Auditor:** ML Dataset & Legal Compliance Auditor  

---

## 1. LICENSING AUDIT SUMMARY

The licensing policy for the Festival Scream Detector research dataset enforces strict commercial compatibility:
- **Eligible Licenses:** Creative Commons Zero (`CC0-1.0`) and Creative Commons Attribution (`CC-BY-3.0`, `CC-BY-4.0`).
- **Ineligible Licenses (Strictly Quarantined):** Non-commercial variants (`CC-BY-NC`, `CC-BY-NC-ND`, `CC-BY-NC-SA`), Sampling+, and All Rights Reserved (`ARR`).

### Audited Dataset License Distribution

| Canonical License | Commercial Status | Recording Count | Percentage | Attribution Obligation |
|---|---|---:|---:|---|
| **CC-BY-4.0** | **ELIGIBLE** | 143 | 70.10% | Attribution required (Creator, Title, License URL) |
| **CC0-1.0** | **ELIGIBLE** | 52 | 25.49% | Public Domain Dedication (No attribution required) |
| **CC-BY-3.0** | **ELIGIBLE** | 9 | 4.41% | Attribution required (Creator, Title, License URL) |
| **Total Ingested Cohort** | | **204** | **100.00%** | **100% Permissive Commercial Eligibility** |

---

## 2. QUARANTINE VERIFICATION

In Stage 8.9.30, 5 candidate sounds discovered during Freesound searches were identified as carrying non-commercial licenses (`CC-BY-NC-3.0` and `CC-BY-NC-4.0`):
- `FS_338936` (`human male scream agony.wav` by natemarler) — CC-BY-NC-4.0
- `FS_338935` (`human male scream scared pain.wav` by natemarler) — CC-BY-NC-4.0
- `FS_338934` (`human male scream desperate pain.wav` by natemarler) — CC-BY-NC-4.0
- `FS_653966` (`Male scream 01` by sfx_lab) — CC-BY-NC-3.0
- `FS_653967` (`Male scream 02` by sfx_lab) — CC-BY-NC-3.0

**Audit Finding:** All 5 restricted files were correctly intercepted before ingestion, recorded in `backend/research/stage_8_9_30/acquisition/failed_downloads.csv`, and **zero non-commercial audio files were downloaded or admitted to the processed cohort**.

---

## 3. ATTRIBUTION LEDGER & COMPLIANCE

For all 152 CC-BY recordings (143 CC-BY-4.0 and 9 CC-BY-3.0), full attribution strings, original URLs, and creator usernames are compiled and locked in [license_reaudit.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_30_1/license_reaudit.csv).

Example attribution string from manifest:
`'Voice_AdultMale_DeathScreams_01' by MrFossy licensed under CC-BY-4.0 (https://freesound.org/sounds/547185/)`

**Compliance Determination:** The 204 ingested recordings satisfy all intellectual property and licensing criteria for commercial-intent research.
