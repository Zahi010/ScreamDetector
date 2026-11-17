# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — False-Positive Forensic Audit & Acoustic Taxonomy

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This forensic report analyzes the 25 false-positive detections produced by the baseline Dual-Resolution Gated Architecture on the 117 non-target recordings of the development cohort (overall dev FPR = $21.37\%$, $25/117$).

The forensic records, physical acoustic features, and root-cause analyses are detailed in [`false_positive_forensic_inventory.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/false_positive_forensic_inventory.csv).

---

## 2. Acoustic Error Taxonomy

The 25 false positives resolve into 6 distinct physical acoustic error classes:

```
False Positive Breakdown by Acoustic Error Class (N = 25)
┌───────────────────────────┬─────────┬──────────────┬────────────────────────┬──────────────────────────────────────────┐
│ Acoustic Error Class      │ FPs     │ Percentage   │ Mean Short Gating Wt   │ Primary Acoustic Mechanism               │
├───────────────────────────┼─────────┼──────────────┼────────────────────────┼──────────────────────────────────────────┤
│ friction_squeak           │ 6       │ 24.0%        │ 0.584                  │ Transient mechanical friction spikes     │
│ chimes_bells_metallic     │ 5       │ 20.0%        │ 0.692                  │ Resonant metallic harmonics & guitar amp │
│ shouted_speech_vocal      │ 5       │ 20.0%        │ 0.536                  │ Non-scream vocal outcries & gasping      │
│ whistle_pure_tone         │ 4       │ 16.0%        │ 0.354                  │ High-pitch tonal energy (dog/referee)    │
│ vehicle_horn_siren        │ 3       │ 12.0%        │ 0.490                  │ Narrowband continuous acoustic blasts    │
│ environmental_transient   │ 2       │ 8.0%         │ 0.685                  │ Clapping and wind turbulence gusts       │
└───────────────────────────┴─────────┴──────────────┴────────────────────────┴──────────────────────────────────────────┘
```

---

## 3. Physical Failure Mode Analysis

### 3.1 Mechanical Friction Squeaks (24.0% of FPs)
- **Examples:** Plastic tube squeaks (`109827`, `109830`, `109831`), rubber wheel squeaks (`235667`), chair creaks (`323723`).
- **Failure Mode:** These impulsive friction sounds concentrate high acoustic energy within the $1.5$–$4.0\,\text{kHz}$ spectrum over very short durations ($100$–$300\,\text{ms}$). Because the short-event branch was specifically engineered to be sensitive to rapid transient bursts, it assigns high confidence ($w_{\text{short}} > 0.50$), misclassifying mechanical slip-stick friction as human distress.

### 3.2 Resonant Metallic Chimes & Bells (20.0% of FPs)
- **Examples:** Windchimes (`118979`, `375627`, `50405`), rally bells (`36160`), distorted guitar harmonic breaks (`50744`).
- **Failure Mode:** Percussive striking of metal produces sharp initial transients followed by slowly decaying harmonic partials. The dual-resolution network's short branch triggers on the sharp strike, while the sustained branch detects the prolonged ringing harmonic decay.

### 3.3 Shouted Speech & Non-Scream Vocalizations (20.0% of FPs)
- **Examples:** Children group singing/shouting (`350438`, `350452`), infant crying (`162880`), sobbing with breath gasps (`196156`), victim gasps (`s60_rec_0332`).
- **Failure Mode:** Severe physiological strain during shouting or sobbing produces vocal fold biphonation and subharmonics that closely mirror distress screams.

### 3.4 Whistles & Acoustic Pure Tones (16.0% of FPs)
- **Examples:** Acoustic dog whistles (`169005`), rocket whistles (`186933`), referee tone samples (`s60_rec_0555`, `s60_rec_0556`).
- **Failure Mode:** Monolithic spectral energy concentrated precisely at the peak sensitivity band of the scream detector ($2.5$–$3.5\,\text{kHz}$).

---

## 4. Suppression Strategy for Phase E4

Based on this forensic distribution, suppression requires a multi-pronged approach:
1. **HNR Tonal Veto:** Suppresses pure whistles and tones ($HNR > 7.5\,\text{dB}, SF < 0.008$).
2. **Contrastive Hard-Negative Training:** Incorporates hard friction, metallic strikes, and shouts into the feature space.
3. **Temporal Corroboration ($K=2$):** Rejects isolated friction squeaks and transient strikes that do not persist across consecutive rolling frames.

