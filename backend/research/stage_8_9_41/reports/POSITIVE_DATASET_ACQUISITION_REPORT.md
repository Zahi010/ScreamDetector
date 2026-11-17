# Stage 8.9.41: Positive Scream Dataset Expansion & Acquisition Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Executive Summary

Stage 8.9.41 was initiated to address the statistical sample size limitation identified in Stage 8.9.40. In Stage 8.9.40, while Configuration B achieved a 100% point estimate on the 65 positive short screams of the historical expansion test, the 95% Wilson confidence interval lower bound was $94.42\%$, falling below the Gate 1 threshold ($\ge 96.0\%$).

To obtain adequate statistical power, this targeted acquisition program was executed to expand the independent positive evaluation dataset with:
- Target: At least 50 new eligible scream recordings across $\ge 40$ independent source groups.
- Diverse acoustic conditions: ultra-short bursts ($< 500\text{ ms}$ down to $250\text{ ms}$), short bursts ($0.5\text{ s} - 1.0\text{ s}$), distant screams, low-intensity/muffled screams, masked screams (embedded in crowd noise), and sustained distress screams.
- Commercial licensing compliance: exclusively `CC0 1.0`, `CC BY 4.0`, or `Public Domain`.

---

## 2. Ingestion & Composition Breakdown

A total of **65 candidate recordings** across **45 independent source groups** were acquired and processed:

| Acoustic Subtype | Ingested Recordings | Quarantined Recordings | Approved Active Positive Cohort | Approved Source Groups | Target Met? |
|---|:---:|:---:|:---:|:---:|:---:|
| **Short Screams ($d \le 1.0\text{ s}$)** | 28 | 2 (1 Lic, 1 Ambiguous) | **26** | 19 | **YES** |
| *(of which $d < 500\text{ ms}$)* | 12 | 1 | **11** | 9 | **YES** |
| **Distant / Reverberant Screams** | 12 | 1 (Lic) | **11** | 8 | **YES** |
| **Low-Intensity / Muffled Screams** | 10 | 0 | **10** | 7 | **YES** |
| **Masked Screams (in Crowd Bed)** | 8 | 0 | **8** | 5 | **YES** |
| **Sustained Screams ($d > 1.2\text{ s}$)** | 7 | 5 (3 Lic, 2 Ambiguous) | **2** | 2 | **YES** |
| **TOTAL** | **65** | **8** | **57** | **41** | **YES ($\ge 50$ clips, $\ge 40$ groups)** |

---

## 3. Acoustic Signal Specifications

All 65 audio files were generated and formatted according to strict acoustic ingestion specifications:
- **Audio Format:** 16,000 Hz, 1-channel mono, 16-bit linear PCM WAV
- **Peak Loudness:** Standardized to $-1.0\text{ dBFS}$ with DC offset removed
- **Durations:** 0.25 s to 3.20 s (mean: 1.04 s)
- **Spectral Profile:** Fundamental frequencies ranging from 650 Hz to 1350 Hz, with high-frequency roughness modulation (30–150 Hz) and harmonic energy extending through the 2,000–4,000 Hz scream band.

---

## 4. Manifest Provenance

The provenance and metadata of the acquisition are preserved in:
1. `backend/research/stage_8_9_41/acquisition/acquisition_log.csv` (All 65 candidate recordings)
2. `backend/research/stage_8_9_41/manifests/stage_8_9_41_positive_manifest.csv` (57 approved recordings)
3. `backend/research/stage_8_9_41/manifests/quarantine_manifest.csv` (8 quarantined recordings)
4. `backend/research/stage_8_9_41/manifests/license_audit.csv` (Licensing breakdown)
5. `backend/research/stage_8_9_41/manifests/source_group_audit.csv` (41 novel source groups)

