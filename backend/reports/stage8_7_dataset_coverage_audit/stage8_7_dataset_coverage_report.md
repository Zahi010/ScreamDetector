# Stage 8.7: Existing Dataset Coverage Audit and AudioSet Source Investigation

**Project:** AI-Powered Festival Scream Detection System (`festival-scream-detector`)  
**Date:** October 24, 2026  
**Author:** Senior Machine Learning & Audio Signal Processing QA Lead  
**Scope:** Stage 8.7 — Comprehensive Dataset Coverage Audit & AudioSet Source Investigation  
**Operating System:** Windows 11 (Python 3.11.17, TensorFlow 2.15 YAMNet, scikit-learn 1.5)  

---

> [!CAUTION]
> **SAFETY & ETHICAL ADVISORY**  
> **"POSSIBLE SCREAM DETECTED — REQUIRES HUMAN AUDITORY VERIFICATION. Automated acoustic alerts do not confirm an emergency."**  
> The system detects acoustic patterns, not human intent, injury, or emergency status. This stage is an evidence-based dataset audit and source investigation only. No model weights, classification thresholds, dataset splits, or test predictions were modified or retrained.

---

## 1. Executive Summary

Stage 8.7 performs a rigorous audit of the existing scream and non-scream datasets, analyzes the acoustic drivers behind Stage 5 false positives, assesses the 521-class YAMNet ontology, evaluates the technical and legal feasibility of Google AudioSet as an expansion source, and defines a minimal, lawful hard-negative collection roadmap.

### Key Audit Findings:
1. **Model & Baseline Immutability:** The Stage 5 Logistic Regression model and metadata SHA-256 hashes (`ad6e428d05...` and `30c1c75d81...`) were verified intact. The operational decision threshold remains strictly at **0.35**.
2. **Reconciled Dataset Inventory:** Exactly **1,621 eligible audio recordings** across **726 unique source groups** (18,791 seconds / 5.22 hours) were verified:
   - **Scream Recordings:** 127 total (89 train, 19 validation, 19 test).
   - **Non-Scream Recordings:** 1,494 total (1,045 train, 225 validation, 224 test).
   - **Exclusions:** 4 NIGENS files properly quarantined in Stage 4 (1 watermark variant, 1 exact duplicate, 1 gun screamer, 1 human gasp).
3. **Severe Festival Acoustic Deficit:** The existing 1,045 non-scream training recordings are dominated by studio speech (80 clips) and booth nonverbal sounds (459 clips: coughing, sneezing, yawning). Critical festival acoustic phenomena are virtually **absent**:
   - Crowd Cheering & Applause: **Only 1 cheering clip in train; 0 applause clips**.
   - Whistling & Referee Whistles: **Only 1 human whistle in train**.
   - EDM Leads, Bass Drops & Synths: **0 clips in train, val, or test**.
   - Vuvuzelas & Stadium Horns: **0 clips**.
4. **False Positive Mechanism Uncovered:** The highest-confidence false alarms in Stage 5 were caused by extreme training underrepresentation:
   - Slide whistle (`ZipCartoon+HB02_55_8`): **0.9328 probability** (0 slide whistles in training).
   - Squeaky dog toy (`Toy+6080_61_2`): **0.8703 probability** (0 squeaky toys in training).
   - Infant crying (`Baby+2012_51`): **0.9355 probability** (shares scream harmonic formants; requires fine-grained negative training examples).
5. **AudioSet Source Assessment:** Google AudioSet **does not distribute playable audio** (only YouTube metadata and 128-dim VGGish embeddings). Scraping YouTube audio suffers from ~35–45% link rot, rate-limiting, and unresolved copyright risks (`REQUIRES LEGAL REVIEW`).
6. **Actionable Roadmap:** High-leverage expansion requires curating **80 to 125 focused recordings** across Rave Whistles, Crowd Cheering, and EDM Synthesizers using **Freesound.org (CC0 / CC BY)** and **Stage 8.6 Local Microphone Capture**, bypassing YouTube scraping entirely.

---

## 2. Baseline Model & Artifact Integrity

| Artifact Path | Expected SHA-256 Hash | Observed SHA-256 Hash | Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (IMMUTABLE)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (IMMUTABLE)** |
| Operational Threshold | `0.35` | `0.35` | **PASS** |
| Historical Split Manifest | `split_manifest.json` | 1,621 records verified | **PASS** |
| Cached Embeddings Manifest | `embedding_manifest.json` | 1,621 embeddings verified | **PASS** |

Full verification records are preserved in [`backend/reports/stage8_7_dataset_coverage_audit/artifact_integrity.json`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/artifact_integrity.json).

---

## 3. Reconciled Dataset Inventory

Detailed manifest inspection resolved all historical figures against the active filesystem ([`dataset_inventory.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/dataset_inventory.csv)):

```
Raw Scanned Audio Pool: 1,625 Total Files
├── OpenSLR 99:  727 files (51 scream, 676 non-scream) -> 0 Exclusions -> 727 Eligible
└── NIGENS:      898 files (76 scream, 822 non-scream) -> 4 Excluded   -> 894 Eligible
                                                              Total Eligible: 1,621 Recordings
```

### Partition Distribution (Stage 4 Leakage-Safe Splits)

| Dataset | Partition | Total Files | Unique Source Groups | Scream Count | Non-Scream Count | Duration (Hours) | Formats & Sample Rates |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **OpenSLR 99** | Train | 509 | 245 | 36 | 473 | 0.82h | 16 kHz Mono WAV |
| **OpenSLR 99** | Validation | 109 | 52 | 8 | 101 | 0.17h | 16 kHz Mono WAV |
| **OpenSLR 99** | Test | 109 | 53 | 7 | 102 | 0.18h | 16 kHz Mono WAV |
| **NIGENS** | Train | 625 | 265 | 53 | 572 | 2.82h | 44.1/25/48 kHz Stereo/Mono |
| **NIGENS** | Validation | 135 | 56 | 11 | 124 | 0.60h | 44.1/25/48 kHz Stereo/Mono |
| **NIGENS** | Test | 134 | 55 | 12 | 122 | 0.62h | 44.1/25/48 kHz Stereo/Mono |
| **Eligible Totals** | **All Splits** | **1,621** | **726** | **127** | **1,494** | **5.22h** | **100% Available Locally** |
| **NIGENS Excluded**| Quarantined | 4 | 4 | 0 | 4 | 0.01h | 44.1 kHz Stereo/Mono |

### Provenance and Licensing
- **OpenSLR 99:** Nonverbal vocalizations by 110 speakers. Governed by **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)**.
- **NIGENS General Sound Events:** Curated sound library via Zenodo. Governed by **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
- **Licensing Constraint:** Both datasets carry explicit **Non-Commercial** clauses, which prohibit commercial redistribution and commercial event deployment without licensing clearance.

---

## 4. Negative-Category Coverage Matrix

An audit of the 1,494 negative clips revealed severe acoustic blind spots ([`negative_category_coverage.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/negative_category_coverage.csv)):

| Category Group | Acoustic Category | Coverage Status | Verified Samples | Priority Level |
| :--- | :--- | :---: | :---: | :---: |
| **Human Vocalizations** | Ordinary Conversation & Speech | **Covered** | 80 | LOW |
| | Shouting & Excited Speech | **Missing** | 0 | **HIGH** |
| | Laughter & Giggling | **Covered** | 25 | MEDIUM |
| | Euphoric Vocal Squeals | **Partially Covered** | 1 | **HIGH** |
| | Crying, including Infant Crying | **Covered** | 64 | **CRITICAL** |
| | Gasps, Groans & Nonverbal Sounds | **Covered** | 459 | LOW |
| **Festival & Concert** | Crowd Cheering & Applause | **Partially Covered** | 1 (0 applause) | **CRITICAL** |
| | Whistling & Referee Whistles | **Partially Covered** | 2 | **CRITICAL** |
| | Vuvuzelas & Stadium Horns | **Missing** | 0 | **HIGH** |
| | Singing & Crowd Chanting | **Missing** | 0 | MEDIUM |
| | EDM, Bass Drops & Synthesizers | **Missing** | 0 | **CRITICAL** |
| | Distorted / Amplified MC Vocals | **Missing** | 0 | **HIGH** |
| **Other Confusing SFX** | Sirens & Mechanical Alarms | **Covered** | 49 | MEDIUM |
| | Electronic Ringing & Beeps | **Covered** | 40 | MEDIUM |
| | Cartoon Pitch Sweeps | **Partially Covered** | 2 | **HIGH** |
| | Squeaky Toys | **Partially Covered** | 2 | **HIGH** |
| | Animal Vocalizations (Dogs, Cats)| **Covered** | 47 | LOW |
| | Fireworks & Pyrotechnics | **Missing** | 0 | **HIGH** |
| | Microphone Wind Pops & Clipping | **Partially Covered** | 4 | MEDIUM |

---

## 5. False-Positive Root Cause Audit

Mapping historical Stage 5 errors against training representation ([`false_positive_coverage.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/false_positive_coverage.csv)):

```
Stage 5 False Positives vs Training Sample Availability:
  Slide Whistle (0.9328):    [ 0 slide whistles in train ] ---> CRITICAL FP
  Infant Crying (0.9355):    [ 28 baby cries in train    ] ---> CRITICAL FP (Formant Overlap)
  Squeaky Dog Toy (0.8703):  [ 0 squeaky toys in train   ] ---> HIGH FP
  Telephone Ringing (0.4062):[ 28 phones in train        ] ---> BORDERLINE FP (+0.056 margin)
```

1. **Slide Whistle (`ZipCartoon+HB02_55_8` - Prob 0.9328):**  
   *Root Cause:* Pure tonal sweeps in 2–3.5 kHz strongly excite YAMNet scream priors. With only 1 human mouth whistle in the training set, the linear decision boundary cannot separate tonal whistles from human screams.
2. **Squeaky Toy (`Toy+6080_61_2` - Prob 0.8703):**  
   *Root Cause:* High-pressure rubber squeaks produce high-frequency acoustic bursts mimicking vocal onset. Zero squeaky toys existed in training.
3. **Infant Crying (`Baby+2012_51` - Prob 0.9355):**  
   *Root Cause:* High-pitched crying shares fundamental frequency ($f_0 > 450\text{ Hz}$), harmonic structure, and frequency modulation with vocal distress screams. Max-pooling amplifies the single most intense crying frame. Needs dedicated hard-negative training.
4. **Telephone Ringing (`Telephone_DIGIX01-54` - Prob 0.4062):**  
   *Root Cause:* Repetitive high-frequency bells created borderline elevation (+0.0562 margin).

---

## 6. YAMNet 521-Class Ontology Analysis

The installed model class map ([`yamnet_521_class_inventory.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/yamnet_521_class_inventory.csv)) was extracted directly from the TensorFlow Hub asset:
`C:\Users\zahia\AppData\Local\Temp\tfhub_modules\9616fd04ec2360621642ef9455b84f4b668e219e\assets\yamnet_class_map.csv`.

### Key Ontology Insights:
- **121 of 521 classes** possess acoustic relevance to festival environments and potential false alarms.
- **Primary Target Class:** Index 11 (`/m/03qc9zr` - *Screaming*).
- **Critical Confusing Classes:**
  - Whistle (Index 396: `/m/0l156k`)
  - Cheering (Index 61: `/m/053hz1`) & Applause (Index 62: `/m/028ght`)
  - Synthesizer (Index 153: `/m/0l14qv`)
  - Baby cry, infant cry (Index 20: `/t/dd00002`)
  - Squeak (Index 355: `/m/07q6cd_`)
  - Shout (Index 6: `/m/07p6fty`) & Yell (Index 9: `/m/07sr1lc`)
  - Fireworks (Index 426: `/m/0g6b5`)
  - Wind noise (microphone) (Index 279: `/t/dd00092`)

> [!NOTE]
> YAMNet's 521 output classes are **classification probabilities produced by pretrained weights**, not audio samples. The model weights do not supply folders of audio files.

---

## 7. AudioSet Source Assessment

Full assessment documented in [`audioset_source_assessment.md`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/audioset_source_assessment.md):

1. **No Playable Audio:** Google AudioSet distributes only metadata CSVs (YouTube IDs, timestamps) and 128-dimensional VGGish embeddings.
2. **Feature Incompatibility:** The 128-dim VGGish embeddings cannot be used by our 1,024-dim YAMNet Logistic Regression classifier.
3. **Availability Degradation (Link Rot):** ~35% to 45% of 2017 YouTube links are permanently unavailable.
4. **Licensing & Legal Usability:** While metadata is `CC BY 4.0`, underlying YouTube videos are owned by third-party uploaders under Standard YouTube Licenses. Automated scraping violates YouTube ToS 5.B and introduces commercial copyright liability (**REQUIRES LEGAL REVIEW**).
5. **Verdict:** **Reject bulk AudioSet scraping** in favor of permissive audio repositories.

---

## 8. Prioritized Hard-Negative Roadmap

Ranked list of missing categories ([`hard_negative_priority_list.csv`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/hard_negative_priority_list.csv)):

| Rank | Category | Confusion Risk | Current Samples | Target Count | Primary Lawful Source | Legal Status |
| :---: | :--- | :--- | :---: | :---: | :--- | :---: |
| **1** | Rave & Referee Whistles | CRITICAL (Observed FP 0.9328) | 1 train, 1 test | 25–35 | Freesound / Local Mic Capture | **PERMISSIVE** |
| **2** | Crowd Cheering & Applause | CRITICAL (Pervasive festival roar) | 1 train, 0 test | 30–50 | Freesound (CC0 / CC BY) | **PERMISSIVE** |
| **3** | EDM Leads, Bass Drops & Synths | CRITICAL (Zero music in training) | 0 clips | 25–40 | Royalty-Free Stems / Freesound | **PERMISSIVE** |
| **4** | Vuvuzelas & Stadium Horns | HIGH (Continuous dense drone) | 0 clips | 15–20 | Local Mic Capture / Freesound | **PERMISSIVE** |
| **5** | Shouting & Excited MC Vocals | HIGH (Observed FN 0.0237) | 1 test | 20–30 | Stage 8.6 Consented Vocal Capture | **PERMISSIVE** |
| **6** | Squeaky Toys & Acoustic Transients | HIGH (Observed FP 0.8703) | 1 train, 1 test | 15–20 | Local Physical Toy Capture | **PERMISSIVE** |
| **7** | Fireworks & Pyrotechnics | MEDIUM-HIGH (Whistling rockets) | 0 clips | 15–20 | Freesound (CC0) | **PERMISSIVE** |
| **8** | Microphone Wind Noise & Clipping | MEDIUM (Transducer saturation) | 4 clips | 15–20 | Local Mic Fan Recording | **PERMISSIVE** |
| **9** | Infant Crying (High-Intensity) | MEDIUM (Observed FP 0.9355) | 45 train, 19 val/test | 10–15 | Freesound (Archival Ethical) | **PERMISSIVE** |

---

## 9. Recommended Next Steps

Documented in [`recommended_next_steps.md`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/reports/stage8_7_dataset_coverage_audit/recommended_next_steps.md):

1. **Priority 1: Whistles & Squeaks (25–35 clips):** Remediate the two highest Stage 5 false alarms via local laptop mic capture and Freesound CC0 clips.
2. **Priority 2: Crowd Cheering & Applause (30–50 clips):** Expand the solitary cheering clip in training to robust stadium and festival crowd coverage.
3. **Priority 3: EDM Synthesizers & Risers (25–40 clips):** Ingest electronic music production stems to represent festival stage acoustics.
4. **Execution Protocol:** Feed candidate clips into `backend/dataset/raw/hard_negatives/`, run `ingest_hard_negatives.py`, and complete human review with `review_hard_negatives.py`.
