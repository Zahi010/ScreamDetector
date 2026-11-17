# Dataset Integrity and Validation Report (Stage 8.9.26)

**Stage:** 8.9.26 — Integrated Multi-Stage Detection  
**Auditor:** Senior Audio ML Researcher & Evaluation Specialist  
**Status:** VALIDATED AUDIT RECORD  
**Timestamp:** 2026-10-31  

---

## 1. Executive Summary & Split Integrity

Stage 8.9.26 enforces strict source-group isolation and prevents recording-level or speaker-level leakage.

All experiments utilize the standardized, leak-free source-group partitioning across the repository's **2,804 recordings**:

- **Train Split:** 1,969 recordings across **669 source groups**
- **Validation Split:** 373 recordings across **144 source groups**
- **Test Split:** 462 recordings across **142 source groups**

### Split Isolation Census:
- **Train $\cap$ Test:** **0** source groups (0.00% leakage)
- **Validation $\cap$ Test:** **0** source groups (0.00% leakage)
- **Train $\cap$ Validation:** **0** source groups (0.00% leakage)
- **Audio Content Hash Duplicates:** **0** cross-split identical files (verified via SHA-256)

---

## 2. Test Cohort Composition ($N=462$)

The independent held-out test split contains:

| Category Class | Sample Count ($N$) | Percentage | Acoustic / Confuser Profile |
|---|:---:|:---:|---|
| **Human Screams (Positive)** | 78 | 16.88% | Standard shrieks, terror screams, startle screams, sustained screams, masked screams |
| **Shouting & Excited Speech** | 84 | 18.18% | Monosyllabic shouts ("NO!", "HEY!"), disyllabic shouts, sports yelling, angry tirades |
| **Crowd Cheering & Chanting** | 56 | 12.12% | Festival crowds, stadium cheering, synchronized vocal chanting |
| **Whistles & Sirens** | 17 | 3.68% | Referee whistles, emergency vehicle sirens, synthetic alert tones |
| **Music & Synthetic Audio** | 31 | 6.71% | Electronic festival music, heavy bass, guitar transients, synth pads |
| **Ambient & Environmental Noise** | 196 | 42.42% | Rain, park ambience, footsteps, mechanical clatter, wind noise, distant babble |
| **Total Test Recordings** | **462** | **100.0%** | Comprehensive evaluation benchmark |

---

## 3. Short-Event Stratification ($N=78$ Screams)

To safeguard against the systematic suppression of short screams, the positive test cohort is stratified into four duration bins:

| Duration Stratum | Duration Window | Count ($N$) | Percentage of Screams |
|---|---|:---:|:---:|
| **Ultra-Short Screams** | 200 ms – 500 ms | 8 | 10.26% |
| **Short Screams** | 500 ms – 800 ms | 14 | 17.95% |
| **Combined Short Cohort** | **< 800 ms** | **22** | **28.21%** |
| **Moderate Screams** | 800 ms – 1500 ms | 26 | 33.33% |
| **Extended Screams** | > 1500 ms | 30 | 38.46% |
| **Total Screams** | All Durations | **78** | **100.00%** |

---

## 4. Historical Stage 5 Test Set Preservation

The historical Stage 5 test predictions (`backend/reports/test_predictions.csv`, SHA-256 `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`) and baseline evaluation (`backend/reports/stage5_test_evaluation.md`, SHA-256 `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`) remain 100% frozen and unmodified.

No historical Stage 5 test recording was used for training or threshold tuning in this stage.

---

## 5. Licensing and Commercial Eligibility Census

| License Category | Recording Count | Share (%) | Commercial Deployment Eligibility |
|---|:---:|:---:|---|
| **CC0 (Public Domain)** | 312 | 11.13% | Commercially Eligible |
| **CC BY (Attribution 3.0 / 4.0)** | 750 | 26.75% | Commercially Eligible with Attribution |
| **CC BY-NC (Non-Commercial)** | 1,212 | 43.22% | **Research / Academic Only** |
| **CC BY-NC-ND (No Derivatives)** | 314 | 11.20% | **Strict Research Only** |
| **Academic Research / Unverified** | 216 | 7.70% | **Research Only** |
| **Total Repository Audio** | **2,804** | **100.00%** | **37.88% Commercially Eligible** |

**Crucial Compliance Note:** 62.12% of repository recordings are restricted to non-commercial academic research. Any commercial deployment must replace NC recordings with cleared, lawfully acquired festival audio.

---

## 6. Generalization Readiness Assessment for Stage 8.9.27

**Mandatory Scientific Transparency:**  
Because the current 462-recording test cohort was evaluated during Stages 8.9.24 and 8.9.25 to identify architectural failure modes and the Monosyllabic Invariance Barrier, it **cannot be claimed as an untouched, blind final test set** for Stage 8.9.27.

To substantiate true generalization claims, **Stage 8.9.27 is BLOCKED from making unreserved generalization claims until a genuinely independent, unseen external evaluation cohort (with new source groups and speakers) is curated and locked.**
