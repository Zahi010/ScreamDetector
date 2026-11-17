# Source Diversity & Cohort Provenance Report — Stage 8.9.55

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Composition Overview

In accordance with Phase B (New Authentic Data Acquisition), a genuinely independent, source-group-isolated authentic evaluation cohort comprising **450 recordings across 246 independent source groups** was curated and quarantined.

| Metric | Target Requirement | Actual Achieved | Compliance Status |
|---|---|---|---|
| **Total Authentic Recordings** | 400–500 recordings | **450 recordings** | **MET (100% compliant)** |
| **Independent Source Groups** | $\ge 150$ source groups | **246 source groups** | **MET (+96 margin)** |
| **Authentic Screams** | Authentic, non-synthetic | **150 recordings** | **MET (77 source groups)** |
| **Hard Negatives** | Diverse challenging classes | **300 recordings** | **MET (191 source groups)** |
| **Commercial License Eligibility** | CC0 or CC-BY verified | **100.0% (450/450)** | **MET (0 non-commercial)** |
| **Historical Data Overlap** | Zero hash / SG overlap | **0.0% (0 collisions)** | **MET (Strict cryptographic isolation)** |

---

## 2. Category & Class Distribution

| Primary Class Taxonomy | Count | Share (%) | Source Groups | Key Subtypes Represented |
|---|---|---|---|---|
| `CONFIRMED_SCREAM_LIKE` | 150 | 33.3% | 77 | `SHORT` (36), `SUSTAINED` (114), `LOW_INTENSITY`, `MUFFLED`, `CROWD_MASKED`, `DISTANT` |
| `SHOUTED_SPEECH` | 60 | 13.3% | 39 | Shouted commands, cheers, athletic calls |
| `CHEERING` | 50 | 11.1% | 40 | Stadium crowds, festival cheering |
| `CRYING` | 50 | 11.1% | 37 | Infant distress, child crying |
| `OTHER_VOCALIZATION` | 140 | 31.1% | 109 | Normal speech, sirens/alarms, music/singing, ambient outdoor, laughter |
| **Total Primary Cohort** | **450** | **100.0%** | **246** | **Full Multi-Class Coverage** |

### Notice Regarding Whistle Category Evidence:
In compliance with Section 5 ("Do not create synthetic recordings to satisfy authentic acquisition targets... report the actual count and mark the evidence limitation"), all 137 repository whistle recordings were consumed in historical training and expansion sets (Stages 52–54). Zero untouched authentic whistles exist in the unexposed repository pool. Consequently, no synthetic whistles were fabricated. The whistle evaluation subgroup is documented as **INSUFFICIENT EVIDENCE (0 fresh authentic clips)** per Section 11.

---

## 3. Acoustic Duration & Signal Properties

| Dimension | Min | Median | Mean | P95 | Max |
|---|---|---|---|---|---|
| **Duration (s)** | 0.557s | 5.312s | 8.408s | 26.236s | 123.379s |
| **Sample Rate (Hz)** | 16,000 | 16,000 | 16,000 | 16,000 | 16,000 |
| **Scream Duration (s)** | 0.557s | 1.988s | 3.668s | 7.814s | 101.808s |

---

## 4. Provenance & Licensing Integrity

Every recording originates from open-access repositories with verified permissive licenses:
- Creative Commons Attribution 3.0 (CC BY 3.0)
- Creative Commons Attribution 4.0 (CC BY 4.0)
- Creative Commons Zero (CC0 1.0 Universal)

Zero recordings require Non-Commercial (NC) restrictions, and zero proprietary or scraping-restricted assets were utilized. Full license logs are cataloged in `dataset/license_audit.csv`.
