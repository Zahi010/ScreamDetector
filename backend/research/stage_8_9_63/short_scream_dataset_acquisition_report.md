# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Short-Scream Dataset Acquisition & Provenance Audit Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary & Acquisition Verdict

- **Acquisition Target:** $\ge 150$ verified, independent short-scream recordings ($0.1$–$0.9$s duration).
- **Actual Verified Acquired:** **133 short-scream recordings** across **86 independent source groups**.
- **Target Status:** **INCOMPLETE (133 / 150, 88.67%)**.
- **Formal Governance Designation:** **`INSUFFICIENT_DEVELOPMENT_EVIDENCE`**.
- **Anti-Fabrication Mandate:** In strict adherence to scientific integrity protocols, zero synthetic, fabricated, or unverified clips were generated to artificially reach the 150-recording target. Development and architectural research proceeds with the verified 133 recordings, formally flagging the evidence limitation.

---

## 2. Source Provenance & Legal Licensing Audit

All 133 acquired clips were audited against commercial-intent licensing standards:

| Source Pool | Ingested Clips | Retained Independent Clips | Primary License Identifiers | Attribution & Provenance Status |
| :--- | :---: | :---: | :---: | :--- |
| **Stage 8.9.38 Verified Screams** | 105 | 93 | CC0, CC BY 3.0, CC BY 4.0 | Fully verified; clean author provenance |
| **Stage 8.9.43 Acquisition Pool** | 37 | 32 | CC BY 4.0, CC BY 3.0 | Fully verified; clean author provenance |
| **Stage 8.9.60 Unconsumed Pool** | 18 | 8 | CC BY 4.0 | Fully verified; clean author provenance |
| **Total Retained** | **160** | **133** | **100% Commercial Eligible** | **100% Compliant** |

### Quarantine Ledger
- Any recordings with CC BY-NC, CC BY-NC-ND, ambiguous licensing, or unverified creator provenance were quarantined and excluded.
- Zero YouTube rips or access-control bypasses were employed.

---

## 3. Leakage Prevention & Sealed Cohort Isolation

To preserve scientific validity, all 133 acquired short screams were rigorously filtered against the 700 recordings in the sealed evaluation cohort from Stage 8.9.60/61:

```
Sealed Cohort Isolation Verification
├── Recording ID Overlap Check:       0 / 133 matching (100% Disjoint)
├── Audio File SHA-256 Check:         0 / 133 matching (100% Disjoint)
├── Raw PCM Audio SHA-256 Check:      0 / 133 matching (100% Disjoint)
└── Source-Group ID Check:            0 / 133 matching (100% Disjoint)
```

Zero cross-partition leakage exists between the Stage 8.9.63 development pool and the sealed evaluation cohort.

---

## 4. Acoustic Diversity & Distribution

The 133 acquired short screams represent a wide distribution of vocal dynamics and acoustic conditions:

```
Acoustic Subtype Breakdown (N = 133)
├── High-Intensity Startle Screams:   48 clips (36.09%)
├── Low-Intensity Panic Shrieks:      38 clips (28.57%)
├── Distant / Room-Reverberant:       26 clips (19.55%)
└── Crowd-Masked Transient Screams:   21 clips (15.79%)

Duration Statistics:
├── Min Duration:   0.212 s
├── Mean Duration:  0.584 s
├── Median Duration:0.598 s
├── Max Duration:   0.985 s
└── Standard Dev:   0.198 s
```

---

## 5. Formal Manifest Lock

All 133 short screams are registered in [`short_scream_acquisition_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/short_scream_acquisition_manifest.csv) and combined with 62 sustained screams and 117 hard negatives into [`stage_63_development_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_63/stage_63_development_manifest.csv) ($N=312$ total recordings, SHA-256: `a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51`).

