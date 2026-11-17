# Stage 8.9.35 — Spatial Audio Simulation Report (Track B)

**Stage:** 8.9.35 — Spatial Audio Research & Multi-Pathway Fusion  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Hardware Status:** SINGLE INMP441 OMNIDIRECTIONAL MICROPHONE (MONOPHONIC)  
**Corpus Status:** 100% MONOPHONIC (1,328 / 1,328 recordings have Channel Count = 1)  
**Evaluation Designation:** SYNTHETIC_SIMULATION_ONLY — NOT EVALUABLE ON PHYSICAL MULTICHANNEL DATA  
**Artifact Reference:** `backend/research/stage_8_9_35/spatial_analysis/spatial_experiment_results.csv`  

---

## 1. Physical Hardware and Data Constraints

As established in the Stage 8.9.35 Checkpoint 1 audit:
1. **Physical Hardware Limitation:** The documented edge device utilizes a single INMP441 omnidirectional I2S MEMS microphone. Single-microphone hardware cannot capture phase, time-of-arrival, or level differences. Physical beamforming is physically impossible on this hardware without upgrading to a physical multi-microphone array ($N \ge 2$).
2. **Corpus Channel Limitation:** 100% of all 1,328 audio files across training, validation, and test partitions are monophonic (1 channel, 16 kHz).
3. **Audit Rule Enforcement:** No physical spatial evaluation could be performed on the independent held-out test cohort. Under strict scientific protocol, physical spatial performance on the empirical cohort is classified as **NOT EVALUABLE**.

---

## 2. Track B: Controlled Spatial Simulation Methodology

To explore the theoretical performance bounds of an array upgrade, a controlled physics-based simulation was implemented:

- **Array Geometry:** 2-element uniform linear array (ULA) with inter-microphone spacing $d = 0.05\text{ m}$ (50 mm), corresponding to a half-wavelength spatial aliasing limit of $f_{\text{alias}} = \frac{c}{2d} = \frac{343}{0.10} = 3,430\text{ Hz}$.
- **Acoustic Environment:** Free-field planar wave propagation ($c = 343\text{ m/s}$), target scream source at azimuth $\theta_{\text{target}} \in [-60^\circ, +60^\circ]$.
- **Acoustic Interferers:** Competing shouted speech at $\theta_{\text{comp}} = -45^\circ$, diffuse crowd cheering background noise uncorrelated across channels.
- **Signal-to-Noise Ratios:** Evaluated across four controlled SNR regimes: $+10\text{ dB}$, $+5\text{ dB}$, $0\text{ dB}$, and $-5\text{ dB}$.
- **Algorithms:**
  - **TDoA / DOA Estimation:** Generalized Cross-Correlation with Phase Transform (GCC-PHAT):
    $$\hat{\tau} = \arg\max_{\tau} \int_{-\infty}^{\infty} \frac{X_1(f) X_2^*(f)}{|X_1(f) X_2^*(f)|} e^{j 2 \pi f \tau} df$$
    $$\hat{\theta} = \arcsin\left(\frac{c \hat{\tau}}{d}\right)$$
  - **Spatial Filtering:** Frequency-domain Delay-and-Sum (DAS) beamforming steered to estimated DOA $\hat{\theta}$.

---

## 3. Empirical Simulation Findings

Across 200 Monte Carlo simulation trials per SNR regime, the following metrics were recorded:

| Input SNR | Target DOA Error (Mean) | Target DOA Error (P95) | Post-Beamforming SNR Gain | Detection Recall (Simulated Target) | False Steering Attenuation Risk |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **+10 dB** | $12.3^\circ$ | $24.1^\circ$ | **+2.7 dB** | 94.0% | 1.2% |
| **+5 dB** | $18.7^\circ$ | $35.6^\circ$ | **+2.5 dB** | 91.5% | 4.5% |
| **0 dB** | $26.4^\circ$ | $51.2^\circ$ | **+2.3 dB** | 87.0% | 11.0% |
| **-5 dB** | $41.8^\circ$ | $72.5^\circ$ | **+2.1 dB** | 78.5% | **22.5%** |

---

## 4. Critical Scientific Conclusions & Cautions

1. **Theoretical SNR Benefits:**
   - Under moderate noise conditions ($>0\text{ dB}$ SNR), a 2-element array provides $+2.3\text{ dB}$ to $+2.7\text{ dB}$ of coherent signal enhancement, improving the detectability of distant screams.
2. **The False-Steering Target Suppression Hazard:**
   - In low-SNR conditions ($-5\text{ dB}$), diffuse crowd babble and competing shouts degrade GCC-PHAT phase stability, causing large DOA estimation errors (mean $41.8^\circ$, P95 $72.5^\circ$).
   - When the beamformer steers to an erroneous direction, Delay-and-Sum beamforming places the actual scream into an acoustic spatial null, attenuating the genuine target by $-1.8\text{ dB}$ to $-3.4\text{ dB}$. This occurred in **22.5%** of low-SNR trials.
   - **Protection Rule:** In any future hardware deployment, spatial beamforming must never be used as a hard pre-filter that suppresses unsteered energy unless DOA confidence exceeds a validated threshold.
3. **Non-Deployable Status:**
   - These simulation results reflect an idealized free-field model without room reverberation, multipath reflections, or microphone casing diffraction. They are **RESEARCH SIMULATIONS ONLY** and must not be used as proof of field readiness.
