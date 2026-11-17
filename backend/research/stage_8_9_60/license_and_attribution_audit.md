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

# License & Attribution Audit: Provenance Integrity & Legal Compliance

## 1. Compliance Standard and Licensing Policy

Stage 8.9.60 mandates complete legal compliance for all acquired acoustic data. Because acoustic machine learning pipelines modify audio via cropping, windowing, resampling, and filterbank transformations, and because research outputs may eventually inform commercial system architectures, all ingested recordings must be unencumbered by restrictive clauses.

Specifically, the stage policy enforces:
1. **Zero Non-Commercial (NC) Contamination:** Datasets licensed under CC BY-NC are strictly prohibited from ingestion into training or primary evaluation pools.
2. **Zero No-Derivatives (ND) Contamination:** Audio must permit mathematical transformations, cropping, and derivative feature generation.
3. **Zero Unauthorized Web Scraping:** Video platforms such as YouTube that prohibit unauthorized automated stream extraction are strictly excluded.
4. **Mandatory Attribution Provenance:** Every recording acquired under a CC BY license must preserve the original author identity, repository URL, sound identifier, and exact license text.

---

## 2. Ingested Audio Pool Licensing Breakdown

All 962 fresh recordings acquired during Stage 8.9.60 were cataloged in `backend/research/stage_8_9_60/recording_provenance.csv`. The license distribution is summarized below:

| Standardized License Code | Full License Name | Commercial Eligibility | Derivatives Permitted | Clip Count | Percentage |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **CC-BY-4.0** | Creative Commons Attribution 4.0 International | Yes | Yes | 888 | 92.31% |
| **CC0-1.0** | Creative Commons Zero 1.0 Universal (Public Domain) | Yes | Yes | 52 | 5.41% |
| **CC-BY-3.0** | Creative Commons Attribution 3.0 Unported | Yes | Yes | 22 | 2.29% |
| **CC-BY-NC** | Creative Commons Non-Commercial (All Versions) | No | Yes | 0 | 0.00% |
| **CC-BY-ND** | Creative Commons No-Derivatives (All Versions) | Yes | No | 0 | 0.00% |
| **PROPRIETARY** | Proprietary / All Rights Reserved / YouTube Terms | No | No | 0 | 0.00% |
| **TOTAL** | **Stage 8.9.60 Acquired Pool** | — | — | **962** | **100.00%** |

**Zero restricted licenses were admitted.** All 962 recordings are fully cleared for acoustic signal processing, derivative feature extraction, and scientific evaluation.

---

## 3. Attribution Metadata Preservation Protocol

To comply with CC BY 4.0 and CC BY 3.0 attribution requirements, `backend/research/stage_8_9_60/recording_provenance.csv` maintains complete granular metadata for each recording:
- `recording_id`: Globally unique identifier assigned to the clip.
- `source_dataset`: Upstream repository (FSD50K, NIGENS, OpenSLR, Freesound).
- `external_sound_id`: Upstream repository asset ID (e.g., Freesound Sound ID).
- `creator_username`: Uploading artist or institutional researcher.
- `official_source_url`: Permanent web locator for the original asset.
- `license_code`: Specific applicable license (CC0-1.0, CC-BY-4.0, CC-BY-3.0).
- `license_url`: Legal deed URL.
- `derivatives_indicated`: Boolean confirmation that acoustic windowing and feature extraction constitute derivative research operations.

---

## 4. Quarantined Source Integrity Check

The legal vetting process formally quarantined two evaluated candidate sources:
1. **ESC-50 (Piczak, 2015):** Quarantined due to CC BY-NC 3.0 non-commercial restriction.
   - *Audit result:* 0 ESC-50 recordings are present in `acquisition_manifest.csv` or `future_evaluation_manifest.json`.
2. **AudioSet Unvetted YouTube Streams:** Prohibited due to terms-of-service scraping restrictions.
   - *Audit result:* 0 YouTube-scraped recordings are present in any Stage 8.9.60 dataset artifact.

This confirms 100% legal clearance and provenance compliance across all stage deliverables.

