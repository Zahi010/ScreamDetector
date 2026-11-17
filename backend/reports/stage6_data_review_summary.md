# Stage 6 Hard-Negative Data Ingestion & Review Audit

**Generated**: 2026-10-24 15:19:07

---

## 1. Directory & Ingestion Summary

- **Primary Ingestion Directory**: `C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\data\raw\hard_negatives`
- **Fallback Ingestion Directory**: `C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend\dataset\raw\hard_negatives`
- **Total Discovered WAV Files**: **0**
- **Successfully Ingested**: **0**
- **Duplicates Skipped (Hash Collisions)**: **0**

> [!NOTE]
> **Empty Ingestion Directory Status**:
> Currently, 0 external hard-negative audio files have been placed into the ingestion directories. In accordance with project methodology, no synthetic or fabricated files were generated to simulate data. Model retraining is safely blocked until real, human-reviewed recordings are ingested.

---

## 2. Review Status Breakdown

| Review Status | Description | Count |
| :--- | :--- | :--- |
| **`pending_review`** | Ingested but awaiting human listening verification. Kept out of training. | 0 |
| **`approved_non_scream`** | Human-verified as non-scream audio. Eligible for negative training set. | 0 |
| **`approved_scream`** | Human-verified as genuine distress scream. Eligible for positive training set. | 0 |
| **`rejected_ambiguous`** | Unclear acoustic intent, mixed cheer/scream, or licensing defect. Excluded. | 0 |
| **Total** | All tracked hard-negative records | **0** |

---

## 3. Acoustic Category Breakdown

| Category | Description | Ingested Count |
| :--- | :--- | :--- |
| **`festival_whistle`** | Rave whistles, referee whistles, vuvuzelas, party noisemakers | 0 |
| **`crowd_cheering`** | Stadium applause, celebratory shouts, concert cheering, festival chants | 0 |
| **`music_and_effects`** | EDM bass drops, synth risers, distorted vocals, microphone feedback | 0 |
| **`vocal_non_scream`** | Crying, laughing, coughing, loud conversation, spoken shouting | 0 |
| **`sfx_transients`** | Sirens, bells, car horns, squeaky toys, electronic phone ringing | 0 |
| **`environmental_noise`** | Wind gusts, mic handling, cable pops, crowd murmur, outdoor rumble | 0 |
| **`genuine_scream`** | Verified distress vocalizations from newly collected sources | 0 |

---

## 4. Licensing and Rights Audit

All ingested hard-negative audio must carry explicit licensing tags. OpenSLR 99 and NIGENS carry **CC BY-NC-ND 4.0** licenses, which prohibit commercial deployment and derivative distribution. New hard negatives must prioritize permissive licenses:
- **Commercial-Safe**: Creative Commons Zero (`CC0 1.0`), Public Domain, or Attribution (`CC BY 4.0`).
- **Research-Only**: Non-Commercial (`CC BY-NC 4.0`) or ShareAlike (`CC BY-SA 4.0`) must be flagged as non-commercial.

---

## 5. Next Steps for Data Collection

To populate hard negatives:
1. Place candidate WAV files into `data/raw/hard_negatives/<category>/`.
2. Run `python backend/scripts/ingest_hard_negatives.py` to index and hash them.
3. Review clips using `python backend/scripts/review_hard_negatives.py` to approve or reject.
