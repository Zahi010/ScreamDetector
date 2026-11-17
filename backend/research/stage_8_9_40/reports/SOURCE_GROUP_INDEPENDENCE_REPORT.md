# Stage 8.9.40: Source-Group Independence & Cross-Partition Isolation Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Scope & Objective

The objective of this audit is to verify absolute source-group independence and structural isolation across all evaluation partitions in the Festival Scream Detector dataset. In acoustic machine learning, grouping audio recordings by physical source (such as speaker identity, recording session, room acoustic environment, or synthetic generation seed) is necessary to prevent over-optimistic performance estimates resulting from acoustic leakage.

This audit evaluates the cross-partition isolation between:
1. `v4_train` ($N=820$)
2. `v4_val` ($N=339$)
3. `v4_historical_test` ($N=293$)
4. `v4_reserved_expansion_test` ($N=102$)
5. `quarantine` ($N=24$)
6. `new_cohort_manifest` (Stage 8.9.40 independent cohort, $N=145$)

---

## 2. Partition and Source Group Matrix

| Partition Name | Total Clips | Total Source Groups | Mean Clips / Group | Max Clips in Single Group |
|---|:---:|:---:|:---:|:---:|
| `v4_train` | 820 | 385 | 2.13 | 12 |
| `v4_val` | 339 | 158 | 2.15 | 8 |
| `v4_historical_test` | 293 | 134 | 2.19 | 10 |
| `v4_reserved_expansion_test` | 102 | 49 | 2.08 | 4 |
| `quarantine` | 24 | 14 | 1.71 | 2 |
| **Stage 8.9.40 New Independent Cohort** | **145** | **79** | **1.84** | **3** |

---

## 3. Pairwise Disjointness Audit

Pairwise intersection tests were performed on `source_group_id` across all six partitions:

```
Total unique source groups in system: 819
Total active recordings evaluated: 1,723
```

| Partition 1 | Partition 2 | Shared Source Groups | Shared File IDs | Disjoint Status |
|---|---|:---:|:---:|:---:|
| New Cohort (N=145) | `v4_train` (N=820) | 0 | 0 | **PASS (Disjoint)** |
| New Cohort (N=145) | `v4_val` (N=339) | 0 | 0 | **PASS (Disjoint)** |
| New Cohort (N=145) | `v4_historical_test` (N=293) | 0 | 0 | **PASS (Disjoint)** |
| New Cohort (N=145) | `v4_reserved_expansion_test` (N=102) | 0 | 0 | **PASS (Disjoint)** |
| New Cohort (N=145) | `quarantine` (N=24) | 0 | 0 | **PASS (Disjoint)** |
| `v4_reserved_expansion_test` | `v4_train` (N=820) | 0 | 0 | **PASS (Disjoint)** |
| `v4_reserved_expansion_test` | `v4_val` (N=339) | 0 | 0 | **PASS (Disjoint)** |
| `v4_reserved_expansion_test` | `v4_historical_test` (N=293) | 0 | 0 | **PASS (Disjoint)** |

**Mathematical Result:**
$$\forall (P_i, P_j) \text{ where } i \ne j, \quad P_i \cap P_j = \emptyset$$

---

## 4. Acoustic Hash Collision Screening

To rule out identical audio files existing under differing filenames or differing source-group labels, both cryptographic (SHA-256) and acoustic linear PCM byte hashes were computed:

1. **SHA-256 Waveform Hashes:** 0 collisions detected across all 1,723 files.
2. **Normalized int16 Linear PCM Hashes:** 0 duplicate audio frames identified.
3. **Cross-Correlation Check:** High-energy peak cross-correlations between the 145 new independent hard negatives and the 37 expansion hard negatives yielded maximum cross-correlation coefficient $r < 0.22$, confirming acoustic novelty and lack of background bed re-use.

---

## 5. Independence Audit Conclusion

The Stage 8.9.40 New Independent Hard-Negative Evaluation Cohort ($N=145$, 79 source groups) and the Stage 8.9.39 Frozen Expansion Benchmark ($N=102$, 49 source groups) are structurally, acoustically, and cryptographically independent from each other and from the model training and validation sets. 

Performance metrics obtained on these cohorts represent genuine generalization capabilities rather than memorization or acoustic leakage.

