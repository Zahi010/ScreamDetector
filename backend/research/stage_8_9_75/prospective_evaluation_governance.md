# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Prospective Evaluation Governance, Cohort Sealing & Anti-Leakage Protocol

**Project:** Festival Scream Detector  
**Stage:** 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Effective Date:** 2026-11-14  
**Author:** Statistical Validation Engineer & Research Governance Auditor  

---

## 1. Executive Summary & Purpose

In Stages 61–63, the Stage 60 evaluation cohort was unsealed and evaluated, generating 2,800 predictions. However, in Stages 67–73, subsequent reports erroneously described that cohort as *"sealed, untouched, and pristine"*, based solely on verifying the static SHA-256 hash of the manifest file on disk. This conflation of static file integrity with absence of evaluation demonstrated a critical vulnerability in research governance.

Stage 8.9.75 introduces an enforceable **Prospective Evaluation Governance Framework** to prevent circular evaluation, threshold snooping, uploader leakage, and false claims of generalization.

---

## 2. Core Governance Tenets

### 1. Source-Group Atomicity & Partition Isolation
- Every audio recording and its underlying acoustic source (creator, recording session, physical environment) belongs to exactly one logical partition: `TRAINING`, `DEVELOPMENT`, or `PROSPECTIVE_EVALUATION`.
- **Zero-Tolerance Leakage:** Under no circumstances may a source group exist in multiple partitions.
- **Lineage Inheritance:** Synthetic transformations (RIR convolution, background mixing, speed/pitch perturbation) and temporal excerpts automatically inherit the source group and partition of their seed recording.

### 2. Comprehensive Pre-Evaluation Freeze
Before prospective evaluation labels may be accessed or decrypted, the research candidate must be fully frozen. Ten specific assets must be cryptographically locked:
1. Candidate neural network architecture and layer definitions.
2. Model weight checkpoint (SHA-256 hash recorded).
3. Audio preprocessing pipeline (resampling, framing, FFT, mel filterbanks).
4. Full inference pipeline (temporal aggregation, hop size, window smoothing).
5. Primary classification probability threshold.
6. Hand-crafted acoustic veto rules (e.g. distress ratio, roughness veto, crest factor).
7. Formal metric mathematical definitions.
8. Acceptance gate criteria (the immutable 5 gates).
9. Full manifest of the prospective evaluation cohort.
10. Evaluation preregistration document signed and hashed.

### 3. Single Execution Mandate
- A prospective evaluation cohort may be evaluated **exactly once** for a preregistered candidate.
- Batch re-evaluation, iterative hyperparameter tuning, post-hoc threshold adjustment, or selective veto disabling against the prospective cohort is strictly forbidden.

### 4. Immediate Exposure Reclassification
- The moment a prospective evaluation cohort is unsealed and scored, its status immediately transitions to `HISTORICALLY_EXPOSED_COHORT`.
- It is permanently barred from being cited as an untouched prospective benchmark in future stages. Any subsequent prospective evaluation demands acquiring a completely new independent cohort.

---

## 3. Local Access-Control Boundaries & Limitations

In a local Git working tree environment without enterprise role-based cryptographic access control (RBAC) or air-gapped hardware security modules (HSM), absolute technical isolation cannot be enforced at the OS filesystem layer. Any local process with user permissions could theoretically read files.

To maintain scientific integrity despite local environment constraints, the following **Procedural and Cryptographic Controls** are established:

1. **Partition Wall:** Evaluation cohort label files are segregated into quarantine manifests (`evaluation_labels_quarantine.json`) and omitted from standard dataset loading scripts (`data_loader.py`).
2. **Access Audit Logging:** Every programmatic attempt to read, evaluate, or unseal prospective labels must append an entry to `evaluation_access_log.csv`.
3. **Automated Leakage CI Assertion:** Continuous integration tests (`tests/test_stage_8_9_75.py`) verify that training and development data loaders do not access prospective evaluation source groups.
4. **Honest Documentation of Exposure:** If any prospective data is accessed for error inspection, developers must immediately disclose the access in the stage progress tracker.

---

## 4. Prospective Evaluation Lifecycle

```
[Candidate Development & Tuning] ─── (Restricted to TRAINING & DEVELOPMENT partitions)
               │
               ▼
   [Five-Gate Candidate Freeze] ─── (All 10 assets cryptographically hashed)
               │
               ▼
[Preregistration Document Signed] ─── (Formal submission to audit log)
               │
               ▼
  [Authorized Cohort Unsealing] ─── (One-time evaluation run executed)
               │
               ▼
[Scoring & Completion Reporting] ─── (Report published with immutable verdict)
               │
               ▼
[Permanent Cohort Reclassification] ─── (Marked HISTORICALLY_EXPOSED_COHORT)
```

---

## 5. Summary of Governance Commitments

- Candidate 71-D remains the active frozen champion (`e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`).
- Stage 54, 60, and 64 cohorts are permanently classified as exposed historical data.
- The project will NOT claim prospective evaluation readiness until newly acquired candidates are independently labeled by double-blind human annotators under the governance framework.

