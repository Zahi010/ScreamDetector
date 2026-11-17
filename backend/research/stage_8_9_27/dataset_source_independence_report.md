# STAGE 8.9.27 INDEPENDENT EVALUATION REPORT: Dataset Source Independence & De-Duplication Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.27  
**Operating Mode:** Offline Research & Independent Evaluation  
**Production Status:** FROZEN — Zero Production Modifications  
**Locked Manifest Checksum:** `ad976bca78177202ba2e405a8c2f7f5198eb307c731a962019615ef18387ad67`

---

## 1. Executive Summary & Audit Mandate

In Stage 8.9.27, our primary mission is to establish whether the integrated multi-stage scream detection pipeline developed in Stage 8.9.26 generalizes to genuinely unseen recordings. Under strict forensic standards, **independence cannot be assumed or superficially asserted**; it must be mathematically and provenance-verified across every candidate recording.

Prior stages (Stages 8.9.22–8.9.26) relied on a 2,804-recording benchmark split (`train: 1969`, `val: 373`, `test: 462`) established in Stage 8.9.17. While that split enforced cross-split disjointness, candidate architectures and fusion weights were repeatedly tuned against the test cohort ($N=462$). Therefore, the historical test set could no longer provide an untouched, prospective-blind evaluation.

This audit evaluated all **2,694 audio files** on disk to construct an independent cohort, applying strict four-tier verification:
1. **Tier 1: Exact Bit-Level Audio Hash Matching (SHA-256):** Comparing physical audio file contents against all 2,804 historical records.
2. **Tier 2: Source Sound Identifier Matching:** Tracing numeric sound IDs (e.g., Freesound clip numbers) across naming variants to catch un-normalized copies.
3. **Tier 3: Source-Group & Uploader Disjointness:** Excluding any candidate originating from a creator, uploader, or recording session present in the 2,804 splits.
4. **Tier 4: Acoustic Provenance & Ground-Truth Sanity Audit:** Quarantining ambiguous files, misleading folder probes, and mislabeled confusers.

---

## 2. Forensic Discovery: The "Independence Illusion" of Renamed Files

During the audit of candidate directories (`backend/dataset/stage8_8_hard_negatives/approved` containing 339 WAV files), an apparent discrepancy emerged:
- Initial SHA-256 hashing showed **0 out of 339 files** directly matched the recorded SHA-256 hashes of the 2,804 split files.
- A superficial auditor might have concluded that all 339 approved recordings were genuinely independent from the training and test sets.

### Forensic Finding: The Stage 8.9.17 Ingestion Prefix
Forensic investigation revealed that in Stage 8.9.17:
- Files from `stage8_8_hard_negatives` (with IDs such as `fs_169001`, `fs_269001`) had been ingested into `experiments/v2_hard_negative_training/audio/` by prefixing their filenames with `v2_` (e.g., `v2_fs_169001.wav`).
- During ingestion, files underwent 16 kHz mono standardized PCM resampling and bit-quantization.
- **332 out of the 339 "approved" candidate files** had actually been placed directly into the 2,804 development splits (`train: 261`, `val: 39`, `test: 32`).
- Including these files in the independent cohort would have caused **catastrophic data leakage**, testing the model on samples already seen during training!

**Corrective Action Taken:** All 332 files were flagged as historical split overlaps and strictly excluded from the independent evaluation cohort.

---

## 3. Forensic Discovery: Folder Mislabling in Supplementary Folders

In `backend/experiments/stage8_9_20_acoustic_discriminability/data/supplementary_short_screams/`, 113 WAV files were cataloged. A naive pipeline might have loaded all files in this folder as ground-truth positive screams.

### Forensic Finding: Acoustic Probe Injection
By cross-referencing original metadata in `stage8_8_manifest.json` and `candidates` database:
- `supp_short_scream_016_186931.wav`: Original title `rocket-whistle2.wav: single short whistle` (Fireworks / Pyrotechnics).
- `supp_short_scream_018_186955.wav`: Original title `explosion_small.wav: small weak explosion` (Fireworks / Pyrotechnics).
- `supp_short_scream_021_186958.wav`: Original title `explosion7.wav: small weak explosion` (Fireworks / Pyrotechnics).
- `supp_short_scream_039_344067.wav`: Original title `double squeak.wav: a squeak of sorts` (Whistles / Squeaks).
- `supp_short_scream_044_169003.wav`: Original title `Rubber Dog Toy Squeak Repeated` (Dog Toy Squeak).
- `supp_short_scream_045_169005.wav`: Original title `Ultra High Pitch Dog Whistle` (Acoustic Dog Whistle).
- `supp_short_scream_047_369003.wav`: Original title `Acid Synth Resonance Filter Sweep` (EDM Synthesizer).

These files were injected in Stage 8.9.20 as acoustic probes to test specific edge-case false positives. **None of them are screams.** Treating them as screams would have corrupted the independent ground truth with 7 false positive labels.

**Corrective Action Taken:** All acoustic probe files were quarantined and removed from the positive scream evaluation set.

---

## 4. Source-Group and Speaker Overlap Verification

Section 5 dictates: *"No recording or identifiable source group from previous development splits may enter the new independent cohort."*

FSD50K and Freesound recordings contain metadata identifying the uploader/author account. When multiple recordings share the same uploader, acoustic properties (microphone type, room acoustics, vocal tract of the speaker) are shared, creating potential acoustic leakage.

Using the uploader index from `stage8_9_11_dataset_manifest.csv` and `source_group_splits.csv`:
- We identified **26 candidate recordings** whose original uploader was present in the 2,804 development splits (e.g., `fsd50k_user_snakebarney`, `fsd50k_user_klankbeeld`, `stage8_9_readeonly`, `stage8_9_reitanna`).
- Although these specific audio recordings were not in the training set, their shared acoustic provenance violated the strict source-group independence mandate.

**Corrective Action Taken:** All 26 source-group overlapping recordings were excluded from the final primary cohort.

---

## 5. Comprehensive Audio Census & Reconciliation

| Audit Classification Category | Recording Count | Percentage | Forensic Action & Disposition |
|:---|:---:|:---:|:---|
| **Historical Development Splits (Train/Val/Test)** | 1,798 | 66.74% | **EXCLUDED:** Exact SHA-256 or PCM match to 2,804 splits |
| **Sound ID / Ingestion Overlaps** | 524 | 19.45% | **EXCLUDED:** Renamed variants (e.g. `v2_` prefix), resampled duplicates |
| **Source-Group / Uploader Overlaps** | 26 | 0.97% | **EXCLUDED:** Shared uploader / recording environment with splits |
| **Acoustic Probes & Ambiguous Records** | 51 | 1.89% | **QUARANTINED:** Dog whistles, fireworks, synthetic probe mixtures |
| **Primary Independent Blind Evaluation Cohort** | **254** | **9.43%** | **LOCKED & ACCEPTED:** Strictly disjoint real-world audio |
| **Secondary Robustness Cohort (Synthetic SNR)** | **41** | **1.52%** | **LOCKED & ACCEPTED:** Separately evaluated noise mixtures |
| **Total Workspace Audio Files Audited** | **2,694** | **100.0%** | Full repository census completed |

---

## 6. Composition of the Locked Independent Evaluation Cohort

The locked independent evaluation manifest contains **254 real-world recordings** and **41 secondary robustness recordings** ($N_{\text{total}} = 295$):

### 6.1 Primary Blind Real Cohort ($N = 254$)
- **Positive Human Screams ($N = 14$):**
  - **Short Screams ($\le 1.50\text{s}$):** 4 recordings (durations: 0.499s, 0.540s, 0.743s, 1.266s).
  - **Sustained Screams ($> 1.50\text{s}$):** 10 recordings (durations: 2.19s to 8.00s).
  - **Scarcity Finding:** While over 228 scream files exist in the repository, only 14 positive screams satisfy 100% strict independence from the 2,804 training splits and have verified real human distress ground truth. As required by Section 12, this positive data scarcity is transparently documented and prevents claiming full statistical power for positive scream generalization.
- **Negative Confusers & Hard Negatives ($N = 240$):**
  - **Monosyllabic Shouting ($< 0.90\text{s}$):** 11 recordings (isolated commands: "NO!", "HEY!", "STOP!").
  - **Disyllabic Shouting ($0.90\text{–}2.20\text{s}$):** 57 recordings.
  - **Multi-syllabic Shouting ($> 2.20\text{s}$):** 52 recordings.
  - **Crowd Cheering & Chanting:** 55 recordings.
  - **Whistles & High-Pitch Squeaks:** 24 recordings.
  - **Ambient Environmental Noise:** 17 recordings.
  - **Sirens & Fireworks:** 11 recordings.
  - **Infant Crying:** 9 recordings.
  - **Other Vocal/Acoustic Hard Negatives:** 4 recordings.

### 6.2 Secondary Robustness Cohort ($N = 41$)
- **Synthesized Masked Screams:** 41 recordings spanning SNR levels from -6 dB to +6 dB against festival crowd and EDM background tracks.

---

## 7. Limitations of Speaker Identification in Public Data

When curating from public datasets (FSD50K, NIGENS, Freesound):
1. **Metadata Anonymization:** Uploader account names represent Freesound user profiles, not necessarily individual voice actors. A single user may upload recordings of multiple actors, or multiple users may upload sound design clips recorded by the same voice talent.
2. **Text-Free Annotation:** In shouting recordings, linguistic transcriptions are rarely provided. Phonetic syllabic classification (monosyllabic vs multi-syllabic) had to be determined by duration analysis and energy envelope peaks.
3. **Conservative Posture:** Where speaker independence could not be mathematically guaranteed due to shared uploaders, the recordings were conservatively excluded.

---

## 8. Integrity Declaration & Manifest Locking

The independent evaluation manifest was serialized to [independent_dataset_manifest.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_27/independent_dataset_manifest.csv).

Before any candidate model was evaluated, the manifest was sealed with SHA-256 checksum:
`ad976bca78177202ba2e405a8c2f7f5198eb307c731a962019615ef18387ad67`
recorded in `backend/research/stage_8_9_27/manifest_lock.json`. Zero model training, threshold tuning, or hyperparameter adjustment was performed on this dataset.
