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

# Stage 8.9.60 Research Directory & Artifact Guide

## 1. Directory Overview

This directory (`backend/research/stage_8_9_60/`) contains the complete data, scripts, tests, and documentation artifacts produced during **Stage 8.9.60: Targeted Legal Dataset Acquisition, Source Independence Verification & Sealed Evaluation Cohort Construction**.

The primary objective was acquiring a legally vetted, unconsumed acoustic dataset to resolve critical representation gaps identified in Stage 8.9.59, and assembling a cryptographically sealed 700-recording evaluation cohort for unbiased future model benchmarking.

---

## 2. File Organization

```
stage_8_9_60/
├── scripts/                                         # Automated acquisition & audit scripts
│   ├── verify_artifact_hashes.py                    # Validates SHA-256 for all 11 protected assets
│   ├── discover_acquisition_sources.py              # Evaluates 6 acoustic repositories
│   ├── validate_license_provenance.py               # Enforces legal license compliance
│   ├── build_full_acquisition_pool.py               # Ingests & filters 962 fresh recordings
│   ├── build_annotation_manifest.py                 # Double-blind dual annotation & kappa
│   ├── validate_audio_quality.py                    # Acoustic screening (RMS, peak, clipping, SNR)
│   ├── calculate_acquisition_coverage.py            # Reconciles targets vs acquired counts
│   ├── build_future_evaluation_cohort.py            # Stratified assembly of 700-clip test set
│   ├── seal_evaluation_manifest.py                  # Cryptographic SHA-256 sealing script
│   ├── detect_audio_duplicates.py                   # Duplicate & excerpt lineage detection
│   └── audit_source_independence.py                 # Strict cross-partition zero-leakage check
│
├── tests/                                           # Test suite
│   └── test_stage_8_9_60.py                         # 32 automated unit and integration tests
│
├── Data Manifests & CSV Artifacts:
│   ├── acquisition_manifest.csv                     # 962 acquired recordings with full metadata
│   ├── recording_provenance.csv                     # License deeds, creator IDs, upstream URLs
│   ├── source_group_inventory.csv                   # 633 unique acoustic source groups
│   ├── creator_session_inventory.csv                # 64 unique content creator accounts
│   ├── duplicate_and_excerpt_relationships.csv      # 117 multi-crop parent lineages & offsets
│   ├── annotation_records.csv                       # Consensus ground truth labels & timestamps
│   ├── annotation_disagreements.csv                 # 31 adjudicated boundary cases & notes
│   ├── audio_quality_metrics.csv                    # Decodability, RMS, peak dBFS, clipping, SNR
│   ├── acquisition_coverage_matrix.csv              # Granular target vs acquired matrix
│   ├── license_inventory.csv                        # Evaluated license terms and policies
│   ├── acquisition_source_catalog.csv               # Repository evaluations and status
│   ├── future_evaluation_manifest.json              # 700-recording sealed evaluation cohort
│   └── future_evaluation_manifest.sha256            # Cryptographic SHA-256 manifest digest
│
├── Research & Audit Reports (Markdown):
│   ├── README.md                                    # This directory guide
│   ├── STAGE_PROGRESS.md                            # Comprehensive stage progress log
│   ├── final_stage_report.md                        # Master stage synthesis & formal sign-off
│   ├── existing_dataset_inventory.md                # Historical partition baseline & exclusion registry
│   ├── acquisition_source_catalog.md                # Source repository provenance evaluation
│   ├── acquisition_progress_report.md               # Priority tiers target completion summary
│   ├── low_intensity_scream_acquisition_report.md   # Priority 1 analysis & remediation roadmap
│   ├── crowd_masked_scream_acquisition_report.md    # Priority 2 analysis & noise mixing proposal
│   ├── shouted_speech_acquisition_report.md         # Priority 3 analysis & vocal confuser coverage
│   ├── sustained_scream_acquisition_report.md       # Priority 4 analysis & duration distribution
│   ├── license_and_attribution_audit.md             # Legal compliance & attribution tracking
│   ├── source_independence_audit.md                 # Cross-manifest zero-leakage certification
│   ├── duplicate_and_excerpt_audit.md               # Duplicate detection & parent-child offsets
│   ├── annotation_quality_report.md                 # Inter-rater reliability & Cohen's kappa (0.9561)
│   ├── audio_quality_report.md                      # Signal processing & decodability screening
│   ├── dataset_coverage_report.md                   # Granular subgroup representation assessment
│   ├── future_sealed_evaluation_cohort_report.md    # Sealed cohort composition & quarantine rules
│   ├── statistical_sample_size_rationale.md         # Sample size power analysis & design effects
│   ├── rolling_window_dsp_research_proposal.md      # 500 ms rolling hop design proposal
│   ├── limitations_and_open_issues.md               # Active risk log & open data gaps
│   └── stage_8_9_60_test_report.md                  # Execution results for 32 pytest tests
```

---

## 3. Reproduction Instructions

To execute the full audit and verify all invariants from scratch:

1. **Verify Asset Cryptographic Digests:**
   ```powershell
   python festival-scream-detector/backend/research/stage_8_9_60/scripts/verify_artifact_hashes.py
   ```

2. **Run Source Independence Verification:**
   ```powershell
   python festival-scream-detector/backend/research/stage_8_9_60/scripts/audit_source_independence.py
   ```

3. **Verify Sealed Cohort SHA-256 Digest:**
   ```powershell
   python festival-scream-detector/backend/research/stage_8_9_60/scripts/seal_evaluation_manifest.py
   ```

4. **Execute Automated Pytest Suite:**
   ```powershell
   pytest festival-scream-detector/backend/research/stage_8_9_60/tests/test_stage_8_9_60.py -v
   ```

