# STAGE 8.9.27 LEGAL & ETHICAL AUDIT: License, Attribution & Provenance Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.27  
**Operating Mode:** Offline Research & Independent Evaluation  
**Production Status:** FROZEN — Zero Production Modifications  

---

## 1. Compliance Mandate & Acquisition Principles

Under the Stage 8.9.27 specifications (Section 3 & Section 4):
1. **Lawful Sources Only:** Data must be sourced exclusively from lawful public repositories with verified, explicit open licenses (FSD50K, NIGENS, Freesound).
2. **Zero Unauthorized Scraping:** No automated scraping of YouTube, commercial streaming platforms, social media, or access-restricted APIs was conducted.
3. **Transparent Licensing & Commercial Readiness:** Every single audio recording must maintain explicit licensing metadata, creator attribution, and commercial suitability classification.
4. **No Synthesized Stand-Ins for Real Evaluation:** Synthetic mixtures must never replace real recordings in the primary evaluation cohort.

---

## 2. License Distribution Across the Independent Cohort

Across the **295 total recordings** (254 primary real-world recordings and 41 secondary robustness recordings):

| License Designation | Primary Real Cohort ($N=254$) | Secondary Robustness ($N=41$) | Total Recordings | Commercial Suitability | Attribution Required? |
|:---|:---:|:---:|:---:|:---|:---:|
| **Creative Commons 0 (CC0 1.0 Universal)** | 118 (46.46%) | 41 (100.0%) | 159 (53.90%) | **Eligible** (Public Domain dedication) | No |
| **Creative Commons Attribution 4.0 (CC BY 4.0)** | 98 (38.58%) | 0 (0.00%) | 98 (33.22%) | **Eligible** (Commercial use permitted with attribution) | **Yes** |
| **Creative Commons Attribution 3.0 (CC BY 3.0)** | 28 (11.02%) | 0 (0.00%) | 28 (9.49%) | **Eligible** (Commercial use permitted with attribution) | **Yes** |
| **Creative Commons Non-Commercial (CC BY-NC 3.0/4.0)** | 10 (3.94%) | 0 (0.00%) | 10 (3.39%) | **Research Only** (Non-commercial evaluation only) | **Yes** |
| **Total Cohort** | **254 (100.0%)** | **41 (100.0%)** | **295 (100.0%)** | **96.06% Commercial Eligible** | Full records maintained |

### Commercial Compatibility Assessment
- **96.06% ($N = 244$)** of the primary independent real-world recordings are strictly **Commercial Deployment Eligible** under CC0, CC BY 3.0, and CC BY 4.0.
- **3.94% ($N = 10$)** carry non-commercial clauses (`CC BY-NC`). These are restricted exclusively to offline academic research and evaluation benchmarks. If any production deployment pipeline packages training or verification assets, these 10 files are quarantined and blocked from commercial distribution.

---

## 3. Provenance & Dataset Sources

| Source Provider / Repository | Primary Real Count | Robustness Count | Primary Source URL / DOI |
|:---|:---:|:---:|:---|
| **FSD50K (Freesound Dataset 50K)** | 224 | 0 | [Zenodo DOI: 10.5281/zenodo.4060432](https://zenodo.org/record/4060432) |
| **Freesound.org (Independent Verified)** | 29 | 0 | [https://freesound.org](https://freesound.org) |
| **NIGENS General Sound Event Database** | 1 | 0 | [Zenodo DOI: 10.5281/zenodo.2552860](https://zenodo.org/record/2552860) |
| **Synthesized Masked Scream Pipeline (Local)** | 0 | 41 | Internal Stage 8.9.11/8.9.21 Robustness Generator |
| **Total Cohort** | **254** | **41** | **100% Traceable Provenance** |

---

## 4. Attribution Registry

As required by CC BY 3.0 and CC BY 4.0 licenses, every recording maintains full attribution fields in [independent_dataset_manifest.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_27/independent_dataset_manifest.csv):
- `original_source_id`: The canonical Freesound sound ID or dataset clip index.
- `original_filename`: The creator's original file title.
- `attribution`: The designated author/uploader name.
- `source_url`: Clickable web link directly to the source asset.

---

## 5. Ethical Considerations & Human Subjects Protection

1. **Acoustic Vocalizations vs Personal Data:**
   - All voice recordings analyzed in this research were published openly by their creators or voluntary research participants under permissive open licenses for audio research.
   - Recordings contain no personally identifiable biometric markers, names, or addresses.
2. **Exclusion of Sensitive Non-Scream Data:**
   - Infant crying recordings in this cohort represent archival laboratory and domestic vocalizations published for acoustic acoustic classification benchmarks.
   - Assault, domestic violence, emergency dispatcher audio, and distress crisis calls were strictly **excluded** from this investigation.
   - Scope remains strictly confined to: *Detect human scream-like vocalizations and distinguish them from other sounds, particularly speech-like shouting.*
