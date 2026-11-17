# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Storage Capacity, Disk Allocation & Data Volume Audit

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Auditor:** Statistical Validation & Research Governance Auditor  

---

## 1. Executive Summary

A hardware disk storage audit was performed across all attached file systems to establish storage safety constraints, quota ceilings, and data volume budgets prior to executing independent dataset acquisition in Stage 8.9.75.

Historically, earlier stages encountered severe C: drive capacity depletion during unconstrained audio acquisition. To prevent system instability, file system saturation, or corrupted recordings, strict disk quotas and a metadata-first acquisition architecture are mandated.

---

## 2. Storage System Inspection Results

System disk audit conducted on 2026-11-14 via PowerShell `Get-PSDrive -PSProvider FileSystem`:

| Drive | Total Size (GB) | Used Space (GB) | Free Space (GB) | Free Capacity (%) | Mount Status | Designation / Role |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **C:\\** | ~268.05 | 252.12 | **15.93** | **5.94%** | Primary System Drive | Operating System, Git Working Tree, Active Python Venv |
| **D:\\** | ~341.80 | 290.35 | **51.45** | **15.05%** | Secondary Volume | Local Storage / Backup |
| **E:\\** | ~341.80 | 268.40 | **73.40** | **21.47%** | Tertiary Volume | High-Capacity Audio Storage Archive |

---

## 3. Existing Project Storage Footprint

Audio recordings and cached feature tensors within `c:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector` consume:

| Directory Path | Role / Content | Storage Footprint |
| :--- | :--- | :---: |
| `backend/dataset/` | Core historical dataset, raw audio, and manifests | 912.64 MB |
| `backend/experiments/` | Stage 11–21 experimental audio, synthetic mixtures, and splits | 599.43 MB |
| `backend/research/` | Research stage reports, scripts, models, and metadata | ~85.20 MB |
| `data/` (working audio) | Local working staging directory | 0.00 MB |
| **Total Project Footprint** | Complete repository tree on C: drive | **~1.60 GB** |

---

## 4. Storage Safety Rules & Acquisition Budgets

Given that C: drive has only **15.93 GB** free space (5.94% free), the following strict storage policies are in effect:

1. **Safety Redline Quota (C: Drive):**
   - Minimum free space buffer: **10.00 GB**.
   - Maximum allowable new data footprint on C: drive for Stage 8.9.75: **500.00 MB**.
   - If free space on C: drops below 10.00 GB, all download operations must immediately halt.
2. **Metadata-First Architecture:**
   - All newly targeted recordings must be cataloged in manifest format (`acquisition_manifest.csv`, `acquisition_targets.csv`) containing source URLs, license identifiers, cryptographic checksums, sample rates, durations, and source-group IDs before any raw PCM waveform is fetched.
   - Large raw audio downloads (>500 MB) must be targeted to tertiary storage (`E:\audio_archive\` if configured) or processed in streaming batch mode without retaining duplicate raw audio files.
3. **No Duplicate Waveform Storage:**
   - Raw audio must not be duplicated across multiple stage directories.
   - Resampled audio must be generated on-the-fly or cached with strict single-instance reference pointers.
4. **File Immutability & Safety:**
   - No existing audio recordings or manifests may be deleted or moved without explicit authorization.
   - No overwriting of existing historical recording files.

---

## 5. Storage Audit Conclusion

Storage capacity is **CONSTRAINED ON C: DRIVE (15.93 GB FREE)**. The metadata-first acquisition protocol ensures full dataset cataloging, gap identification, and governance without exceeding disk space thresholds.

