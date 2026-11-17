# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.63 — Short-Scream Dual-Reviewer Annotation Protocol

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Protocol Purpose & Scope

This protocol establishes the standardized, blinded multi-reviewer methodology for annotating short transient scream vocalizations ($< 1.0$s duration) acquired in Stage 8.9.63.

All acquired audio recordings are reviewed independently by two blinded acoustic annotators without knowledge of model predictions, candidate outputs, or prior benchmark results.

---

## 2. Standardized Annotation Schema

For every candidate audio clip, annotators record the following primary attributes:

1. **Temporal Boundaries:**
   - `event_onset_timestamp`: High-precision timestamp (seconds, to millisecond precision) where acoustic vocal energy exceeds ambient background noise.
   - `event_offset_timestamp`: High-precision timestamp where phonation/vocal fold vibration ceases or drops below ambient noise floor.
   - `event_duration`: Calculated as $\Delta t = \text{offset} - \text{onset}$.
2. **Vocal Event Typology (Categorical):**
   - `distress_scream`: Authentic distress, pain, or danger shriek with rough phonation, non-linear vocal bifurcations, or high-pitch subharmonics.
   - `panic_shriek`: High-frequency sudden burst of panic or shock vocalization.
   - `sudden_startle`: Brief reflexive scare reaction vocalization.
   - `vocal_outcry`: General high-energy emotional exclamation.
3. **Acoustic Environment & Channel Quality:**
   - `intensity_level`: `High` (unconstrained vocal effort), `Medium` (moderate effort), `Low` (stifled, distant, or quiet).
   - `channel_condition`: `Clean` (near-field recording), `Reverberant` (indoor reflections), `Crowd_Masked` (ambient babble), `Noisy` (traffic/machinery).
   - `audibility_status`: Boolean indicator of whether the vocal burst is perceptually audible to human ears without digital amplification.
4. **Subjective Confidence:**
   - Continuous confidence score $\in [0.50, 1.00]$ assigned by the reviewer.

---

## 3. Adjudication & Consensus Rules

- **Temporal Disagreement Threshold:**
  - If $|\text{onset}_1 - \text{onset}_2| \le 50$ ms and $|\text{offset}_1 - \text{offset}_2| \le 75$ ms: Boundaries are averaged to form the consensus span.
  - If temporal boundary disagreement exceeds these thresholds: The file is flagged for waveform-level spectrogram adjudication.
- **Categorical Typology Disagreement:**
  - If categorical labels match: Classified as `CONSENSUS_AGREED`.
  - If categorical labels diverge: A third senior adjudicator reviews the recording and establishes the binding ground truth.
- **Zero Prediction-Driven Labeling:**
  - In strict compliance with research governance, zero automated labels from neural network models or heuristic detectors were used during the annotation process.

