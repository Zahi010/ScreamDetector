# STAGE 8.9.31 — END-OF-STREAM BUFFER & FLUSH POLICY SPECIFICATION

**Project:** Festival Scream Detector  
**Stage:** 8.9.31  
**Document:** End-of-Stream Buffer Flush & Ingestion Lifecycle Policy  
**Production Status:** STRICTLY FROZEN (Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. PURPOSE AND MOTIVATION

Stage 8.9.30.2 demonstrated that the original streaming evaluation harness suffered from an unhandled buffer underflow defect:
- The streaming manager accumulated audio in an unpadded 15,600-sample (0.975s) circular buffer.
- When an entire audio file shorter than 15,600 samples was submitted, zero complete windows were generated.
- The evaluation harness silently discarded the residual audio and reported `max_score = 0.0`.
- As a consequence, all 6 genuine short screams were reported as 0/6 detected without ever executing the model.

This policy establishes an explicit, deterministic end-of-stream ingestion and flush protocol.

---

## 2. POLICY PRINCIPLES

### 2.1 The Minimum Valid Audio Requirement
Audio events shorter than 200 ms (3,200 samples at 16 kHz) contain insufficient acoustic information for stable phonation or modulation classification:
- **Duration < 200 ms:** Classified as `INSUFFICIENT_AUDIO`. The buffer clears residual samples upon flush without extracting an artificial window.
- **Duration >= 200 ms and < 975 ms:** Classified as `VALID_SHORT_RECORDING`. The buffer flushes the residual audio, pads rightward with zeros to 15,600 samples, and produces an explicit `PADDED_END_OF_STREAM_WINDOW`.

### 2.2 Sample Provenance & Metadata Transparency
Every generated window is tagged with exact metadata:
- `valid_samples`: Count of real input audio samples ($N_{valid}$).
- `padded_samples`: Count of synthetic zero samples added ($N_{padded}$).
- `padding_fraction`: $N_{padded} / N_{window}$.
- `is_end_of_stream`: Boolean flag indicating whether this window was produced via `flush()`.

### 2.3 Idempotence and Stream Lifecycle
1. **Flush Idempotence:** Subsequent calls to `flush()` on an already flushed stream return an empty list (`[]`).
2. **Rejection After Flush:** Ingesting audio into a flushed stream raises a `RuntimeError` to prevent silent corruption.
3. **Explicit Reset:** Calling `reset()` clears all state, zeroes memory, and restores the buffer to ingestion readiness.
