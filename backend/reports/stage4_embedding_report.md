# Stage 4 YAMNet Embedding Extraction Report

**AI-Powered Festival Scream Detection System — Stage 4 Verification**

---

## 1. Extraction Pipeline Overview
- **Total Target Recordings**: **1621**
- **Successfully Cached**: **1621** (100.0% completion of eligible set)
  - Newly Extracted: 0
  - Reused from Valid Cache: 1621
- **Failed Extractions**: **0**
- **Total Cache Size on Disk**: **39.77 MB**
- **Execution Duration**: **3.2 seconds**

---

## 2. Feature Representation & Embedding Dimensions

Every recording is processed into two complementary feature representations:
1. **Frame-Level Sequence (`frame_embeddings`)**:
   - **Shape**: `(N_frames, 1024)` float32 array, preserved in chronological order.
   - **Frame Length**: 0.975s (15,600 samples) with 0.4875s hop step (~50% overlap).
   - **Frame Distribution**: Min: **1**, Mean: **23.6**, Max: **408** frames per audio file.
   - **Use Case**: Allows Stage 5 to evaluate temporal aggregation, recurrent models, attention pooling, or sliding-window alert triggers without re-running YAMNet.

2. **Clip-Level Pooled Representation (`clip_embedding`)**:
   - **Shape**: `(2048,)` float32 array.
   - **Construction**: Concatenation of mean pooling `(1024,)` and max pooling `(1024,)` across all frames in the clip.
   - **Use Case**: Provides a robust, fixed-dimensional baseline representation for training lightweight classifiers (Logistic Regression, Linear SVM, MLP) in Stage 5.

---

## 3. Embedding Breakdown by Split and Class

| Partition | Screams Cached | Non-Screams Cached | Total Cached | Storage Size |
| :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | **89** | 1045 | **1134** | 28.76 MB |
| **VAL** | **19** | 225 | **244** | 5.94 MB |
| **TEST** | **19** | 224 | **243** | 5.07 MB |

---

## 4. Methodological Limitations & Stage 5 Guidance

1. **Clip-Level vs. Frame-Level Weak Labeling**:
   - A recording labeled as `scream` may contain 1-2 seconds of screaming preceded or followed by quiet breathing or ambient room noise.
   - Max pooling captures the peak acoustic distress energy across the clip, while mean pooling reflects overall duration. Stage 5 should evaluate both pooled features and frame-level maximum thresholds.
2. **No Data Fabrication**:
   - All cached embeddings correspond strictly to verified audio from OpenSLR 99 and NIGENS. No synthetic audio was added to fill class splits.