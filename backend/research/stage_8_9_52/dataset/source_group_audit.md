# Source-Group Partitioning & Independence Audit — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

This audit verifies the source-group partitioning of the **1,732 authentic recordings** curated in the Stage 8.9.52 Targeted Expansion Dataset.

To prevent intra-session, recording-environment, or uploader leakage, all recordings originating from the same recording session, uploader, or video were assigned strictly as an indivisible unit to exactly one partition:
- `expansion_train`
- `expansion_val`
- `expansion_reserved_test`

---

## 2. Partition & Source-Group Distribution

| Partition Name | Total Clips | Positive Clips | Negative Clips | Total Source Groups | Source-Group Ratio | Partition Role |
|---|---|---|---|---|---|---|
| **`expansion_train`** | 1,055 | 371 | 684 | 423 | 2.49 clips/group | Supervised Training |
| **`expansion_val`** | 311 | 108 | 203 | 141 | 2.21 clips/group | Hyperparameter & Threshold Tuning |
| **`expansion_reserved_test`** | 366 | 125 | 241 | 141 | 2.60 clips/group | **Newly Reserved Untouched Test Set** |
| **Total Expansion Cohort** | **1,732** | **604** | **1,128** | **705** | **2.46 clips/group** | **100% Permissive Commercial-Intent** |

---

## 3. Strict Source-Group Isolation Verification

Set intersections across partitions were evaluated:
$$\mathcal{SG}_{\text{train}} \cap \mathcal{SG}_{\text{val}} = \emptyset \quad (\text{Count: } 0)$$
$$\mathcal{SG}_{\text{train}} \cap \mathcal{SG}_{\text{test}} = \emptyset \quad (\text{Count: } 0)$$
$$\mathcal{SG}_{\text{val}} \cap \mathcal{SG}_{\text{test}} = \emptyset \quad (\text{Count: } 0)$$

Additionally, all source groups were checked against historical evaluation partitions (Stages 47, 49, 50, 51):
$$\mathcal{SG}_{\text{expansion}} \cap \mathcal{SG}_{\text{historical\_indep}} = \emptyset \quad (\text{Count: } 0)$$

Zero source groups, recording sessions, or uploaders overlap between training, validation, newly reserved test, or historical independent cohorts.

---

## 4. Newly Reserved Independent Test Set Governance

The **`expansion_reserved_test`** partition ($N=366$, 125 positives, 241 negatives across 141 source groups) is officially quarantined as an untouched independent test set:
- It must **never** be used for model training.
- It must **never** be used for hyperparameter search.
- It must **never** be used for threshold calibration.
- Candidate E's threshold was frozen at $\theta = 0.4000$ prior to any future evaluation on this reserved set.

