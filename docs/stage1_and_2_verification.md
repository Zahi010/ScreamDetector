# Milestone 1: Stage 1 & Stage 2 Technical Verification Report

## 1. Project Overview
The Festival Scream Detection System is an end-to-end AI platform engineered to detect human scream-like distress vocalizations in dense, acoustic festival environments (music, crowd noise, shouting, cheer, whistling).

This document certifies the successful completion of **Stage 1 (Environment & Architecture Setup)** and **Stage 2 (Dataset Discovery & Pretrained YAMNet Verification)**.

---

## 2. Discovered Datasets & Physical File Inventory
The user's local filesystem was inspected without making alterations or deletions to the original downloads.

### Dataset A: OpenSLR 99 (Deeply Nonverbal Vocalization)
- **Official Source**: [https://openslr.org/99/](https://openslr.org/99/)
- **Discovered Location**: `C:\Users\zahia\Downloads\NonverbalVocalization\NonverbalVocalization`
- **Total Audio Files**: 727 WAV files
- **Target Scream Class (`screaming`)**: 51 WAV recordings
- **Candidate Non-Scream Classes**: 676 WAV recordings
  - Classes present: `coughing`, `crying`, `laughing`, `lip-popping`, `lip-smacking`, `moaning`, `nose-blowing`, `panting`, `sighing`, `sneezing`, `teeth-chattering`, `teeth-grinding`, `throat-clearing`, `tongue-clicking`, `yawning`
- **Metadata Files Present**: `README.md`, `Nonverbal_Vocalization.json`, `Deeply Nonverbal Vocalization Dataset description.pdf`

### Dataset B: NIGENS General Sound Events Database
- **Official Source**: [https://zenodo.org/records/2535878](https://zenodo.org/records/2535878)
- **Discovered Location**: `C:\Users\zahia\Downloads\NIGENS\NIGENS`
- **Total Audio Files**: 898 WAV files
- **Positive Scream Recordings**: 76 WAV recordings
  - `femaleScream`: 45 recordings
  - `maleScream`: 31 recordings
- **Candidate Non-Scream Acoustic Classes**: 822 WAV recordings
  - Classes present: `alarm`, `baby`, `crash`, `dog`, `engine`, `femaleSpeech`, `fire`, `footsteps`, `general`, `knock`, `maleSpeech`, `phone`, `piano`
- **Metadata Files Present**: Official 8-fold cross-validation split lists (`.flist` files)

### Combined Acoustic Dataset Inventory
| Metric | Count |
| :--- | :--- |
| Total Discovered Audio Files | **1,625 WAV files** |
| Total Positive Scream Recordings | **127 recordings** (51 OpenSLR + 45 NIGENS Female + 31 NIGENS Male) |
| Total Candidate Negative Recordings | **1,498 recordings** (676 OpenSLR + 822 NIGENS Environmental) |

---

## 3. Environment & Dependency Resolution
- **Python Version**: Python 3.11.17 (Isolated in `.venv` via `uv`)
- **Operating System**: Windows 11 AMD64

### Compatibility Fixes Applied
1. **NumPy Compatibility**: Pinned `numpy>=1.24.0,<2.0.0` (installed `v1.26.4`) to prevent C-extension binary incompatibility with TensorFlow Hub and SciPy.
2. **TensorFlow Hub `pkg_resources` Resolution**: Modern `setuptools >= 70` removed `pkg_resources`, which `tensorflow_hub.resolver` historically relied upon. Pinned `setuptools<70.0.0` (installed `v69.5.1`) to guarantee seamless loading without runtime `ModuleNotFoundError`.
3. **Audio Preprocessor Resampling**: Implemented `scipy.signal.resample_poly` with GCD rational factors, guaranteeing exact 16,000 Hz conversion across non-standard sampling rates (e.g. 44.1 kHz, 48 kHz).

---

## 4. Pretrained YAMNet Model Verification
- **Model Handle**: `https://tfhub.dev/google/yamnet/1`
- **Input Requirements**: Mono, 16,000 Hz, 1D float32 array in `[-1.0, 1.0]`
- **Frame Spec**: Window duration: 0.975s (15,600 samples), Hop step: 0.4875s (7,800 samples)
- **Embedding Matrix Verified**: Shape `(N_frames, 1024)` -> **Confirmed 1,024 features per audio frame**
- **AudioSet Output Vocabulary**: 521 acoustic categories

### Real Audio Inference Results
#### OpenSLR 99 Test (`screaming/2CVI_15_11_0_15_0_0_0.wav`):
- Native Sample Rate: 16,000 Hz | Duration: 2.240s | Samples: 35,840
- Embeddings: `(4, 1024)`
- Frame 2 & 3: Predicted class `[11] Screaming` (score up to 0.3196).

#### NIGENS Test (`femaleScream/118521__huboftheuniverseprod__thegutbezahlscream.wav`):
- Native Sample Rate: 44,100 Hz -> Resampled to 16,000 Hz | Duration: 2.769s | Samples: 44,304
- Embeddings: `(5, 1024)`
- Pretrained Predictions: Rank 1: `[11] Screaming` (Mean score: 0.3396, Peak: 0.6103).

---

## 5. Architectural Distinction
It is critical to distinguish between:
1. **Pretrained YAMNet**: A 521-class general AudioSet classifier that serves exclusively as a **frozen acoustic feature extractor**.
2. **Custom Festival Classifier (Stage 5)**: A trained discriminator consuming the 1,024-dimensional embeddings, specifically calibrated with probability thresholds and temporal event-aggregation rules to distinguish festival screams from music drops, cheering crowds, sirens, and microphone pops.
