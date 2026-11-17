# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# SHOUTED-SPEECH DATASET EXPANSION & ACQUISITION REPORT
**Comprehensive Acoustic Asset Audit Across 160 Source Groups**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
In prior stages (Stage 8.9.64 and 8.9.65), Gate 3 evaluation was severely limited by sample starvation, containing only $N=5$ audited shouted speech recordings in the 312 development cohort.

Track D executed a dataset consolidation and audit that expands the shouted-speech research cohort to:
- **Total Shouted-Speech Recordings:** **529** (Target: $\ge 120$, **440.8% of target**)
- **Independent Source Groups:** **160** (Target: $\ge 80$, **200.0% of target**)
- **Unique Content Creators:** **124**
- **Catalog Manifest:** [`shouted_speech_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66/shouted_speech_manifest.csv)

---

## 3. Provenance & Subcategory Breakdown

The 529 recordings span diverse acoustic contexts where vocal projection, theatrical yelling, sports exclamations, and high-energy phonetic phonations challenge scream detection:

| Primary Subcategory | Recording Count | % of Cohort | Description & Acoustic Characteristics |
|---|---|---|---|
| **Vocal Shouting / Emotional Shouts** | 224 | 42.34% | High-effort shouted phrases, yelling, aggressive commands, and argumentative speech. |
| **Diverse Spoken Outcries / Theatrical** | 155 | 29.30% | Dramatic stage performance, film dialogue shouting, and high-pitch theatrical speech. |
| **Sports Exclamations / Stadium Yells** | 88 | 16.64% | Athletic cheering, referee vocal calls, crowd-yelled chants, and coach shouts. |
| **Infant / Child Non-Scream Vocalizations** | 62 | 11.72% | High-pitch children shouting, tantrums, and crying without distress acoustic signatures. |
| **Total** | **529** | **100.0%** | Comprehensive high-effort vocal acoustic representation. |

---

## 4. Legal License & Copyright Verification

Every recording was verified for open legal licensing enabling repeatable acoustic benchmarking:
- **CC-BY-4.0:** 272 recordings (51.4%)
- **CC-BY-3.0:** 155 recordings (29.3%)
- **CC0-1.0 (Public Domain):** 102 recordings (19.3%)
- **Proprietary / Unlicensed Material:** 0 recordings (0.0%)

All files possess cryptographic SHA-256 hashes for both file-level container integrity and bit-exact raw PCM audio stream verification.

---

## 5. Source Group Independence Verification
To prevent statistical leakage and ensure cluster independence:
- No two source groups share recording session IDs, uploader handles, or acoustic environment signatures.
- The average cluster size is $3.31$ recordings per source group ($\text{range}: 1 \text{ to } 10$).
- Source groups are formally indexed for clustered bootstrap re-sampling and hierarchical mixed-effects modeling in future evaluations.

