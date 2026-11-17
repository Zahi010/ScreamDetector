# Stage 8.9.59 Final Research Report — Independent Generalization Audit, Error-Driven Dataset Expansion & Evaluation Governance

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments must use legally acquired recorded audio and safe recorded-audio playback only.  
> **Strict prohibitions:** No live-fire experiments, no real-world emergency-response testing, no autonomous emergency dispatch, no external emergency alerts, no police notification, no claims of life-safety efficacy, no production promotion, no model training, and no threshold modifications.

---

## 1. Stage Verdict & Executive Assessment

Stage 8.9.59 has formally concluded its audit and dataset acquisition planning objectives.

In accordance with strict project governance:
- **No models were trained or fine-tuned.**
- **No classification thresholds were modified.**
- **No production assets were altered (100% cryptographic SHA-256 match confirmed).**
- **The Original Five Project Acceptance Gates were restored as the authoritative benchmark.**

### Official Stage Verdict
$$\mathbf{2. \text{ MORE DATA REQUIRED BEFORE MODEL RESEARCH}}$$

**Rationale:** The forensic error audit revealed that Candidate E1’s remaining classification failures (83.84% recall vs 96% gate; 11.36% shouted-speech FPR vs 15% gate) are directly caused by acoustic coverage deficits in the underlying dataset:
1. Low-intensity and muffled screams are critically underrepresented across the entire corpus (only 7 source groups exist, 0 in validation).
2. Sustained screams ($\ge 1.0$s) suffer from window-level temporal averaging dilution (76.67% recall).
3. Exactly 90% of shouting false alarms (9 of 10) are concentrated in just 2 uploader recording sessions (`reitanna` and `ericsueiro`) exhibiting extreme vocal fry and microphone soft clipping.

Retraining or tweaking model architectures on the existing dataset would merely overfit to these acoustic artifacts. Acquiring legally compliant, source-independent expansion audio addressing these specific failure modes is the mandatory next step.

---

## 2. Frozen Artifact Hash Results

All 10 target assets were audited using cryptographic SHA-256 hashing at stage onset and stage conclusion. All files matched their authoritative digests bit-for-bit with zero drift:

| Asset Name | Relative Path | Authoritative SHA-256 | Actual Verified SHA-256 | Status |
|---|---|---|---|:---:|
| **Production Model** | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH (FROZEN)** |
| **Model Metadata** | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH (FROZEN)** |
| **Production Test Preds**| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH (FROZEN)** |
| **Stage 5 Evaluation** | `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH (FROZEN)** |
| **Candidate E1 Model** | `backend/research/stage_8_9_54/.../candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | **MATCH (FROZEN)** |
| **Candidate B Model** | `backend/research/stage_8_9_44/.../config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | **MATCH (FROZEN)** |
| **Intervention D** | `backend/research/stage_8_9_49/.../whistle_discriminator.py` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` | **MATCH (FROZEN)** |
| **C5 Combined DSP** | `backend/research/stage_8_9_57/.../c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` | **MATCH (FROZEN)** |
| **Original E1 DSP** | `backend/research/stage_8_9_57/.../benchmark_original_dsp.py` | `192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905` | `192e928c6ea427737ef8a3ec4449c890c1d41f01d71c80cefde3f2a0363f5905` | **MATCH (FROZEN)** |
| **Stage 55 Test Manifest**| `backend/research/stage_8_9_55/.../frozen_test_manifest.json` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | `06c9db80d3969e60f78dd441eb1495a9dab97f1646f08ab5825ea979719021f2` | **MATCH (FROZEN)** |

---

## 3. Verified Dataset Inventory

An exhaustive audit of 6 major dataset collections spanning **7,407 recording entries** was conducted across the repository:
- **Stage 8.9.54 Expansion Corpus:** 1,732 total recordings (604 screams, 1,128 hard negatives) across 693 source groups.
  - `expansion_train`: 1,055 recordings (403 positive, 652 negative) across 415 source groups.
  - `expansion_val`: 311 recordings (99 positive, 212 negative) across 138 source groups.
  - `expansion_reserved_test`: 366 recordings (102 positive, 264 negative) across 140 source groups.
- **Historical Cohorts Audited:** Stage 8.9.17 reconstructed dataset (2,804 recordings), Stage 8.9.47 independent cohort (480 recordings), Stage 8.9.49 whistle development set (320 recordings), Stage 8.9.55 acquisition cohort (450 recordings).

---

## 4. Candidate E1 False-Negative Forensics

On the validation set (`expansion_val`, $N=311$), frozen Candidate E1 + C5 ($\theta = 0.6800$) produced exactly **16 false negatives** (83/99 recall = **83.84%**):
- **Short Screams (<1.0s):** **94.87% Recall (37/39)**, 2 False Negatives. Ultra-short screams (<0.5s) achieved **100.0% Recall (15/15)**.
- **Sustained Screams ($\ge 1.0$s):** **76.67% Recall (46/60)**, 14 False Negatives.

### Forensic Failure Mechanisms:
1. **Window-Level Temporal Averaging Dilution (5 clips):** Screams lasting 0.8s followed by 2.0s of vocal release or decay suffer from global window averaging, which dilutes the `scream_to_low_energy_ratio` and lowers overall spectral centroid.
2. **Heavy Crowd Noise Masking (6 clips):** Low SNR ($-6\text{ dB}$ to $+4\text{ dB}$) from ambient festival crowd chatter elevates low-band energy and masks scream harmonics.
3. **Ambiguous Phonation / Perceptual Gasps (3 clips):** Foley gasps (`gasp-oooh`, `another-surprised-gasp`) lack vocal fold chaos, over-blowing, or high fundamental frequency. The model's rejection ($p < 0.30$) reflects accurate acoustic discrimination.
4. **Low-Intensity Damped Vocalization (2 clips):** Low RMS energy ($<0.024$). One clip missed the threshold by only **$0.0030$** (`exp_v2_nigens_332044`, $p = 0.6770$ vs $\theta = 0.6800$).

---

## 5. False-Positive Analysis

On the validation set ($N=212$ hard negatives), frozen Candidate E1 + C5 produced **13 false positives (6.13% FPR)**:
- **Shouted Speech:** 10 / 88 (11.36% FPR).
- **Infant Crying:** 2 / 20 (10.00% FPR) — Driven by high fundamental frequencies ($>500\text{ Hz}$) and distress roughness.
- **Cheering / Chanting:** 1 / 37 (2.70% FPR) — High-pitched female sports celebration.
- **Whistles & Squeaks:** **0 / 22 (0.00% FPR)** — Native 100% rejection without auxiliary veto modules.
- **Environmental Noise & Sirens:** **0 / 45 (0.00% FPR)** — Zero false alarms on sirens, fireworks, or park ambience.

---

## 6. Shouted-Speech Concentration Proof

Forensic investigation of the 10 shouted-speech false alarms established a remarkable empirical finding:
$$\mathbf{90.0\% \text{ (9 of 10) of all shouted-speech false positives originate from just TWO uploader sessions:}}$$
1. `reitanna` (Session 3439, 5 false positives): Aggressive sustained shouting with extreme vocal fry and acoustic strain.
2. `ericsueiro` (Session 2208, 4 false positives): Theatrical performance lines recorded with preamplifier soft clipping.

The remaining 35 independent shouting source groups in the validation partition generated only **1 false alarm across 79 clips (1.27% FPR)**. The detector does NOT suffer from a generalized inability to reject shouted speech; errors are strictly driven by acoustic distortion and borderline vocal fry in concentrated sessions.

---

## 7. Cross-Candidate Error Comparison

Candidate E1 + C5 was evaluated against Candidate B Baseline and Candidate B + Intervention D across identical validation clips:
- **Decision Concordance:** Candidates agree on **298 of 311 recordings (95.82%)**.
- **Shared Failures:** 12 shared false negatives ($75.0\%$ of all FN) and 10 shared false positives ($76.9\%$ of all FP).
- **Architecture Parity:** Both models exhibit virtually identical recall (83.84%) and F1 scores ($0.8513$ vs $0.8601$).
- **Computational Advantage:** Candidate E1 + C5 achieves faster forward latency (**0.50 ms P95** vs 0.68 ms P95) and full native whistle rejection (**0.00% FPR** vs 4.55% for B without Intervention D).

---

## 8. Source-Group Independence & Leakage Audit

Audit of the 1,732-recording expansion corpus verified:
- **0 exact file hash overlaps** between Train, Val, and Test.
- **0 PCM-level hash overlaps** between Train, Val, and Test.
- **0 source group overlaps** between Train, Val, and Test.
- **0 multi-crop parent leaks** across partitions (132 parent recordings have multiple crops; 100% are strictly quarantined within the same split).
- **Identified Risk:** **7 creators/uploaders overlap between Train and Val**, and **10 creators overlap between Train and Test**. All future evaluation cohorts must enforce creator-level clustering.

---

## 9. Dataset Coverage Gaps

Analysis across 11 acoustic categories revealed critical gaps in the existing corpus:
1. **Low-Intensity & Muffled Screams:** **CRITICALLY INSUFFICIENT** (only 10 clips from 7 source groups exist across the entire corpus; 0 in validation).
2. **Crowd-Masked Screams:** **UNDERREPRESENTED** (only 26 source groups exist across the corpus).
3. **Shouting Diversity Deficit:** Despite 174 source groups, 90% of validation errors cluster in 2 sessions.

---

## 10. License & Commercial Provenance Audit

- **100% of recordings** in the Stage 8.9.54 corpus are legally verified for commercial-intent research:
  - **CC0 / Public Domain:** 858 recordings (49.54%).
  - **CC BY (Attribution):** 874 recordings (50.46%).
  - **Non-Commercial / Proprietary:** **0 recordings** (zero CC BY-NC or All Rights Reserved).

---

## 11. Future Acquisition Priorities

Acquisition for Stage 8.9.60 must prioritize:
1. **Priority 1: Low-Intensity & Muffled Screams:** Target $\ge 50$ independent source groups ($\ge 100$ clips).
2. **Priority 2: Crowd-Masked Screams (SNR < 10 dB):** Target $\ge 60$ independent source groups ($\ge 150$ clips).
3. **Priority 3: Diverse Independent Shouted Speech:** Target $\ge 100$ independent source groups ($\ge 200$ clips).
4. **Priority 4: Independent Sustained Screams ($\ge 1.0$s):** Target $\ge 80$ independent source groups ($\ge 160$ clips).

---

## 12. Future Independent Evaluation Design

Designed an untouched future evaluation cohort:
- **Cohort Size:** 700 recordings (200 authentic screams, 500 hard negatives) spanning **$\ge 370$ independent source groups**.
- **Quarantine Safeguards:** 100% creator/uploader level isolation; dual-annotator verification (inter-annotator $\kappa \ge 0.85$); pre-frozen cryptographic SHA-256 seal; evaluated exactly once without threshold sweeping.

---

## 13. Statistical Analysis Plan (SAP)

Preregistered SAP restoring the Original Five Project Gates:
- **Primary Endpoint:** Overall scream recall $\ge 96.00\%$.
- **Clustered Bootstrap:** Resampling at the source-group cluster level ($B = 2,000$ iterations) with Bias-Corrected and Accelerated ($\text{BC}_a$) 95% confidence intervals to eliminate pseudo-replication.
- **Hypothesis Testing:** Paired McNemar exact test on discordant pairs for candidate comparisons.
- **Multiplicity Correction:** Benjamini-Hochberg FDR control at $q = 0.05$.
- **Subgroup Evidence Threshold:** Minimum 30 independent source groups required for formal statistical claims.

---

## 14. Original Five Acceptance-Gate Compliance Status

| Gate # | Project Acceptance Gate | Candidate E1 + C5 Status | Status | Primary Cause |
|:---:|---|:---:|:---:|---|
| **Gate 1** | Overall Scream Recall $\ge 96.00\%$ | **83.84% (83/99)** | **NOT MET** | Window temporal averaging on sustained screams & crowd noise |
| **Gate 2** | Hard-Negative FPR $\le 5.00\%$ | **6.13% (13/212)** | **NOT MET** | Borderline shouting (10 FP) and infant crying (2 FP) |
| **Gate 3** | Shouted-Speech FPR $\le 15.00\%$ | **11.36% (10/88)** | **PASS** | Comfortably clears 15% threshold; 90% driven by 2 sessions |
| **Gate 4** | Short-Scream Recall $\ge 90.00\%$ | **94.87% (37/39)** | **PASS** | Exceeds 90% target; 100.0% on ultra-short screams |
| **Gate 5** | Model Forward Inference P95 $\le 25.0\text{ ms}$| **0.50 ms** | **PASS** | Consumes 2% of budget (50x safety margin) |

---

## 15. Model-Development Readiness Decision

$$\mathbf{\text{VERDICT: 2. MORE DATA REQUIRED BEFORE MODEL RESEARCH}}$$
No model training is authorized until targeted legal dataset expansion (Priorities 1–4) has been executed.

---

## 16. Automated Test Results

The comprehensive test suite in `tests/test_stage_8_9_59.py` was executed:
- **Test Command:** `pytest festival-scream-detector/backend/research/stage_8_9_59/tests/test_stage_8_9_59.py -v`
- **Result:** **23 PASSED, 0 FAILED, 0 SKIPPED** in 1.29 seconds.
- **Coverage:** Verified hash immutability across all production and research assets, threshold preservation, denominator consistency, duplicate prevention, multi-crop isolation, license completeness, and statistical formulas.

---

## 17. Remaining Limitations

1. **Acoustic Low-Intensity Blindspot:** The system remains unproven on subdued, muffled, or long-distance screams due to lack of training data.
2. **Temporal Window Averaging:** Static buffer averaging penalizes sustained screams with long decays. Rolling window DSP segmentation is needed.
3. **Theatrical Shouting Vulnerability:** Extreme vocal fry and preamplifier distortion can trigger false positives.
4. **Mandatory Life-Safety Prohibition:** The prototype is an experimental acoustic research system. It is strictly prohibited from use in emergency dispatch, police notification, or life-safety applications.

---

## 18. Recommended Stage 8.9.60 Objectives

1. **Phase 1: Legal Acquisition Execution:** Execute targeted acquisition of Priority 1 (Low-Intensity Screams, $\ge 50$ SGs) and Priority 2 (Crowd-Masked Screams, $\ge 60$ SGs) under CC0 / CC BY licensing.
2. **Phase 2: Shouting Diversity Expansion:** Acquire Priority 3 (Diverse Shouted Speech, $\ge 100$ SGs from single-clip independent speakers) to eliminate session-specific false alarms.
3. **Phase 3: Rolling Window DSP Research:** Investigate sub-window temporal aggregation (e.g., 500 ms rolling hops) within C5 to eliminate temporal averaging dilution on sustained screams.
4. **Phase 4: Sealed Independent Cohort Assembly:** Assemble and cryptographically seal the $N=700$ independent evaluation cohort according to Phase H specifications prior to authoring any new training stages.

