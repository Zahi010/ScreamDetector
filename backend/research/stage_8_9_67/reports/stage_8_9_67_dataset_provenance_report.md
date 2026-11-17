# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.67 DATASET PROVENANCE REPORT: Source Independence, Partition Integrity & Sealed Cohort Isolation

**Safety Designation:** Non-certified experimental acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, police notification, active-shooter systems, or critical security operations. Safe recorded-audio playback only.

---

## 1. Overview & Partition Architecture

Stage 8.9.67 enforces strict source-group isolation across all dataset splits to prevent data leakage and guarantee that evaluation metrics reflect genuine generalization to previously unobserved recording environments, acoustic devices, and human vocalists.

The evaluation architecture consists of three strictly isolated partitions:
1. **Stage 54 Verified Expansion Cohort ($N=1,366$):** Partitioned into training and validation splits strictly by `source_group`.
2. **Stage 64 Held-Out Short-Scream Cohort ($N=268$):** A specialized cohort of short screams ($<1.0$s) drawn from 7 distinct source groups.
3. **Stage 60 Sealed Independent Cohort ($N=700$):** Locked evaluation set preserved under cryptographic seal (`9dfa4ced7f2cb1924519fbb9f9a12c8ff4a372e90f23fd35f60fc10aa7fa297f`).

---

## 2. Stage 54 Verified Expansion Cohort ($N=1,366$)

- **Manifest File:** `backend/research/stage_8_9_54/dataset/partition_manifest_verified.csv`
- **Total Recordings:** 1,366 audio files
- **Total Source Groups:** 553 distinct recording groups
- **Partitioning Strategy:** Group-k-fold splitting ensuring complete disjunction between `expansion_train` and `expansion_val`.

### Detailed Partition Breakdown

| Split Name | Clips ($N$) | Source Groups ($K$) | Screams ($N$) | Shouted Speech ($N$) | Diverse Hard Negatives ($N$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`expansion_train`** | 1,055 | 415 | 403 (38.2%) | 147 (13.9%) | 505 (47.9%) |
| **`expansion_val`** | 311 | 138 | 99 (31.8%) | 88 (28.3%) | 124 (39.9%) |
| **Total** | **1,366** | **553** | **502** | **235** | **629** |

### Hard Negative Category Composition in Validation ($N=124$)
The 124 diverse hard negative files in `expansion_val` cover challenging non-scream acoustic events:
- Crowd cheering and shouting: 32 clips
- Brass and percussion instruments: 21 clips
- Sirens and emergency vehicle alarms: 18 clips
- Synthetic alarms, whistles, and sweeps: 19 clips
- High-intensity laughter and vocalizations: 16 clips
- Ambient festival background and PA announcements: 18 clips

### Source-Group Disjointness Verification
A cross-partition set intersection was executed across `source_group` identifiers:
$$\text{Train Groups} \cap \text{Val Groups} = \emptyset$$
- Unique training groups: 415
- Unique validation groups: 138
- Overlap: **0 groups (0.00%)**
- Filename overlap: **0 files (0.00%)**

---

## 3. Stage 64 Held-Out Short-Scream Cohort ($N=268$)

- **Manifest File:** `backend/research/stage_8_9_64/dataset/held_out_short_screams_manifest.csv`
- **Total Recordings:** 268 audio files
- **Duration Criteria:** $T < 1.0$ second (mean duration: 420 ms, min duration: 95 ms)
- **Source Groups:** 7 distinct source groups (`ho_sg_01` through `ho_sg_07`)
- **Isolation Status:** Disjoint from development training partitions; reserved exclusively for secondary short-scream generalization probing.

---

## 4. Sealed Evaluation Cohort Isolation Audit ($N=700$)

The Stage 60 sealed evaluation manifest (`future_evaluation_manifest.json`) contains 700 pristine audio recordings (200 screams, 500 negatives) designated for final blind evaluation.

### Cryptographic Hash Verification
- **Path:** `backend/research/stage_8_9_60/future_evaluation_manifest.json`
- **Expected SHA-256:** `9dfa4ced7f2cb1924519fbb9f9a12c8ff4a372e90f23fd35f60fc10aa7fa297f`
- **Observed SHA-256:** `9dfa4ced7f2cb1924519fbb9f9a12c8ff4a372e90f23fd35f60fc10aa7fa297f`
- **Status:** **VERIFIED SEALED & UNMODIFIED**

### Data Contamination Check
To verify that neither the training set nor validation sets leaked any audio from the sealed cohort, an automated intersection audit was conducted between all Stage 54/64 files and the sealed manifest:
- Total sealed manifest entries: 700
- Overlapping files with `expansion_train`: **0 (0.0%)**
- Overlapping files with `expansion_val`: **0 (0.0%)**
- Overlapping files with `held_out_short_screams`: **0 (0.0%)**
- Overlapping source groups: **0 (0.0%)**

---

## 5. Legal Provenance and Licensing Compliance

All audio files utilized in Stage 8.9.67 were legally obtained and comply with ethical research licensing:
- **Licensing:** Creative Commons Zero (CC0), Creative Commons Attribution (CC-BY, CC-BY-SA), or synthetic recorded tones generated via local offline DSP synthesis.
- **Safety Protocol:** Safe recorded audio playback only. No live audio acquisition in real emergency situations. No human subjects placed at distress or physical risk during data collection.
- **Exclusions:** No private intercepted communications, no copyrighted musical broadcasts without research exemption, and no live emergency-dispatch audio.

