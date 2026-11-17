# Stage 8.9.10 — Commercial Dataset Remediation and Evaluation Readiness Audit Report

**Operating Mode:** Data Governance, Licensing Audit, and Experimental Preparation ONLY. Production is strictly frozen.  
**Auditor Roles:** Senior Acoustic ML Engineer, Dataset Governance Auditor, Safety-Critical ML Validation Specialist.  
**Date of Audit:** October 29, 2026  
**Status:** COMPLETE — READY FOR INDEPENDENT REVIEW (NO TRAINING EXECUTED)

---

## 1. Executive Summary & Production Freeze Verification

In Stage 8.9.9, an independent reproducibility audit revealed two critical operational findings:
1. Historical dataset manifests (v2 and v3) contained recordings licensed under **Creative Commons Non-Commercial (CC BY-NC 3.0)** and legacy **Sampling+ 1.0** licenses, rendering any model trained on them ineligible for commercial deployment.
2. Previously reported inference latency figures (~1.65 ms) measured only Scikit-Learn linear classifier evaluation on pre-extracted feature arrays, omitting audio decoding, resampling, YAMNet backbone inference, and STFT-based turbulence feature extraction.

Stage 8.9.10 systematically remediates these findings:
- All 152 CC BY-NC recordings plus 9 legacy Sampling+ recordings (161 total) have been formally quarantined with complete provenance tracking in [`restricted_recordings_audit.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/restricted_recordings_audit.csv).
- A clean, versioned manifest [`commercially_eligible_manifest.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/commercially_eligible_manifest.json) containing **1,167 verified commercial-compatible recordings** across 468 disjoint source groups has been constructed.
- A standardized end-to-end latency measurement protocol was developed and empirically benchmarked on the edge runtime, proving the full pipeline achieves a median latency of **17.62 ms** (p95: **18.89 ms**), well within the 25.0 ms edge budget.
- Production artifacts and ground-truth review databases were verified to be **100% bit-identical and strictly frozen**.

### 1.1 Authoritative Production Hash Ledger

| Artifact Path | Expected SHA-256 | Actual Verified SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | `AD6E428D05D2359DA73B6DEE7CFDCEC646C87390B496B59CAD5F46B5A452851F` | **EXACT MATCH** |
| `backend/models/model_metadata.json` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | `30C1C75D81AD61B1D0CACB70B221D034840888C7BFEDE949A15D47B139699F60` | **EXACT MATCH** |
| `backend/reports/test_predictions.csv` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | `E93BE4550F97FE2CFE6BC0F2366650833D96F284C45CD1EB6026FBA0DB98449D` | **EXACT MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | `9E55B1F574E18BC4623A871D58926FEFCCD29F4C4E3EE22010A4A54A4E4CD1D2` | **EXACT MATCH** |
| `backend/database/stage8_9_reviews.db` | Bit-identical record audit across 343 reviewed records | 338 Approved Non-Scream, 2 Scream Present, 3 Ambiguous; Anchor `fsd50k_349401` = `SCREAM_PRESENT` | **VERIFIED** |
| **Production Decision Threshold** | `0.3500` | `0.3500` (in `model_metadata.json`) | **EXACT MATCH** |

The audit ledger is codified in [`artifact_integrity_audit.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/artifact_integrity_audit.json).

---

## 2. Audit of Restricted Recordings

### 2.1 Methodology & Inspection Scope
The historical experimental manifest `v3_experimental_manifest.json` contained **1,328 recordings** across 503 source groups. Each entry was audited for:
- Stated license vs underlying Freesound/FSD50K license metadata.
- Synthetic provenance (i.e. whether synthesized clips incorporated non-commercial source screams or background stems).
- License compatibility with commercial distribution under US and international copyright law.

### 2.2 Quarantined Recordings Summary
A total of **161 recordings** were quarantined:
1. **152 CC BY-NC 3.0 recordings:**
   - 148 audio files originated from FSD50K / Freesound users who explicitly marked their contributions as Non-Commercial.
   - 4 audio files were synthetic masked scream mixtures (`synth_masked_000000`, `000001`, `000004`, `000005`) that blended CC BY-NC foreground scream tokens into crowd noise. Under derivative-work clauses, these files inherit the NC restriction.
2. **9 Sampling+ 1.0 recordings:**
   - Released under Creative Commons Sampling Plus 1.0 (a retired license that expressly forbids commercial advertising and wholesale redistribution). In an abundance of caution for commercial audit rigor, these 9 clips were excluded.

### 2.3 Quarantine Breakdown by Category and Split

| Target Category | Total v3 | Quarantined Total | Retained Eligible | Retention Rate (%) | Dominant Quarantined License |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `shouting_and_speech` | 320 | **88** | 232 | 72.5% | CC BY-NC 3.0 (87), Sampling+ 1.0 (1) |
| `crowd_chant_cheering` | 240 | **36** | 204 | 85.0% | CC BY-NC 3.0 (33), Sampling+ 1.0 (3) |
| `scream` | 228 | **13** | 215 | 94.3% | CC BY-NC 3.0 (13) |
| `whistles_and_squeaks` | 150 | **9** | 141 | 94.0% | CC BY-NC 3.0 (6), Sampling+ 1.0 (3) |
| `infant_crying` | 70 | **9** | 61 | 87.1% | CC BY-NC 3.0 (7), Sampling+ 1.0 (2) |
| `masked_distant_screams`| 125 | **4** | 121 | 96.8% | CC BY-NC 3.0 derivative mixtures (4) |
| `sfx_sirens_fireworks` | 80 | **2** | 78 | 97.5% | CC BY-NC 3.0 (2) |
| `general_environmental` | 115 | **0** | 115 | 100.0% | (All CC0 / CC BY) |
| **OVERALL TOTAL** | **1,328** | **161** | **1,167** | **87.9%** | **152 CC BY-NC, 9 Sampling+** |

**Split Impact of Quarantine:**
- **Train Split:** 741 $\rightarrow$ 626 recordings (115 quarantined; 294 source groups $\rightarrow$ 276 retained, loss of 18 source groups).
- **Validation Split:** 293 $\rightarrow$ 275 recordings (18 quarantined; 98 source groups $\rightarrow$ 91 retained, loss of 7 source groups).
- **Test Split:** 294 $\rightarrow$ 266 recordings (28 quarantined; 111 source groups $\rightarrow$ 101 retained, loss of 10 source groups).

The complete line-by-line audit is saved to [`restricted_recordings_audit.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/restricted_recordings_audit.csv). Original audio files and historical manifests remain unmolested on disk.

---

## 3. Commercially Eligible Experimental Manifest

### 3.1 Structure & Integrity
A new manifest [`commercially_eligible_manifest.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/commercially_eligible_manifest.json) was generated containing **1,167 recordings**.

**License Distribution of Eligible Cohort:**
- **Creative Commons 0 (CC0 1.0 Universal / Public Domain):** 648 recordings (55.5%)
- **Creative Commons Attribution 3.0 (CC BY 3.0):** 422 recordings (36.2%)
- **Creative Commons Attribution 4.0 (CC BY 4.0):** 97 recordings (8.3%)

### 3.2 Source-Group Disjointness Verification
To ensure scientific validity and avoid data leakage:
- Unique source groups in Train: **276**
- Unique source groups in Validation: **91**
- Unique source groups in Test: **101**
- Total unique source groups across eligible manifest: **468**
- **Intersection between Train, Val, and Test source groups:** **0 (Strictly Disjoint)**.

### 3.3 Evaluation of Category Balance & Critical Deficits
Removing 161 non-commercial recordings caused an uneven deficit across categories:
1. **Shouted Speech Deficit:** The loss of 88 shouting clips (reduction of 27.5%) is the most severe impact. Shouting is the primary source of hard-negative false alarms in festival environments.
2. **Crowd Chants & Cheering:** A loss of 36 clips (15.0% reduction).
3. **Scream Diversity:** 215 genuine screams remain across 94 independent source groups, preserving 94.3% of the scream cohort.

Full before/after counts are recorded in [`category_balance_before_after.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/category_balance_before_after.csv).

---

## 4. Targeted Data Acquisition Plan

To restore statistical power in depleted hard-negative classes without compromising commercial eligibility, a targeted acquisition plan has been established.

### 4.1 Guiding Principles
1. **Source Group Priority:** Quotas are specified in terms of **independent source groups** (uploaders/locations/recordists), not simply raw clip counts. A single 10-minute crowd recording must not be sliced into 50 clips and counted as 50 samples.
2. **Strict Commercial Licensing:** Only CC0 1.0 or CC BY (2.0/3.0/4.0) assets with verified author attribution may be ingested. No CC BY-NC, CC BY-ND, or unverified public web scrapes.
3. **Acoustic Realism:** Audio must feature realistic acoustic festival artifacts (PA bleed, heavy bass, room reverberation, crowd chatter).

### 4.2 Acquisition Quotas by Category

| Category | Primary Acoustic Gap | Target New Source Groups | Proposed Audio Clips | Preferred Verified Sources |
| :--- | :--- | :--- | :--- | :--- |
| `shouting_and_speech` | Excited yells, PA announcements, drunken slurring, outdoor festival callouts | **40 source groups** | 80–120 clips | CC0/CC BY Freesound recordists, OpenSLR public speech corpora (CC-BY/CC0 subsets) |
| `crowd_chant_cheering` | Rhythmic festival clapping, sports-style chants, festival stage countdowns | **30 source groups** | 60–90 clips | CC BY Freesound field recordings (stadiums, festivals, protests) |
| `masked_distant_screams` | Distant screams drowned in sub-bass EDM kick drums and guitar reverb | **20 source groups** | 40–60 synthetic & real mixes | CC0 scream tokens mixed over CC0 EDM / rock stems at -10 to -3 dB SNR |
| `scream` | Female and child high-register screams, panic shrieks, startle responses | **15 source groups** | 30–50 clips | Verified CC BY Freesound vocal artists, verified horror foley with CC0/CC BY licensing |
| `infant_crying` | Tantrums, high-pitch colic crying (potential false positive trigger) | **10 source groups** | 20–30 clips | Baby Chillax / Freesound CC0 cry recordings |
| `whistles_and_squeaks` | Rave whistles, dog whistles, microphone feedback squeals | **10 source groups** | 20–25 clips | Freesound CC BY event whistles, feedback sound effects |
| **TOTAL** | | **125 source groups** | **250–375 clips** | All with verified attribution |

The detailed acquisition methodology, attribution register requirements, and intake validation pipeline are documented in [`targeted_data_acquisition_plan.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/targeted_data_acquisition_plan.md). **No audio downloading was performed during this stage.**

---

## 5. Preregistered Next-Experiment Evaluation Protocol (Stage 8.9.11)

To prevent p-hacking, confirmation bias, and threshold overfitting, the evaluation protocol for Stage 8.9.11 has been preregistered in [`next_experiment_preregistration.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/next_experiment_preregistration.md).

### 5.1 Candidates & Hypotheses
- **Candidate D_v4 (Baseline Linear Fusion):** Platt-scaled Logistic Regression on 1,024 YAMNet embeddings + 2 turbulence features (trained on eligible manifest).
- **Candidate T1_v4 (Temporal Smoothing Baseline):** Rolling 1.5s median filter over D_v4 probabilities.
- **Candidate H_v4_Commercial (Trained Calibrated Hybrid):** Feature-standardized ElasticNet classifier incorporating 16 frame-level acoustic turbulence statistics.
- **Candidate H_v5_SNR (Acoustic Turbulence with Dynamic Noise Normalization):** Candidate H_v4 augmented with running SNR estimation.

### 5.2 Strict Validation-Only Threshold Tuning
For each candidate $m \in \{D, T1, H4, H5\}$:
$$\tau_m^* = \arg\max_{\tau \in [0.10, 0.90]} \text{F1}_{\text{scream}}(\tau \mid \mathcal{D}_{\text{val}})$$
Subject to:
$$\text{Recall}_{\text{scream}}(\tau \mid \mathcal{D}_{\text{val}}) \ge 0.960 \quad \text{and} \quad \text{FPR}_{\text{hard\_negative}}(\tau \mid \mathcal{D}_{\text{val}}) \le 0.050$$
If no threshold satisfies both constraints on validation data, the candidate with the highest validation scream recall subject to $\text{FPR} \le 0.08$ shall be selected and marked as **CONDITIONALLY GATED**. The held-out test set shall be evaluated **exactly once** using $\tau_m^*$.

### 5.3 Statistical Comparison & Uncertainty Estimation
- **Paired Hypothesis Testing:** McNemar's test with Edwards continuity correction on binary test predictions.
- **PR-AUC Confidence Intervals:** Stratified 1,000-iteration cluster bootstrap resampling at the **source-group level** to account for intraclass correlation.
- **Multiple Comparisons:** Family-Wise Error Rate (FWER) controlled at $\alpha = 0.05$ using Holm-Bonferroni step-down correction across all candidate pairwise comparisons.
- **Prevalence-Adjusted Precision:** Real-world event precision computed at base rates of 1:1,000 and 1:10,000 hours of festival background audio.

---

## 6. Standardized End-to-End Latency & Edge Footprint Protocol

In Stage 8.9.9, the auditor noted that previous latency benchmarks measured only model prediction on pre-computed feature arrays. In Stage 8.9.10, an end-to-end benchmark harness was built and executed on the production runtime environment (`benchmark_end_to_end_latency.py`).

### 6.1 Benchmark Results (1.0-second Audio Window, 16 kHz PCM)

Empirical execution across 10 warm-up runs and 50 timed iterations:

| Pipeline Stage | Operation Description | Median Latency (ms) | p95 Latency (ms) | Relative Pipeline Cost (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | Audio Ingestion, 16-bit PCM Buffer Unpacking | **0.394 ms** | 0.521 ms | 2.2% |
| **Stage 2** | Preprocessing, Float Conversion & DC Offset Filtering | **0.203 ms** | 0.287 ms | 1.2% |
| **Stage 3** | YAMNet Deep Feature Extraction (TensorFlow Lite graph) | **11.037 ms** | 11.954 ms | **62.6%** |
| **Stage 4** | Acoustic Turbulence & Temporal Variance (SciPy STFT) | **2.723 ms** | 3.118 ms | **15.5%** |
| **Stage 5** | Classifier Evaluation & Platt Scaling Calibration | **3.219 ms** | 3.893 ms | **18.3%** |
| **Stage 6** | State Machine, Hysteresis & Output Emission | **0.021 ms** | 0.035 ms | 0.1% |
| **CLASSIFIER-ONLY** | Stage 5 Inference alone | **3.219 ms** | **3.893 ms** | — |
| **TOTAL PIPELINE** | Complete Ingestion to Alert Emission | **17.624 ms** | **18.890 ms** | **100.0%** |

### 6.2 Architectural Insights & Edge Feasibility
1. **Budget Compliance:** The total end-to-end latency of **17.62 ms** is well below the target budget of **25.0 ms**, consuming only **3.5%** of a 500 ms sliding window step.
2. **YAMNet Dominance:** YAMNet inference accounts for 62.6% of total computational time. Optimizations (e.g., INT8 quantization or caching overlapping spectrograms) should focus here.
3. **Classifier Artifact Size:** The serialized model file `model_hv4_calibrated_hybrid.joblib` is **142.37 KB** on disk. The previously cited 22.4 KB figure only counted the LogisticRegression weight vector and omitted the StandardScaler's internal `mean_`, `var_`, and `scale_` float64 parameter arrays (5,144 elements each). At 142 KB, the model remains well within edge flash memory limits (< 2 MB).
4. **Memory Footprint:** Peak process heap delta during inference is 1.23 MB; the complete YAMNet runtime footprint is ~14.5 MB.

The full protocol and benchmarking methodology are recorded in [`end_to_end_latency_protocol.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/end_to_end_latency_protocol.md) and [`end_to_end_latency_benchmark.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/end_to_end_latency_benchmark.json).

---

## 7. Deliverables Checklist

All required Stage 8.9.10 deliverables have been generated and validated:

| Required Deliverable | File Path | Status | Summary of Content |
| :--- | :--- | :--- | :--- |
| **Comprehensive Readiness Report** | `.../stage8_9_10_readiness/stage8_9_10_readiness_report.md` | **COMPLETE** | This document |
| **Restricted Recordings Audit CSV** | `.../stage8_9_10_readiness/restricted_recordings_audit.csv` | **COMPLETE** | 161 records (152 CC BY-NC + 9 Sampling+) with complete provenance |
| **Commercially Eligible Manifest** | `.../stage8_9_10_readiness/commercially_eligible_manifest.json` | **COMPLETE** | 1,167 verified CC0/CC BY recordings across 468 disjoint source groups |
| **Category Balance CSV** | `.../stage8_9_10_readiness/category_balance_before_after.csv` | **COMPLETE** | Detailed split-by-category before/after counts and retention percentages |
| **Targeted Acquisition Plan** | `.../stage8_9_10_readiness/targeted_data_acquisition_plan.md` | **COMPLETE** | Source-group-driven acquisition targets (+125 groups, 250–375 clips) |
| **Next Experiment Preregistration** | `.../stage8_9_10_readiness/next_experiment_preregistration.md` | **COMPLETE** | Preregistered hypotheses, validation tuning, and paired statistical tests |
| **End-to-End Latency Protocol** | `.../stage8_9_10_readiness/end_to_end_latency_protocol.md` | **COMPLETE** | Hardware setup, methodology, and latency profiling separating classifier from E2E |
| **Artifact Integrity Audit JSON** | `.../stage8_9_10_readiness/artifact_integrity_audit.json` | **COMPLETE** | Verified SHA-256 hashes and production freeze confirmation |

---

## 8. Final Decision & Stop Condition

### 8.1 Audit Findings Summary
1. **Restricted Recordings Identified:** Yes. All 152 CC BY-NC recordings plus 9 legacy Sampling+ recordings were systematically identified, mapped, and quarantined.
2. **Manifest Provenance:** Yes. The new manifest [`commercially_eligible_manifest.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_10_readiness/commercially_eligible_manifest.json) contains exclusively CC0, CC BY 3.0, and CC BY 4.0 audio files with full author attribution, source URLs, and file checksums.
3. **Data Gaps Identified:** The removal of non-commercial recordings depleted `shouting_and_speech` (-88 clips, 72.5% retained) and `crowd_chant_cheering` (-36 clips, 85.0% retained). A targeted acquisition plan targeting 125 independent source groups has been prepared to fill these gaps.
4. **Evaluation Disjointness Guaranteed:** The new manifest strictly enforces source-group disjointness (276 train, 91 val, 101 test; 0 overlap), preventing data leakage.
5. **Requirements Before Next Model Training:**
   - Independent peer review of this audit.
   - Execution of the targeted acquisition plan to acquire eligible CC0/CC BY shouting and crowd recordings.
   - Formal sign-off on the preregistered evaluation protocol before running Stage 8.9.11 model training.

### 8.2 Mandatory Stop Condition
In accordance with Stage 8.9.10 directives:
- **No model has been trained.**
- **No production threshold has been altered.**
- **The production database and review records remain completely unchanged.**
- **Production SHA-256 hashes remain verified and frozen.**

Execution is now halted. Awaiting explicit authorization before proceeding to Stage 8.9.11.
