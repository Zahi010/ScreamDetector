# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — INDEPENDENT EVALUATION READINESS ASSESSMENT
**Comprehensive Synthesis of Data Provenance, Unseen-Data Verification, and Pre-Unsealing Audit**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary and Authoritative Determination

Stage 8.9.66.1 conducted a forensic, audit-only investigation into **Candidate 65-F** (`Candidate_65_F_Combined_Selective`) to determine whether its reported performance represents genuine acoustic generalization or development benchmark tuning, and to assess whether the model is ready for formal unsealing and evaluation against the sealed cohort.

### Formal Determination:
> **PRIMARY VERDICT: OPTION B — HISTORICAL DEVELOPMENT RESULTS ONLY**  
> Candidate 65-F's reported metrics (94.36% recall, 5.98% hard-negative FPR, 20% shouted-speech FPR) reflect development tuning and threshold optimization on the $N=312$ development cohort. Under pre-registered classification rules, the $N=312$ dataset is classified as Development Benchmark & Calibration Data (Categories A, B, C, D) and is definitively not an untouched independent evaluation set.

> **EVALUATION READINESS VERDICT: NOT READY FOR INDEPENDENT EVALUATION**  
> Controlled frozen inference on $N=111$ verified out-of-development shouted-speech recordings revealed **49 false alarms**, establishing an observed **shouted-speech FPR of 44.14%** (95% CI: **[35.26%, 53.42%]**). This represents a catastrophic failure of **Gate 3** (maximum allowable threshold $\le 15.00\%$, excess of **+29.14%**). Proceeding to unseal the pristine sealed evaluation cohort under these conditions would expend irreplaceable independent evaluation assets on a candidate with a confirmed, fatal vulnerability to human vocal shouting.

---

## 3. Comprehensive Synthesis of Sub-Stage Audits (8.9.66.1.1 – 8.9.66.1.7)

### 3.1 Provenance Audit (Sub-stage 8.9.66.1.2)
The lineage of Candidate 65-F was forensically traced through Stages 8.9.63, 8.9.64, 8.9.65, and 8.9.66:
- **Weights:** Trained directly on the $N=312$ cohort (`stage_63_development_manifest.csv`) via 5-fold cross-validation during architecture tuning, and trained on 100% of the $N=312$ cohort in the frozen release checkpoint (`candidate_65f_frozen.pt`).
- **Threshold:** The decision threshold $\tau = 0.4800$ was directly calibrated via grid search on the out-of-fold probability distributions of this same cohort.
- **Suppression Stack:** The selective suppression stack (HNR $> 12.0$ dB, Spectral Flatness $< 0.001$, Cosine Agreement $> 0.40$) was explicitly engineered to eliminate the specific 25 false alarms produced by the baseline dual-resolution model on the $N=312$ cohort.
- **Selection:** Candidate 65-F was selected as the champion over 6 competing variants based solely on $N=312$ benchmark scores.

### 3.2 Cohort Classification ($N=312$) (Sub-stage 8.9.66.1.3)
The $N=312$ cohort was formally categorized across the five canonical evaluation roles:
- **Category A (Training Data):** 100% of recordings were utilized during training of the frozen model weights.
- **Category B (Validation Data):** Utilized for out-of-fold hyperparameter validation.
- **Category C (Threshold Calibration Data):** Utilized for threshold selection.
- **Category D (Heuristic Tuning Data):** Utilized to design narrow-band and agreement suppression rules.
- **Category E (Untouched Independent Test Data):** **DEFINITIVELY NEGATIVE (0 / 312).**

### 3.3 Source-Group & Recording Overlap Matrix (Sub-stage 8.9.66.1.4)
Pairwise overlap analysis across all project datasets demonstrated:
- **Zero Contamination of Sealed Evaluation Assets:** There is **0 exact PCM overlap** and **0 source-group overlap** between the $N=312$ development set and the Stage 60 sealed evaluation cohort ($N=700$).
- **Zero Historical Contamination:** The $N=312$ development set is completely disjoint from the Stage 54 train/val/test partitions.
- **Exclusivity:** Candidate 65-F's training set is isolated, proving that no data leakage occurred into the sealed cohort.

### 3.4 Expanded Negative Cohort Exposure & Frozen Inference (Sub-stage 8.9.66.1.5)
Audit of the expanded negative datasets evaluated in Stage 8.9.66 revealed critical exposure and contamination:
- **Hard Negatives ($N=462$):** 116 files (25.1%) are identical to the $N=312$ development set; 331 files (71.6%) are members of the Stage 60 sealed evaluation cohort; 15 files share source groups with the sealed cohort. **Zero hard-negative files were eligible for evaluation without violating the sealed cohort.**
- **Shouted Speech ($N=529$):** 150 files are in the sealed cohort, 235 files were exposed in Stage 54 or dev. Exactly **111 files** from Stage 54 `expansion_reserved_test` were confirmed to be completely unseen by Candidate 65-F and completely disjoint from development and sealed source groups.
- **Frozen Inference Verification:** Executing Candidate 65-F in frozen inference mode on these 111 unseen files produced:
  - Predictions: 49 Positive (False Alarms), 62 Negative (True Rejections).
  - **Empirical Shouted-Speech FPR: 44.14% (49 / 111)**.
  - Wilson Score 95% Confidence Interval: **[35.26%, 53.42%]**.
  - **Verdict:** Gate 3 ($\le 15.00\%$) failed catastrophically (+29.14% excess).

### 3.5 Sealed Evaluation Cohort Governance (Sub-stage 8.9.66.1.6)
- The physical sealed cohort manifest `future_evaluation_manifest.json` ($N=700$, SHA-256 `9dfa4ced...`) remains 100% cryptographically sealed, unopened, and unexposed.
- The discrepancy between the $N=700$ physical manifest and the $N=1,050$ preregistration specification was reconciled: $N=700$ is Benchmark Cohort A; $N=1,050$ ($350$ screams, $700$ negatives) is the authoritative target sampling design for multi-center validation.
- All 14 administrative and governance checks passed with zero unsealing events.

### 3.6 Candidate Artifact Integrity (Sub-stage 8.9.66.1.7)
- Candidate 65-F frozen checkpoint (`06a98025db...`), C5 DSP feature engine (`d73cd3bf...`), inference script (`f78d7816...`), and metadata (`a40672a4...`) are bit-for-bit identical to Stage 8.9.66 releases.
- All four protected baseline production assets (`scream_classifier.joblib`, `model_metadata.json`, `test_predictions.csv`, `stage5_test_evaluation.md`) matched their immutable SHA-256 hashes bit-for-bit.

---

## 4. Evaluation Against Pre-Registered Gates

The performance of Candidate 65-F is systematically evaluated against the five preregistered criteria:

| Gate | Target Metric | Preregistered Criterion | Development Cohort ($N=312$) | Unseen Data Verification ($N=111$) | Gate Compliance Status |
|---|---|---|---|---|---|
| **Gate 1** | Overall Scream Recall | $\ge 96.00\%$ | 94.36% (184 / 195) | *Untested on unseen screams* | **MARGINAL / UNCONFIRMED** |
| **Gate 2** | Hard-Negative FPR | $\le 5.00\%$ | 5.98% (7 / 117) | *Sealed (Zero unexposed files)* | **MARGINAL / UNCONFIRMED** |
| **Gate 3** | Shouted-Speech FPR | $\le 15.00\%$ | 20.00% (1 / 5) | **44.14% (49 / 111)** | **CATASTROPHIC FAILURE (+29.14%)** |
| **Gate 4** | Short-Scream Recall ($< 1.0\text{s}$) | $\ge 90.00\%$ | 98.50% (131 / 133) | *Untested on unseen screams* | **UNCONFIRMED ON UNSEEN** |
| **Gate 5** | Model-only Neural P95 Latency | $\le 25.00\text{ ms}$ | 0.824 ms (Single-stream) | 0.812 ms (Single-stream) | **PASSED** |

### Critical Analysis of Gate 3 Breakdown:
1. **Deceptive Sample Size in Development:** The reported 20% FPR in Stage 66 was derived from exactly 5 shouted speech clips in the $N=312$ dev cohort (1 false alarm, 4 correct rejections). A sample of $N=5$ yields a 95% confidence interval of $[3.6\%, 62.4\%]$, which was statistically incapable of detecting high false alarm rates.
2. **True Out-of-Distribution Vulnerability:** When evaluated on a properly powered sample ($N=111$) of out-of-distribution human shouted speech, Candidate 65-F triggered on nearly every second shouting file (44.14%).
3. **Failure of Suppression Mechanisms:**
   - **Narrow-band Whistle Veto:** Designed for continuous tonal whistles ($\text{HNR} > 12\text{ dB}, \text{Flatness} < 0.001$). Shouted speech has high formant energy, non-stationary pitch contours, and broader spectral distribution, completely bypassing the whistle filter.
   - **Branch Cosine Agreement:** Designed to suppress transient impulse clicks where short branch activates but long branch remains silent. In human shouting sustained for $\ge 300\text{ ms}$, both the short (250 ms) and sustained (1000 ms) branches activate strongly and synchronously, producing branch cosine similarity $> 0.40$ and bypassing the veto.
   - **Neural Representation Overlap:** Candidate 65-F relies heavily on high-frequency spectral centroid and band energy ratios, which cannot reliably separate high-arousal distressed screaming from aggressive vocal shouting.

---

## 5. Technical Failure Mode & Root Cause Analysis

```
                               ┌──────────────────────────────────────────────┐
                               │       High-Arousal Shouted Speech            │
                               │          (Unseen Dataset N=111)              │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │                                                             │
                       ▼                                                             ▼
         ┌───────────────────────────┐                                 ┌───────────────────────────┐
         │ 250 ms Short Branch       │                                 │ 1000 ms Sustained Branch  │
         │ - High vocal energy       │                                 │ - Strong formant energy   │
         │ - High spectral centroid  │                                 │ - High envelope power     │
         │ Latent representation z_s │                                 │ Latent representation z_l │
         └─────────────┬─────────────┘                                 └─────────────┬─────────────┘
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
                                                      ▼
                                       ┌─────────────────────────────┐
                                       │ Cosine Similarity Check     │
                                       │ sim(z_s, z_l) > 0.40?       │
                                       └──────────────┬──────────────┘
                                                      │ YES (Both branches active)
                                                      ▼
                                       ┌─────────────────────────────┐
                                       │ Narrow-Band Whistle Veto    │
                                       │ HNR > 12 dB & Flat < 0.001? │
                                       └──────────────┬──────────────┘
                                                      │ NO (Shouting is broad-band)
                                                      ▼
                                       ┌─────────────────────────────┐
                                       │ Raw Dual-Resolution Score   │
                                       │ p_raw = 0.55 - 0.92         │
                                       └──────────────┬──────────────┘
                                                      │ p > tau (0.48)
                                                      ▼
                                       ┌─────────────────────────────┐
                                       │ FALSE POSITIVE TRIGGERED    │
                                       │ (44.14% False Alarm Rate!)  │
                                       └─────────────────────────────┘
```

The diagram above illustrates the structural failure mode:
The two heuristic suppression mechanisms introduced in Stage 8.9.65 were tailored specifically to **narrow-band acoustic whistles** and **instantaneous mechanical clicks**. Neither mechanism provides discriminant power against **broadband vocal speech**. Because the neural backbone itself was trained on a small development set ($N=312$) with only 5 shouted-speech samples, the neural representations $z_s$ and $z_l$ treat vocal shouting as acoustically indistinguishable from screaming.

---

## 6. Formal Risk Assessment of Unsealing

Unsealing the sealed evaluation cohort is a **one-way, irreversible event**. Once unsealed:
1. The recordings lose their status as a double-blind, pristine test set.
2. Any subsequent model adjustments informed by unsealed errors are permanently contaminated.
3. The statistical validity of future claims is degraded.

Given that Candidate 65-F demonstrably fails Gate 3 by a massive margin (+29.14%), unsealing the cohort now would guarantee a failed validation trial while needlessly destroying the integrity of the project's primary benchmark assets.

---

## 7. Remediation Roadmap & Exit Criteria

Before any candidate can be submitted for independent evaluation cohort unsealing, the following mandatory remediation milestones must be achieved:

### Phase 1: Negative Training Augmentation (Stage 8.9.67 Proposed)
- **Acoustic Dataset Expansion:** Ingest an expanded corpus of non-distress vocalizations (shouting, loud cheering, athletic exertion, dramatic dialogue) from legally acquired public-domain corpora (e.g., FSD50K speech subsets, VoxCeleb subsets) that have zero overlap with the sealed cohort.
- **Negative Contrastive Loss:** Formulate an explicit contrastive loss term penalizing high scream probability on vocal speech features.

### Phase 2: Acoustic Feature Enhancement
- **Harmonic Formant Dispersion:** Incorporate formant dispersion and vocal tract length estimates. Screaming involves non-linear vocal fold phenomena (subharmonics, biphonation, deterministic chaos) that differ fundamentally from shouted speech phonation.
- **Vocal Roughness & Jitter/Shimmer Extraction:** Introduce specialized acoustic metrics for vocal fry, roughness, and subharmonic energy in the feature extraction stage.

### Phase 3: Out-of-Distribution Pre-Validation Gate
- Construct an explicit **Unseen Development Validation Benchmark** consisting of at least:
  - $\ge 150$ out-of-distribution screams.
  - $\ge 200$ out-of-distribution shouted-speech files.
  - $\ge 300$ out-of-distribution environmental negatives.
- Candidate models must pass all 5 gates on this benchmark **prior** to unsealing the sealed cohort.

---

## 8. Final Governance Conclusion

Candidate 65-F has established groundbreaking engineering achievements in dual-resolution latency (0.82 ms P95) and short-scream development recall (98.50%). However, its reported reliability was an artifact of development tuning on the $N=312$ cohort.

When subjected to rigorous unseen verification in Stage 8.9.66.1, Candidate 65-F demonstrated an unacceptable shouted-speech false positive rate of **44.14%**.

**Final Action:**
1. Maintain Candidate 65-F in frozen research state (`models/candidate_65f_frozen.pt`).
2. Maintain the Sealed Evaluation Cohorts ($N=700$ and $N=1,050$) in 100% cryptographically sealed isolation.
3. Advance to Stage 8.9.67 for vocal contrastive learning and feature refinement.
4. Deny unsealing authorization.

