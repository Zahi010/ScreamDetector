# STAGE 8.9.30.2 — FUSION, PERSISTENCE & PIPELINE TRACE REPORT

**Stage:** 8.9.30.2  
**Investigation:** Model-by-Model Failure Localization and Persistence State Audit  
**Production Status:** STRICTLY FROZEN (Threshold = 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. EXECUTIVE SUMMARY

This report traces the 6 short screams through each step of the detection pipeline:
1. Audio ingestion & ring-buffer window extraction.
2. Pre-screener acoustic gating.
3. Feature extraction (temporal phonation, modulation, resonance profile).
4. Individual model evaluation (Model C 1D-CNN, Candidate G, Model E).
5. Asymmetric Confidence Fusion E.
6. Event persistence state machine & debounce.

---

## 2. MODEL COMPARISON ON MISSED SHORT SCREAMS

| Recording ID | Dur (s) | Pre-Screen | Model C (1D-CNN) | Cand G (Mod) | Model E (Multi) | Fusion E | Decision (>=0.35) |
|---|---|---|---|---|---|---|---|
| `S8930_FS_686340` | 0.3947 | PreScreeningResult(passed=True, rms_dbfs=-10.810380935668945, noise_floor_dbfs=-90.0, snr_estimate_db=60.58934783935547, spectral_flux=0.018188808113336563, spectral_centroid_hz=830.5597252418125, zcr=0.0498108853131611, high_band_ratio=0.35566285252571106, processing_time_ms=1.5759000089019537, rejection_reason='') | 0.0258 | 0.2775 | 0.2170 | 0.2882 | **False** (AMBIGUOUS_VOCALIZATION) |
| `S8930_FS_222582` | 0.7185 | PreScreeningResult(passed=True, rms_dbfs=-15.00668716430664, noise_floor_dbfs=-90.0, snr_estimate_db=58.85548782348633, spectral_flux=0.004413314629346132, spectral_centroid_hz=533.9629152826244, zcr=0.04583627155586897, high_band_ratio=0.06986993551254272, processing_time_ms=1.4091000193729997, rejection_reason='') | 0.0001 | 0.5008 | 0.0302 | 0.2809 | **False** (AMBIGUOUS_VOCALIZATION) |
| `S8930_FS_382990` | 0.4210 | PreScreeningResult(passed=True, rms_dbfs=-15.101917266845703, noise_floor_dbfs=-90.0, snr_estimate_db=58.000343322753906, spectral_flux=0.011120940558612347, spectral_centroid_hz=1041.863240846168, zcr=0.08795435604846465, high_band_ratio=0.8274837732315063, processing_time_ms=1.070300000719726, rejection_reason='') | 0.0045 | 0.3691 | 0.0773 | 0.2594 | **False** (AMBIGUOUS_VOCALIZATION) |
| `S8930_FS_547188` | 0.7659 | PreScreeningResult(passed=True, rms_dbfs=-18.874832153320312, noise_floor_dbfs=-90.0, snr_estimate_db=51.1194953918457, spectral_flux=0.0013062995858490467, spectral_centroid_hz=1307.312055805431, zcr=0.13603436117699852, high_band_ratio=0.676191508769989, processing_time_ms=0.8431000169366598, rejection_reason='') | 0.0599 | 0.4009 | 0.2197 | 0.3381 | **False** (AMBIGUOUS_VOCALIZATION) |
| `S8930_FS_788867` | 0.6502 | PreScreeningResult(passed=True, rms_dbfs=-14.046158790588379, noise_floor_dbfs=-90.0, snr_estimate_db=58.433773040771484, spectral_flux=0.004411877132952213, spectral_centroid_hz=1061.5038644306126, zcr=0.0687864606705558, high_band_ratio=0.14075367152690887, processing_time_ms=0.8671999676153064, rejection_reason='') | 0.9563 | 0.3725 | 0.5468 | 0.7578 | **True** (POSSIBLE_SCREAM) |
| `S8930_NIGENS_HUMAN-SCREAM_GEN-HDF-15246` | 0.4993 | PreScreeningResult(passed=True, rms_dbfs=-15.774916648864746, noise_floor_dbfs=-90.0, snr_estimate_db=56.99782943725586, spectral_flux=0.005027127452194691, spectral_centroid_hz=1455.4029846483054, zcr=0.14763766908135137, high_band_ratio=0.9997446537017822, processing_time_ms=0.8849999867379665, rejection_reason='') | 0.0476 | 0.3725 | 0.0925 | 0.2808 | **False** (AMBIGUOUS_VOCALIZATION) |

---

## 3. PIPELINE TRACE & FIRST STAGE OF FAILURE

| Recording ID | Duration | Ingest Windows (Unpadded) | Ingest Windows (Padded) | First Stage Where Evidence Lost | Root Cause Diagnosis |
|---|---|---|---|---|---|
| `S8930_FS_686340` | 0.3947 s | 0 | 1 | `RING_BUFFER_ACCUMULATION (Audio < 15600 samples)` | Audio is 0.395s. MultiStreamInferenceManager requires 0.975s (15600 samples) before releasing a window. In Stage 8.9.30 evaluation, audio was fed unpadded and yielded 0 windows -> defaulted to max_score=0.0. |
| `S8930_FS_222582` | 0.7185 s | 0 | 1 | `RING_BUFFER_ACCUMULATION (Audio < 15600 samples)` | Audio is 0.719s. MultiStreamInferenceManager requires 0.975s (15600 samples) before releasing a window. In Stage 8.9.30 evaluation, audio was fed unpadded and yielded 0 windows -> defaulted to max_score=0.0. |
| `S8930_FS_382990` | 0.4210 s | 0 | 1 | `RING_BUFFER_ACCUMULATION (Audio < 15600 samples)` | Audio is 0.421s. MultiStreamInferenceManager requires 0.975s (15600 samples) before releasing a window. In Stage 8.9.30 evaluation, audio was fed unpadded and yielded 0 windows -> defaulted to max_score=0.0. |
| `S8930_FS_547188` | 0.7659 s | 0 | 1 | `RING_BUFFER_ACCUMULATION (Audio < 15600 samples)` | Audio is 0.766s. MultiStreamInferenceManager requires 0.975s (15600 samples) before releasing a window. In Stage 8.9.30 evaluation, audio was fed unpadded and yielded 0 windows -> defaulted to max_score=0.0. |
| `S8930_FS_788867` | 0.6502 s | 0 | 1 | `RING_BUFFER_ACCUMULATION (Audio < 15600 samples)` | Audio is 0.650s. MultiStreamInferenceManager requires 0.975s (15600 samples) before releasing a window. In Stage 8.9.30 evaluation, audio was fed unpadded and yielded 0 windows -> defaulted to max_score=0.0. |
| `S8930_NIGENS_HUMAN-SCREAM_GEN-HDF-15246` | 0.4993 s | 0 | 1 | `RING_BUFFER_ACCUMULATION (Audio < 15600 samples)` | Audio is 0.499s. MultiStreamInferenceManager requires 0.975s (15600 samples) before releasing a window. In Stage 8.9.30 evaluation, audio was fed unpadded and yielded 0 windows -> defaulted to max_score=0.0. |

---

## 4. PERSISTENCE STATE MACHINE BEHAVIOR

The production system requires alert persistence to suppress transient impulsive false alarms (e.g., mic bumps, door slams):
- **Onset Debounce:** Requires $N \ge 1$ consecutive positive windows.
- **Cooldown / Hangover:** Maintains active state for 3 windows ($750\text{{ ms}}$) following an alert.

### Forensic Finding on Persistence:
- For `S8930_FS_788867` (the scream that achieved 0.7578 when padded), the event state machine **immediately emitted a `ScreamAlertEvent`** on window 0.
- Persistence did **not** suppress this event.
- For the remaining 5 screams, the failure occurred *before* the state machine:
  - In Stage 8.9.30: Occurred at the ring-buffer ingestion stage (zero windows passed to state machine).
  - In padded offline evaluation: Fused scores were marginally below 0.3500 ($0.259 - 0.338$).

---

## 5. ASYMMETRIC FUSION BEHAVIOR

In Stage 8.9.26, Asymmetric Confidence Fusion E was designed to balance fast 1D-CNN detections with Candidate G envelope modulation verification:
- When Model C produces high confidence ($> 0.60$), Fusion E trusts it.
- When Model C is moderate ($0.30 - 0.50$), Fusion E requires Candidate G confirmation.
- On short screams with silence padding:
  - Candidate G correctly detected modulation on `S8930_FS_547188` ($0.4009$).
  - However, Model C produced $0.2882$, which pulled the fused score down to $0.3381$ (missing the $0.3500$ threshold by just $0.0119$).
- **Conclusion:** Asymmetric fusion slightly penalizes short padded screams because Model C's temporal convolution sees silence padding, depressing its score.
