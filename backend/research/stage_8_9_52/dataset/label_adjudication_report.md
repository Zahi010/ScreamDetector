# Dataset Label Adjudication & Taxonomy Report — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Label Governance & Taxonomy Standards

In accordance with Section 6.3, every audio recording admitted into the Stage 8.9.52 Expansion Dataset was mapped to an explicit primary taxonomy and decoupled acoustic subtype tags:

### Primary Label Classes:
- `CONFIRMED_SCREAM_LIKE`: Authentic human screams, distress vocalizations, shrieks, and shriek-adjacent vocal events.
- `SHOUTED_SPEECH`: Loud spoken commands, vocal cheers, athletic coaching calls, disputes, and amplified speech.
- `CHEERING`: Stadium crowd roar, collective cheering, festival singing, applause.
- `CRYING`: Infant, toddler, and child distress crying.
- `WHISTLE`: Referee whistles, pea-trill whistles, electronic whistles, acoustic squeaks.
- `OTHER_VOCALIZATION`: General non-scream environmental sounds, sirens, fireworks clatter.

### Independent Acoustic Subtype Tags:
- `LOW_INTENSITY`: Low acoustic power, quiet or muffled vocalizations.
- `MUFFLED`: High frequencies absorbed by barrier, distance, or enclosure.
- `CROWD_MASKED`: Background multi-talker babble or ambient festival noise.
- `DISTANT`: Physical recording distance $> 15\text{ meters}$.
- `REVERBERANT`: Prominent room impulse or diffuse outdoor reverberation.
- `SHORT`: Duration $0.5 < d \le 1.0\text{ seconds}$.
- `ULTRA_SHORT`: Duration $d \le 0.5\text{ seconds}$.
- `SUSTAINED`: Duration $d > 1.0\text{ seconds}$.

---

## 2. Expansion Dataset Adjudication Summary

| Primary Class Label | Total Clips | Dominant Acoustic Subtypes | Independent Source Groups | Adjudication Status |
|---|---|---|---|---|
| `CONFIRMED_SCREAM_LIKE` | 604 | `CROWD_MASKED` (129), `DISTANT` (132), `SHORT` (136), `SUSTAINED` (468), `LOW_INTENSITY` (10) | 222 | **CONFIRMED_AUDIT_PASS** |
| `SHOUTED_SPEECH` | 346 | `SHORT` (85), `SUSTAINED` (261) | 162 | **CONFIRMED_AUDIT_PASS** |
| `CHEERING` | 294 | `CROWD_MASKED` (210), `SUSTAINED` (294) | 128 | **CONFIRMED_AUDIT_PASS** |
| `WHISTLE` | 171 | `SHORT` (92), `SUSTAINED` (79) | 74 | **CONFIRMED_AUDIT_PASS** |
| `CRYING` | 87 | `SUSTAINED` (87) | 41 | **CONFIRMED_AUDIT_PASS** |
| `OTHER_VOCALIZATION` | 230 | Environmental sirens, fireworks, music | 78 | **CONFIRMED_AUDIT_PASS** |
| **Total Curated Clips** | **1,732** | — | **705** | **100% ADJUDICATED** |

---

## 3. Review Limitation Notice

All 1,732 recordings underwent programmatic dual-pass signal verification and cross-validation against original source metadata. Where two-person human listening adjudication was unavailable, clips were screened using automated spectral centroid, pitch tracking, and HNR metrics. Two recordings flagged as ambiguous during previous stages remain quarantined.

