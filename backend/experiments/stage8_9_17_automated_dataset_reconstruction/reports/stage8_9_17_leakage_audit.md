# Stage 8.9.17 Source-Group Splitting & Data Leakage Prevention Audit

## 1. Leakage Prevention Principles
Audio recordings originating from the same recording session, uploader, or hardware device exhibit correlated acoustic profiles. Random window splitting constitutes severe data leakage. Stage 8.9.17 strictly partitions datasets by **source group identifier**, guaranteeing zero shared uploaders or recording identities across splits.

## 2. Audit Verification Results

| Audit Check | Status | Verification Details |
|---|---|---|
| **Source-Group Disjointness** | **PASSED** | 669 Train groups, 144 Val groups, 142 Test groups. Overlap: 0 groups. |
| **Content Hash Disjointness** | **PASSED** | Audio SHA-256 / MD5 content hashes disjoint across Train, Val, Test. Overlap: 0. |
| **Stage 5 Quarantine Isolation** | **PASSED** | 243 frozen Stage 5 test files & 108 source groups excluded. Overlap: 0. |
| **Test Cohort Statistical Adequacy** | **PASSED** | 462 independent test clips, 78 screams, 14 short screams, 28 silence, 22 infant crying. |

## 3. Split Distribution Statistics

- **Train Split:** 1,969 recordings (70.22%)
- **Validation Split:** 373 recordings (13.30%)
- **Test Split:** 462 recordings (16.48%)
