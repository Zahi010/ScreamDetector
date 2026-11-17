# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Storage Capacity, Disk Allocation & Audio Quota Audit (Stage 8.9.76)

**Stage:** 8.9.76 — Independent Audio Acquisition, Double-Blind Annotation & Label Adjudication  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Auditor:** Senior Audio Dataset & Storage Validation Engineer  

---

## 1. Executive Summary

A hardware file system audit was conducted prior to initiating independent audio downloading in Stage 8.9.76. To prevent depletion of host system capacity, disk safety quotas and pre-download size checks are strictly enforced.

The primary system drive (C:\) possesses **15.91 GB** of free space. A hard **500.0 MB acquisition quota** is mandated for Stage 8.9.76 on C:\ drive.

---

## 2. File System Inspection Summary

Hardware audit conducted on 2026-11-14 via PowerShell `Get-PSDrive -PSProvider FileSystem`:

| Drive | Total Capacity (GB) | Used Space (GB) | Free Space (GB) | Free Percentage (%) | Role & Governance Status |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **C:\\** | ~268.05 | 252.14 | **15.91** | **5.94%** | Primary System Volume (OS, Repo, Stage Working Tree) |
| **D:\\** | ~341.80 | 290.35 | **51.45** | **15.05%** | Secondary Volume (Local Storage) |
| **E:\\** | ~341.80 | 268.40 | **73.40** | **21.47%** | Tertiary Volume (Large Audio Archive) |

---

## 3. Storage Safety Mandates for Stage 8.9.76

1. **Safety Redline Quota:**
   - Minimum free space floor on C:\ drive: **10.00 GB**.
   - Maximum allowable new audio download volume for Stage 76: **500.0 MB**.
   - If free space on C:\ drops below 10.00 GB at any point, download operations must halt immediately.
2. **Pre-Download Inspection:**
   - Every candidate recording must have its byte length inspected from API headers prior to downloading.
   - Any single recording exceeding **30.0 MB** is automatically quarantined from the evaluation pool to avoid skewing storage.
3. **No Duplicate Audio Files:**
   - Audio files are stored once under `backend/research/stage_8_9_76/audio/`.
   - Manifests point to relative audio paths; no redundant copying across research folders.
4. **Download Integrity & Partial Cleanup:**
   - Corrupted or partial downloads must be immediately deleted.
   - Exact SHA-256 digests and decoded PCM hashes must be computed and verified upon completion.

