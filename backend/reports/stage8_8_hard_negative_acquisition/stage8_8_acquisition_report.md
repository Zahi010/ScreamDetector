# Stage 8.8 — Automated Hard-Negative Dataset Acquisition & Licensing Audit Report

**Date**: 2026-10-28 06:40:47 UTC  
**Project**: Festival Scream Detector  
**Scope**: Stage 8.8 Automated Acquisition, Licensing Verification, Quality Control, and Evaluation Preparation  
**Operating Threshold**: 0.35 (Frozen Baseline)  
**Model SHA-256**: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` (VERIFIED)  
**Metadata SHA-256**: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` (VERIFIED)  

---

## 1. Executive Summary

Stage 8.8 establishes a production-grade, automated data acquisition and curation pipeline to resolve the critical hard-negative coverage deficits identified in the Stage 8.7 audit. Rather than relying on manual recording of all negative audio, this pipeline automatically queries public sound archives, audits per-recording legal permissions, verifies audio quality, eliminates duplicate content, and stages candidate recordings for human listening review.

### Key Milestones Completed:
1. **Zero Contamination of Baseline**: Frozen model weights, metadata, decision threshold (0.35), Stage 4 splits, and Stage 5 historical test metrics remain 100% untouched.
2. **Multi-Source Discovery Engine**: Catalogued candidate audio across **FSD50K**, **Freesound API**, and **AudioSet**.
3. **Strict Per-Recording Licensing**: Differentiated collection-level licenses from individual clip rights. Only CC0 and CC BY recordings are certified for downstream commercial use. Non-commercial (`CC BY-NC`) recordings are strictly segregated.
4. **Defensive Storage & Disk Guard**: Kept the full 40,966-clip FSD50K corpus on `E:\FSD50K.dev_audio\` and selectively copied only verified CC0/CC BY candidate clips to host drive (consuming only ~127 MB).
5. **Quality Control & 16 kHz Normalization**: Verified zero NaN/Infs, zero near-silence, checked for clipping, detected duplicates via file and PCM SHA-256, and generated standardized 16 kHz mono derivatives in `processed/`.
6. **Prioritized Review Queue**: Generated a deterministic queue ordered by category gap urgency, licensing confidence, audio cleanliness, and model scream prediction score.

---

## 2. Source-by-Source Investigation & Licensing Audit

| Source Provider | Discovered Candidates | CC0 Verified | CC BY Verified | Non-Commercial (NC) | AudioSet / YouTube | Commercially Permissive |
|---|---|---|---|---|---|---|
| **Freesound API** | 19 | 11 | 8 | 0 | 0 | **100% Eligible** |
| **FSD50K** | 320 | 311 | 8 | 1 | 0 | **99.7% Eligible** |
| **AudioSet** | 22 | 0 | 0 | 0 | 22 | **0% (Metadata Only)** |
| **Curated Permissive** | 9 | 9 | 0 | 0 | 0 | **100% Eligible** |
| **TOTAL** | **370** | **331** | **16** | **1** | **22** | **347 clips** |

### Source A: FSD50K
- **Official Specification**: 51,197 audio clips (WAV, 44.1 kHz mono) covering 200 classes.
- **Archive Size**: ~14 GB for development audio on `E:\FSD50K.dev_audio\`.
- **Action**: Monolithic duplication to C: was avoided. Verified 40,966 WAV files on E: alongside official ground-truth `dev.csv` and per-clip metadata `dev_clips_info_FSD50K.json`. Selectively copied only 176 verified CC0/CC BY clips (127 MB) for active pipeline processing while leaving the complete corpus on E:.

### Source B: Freesound API
- **Client Implementation**: Supports query parameterization, text search, pagination, duration bounds (1.0 to 30.0s), and rate limiting.
- **Authentication**: Configured via `FREESOUND_API_KEY` in `.env`.
- **Dry-Run & Seed Mode**: When `FREESOUND_API_KEY` is not populated, the system automatically falls back to deterministic, verified Freesound seeds with exact attribution text and license URLs, enabling complete testing and audit reporting without external failure.

### Source C: AudioSet
- **Status**: **NOT_ACQUIRED (Metadata & Ontology Mapping Only)**.
- **Legal & Compliance Boundary**: AudioSet annotations are CC BY 4.0, but underlying YouTube video audio remains subject to YouTube Terms of Service and individual content creator copyrights.
- **Strict Prohibition**: In compliance with user instructions, no `yt-dlp`, browser automation, or proxy scraping was used. AudioSet segments are logged strictly as metadata candidates with audio status `NOT_ACQUIRED`.

---

## 3. Category Coverage Delta (Stage 8.7 Baseline vs. Stage 8.8)

| Priority | Target Category | Stage 8.7 Baseline | Stage 8.8 Discovered | Newly Acquired (Audio) | Target Planning Count | Current Status |
|---|---|---|---|---|---|---|
| **1** | Whistles and High-Pitched Squeaks | 2 | 52 | 22 | 30 | **IN_PROGRESS** (+22 audio) |
| **2** | Crowd Cheering, Chanting & Applause | 1 | 48 | 21 | 40 | **IN_PROGRESS** (+21 audio) |
| **3** | EDM, Synthesizer Risers & Bass Drops | 0 | 44 | 21 | 35 | **IN_PROGRESS** (+21 audio) |
| **4** | Shouting, Excited Speech & MC Vocals | 1 | 37 | 20 | 25 | **IN_PROGRESS** (+20 audio) |
| **5** | Vuvuzelas, Stadium Horns & Party Blowers | 0 | 40 | 21 | 20 | **TARGET_REACHED** (+21 audio) |
| **6** | Fireworks, Screechers & Pyrotechnics | 0 | 38 | 20 | 20 | **TARGET_REACHED** (+20 audio) |
| **7** | Microphone Wind Noise & Handling | 4 | 39 | 21 | 20 | **TARGET_REACHED** (+21 audio) |
| **8** | Infant Crying & Tantrums (Ethical Archival) | 64 | 35 | 20 | 15 | **TARGET_REACHED** (+20 audio) |
| **9** | Sirens, Bells & Electronic Ringing | 6 | 37 | 19 | 15 | **TARGET_REACHED** (+19 audio) |

---

## 4. Frozen Baseline Inference Evaluation

The newly acquired clips were evaluated through the frozen Stage 5 inference pipeline (YAMNet embeddings + max pooling + Logistic Regression classifier at threshold 0.35).

- **Total Acquired Clips Evaluated**: 185
- **Model Alerts (Score >= 0.35)**: 20
- **Reviewed Non-Scream Count**: 0
- **Confirmed False Positives**: 0

### Top Vulnerability Findings:
- **whistles_and_squeaks** (`fsd50k_323723`): Model score **0.8892** (Threshold 0.35) — distant creak6.wav: my chair squeaking from a difference. might have background 
- **whistles_and_squeaks** (`fsd50k_323724`): Model score **0.6948** (Threshold 0.35) — distant creak5.wav: my chair squeaking from a difference. might have background 
- **crowd_cheering_applause** (`fsd50k_418897`): Model score **0.9939** (Threshold 0.35) — Applause.wav: This sound effect comes from a video recorded with a mobile phone.
- **crowd_cheering_applause** (`fsd50k_347033`): Model score **0.9715** (Threshold 0.35) — 01 small group clapping - theatre XY mics.wav: short recording of group of 4 peo
- **shouting_and_speech** (`fsd50k_350451`): Model score **0.9999** (Threshold 0.35) — Kid Chorus "School Crossing Guard": A group of young adults yelling "School cros
- **shouting_and_speech** (`fsd50k_249791`): Model score **0.9999** (Threshold 0.35) — Scream.wav: A scream, male. Recorded with a TASCAM DR-05 Linear PCM Recorder.
- **sfx_sirens_ringing** (`fsd50k_268809`): Model score **0.8729** (Threshold 0.35) — Police Car Siren in Traffic: Police Car Siren in Traffic

Record on my Vlog at
- **sfx_sirens_ringing** (`fsd50k_393662`): Model score **0.7590** (Threshold 0.35) — WaHi Siren Blast short.mp3: Ambulance chirping siren
- **infant_crying_archival** (`fsd50k_393769`): Model score **0.9294** (Threshold 0.35) — baby cry.wav: A baby crying.Recorded with a Zoom H1.

> [!IMPORTANT]
> **Ground-Truth Integrity Rule**: In accordance with machine-learning best practices, unreviewed model alerts are recorded as **candidate acoustic vulnerabilities for inspection**, NOT confirmed false positives. A clip enters false-positive reporting only when verified by a human reviewer as `APPROVED_NON_SCREAM`.

---

## 5. Artifact & Integrity Checklist

All 11 Stage 8.8 deliverables are generated in `backend/reports/stage8_8_hard_negative_acquisition/`:
- `stage8_8_acquisition_report.md` (This document)
- `source_licence_audit.csv`
- `discovered_candidates.csv`
- `download_manifest.csv`
- `category_coverage_before_after.csv`
- `audio_quality_report.csv`
- `duplicate_report.csv`
- `review_queue.csv`
- `frozen_model_evaluation.json`
- `artifact_integrity.json`
- `next_stage_recommendations.md`
