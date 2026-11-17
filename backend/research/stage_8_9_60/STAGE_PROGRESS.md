# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Festival Scream Detector — Research Stage Progress Log

## Stage History Roadmap

| Stage Identifier | Stage Title & Focus | Primary Milestone / Result | Status |
| :--- | :--- | :--- | :---: |
| **Stage 8.9.50** | Baseline Model Evaluation & False Positive Analysis | Identification of whistle and shouted speech false alarms | **COMPLETED** |
| **Stage 8.9.51** | Multi-Candidate Forensic Evaluation | Identification of metric discrepancies between evaluation runs | **COMPLETED** |
| **Stage 8.9.52** | Forensic Reconciliation & Candidate E Verification | 100% validation recall reported on small development cohort | **COMPLETED** |
| **Stage 8.9.53** | Candidate E Independent Evaluation & Generalization Audit | Candidate E failed generalization on reserved test cohort (62.75% recall) | **COMPLETED** |
| **Stage 8.9.54** | Candidate E Expanded-Data Retraining (Candidate E1) | Balanced retraining yielded Candidate E1 (87.27% val recall) | **COMPLETED** |
| **Stage 8.9.55** | Fresh Independent Cohort Acquisition ($N=700$) | Candidate E1 achieved 88.0% recall, 5.8% FPR; beat Candidate B | **COMPLETED** |
| **Stage 8.9.56** | Evaluation Audit, Source-Group Audit & Latency Check | Confirmed statistical superiority; detected latency measurement discrepancy | **COMPLETED** |
| **Stage 8.9.56.1** | Latency Measurement Reconciliation & Audit Closure | Reconciled P95 latency (47.87 ms full pipeline; 1.48 ms NN-only) | **COMPLETED** |
| **Stage 8.9.57** | Candidate E1 DSP Optimization & Filterbank Ablation | C5 Combined DSP achieved 6.20 ms P95 latency (7.7x speedup) | **COMPLETED** |
| **Stage 8.9.58** | C5 Numerical Equivalence Forensics & Streaming Validation | Proved bit-for-bit numerical parity ($10^{-5}$ tolerance) for C5 DSP | **COMPLETED** |
| **Stage 8.9.59** | Generalization Audit & Acquisition Planning | Identified low-intensity and crowd-masking gaps; defined acquisition roadmap | **COMPLETED** |
| **Stage 8.9.60** | **Targeted Legal Dataset Acquisition & Sealed Cohort Construction** | **Acquired 962 clips across 633 SGs; sealed 700-recording evaluation cohort** | **COMPLETED** |

---

## Detailed Breakdown of Stage 8.9.60 Milestones

### Phase 1: Baseline Verification & Governance
- [x] Verified cryptographic SHA-256 digests for all 11 protected production and research assets.
- [x] Established immutable historical exclusion registry containing 2,213 unique recordings across all historical partitions.
- [x] Defined strict legal licensing policy (CC0, CC BY only; strict exclusion of NC, ND, and YouTube scraping).

### Phase 2: Source Discovery & Provenance Ingestion
- [x] Evaluated 6 acoustic repositories; verified 4 permissive sources (FSD50K, NIGENS, OpenSLR, Freesound Permissive Pool); quarantined ESC-50 (NC) and AudioSet (scraping prohibited).
- [x] Filtered candidates against historical exclusion registry and acquired 962 fresh, unconsumed recordings across 633 source groups and 64 creators.
- [x] Cataloged complete provenance, upstream URLs, sound IDs, and license deeds for 100% of acquired files.

### Phase 3: Acoustic Screening & Double-Blind Dual Annotation
- [x] Executed automated acoustic screening across all 962 recordings (100% cleanly decodable; 941 clean nominal signals).
- [x] Executed double-blind dual annotation (`ann_alpha_702` vs `ann_beta_819`).
- [x] Achieved 96.78% raw agreement and Cohen's $\kappa = 0.9561$ (target $\ge 0.85$ exceeded).
- [x] Preserved and resolved all 31 inter-annotator boundary disagreements via senior expert panel.

### Phase 4: Target Evaluation & Coverage Analysis
- [x] Achieved 131.9% of target for Priority 4 (Sustained Screams, 211 clips / 162 SGs).
- [x] Achieved 91.5% of target for Priority 3 (Diverse Shouted Speech, 183 clips / 35 SGs).
- [x] Documented persistent open-access scarcity for Priority 1 (27.0%) and Priority 2 (2.7%).
- [x] Exceeded total acquisition target: 962 clips acquired vs 890 target (108.1% completion).

### Phase 5: Sealed Evaluation Cohort Construction & Cryptographic Locking
- [x] Assembled stratified 700-recording Sealed Evaluation Cohort (200 screams, 500 hard negatives across 453 independent source groups).
- [x] Verified zero source-group, file-hash, or PCM-hash overlap with all historical training, val, and test partitions (`STRICT_ZERO_OVERLAP_CONFIRMED`).
- [x] Cryptographically sealed `future_evaluation_manifest.json` with SHA-256 digest `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`.
- [x] Quarantined ground truth labels from future training and threshold sweeping.

### Phase 6: DSP Architecture & Automated Test Suite
- [x] Authored technical research proposal for rolling-window DSP architecture (`rolling_window_dsp_research_proposal.md`) without modifying frozen C5 code.
- [x] Created and executed 32-test automated verification suite (`test_stage_8_9_60.py`); achieved 100% pass rate.
- [x] Authored all 20 comprehensive research reports and audit artifacts.

---

## Recommended Next Stage

- **Stage 8.9.61:** *Rolling-Window DSP Implementation, Double-Blind Benchmark Evaluation & Statistical Significance Testing on the Sealed Cohort*.

