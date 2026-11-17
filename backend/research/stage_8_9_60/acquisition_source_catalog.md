# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Acquisition Source Catalog & Repository Provenance Audit

## 1. Overview & Sourcing Governance

In Stage 8.9.60, candidate acoustic repositories were evaluated against strict legal, licensing, and ethical governance standards. The project enforces an absolute prohibition on unauthorized web scraping, proprietary YouTube video extraction, and datasets with restrictive non-commercial (NC) or no-derivatives (ND) clauses.

Each candidate source repository was vetted for:
1. Clear, legally documented open-source licensing (CC0 1.0 Universal, CC BY 4.0, CC BY 3.0, Apache 2.0).
2. Verifiable institutional or creator provenance.
3. Permissibility of audio cropping, feature extraction, downsampling, and academic publication.
4. Absence of copyright infringement or terms-of-service violations.

---

## 2. Source Repository Evaluation Catalog

| Source Name | Official Repository / URL | Dataset Owner / Maintainer | Primary License | Status | Eligibility Rationale |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **FSD50K** | https://zenodo.org/record/4060432 | Music Technology Group, Universitat Pompeu Fabra | CC BY 4.0 / CC0 | **VERIFIED ELIGIBLE** | Permissive open science dataset; individual clip licenses verified; fully eligible for acoustic research and derivative modeling. |
| **NIGENS** | https://zenodo.org/record/2535879 | Tampere University & Inria | CC BY 4.0 | **VERIFIED ELIGIBLE** | Academic benchmark dataset for sound event detection; CC BY 4.0 permits analysis and derivative pipelines. |
| **OpenSLR** | https://www.openslr.org/ | OpenSLR Consortium | CC0 / CC BY 4.0 / Apache 2.0 | **VERIFIED ELIGIBLE** | Permissive speech corpora for acoustic model training and evaluation; verified commercial and research terms. |
| **Freesound Permissive Pool** | https://freesound.org/ | Freesound / Individual Creators | CC0 1.0 / CC BY 3.0 / CC BY 4.0 | **VERIFIED ELIGIBLE** | Verified permissive sound community uploads; API-compliant ingestion; full attribution and creator metadata captured. |
| **ESC-50** | https://github.com/karolpiczak/ESC-50 | Karol J. Piczak | CC BY-NC 3.0 | **QUARANTINED** | Non-commercial license restriction. Disqualified from production and general evaluation pools to prevent license contamination. |
| **AudioSet Unvetted** | https://research.google.com/audioset/ | Google LLC / YouTube | Proprietary YouTube Terms | **PROHIBITED** | Web-scraping YouTube audio streams is prohibited under Stage 8.9.60 governance and YouTube Terms of Service. |

---

## 3. License Distribution Across Verified Acquisitions

Of the 962 fresh recordings successfully acquired in Stage 8.9.60:
- **CC BY 4.0:** 888 recordings (92.31%) — Fully compliant with creator attribution retained.
- **CC0 1.0 Universal:** 52 recordings (5.41%) — Dedicated public domain; unrestricted use.
- **CC BY 3.0:** 22 recordings (2.29%) — Legacy Freesound permissive license; fully compliant with attribution retained.
- **CC BY-NC / ND / Proprietary:** 0 recordings (0.00%) — Strict zero-contamination achieved.

Full recording-level licensing metadata is recorded in `backend/research/stage_8_9_60/recording_provenance.csv` and cataloged in `backend/research/stage_8_9_60/license_inventory.csv`.

