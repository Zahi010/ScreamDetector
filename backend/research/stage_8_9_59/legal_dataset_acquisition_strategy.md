# Legal Dataset Acquisition Strategy — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase G of Stage 8.9.59, a legally compliant, error-driven dataset acquisition strategy was designed to resolve the acoustic coverage deficits identified in the Candidate E1 error audit.

This strategy establishes strict legal licensing standards, defines mandatory provenance fields, specifies rigorous ethical and copyright boundaries, and prioritizes acquisition targets based directly on observed false-negative and false-positive root causes.

---

## 2. Commercial-Intent Licensing Governance Policy

To preserve future deployment eligibility, all proposed audio acquisitions must adhere to strict copyright governance:

| License Class | Commercial Deployment Eligibility | Handling Protocol | Required Action |
|---|---|---|---|
| **CC0 / Public Domain** | **Fully Eligible** | Permitted for training, validation, and evaluation | Record source URL, uploader, content SHA-256 |
| **CC BY (Attribution)** | **Fully Eligible with Attribution** | Permitted for training, validation, and evaluation | Maintain attribution registry linking clip to creator |
| **CC BY-SA (ShareAlike)** | **Eligible with Caution** | Permitted; downstream models must review terms | Track copyleft boundary implications |
| **CC BY-NC (Non-Commercial)** | **INELIGIBLE FOR COMMERCIAL USE** | **STRICT QUARANTINE** | Do NOT mix into production or commercial pipelines |
| **CC BY-ND (No Derivatives)** | **INELIGIBLE FOR AUGMENTATION** | **STRICT QUARANTINE** | Prohibits audio filtering/DSP augmentation |
| **All Rights Reserved / Proprietary** | **PROHIBITED WITHOUT WRITTEN LICENSE** | **STRICT QUARANTINE** | Do NOT acquire or ingest |
| **Unknown / Unclear Licenses** | **PROHIBITED** | **STRICT QUARANTINE** | Exclude until provenance is established |

---

## 3. Strict Acquisition Safeguards & Prohibitions

In accordance with project integrity and legal compliance:
- **No YouTube Scraping:** Absolutely no automated scraping or downloading of unvetted video streams.
- **No DRM or Access Bypass:** Never circumvent access controls, passwords, download restrictions, or terms of service.
- **No Fabricated Data:** Zero synthetic generation or hallmarked audio without explicit annotation.
- **No Invented Metadata:** All licenses, uploader identities, and source URLs must be verified against original host repositories.
- **No Commercial Usability Assumptions:** Public accessibility on the internet does NOT imply commercial reusability.

---

## 4. Mandatory Recording Provenance Fields

Every acquired audio file must be cataloged with the following 12 metadata attributes:

1. `dataset_name`: Authoritative repository or collection name (e.g., Freesound, FSD50K, NIGENS).
2. `source_url_or_id`: Permanent web URI or database accession identifier.
3. `original_uploader`: Verifiable username or creator identity.
4. `license`: Declared legal license string.
5. `attribution_requirements`: Exact text required for legal compliance.
6. `file_sha256`: Cryptographic digest of raw audio file.
7. `pcm_sha256`: Cryptographic digest of decoded uncompressed audio samples.
8. `source_group_id`: Assigned cluster group linking all recordings from same session/artist.
9. `parent_recording_id`: Identifier of original uninterrupted recording if excerpted.
10. `label_provenance`: Two-reviewer verified ground-truth annotation.
11. `audio_duration_seconds`: Accurate duration measured at native sampling rate.
12. `acquisition_date_utc`: Timestamp of acquisition.

---

## 5. Priority Acquisition Targets (Section 10.1)

Acquisitions must prioritize underrepresented evidence rather than collecting easily accessible generic audio:

| Priority Rank | Target Acoustic Category | Clinical/Acoustic Justification | Minimum Source Groups Target | Minimum Recordings Target |
|:---:|---|---|:---:|:---:|
| **Priority 1** | **Low-Intensity & Muffled Screams** | Primary failure mode (only 7 SGs exist in corpus, 0 in validation). Needed to evaluate distant/subdued screams. | **50 SGs** | **100 Clips** |
| **Priority 2** | **Crowd-Masked Screams (SNR < 10 dB)** | 37.5% of validation false negatives. Needed to train robust subband ratios in heavy ambient festival noise. | **60 SGs** | **150 Clips** |
| **Priority 3** | **Diverse Independent Shouted Speech** | 90% of validation shouting false alarms came from just 2 sessions. Needed to decouple extreme vocal effort from screams. | **100 SGs** | **200 Clips** |
| **Priority 4** | **Independent Sustained Screams ($\ge 1.0$s)** | Sustained screams have lower recall (76.67%) due to non-stationary decay. Needed to train rolling window segmentation. | **80 SGs** | **160 Clips** |
| **Priority 5** | **Cheering & Chanting Crowds** | Needed to preserve high specificity during stadium and festival celebrations. | **50 SGs** | **100 Clips** |
| **Priority 6** | **Infant Crying & Distress Wails** | 2 validation false positives. Needed to train fine phonatory boundary between infant cries and adult screams. | **40 SGs** | **80 Clips** |

---

## 6. Preservation & Traceability

License distributions and commercial eligibility classifications across all current assets are archived in [`license_provenance_inventory.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/license_provenance_inventory.csv).

