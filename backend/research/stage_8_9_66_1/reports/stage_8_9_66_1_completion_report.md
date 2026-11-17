# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — MASTER STAGE COMPLETION REPORT
**Candidate 65-F Data Provenance Audit, Unseen-Data Verification & Independent Evaluation Readiness**

## 1. Safety Designation and Ethical Prohibitions
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All experiments utilize legally acquired recorded audio files and safe playback protocols only. Strictly prohibited from live-fire testing, real-world deployment, and autonomous emergency alerting.

---

## 2. Executive Summary and Definitive Findings

Stage 8.9.66.1 was executed as a **strictly audit-only stage**. Its primary mission was to determine whether the exceptional metrics reported for **Candidate 65-F** in Stage 8.9.66 represented genuine generalization to previously unseen recordings and source groups or whether they reflected development tuning on known audio.

### Definitive Stage Findings:

1. **Classification of the $N=312$ Development Cohort:**
   The $N=312$ cohort (`stage_63_development_manifest.csv`) was used to train Candidate 65-F's weights (100% of frozen weights, 80% per cross-validation fold), tune its decision threshold ($\tau = 0.4800$), calibrate its selective suppression heuristics (whistle and agreement vetoes), and select it over competing architectures. Under established governance rules, the $N=312$ dataset is classified as **Development Benchmark & Calibration Data (Categories A, B, C, D)** and is **definitively not an untouched independent evaluation set (Category E: 0 / 312)**.

2. **Zero Contamination of the Sealed Evaluation Cohort:**
   Pairwise matrix auditing across all 991 active project recordings established that there is **0 exact PCM overlap** and **0 source-group overlap** between Candidate 65-F's training cohort and the Stage 60 sealed evaluation cohort ($N=700$). The sealed evaluation cohort remains 100% cryptographically sealed, unopened, and unpolluted.

3. **Critical Vulnerability on Unseen Shouted Speech (Gate 3 Failure):**
   Evaluating Candidate 65-F in frozen inference mode on $N=111$ verified out-of-development, unseen shouted-speech recordings from Stage 54 `expansion_reserved_test` produced **49 false positives**, establishing an empirical **shouted-speech FPR of 44.14% (49 / 111)** (95% CI: **[35.26%, 53.42%]**). This represents a catastrophic failure of **Gate 3** ($\le 15.00\%$, excess of **+29.14%**).

4. **Authoritative Primary Verdict:**
   **OPTION B — HISTORICAL DEVELOPMENT RESULTS ONLY.**
   Candidate 65-F's reported performance on $N=312$ represents development tuning. The apparent 20% shouted-speech FPR in Stage 66 was a statistical artifact of severe sample starvation (only 5 shouted recordings in the development cohort).

5. **Authoritative Readiness Verdict:**
   **NOT READY FOR INDEPENDENT EVALUATION.**
   Unsealing the sealed evaluation cohort against Candidate 65-F at this stage would violate research governance by consuming an irreplaceable, double-blind benchmark cohort on a candidate with a confirmed, fatal vulnerability to vocal shouting.

6. **Production & Research Asset Bit-Exact Integrity:**
   All four protected baseline production assets and all candidate checkpoints were cryptographically re-verified and confirmed bit-for-bit identical to their reference states. Zero production promotion was performed.

---

## 3. Sub-Stage Audit Reports Ledger

The detailed investigations and forensic data for Stage 8.9.66.1 are documented across the following seven specialized reports and machine-readable artifacts:

| Sub-Stage | Title / Purpose | Document Link | Key Outcome |
|---|---|---|---|
| **8.9.66.1.1** | Artifact Inventory & Lineage Setup | [`artifact_inventory.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/artifact_inventory.csv) | Cataloged 36 project artifacts, manifests, scripts, and checkpoints |
| **8.9.66.1.2** | Candidate 65-F Provenance Audit | [`stage_8_9_66_1_candidate_provenance_audit.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_candidate_provenance_audit.md) | Traced training lineage, threshold calibration, and filter design to $N=312$ |
| **8.9.66.1.3** | $N=312$ Cohort Categorization | [`stage_8_9_66_1_n312_cohort_classification.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_n312_cohort_classification.md) | Classified $N=312$ under Categories A, B, C, D (0% Category E) |
| **8.9.66.1.4** | Source Group & Overlap Matrix | [`stage_8_9_66_1_source_group_leakage_audit.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_source_group_leakage_audit.md) | Confirmed zero overlap between dev cohort and sealed evaluation assets |
| **8.9.66.1.5** | Expanded Negative Provenance & Test | [`stage_8_9_66_1_expanded_negative_provenance.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_expanded_negative_provenance.md) | Discovered 44.14% shouted-speech FPR on $N=111$ unseen clips |
| **8.9.66.1.6** | Sealed Cohort Integrity Audit | [`stage_8_9_66_1_sealed_cohort_integrity.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_sealed_cohort_integrity.md) | Verified all 14 governance items; reconciled $N=700$ vs $N=1,050$ |
| **8.9.66.1.7** | Candidate & Production Integrity | [`stage_8_9_66_1_candidate_artifact_integrity.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_candidate_artifact_integrity.md) | Bit-level verification of all 4 production assets and 65-F checkpoint |
| **8.9.66.1.8** | Independent Evaluation Readiness | [`stage_8_9_66_1_independent_evaluation_readiness.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/stage_8_9_66_1_independent_evaluation_readiness.md) | Issued verdicts: Option B & NOT READY FOR INDEPENDENT EVALUATION |

---

## 4. Comprehensive Cross-Dataset & Performance Synthesis

### 4.1 Dataset Exposure Classification Matrix
Classification across all 991 recordings cataloged in Stage 8.9.66 negative evaluations:

| Dataset / Cohort | Total Clips | Sealed Cohort Member | In Dev Set ($N=312$) | Exposed in Stage 54 | Shared Source Group with Sealed | Confirmed Unseen & Eligible |
|---|---|---|---|---|---|---|
| **Hard Negatives** | 462 | 331 (71.6%) | 116 (25.1%) | 0 (0.0%) | 15 (3.2%) | **0 (0.0%)** |
| **Shouted Speech** | 529 | 150 (28.4%) | 5 (0.9%) | 231 (43.7%) | 32 (6.0%) | **111 (21.0%)** |
| **Total Evaluated** | 991 | 481 (48.5%) | 121 (12.2%) | 231 (23.3%) | 47 (4.7%) | **111 (11.2%)** |

> **Key Takeaway:** 88.8% of the negative recordings cited in Stage 8.9.66 either belonged to the sealed cohort, were present in the development set, or shared acoustic source groups with sealed data. Exactly 111 shouted speech recordings from Stage 54 `expansion_reserved_test` were verified to be pristine, unseen by Candidate 65-F, and legally unencumbered.

### 4.2 Candidate 65-F Pre-Registered Gate Scorecard

| Gate Metric | Target Standard | Development Cohort ($N=312$) | Unseen Data Verification ($N=111$) | Empirical Margin | Formal Gate Status |
|---|---|---|---|---|---|
| **Gate 1: Overall Recall** | $\ge 96.00\%$ | 94.36% (184 / 195) | *Untested (Sealed)* | -1.64% | **MARGINAL / UNCONFIRMED** |
| **Gate 2: Hard-Negative FPR** | $\le 5.00\%$ | 5.98% (7 / 117) | *Untested (Sealed)* | +0.98% | **MARGINAL / UNCONFIRMED** |
| **Gate 3: Shouted-Speech FPR** | $\le 15.00\%$ | 20.00% (1 / 5) | **44.14% (49 / 111)** | **+29.14%** | **CATASTROPHIC FAILURE** |
| **Gate 4: Short-Scream Recall** | $\ge 90.00\%$ | 98.50% (131 / 133) | *Untested (Sealed)* | +8.50% | **UNCONFIRMED ON UNSEEN** |
| **Gate 5: Neural P95 Latency** | $\le 25.00\text{ ms}$ | 0.824 ms | 0.812 ms | -24.18 ms | **PASSED** |

---

## 5. Acoustic Failure Analysis: Why Candidate 65-F Fails on Shouted Speech

The catastrophic failure on unseen shouted speech (44.14% FPR) exposes a critical acoustic limitation in the dual-resolution architecture:

1. **Spectral Overlap Between Screaming and Shouting:**
   Human screams and aggressive vocal shouts share high acoustic intensity, high fundamental frequency ($F_0 > 400\text{ Hz}$), elevated formant energy ($F_1, F_2, F_3$), and broad high-frequency energy up to $4\text{ kHz}$. Candidate 65-F relies heavily on Mel-filterbank energy and spectral centroid, which cannot distinguish high-energy phonation from non-linear distress screams.

2. **Suppression Stack Bypassing:**
   - **Narrow-band Whistle Veto:** Tuned for acoustic whistles with $\text{HNR} > 12\text{ dB}$ and $\text{Flatness} < 0.001$. Shouted speech consists of modulated vowels and turbulent consonants, yielding moderate HNR ($2\text{ to }8\text{ dB}$) and flatness ($0.005\text{ to }0.040$), rendering the whistle veto inactive.
   - **Branch Latent Cosine Agreement:** Tuned to reject transient impulse noise (door slams, clicks) where the short branch triggers ($p_{short} > 0.8$) but the sustained branch is inactive ($p_{sust} < 0.2$), yielding low cosine agreement ($\text{sim} < 0.40$). However, sustained shouting ($> 300\text{ ms}$) provides sustained acoustic energy across both the 250 ms and 1000 ms windows. Consequently, both branches fire synchronously, yielding cosine similarity between $0.45$ and $0.85$, completely bypassing the veto.

3. **Development Set Starvation:**
   The $N=312$ development cohort contained only 5 shouted-speech clips. The model was never exposed during training or tuning to the acoustic variance of shouting (different genders, vocal registers, reverberant festival environments). Consequently, the model's apparent 20% FPR in Stage 66 was a deceptive sampling artifact.

---

## 6. Cryptographic Verification Ledger

All critical project artifacts were audited and verified. The complete hash ledger is recorded below:

### Protected Production Assets (Section 9 Compliance):
| Asset ID | Repository Path | Immutable Expected SHA-256 | Computed SHA-256 | Status |
|---|---|---|---|---|
| **Production Model** | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (BIT-EXACT)** |
| **Production Metadata** | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (BIT-EXACT)** |
| **Historical Test Preds** | `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (BIT-EXACT)** |
| **Historical Test Report** | `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (BIT-EXACT)** |

### Candidate 65-F & Evaluation Infrastructure Assets:
| Component | Repository Path | Cryptographic SHA-256 | Status |
|---|---|---|---|
| **Frozen Checkpoint** | `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt` | `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab` | **BIT-EXACT** |
| **Freeze Metadata** | `backend/research/stage_8_9_66/models/candidate_freeze_metadata.json` | `a40672a42e3a8d1f38f1ff067cb92b6c45e122b12a25c127f7513d78327944d4` | **BIT-EXACT** |
| **C5 DSP Engine** | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | **BIT-EXACT** |
| **Evaluation Script** | `backend/research/stage_8_9_66/scripts/reproduce_candidate_65f.py` | `f78d78161994a76a3f84ca87404dc5d180d6a06d219476029efbfa60cb9d4877` | **BIT-EXACT** |
| **Sealed Cohort Manifest** | `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **SEALED** |

---

## 7. Roadmap & Recommendations for Stage 8.9.67

To overcome the shouted-speech failure mode without compromising Candidate 65-F's high recall on short screams (98.50%) or neural latency (0.82 ms), Stage 8.9.67 should focus on:

1. **Non-Distress Vocal Augmentation in Training:**
   Ingest a targeted development training set of non-distress speech (vocal shouting, crowd cheering, theatrical projections) ensuring strict independence from the sealed evaluation cohort.
2. **Acoustic Non-Linearity Features:**
   Incorporate acoustic markers specific to distressed vocal fold collapse (deterministic chaos, biphonation, subharmonic ratio, high-frequency energy flux) that differentiate true screaming from shouted phonation.
3. **Contrastive Loss Penalization:**
   Train a specialized vocal discriminator head or fine-tune dual-resolution representations with hard-negative vocal margin loss.
4. **Mandatory Out-of-Distribution Development Gate:**
   Prior to any future consideration of unsealing, all candidates must demonstrate shouted-speech $\text{FPR} \le 15.00\%$ on an independent development validation set of at least 200 vocal clips.

---

## 8. Final Safety & Governance Reaffirmation
This system is an **experimental acoustic research prototype**. It is **not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment**.

All results reported herein are derived from legally acquired recorded audio files and safe laboratory protocols. Production promotion is strictly denied.

