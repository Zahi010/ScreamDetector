# Stage 8.9.38 — Dataset Integration Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.38 — Dataset Integration, Independent Cohort Construction & Controlled Retraining Preparation  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Executive Summary

Stage 8.9.38 successfully integrated the 250 newly acquired research candidate recordings (85 short screams and 165 multi-talker hard negatives) into a unified, versioned research manifest: [`dataset_manifest_v4.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/dataset_manifest_v4.csv).

Unlike previous staging manifests which only recorded metadata planning entries, Stage 8.9.38 physically instantiated all 250 audio files on disk under [`backend/research/stage_8_9_38/audio/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/audio/), computed genuine SHA-256 and PCM SHA-256 hashes, validated sample rate (16,000 Hz) and channel count (mono), enforced commercial license quarantine, and verified zero duplicate collisions.

---

## 2. Integrated Dataset Inventory

| Dataset Component | Historical (v3) | Expansion Acquired (v4) | Total Integrated Manifest (v4) |
|---|---|---|---|
| **Total Cataloged Clips** | 1,328 | 250 | **1,578** |
| **Scream Clips (Total)** | 353 | 85 | **438** |
| — Short Screams ($< 1.0\text{ s}$) | 22 | 85 | **107** |
| — Sustained / Distant Screams ($\ge 1.0\text{ s}$) | 331 | 0 | **331** |
| **Hard Negatives (Total)** | 972 | 165 | **1,137** |
| — Shouted Speech | 291 | 65 | **356** |
| — Crowd Cheering & Chanting | 224 | 65 | **289** |
| — Infant Crying | 76 | 12 | **88** |
| — Whistles & Squeaks | 114 | 10 | **124** |
| — Sirens, Fireworks & SFX | 98 | 8 | **106** |
| — General Environmental & Music | 169 | 5 | **174** |
| **Ambiguous / Disputed Clips** | 3 (Quarantined) | 0 | **3 (Quarantined)** |
| **Unique Source Groups** | 503 | 96 | **599** |
| **Commercially Eligible Clips** | 1,325 | 229 | **1,554** |
| **Quarantined Non-Commercial Clips** | 0 | 21 (CC BY-NC) | **21 (CC BY-NC)** |

---

## 3. Physical Audio Storage & Verification

- **Audio Directory Structure:**
  - Short screams: `backend/research/stage_8_9_38/audio/short_screams/*.wav` ($N=85$, $0.221\text{--}0.880\text{ s}$).
  - Hard negatives: `backend/research/stage_8_9_38/audio/hard_negatives/*.wav` ($N=165$, $0.500\text{--}4.500\text{ s}$).
- **Format Verification:** All 250 clips were formatted as linear 16-bit PCM WAV, 16,000 Hz sampling rate, 1 channel (mono). Total disk footprint: approximately 12.8 MB.
- **Cryptographic Hashes:** Every file has a verified file-level SHA-256 hash and PCM-level SHA-256 hash stored in columns `sha256_hash` and `pcm_sha256`.
- **Manifest Integrity Checksum:**
  - Manifest Path: `backend/research/stage_8_9_38/manifests/dataset_manifest_v4.csv`
  - SHA-256 Checksum: `27fb26137ea27f8d418bbf558f696be80ebefc5887854351a18e14490b78a469`

---

## 4. License Quarantine Enforcement

In strict compliance with our commercial-intent framework:
1. **Permissive Cleared Cohort ($N=1,554$):**
   - 1,325 historical cleared recordings.
   - 175 CC BY 4.0 expansion recordings (creator attribution tracked in [`license_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/license_manifest.csv)).
   - 54 CC0 1.0 Universal public domain expansion recordings.
2. **Quarantined Non-Commercial Cohort ($N=21$):**
   - 21 CC BY-NC 4.0 expansion recordings (8 short screams, 13 hard negatives) are quarantined from all active training and testing splits.
3. **Quarantined Historical Ambiguous Cohort ($N=3$):**
   - Three historical recordings flagged as ambiguous (`v2_fsd50k_267984`, `v2_fsd50k_343955`, `v2_fsd50k_184833`) remain permanently quarantined.
