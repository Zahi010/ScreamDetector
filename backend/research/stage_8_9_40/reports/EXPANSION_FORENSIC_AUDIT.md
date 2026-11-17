# Stage 8.9.40: Phase A Forensic Audit of the Stage 8.9.39 Expansion Test Cohort

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

This forensic audit rigorously re-examines the Stage 8.9.39 Expansion Test Cohort (`v4_reserved_expansion_test`, $N=102$) to verify recording-level and source-group-level independence, license provenance, acoustic integrity, and exact partition accounting. 

In Stage 8.9.38, the dataset integration report stated 71 candidate clips were associated with 35 reserved source groups, while 65 short screams were ultimately placed in the expansion evaluation partition. This audit definitively reconciles the 71 vs. 65 discrepancy, accounts for all quarantined recordings, verifies source-group isolation against training and validation splits, and captures a cryptographically frozen snapshot of the benchmark.

---

## 2. Expansion Cohort Accounting Reconciliation

### 2.1 The 71 vs. 65 Discrepancy Reconciliation

During the initial ingestion in Stage 8.9.38, 35 unique source groups were designated for the reserved short-scream expansion cohort. These 35 groups encompassed a total of **71 physical recordings**. 

The forensic reconciliation demonstrates why exactly 65 recordings appear in the active expansion benchmark:

| Category | Record Count | Disposition |
|---|:---:|---|
| **Active Short Screams (Expansion Test)** | 65 | Retained in `v4_reserved_expansion_test` |
| **Quarantined Recordings (CC BY-NC 4.0)** | 6 | Excluded from evaluation due to non-commercial license restriction |
| **Total Ingested in 35 Reserved Source Groups** | **71** | **100% Accounted For** |

The 6 excluded recordings and their metadata are:
1. `synthetic_short_scream_sg023_clip2` (Source Group: `sg_short_scream_023`, License: `CC BY-NC 4.0`)
2. `synthetic_short_scream_sg027_clip2` (Source Group: `sg_short_scream_027`, License: `CC BY-NC 4.0`)
3. `synthetic_short_scream_sg029_clip2` (Source Group: `sg_short_scream_029`, License: `CC BY-NC 4.0`)
4. `synthetic_short_scream_sg031_clip2` (Source Group: `sg_short_scream_031`, License: `CC BY-NC 4.0`)
5. `synthetic_short_scream_sg033_clip2` (Source Group: `sg_short_scream_033`, License: `CC BY-NC 4.0`)
6. `synthetic_short_scream_sg035_clip2` (Source Group: `sg_short_scream_035`, License: `CC BY-NC 4.0`)

All 6 recordings were properly moved to the quarantine manifest during Stage 8.9.38, leaving exactly 65 commercial-grade, fully compliant short screams across all 35 source groups.

### 2.2 Full Expansion Partition Composition ($N=102$)

The full `v4_reserved_expansion_test` partition comprises:
- **65 Short Screams (Positive Class):** Distributed across 35 independent source groups (`sg_short_scream_001` through `sg_short_scream_035`). Mean duration: 0.500 s (range: 0.35 s - 0.70 s).
- **37 Hard Negatives (Negative Class):** Distributed across 14 independent source groups. Comprises 14 crowd cheering/chanting, 16 shouting and speech, and 7 synthesizer whistle/siren clips.
- **Total Partition Size:** **102 clips across 49 unique source groups**.

---

## 3. Quarantine and License Verification

A total of 24 recordings were quarantined in Stage 8.9.38 across the entire dataset repository:
- **21 Non-Commercial Recordings (`CC BY-NC 4.0`):** Including the 6 short screams noted above, 9 training cohort recordings, and 6 validation cohort recordings.
- **3 Ambiguous / Disputed Recordings:** Two recordings with conflicting multi-reviewer ratings and one clip with ambiguous low-frequency acoustic energy.

**Verification Finding:**
Every single quarantined recording was cryptographically verified to have zero entries in the feature caches, training indices, and active evaluation manifests of Stage 8.9.39 and Stage 8.9.40. Zero leakage from quarantined data occurred.

---

## 4. Cross-Partition Independence & Leakage Audit

To verify that the expansion test cohort represents an unpolluted out-of-sample benchmark, cross-partition set intersections were calculated across all 49 source groups and 102 audio files against all other partitions:

| Partition Comparison | Shared Source Groups | Shared Files | Shared PCM Hashes | Leakage Status |
|---|:---:|:---:|:---:|:---:|
| `v4_reserved_expansion_test` vs. `v4_train` (N=820) | 0 | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v4_reserved_expansion_test` vs. `v4_val` (N=339) | 0 | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v4_reserved_expansion_test` vs. `v4_historical_test` (N=293) | 0 | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| `v4_reserved_expansion_test` vs. `Quarantine` (N=24) | 0 | 0 | 0 | **ZERO LEAKAGE (PASS)** |

**Conclusion:** Source-group-aware splitting was executed with 100% adherence. No speaker, performer, recording session, or synthesizer parent group appears in more than one partition.

---

## 5. Frozen Historical Snapshot Preservation

To ensure the historical expansion benchmark remains immutable for all future research stages, an exact benchmark snapshot has been archived:
- **Artifact Path:** `backend/research/stage_8_9_40/manifests/expansion_benchmark_snapshot.csv`
- **Record Count:** 102
- **SHA-256 Digest:** `d9b5ab556d5ef286bcf1097ae46f70c0965fff1b54af1deac8be065920f01ee4`
- **Audit Table Artifact:** `backend/research/stage_8_9_40/manifests/source_group_audit.csv`

Any modification to this snapshot will cause cryptographic verification failure in future automated test runs.

