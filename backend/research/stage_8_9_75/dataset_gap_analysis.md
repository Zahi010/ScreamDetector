# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Acoustic Dataset Gap Analysis & Distributional Deficits

**Stage:** 8.9.75  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  

---

## 1. Executive Summary

An empirical gap analysis of the historical 3694-recording dataset was performed to evaluate acoustic coverage against real-world festival conditions, multi-class vocalization discrimination, and the five immutable acceptance gates.

### Critical Deficit Findings:
1. **Complete Absence of Unexposed Prospective Data:** 100% of historical repository recordings belong to `EXPOSED_DEVELOPMENT_COHORT`, `HISTORICALLY_EXPOSED_COHORT`, or `EXPOSED_DIAGNOSTIC_COHORT`. Genuine prospective validation is impossible without new data.
2. **Child Scream Acoustic Deficit:** Prepubescent child screams are severely underrepresented. Because child vocal tracts produce higher pitch ($F_0 > 500$ Hz) and lower auditory roughness ($< 0.022$), Candidate 71-D's distress veto misclassifies them as non-distress.
3. **Severe Uploader Concentration in Hard Negatives:** Shouted speech has been dominated by a tiny cluster of uploaders (notably `reitanna` and `ericsueiro`), leading to high false-alarm variance across arbitrary speaker styles.
4. **Masked & Low-Intensity Scream Deficit:** Authentic distant and crowd-masked screams are scarce; historical models relied heavily on artificial synthetic mixing rather than ecologically valid outdoor recordings.
5. **Non-Scream Distress Lookalike Scarcity:** Infant crying, gasps, and unison cheering lack multi-annotator gold standards.

---

## 2. Acoustic Gap Matrix

| Acoustic Category | Class Role | Current Unexposed Count | Target Count | Target SGs | Deficit Severity | Primary Failure Mode Addressed |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `VOCAL_SCREAM_CHILD` | POSITIVE | 0 | **150** | 50 | **CRITICAL** | High fundamental pitch (>500 Hz) and low auditory roughness (<0.022) are severely suppressed by current distress veto. |
| `VOCAL_SCREAM_ADULT_LOW_INTENSITY` | POSITIVE | 0 | **150** | 60 | **HIGH** | Low-intensity and distant screams under festival masking fail energy and roughness gating. |
| `VOCAL_SCREAM_SHORT` | POSITIVE | 0 | **200** | 80 | **HIGH** | Historical short screams were 61% clustered from a single uploader; independent short screams (<1.0s) needed for Gate 4. |
| `VOCAL_SCREAM_CROWD_MASKED` | POSITIVE | 0 | **150** | 50 | **HIGH** | Acoustic evaluation in outdoor crowd noise (-6 dB to 0 dB SNR) with natural Lombard effect. |
| `INFANT_CRY` | HARD_NEGATIVE | 0 | **150** | 50 | **CRITICAL** | Infant crying shares high F0 and cry-burst temporal modulation with child screams, creating severe false alarms. |
| `SHOUTED_SPEECH_HIGH_EFFORT` | HARD_NEGATIVE | 0 | **200** | 75 | **CRITICAL** | Historical shouted speech was dominated by uploader 'reitanna'. Need diverse phonemes and lexical shouts for Gate 3. |
| `THEATRICAL_SHOUT` | HARD_NEGATIVE | 0 | **100** | 40 | **HIGH** | Dramatic acting, stage shouts, and radio drama vocalizations that mimic scream acoustic contours. |
| `EXCITED_CHEER_AND_CHANT` | HARD_NEGATIVE | 0 | **150** | 50 | **HIGH** | Concert and sporting event crowd roars produce high spectral flux and high roughness. |
| `GASPS_AND_SURPRISE` | HARD_NEGATIVE | 0 | **100** | 40 | **MEDIUM** | Sudden inhalation and startle gasps exhibit rapid spectral onsets mimicking short scream transients. |
| `WHISTLE_AND_SIREN` | HARD_NEGATIVE | 0 | **150** | 50 | **HIGH** | Referee whistles and emergency sirens trigger tonal harmonic detectors unless vetoed. |
| `FESTIVAL_AMBIENT_AND_MUSIC` | ORDINARY_NEGATIVE | 0 | **250** | 80 | **MEDIUM** | Broadband festival ambience, stage bass, crowd murmur, and fairground machinery for Gate 2 background robustness. |

---

## 3. Storage and Capacity Feasibility

- Total Targeted Clips: **1750**
- Total Distinct Source Groups: **625**
- Estimated Audio Data Footprint: **480.0 MB**
- **Host Storage Feasibility:** The required volume easily fits within the **500 MB C: drive quota** and 15.93 GB available space.
