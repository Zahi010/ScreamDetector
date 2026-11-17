# Forensic Investigation of False-Negative Screams — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary

This forensic report investigates all **29 false negatives** out of the 160 authentic screams in the Stage 8.9.50 independent evaluation cohort ($N=480$). Frozen Candidate B (`config_b_mask.pt`, $\theta=0.8000$) detected 131/160 authentic screams (**81.88% recall**, 95% Wilson CI: $[75.19\%, 87.05\%]$) and missed 29 screams (**18.12% false negative rate**).

All 29 misses occurred natively at Candidate B's threshold boundary prior to Intervention D. Intervention D accepted 100% of Candidate B's raw positive detections, protected by its vocal formant gate ($\text{vocal\_band\_ratio} > 0.18$), and rejected zero authentic screams.

```
Total Authentic Positives: 160
├── Detected (True Positives): 131 (81.88%)
└── Missed (False Negatives):   29 (18.12%)
    ├── Low-Intensity / Muffled:  9 misses (Subtype Recall: 40.00%, 6/15)
    ├── Crowd-Masked Screams:     7 misses (Subtype Recall: 65.00%, 13/20)
    ├── Sustained Screams:        9 misses (Subtype Recall: 74.29%, 26/35)
    ├── Short Screams:            4 misses (Subtype Recall: 91.11%, 41/45)
    ├── Distant / Reverberant:    0 misses (Subtype Recall: 100.0%, 20/20)
    └── Ultra-Short Screams:      0 misses (Subtype Recall: 100.0%, 25/25)
```

---

## 2. Forensic Investigation of the 29 Missed Recordings

Each of the 29 false negatives was forensically analyzed across four domains:
1. **Basic Acoustic Properties:** RMS amplitude, peak amplitude, crest factor, dynamic range, clipping ratio, silence ratio, estimated SNR, noise floor.
2. **Spectral & Vocal Characteristics:** Spectral centroid, bandwidth, 85% spectral rolloff, zero-crossing rate (ZCR), subband energy fractions (low $<1$ kHz, mid $1-4$ kHz, high $>4$ kHz), vocal formant band ratio (300–1800 Hz), whistle band ratio (2.5–3.8 kHz), spectral flatness, $f_0$ pitch tracking, and HNR.
3. **Temporal Dynamics & Framing:** Attack time, decay time, vocal onset, active vocal duration, amplitude envelope coefficient of variation (CV), temporal persistence, intermittent vs continuous status, padding ratio relative to YAMNet 960 ms window, valid frames, padded frames, window alignment offset.
4. **Frozen Model Representations:** Candidate B raw probability, logit, YAMNet semantic embedding stats (norm, mean, std), acoustic branch features (`vocal_max`, `vocal_mean`, `crowd_max`, `crowd_mean`, `scream_max`, `scream_mean`), subband feature vector, and intermediate projection norms.

The complete record-by-record dataset is emitted in [`FALSE_NEGATIVE_FORENSICS_DETAILED.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/results/FALSE_NEGATIVE_FORENSICS_DETAILED.csv).

---

## 3. Detailed Failure Breakdown by Acoustic Subtype

### 3.1 Low-Intensity and Muffled Screams ($N=9$ misses out of 15; Recall: 40.00%)
- **Acoustic Signature:** High average noise floor ($-4.8\text{ dB}$ RMS), low dynamic contrast, compressed dynamic range ($11.2\text{ dB}$ vs $28.4\text{ dB}$ for typical screams), and severe spectral tilt toward lower frequencies (spectral centroid $1,840\text{ Hz}$ vs $2,780\text{ Hz}$ for true positives).
- **Model Mechanism:** Because high frequencies are absorbed or attenuated by physical muffling (e.g., screaming into fabric, hands, or distant enclosure), YAMNet's higher-frequency convolutional filters fail to activate. The acoustic branch `acoust_scream_max` collapses to an average of **$0.00018$** (compared to $0.00420$ on detected screams).
- **Probability Distribution:** Scores ranged from $0.1033$ to $0.7054$ (mean: $0.3667$). The 4 lowest probabilities in the entire evaluation cohort (`s49_indep_pos_0159`: $0.1033$; `s49_indep_pos_0157`: $0.1233$; `s49_indep_pos_0148`: $0.1840$; `s49_indep_pos_0155`: $0.2772$) all belong to this subtype.

### 3.2 Crowd-Masked Screams ($N=7$ misses out of 20; Recall: 65.00%)
- **Acoustic Signature:** High ambient background energy, elevated noise floor ($-8.3\text{ dB}$), low estimated SNR ($0.31\text{ dB}$ active-to-background contrast), and prominent multi-speaker babble energy across 500–2500 Hz.
- **Model Mechanism:** In crowd-masked clips, the YAMNet crowd class detector fires strongly: `acoust_crowd_max` averages **$0.482$** (with several clips reaching $>0.75$). Candidate B's phonation fusion head applies negative weighting to high crowd activations, directly suppressing the scream classification logit.
- **Probability Distribution:** Scores ranged from $0.4028$ to $0.7990$ (mean: $0.6482$). Noticeably, `s49_indep_pos_0142` scored **$0.7990$**—failing detection by a razor-thin margin of **$0.0010$** below the $0.8000$ threshold.

### 3.3 Sustained Screams ($N=9$ misses out of 35; Recall: 74.29%)
- **Acoustic Signature:** Long duration ($1.58\text{ s}$ to $2.79\text{ s}$), low dynamic envelope modulation (CV $= 0.42$ vs $0.78$ for short screams), and steady-state phonation that lacks transient burst onsets.
- **Model Mechanism:** The Dual-Encoder architecture averages YAMNet frame embeddings over the full duration. When a sustained scream exhibits temporal fluctuations or intermittent pitch dropouts, the frame-averaged embedding $\bar{z}_{\text{sem}}$ is diluted by less energetic frames.
- **Probability Distribution:** Scores ranged from $0.1276$ to $0.7753$ (mean: $0.5608$). Four clips scored near the threshold boundary ($0.7055$ to $0.7753$).

### 3.4 Short Screams ($N=4$ misses out of 45; Recall: 91.11%)
- **Acoustic Signature:** Moderate duration ($0.80\text{ s}$ to $0.96\text{ s}$), moderate SNR ($1.51\text{ dB}$ to $2.14\text{ dB}$).
- **Model Mechanism:** All 4 missed short screams scored high probabilities: $0.5583$, $0.6902$, $0.7316$, and $0.7923$. None suffered severe representational collapse; they simply fell just short of the conservative $\theta = 0.8000$ operating point chosen to guarantee zero hard-negative false alarms.
- **Note on Ultra-Short Screams:** All 25 ultra-short screams ($d \le 0.50\text{ s}$) were **100.0% detected** (25/25), confirming that Candidate B's training with short-vocalization augmentation successfully cured the Stage 8.9.41 ultra-short recall defect.

---

## 4. Retrospective Adjudication and Ambiguity Assessment

- **Acoustic Authenticity:** All 29 missed recordings were re-inspected. None were non-screams or corrupted files. All 29 contain genuine, audible human screams.
- **Annotation Ambiguity:** 2 recordings (`s49_indep_pos_0072` and `s49_indep_pos_0090`) exhibit borderline vocal-fry/groan phonation mixed with screaming, warranting human adjudication prior to future inclusion in supervised training.
- **Data Quarantine Protocol:** As mandated by Section 8, **none of the 29 false-negative recordings have been or will be added to the training set**, preventing data snooping and preserving evaluation integrity.

---

## 5. Deliverable References

- Detailed Forensic Metrics: [`results/FALSE_NEGATIVE_FORENSICS_DETAILED.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/results/FALSE_NEGATIVE_FORENSICS_DETAILED.csv)
- Auditable Taxonomy: [`FALSE_NEGATIVE_TAXONOMY.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/FALSE_NEGATIVE_TAXONOMY.csv)
- Acoustic Profile Cards: [`FALSE_NEGATIVE_ACOUSTIC_PROFILES.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/FALSE_NEGATIVE_ACOUSTIC_PROFILES.md)

