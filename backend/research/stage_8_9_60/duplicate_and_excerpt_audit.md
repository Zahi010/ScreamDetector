# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Duplicate & Excerpt Audit: Near-Duplicate Detection and Lineage Tracking

## 1. Audit Rationale & Multi-Crop Detection

In large-scale sound repositories like Freesound and FSD50K, multiple sound clips frequently originate from a single continuous audio recording:
- Users crop a 2-minute field recording into three 5-second events.
- Re-encoding or resampling can yield different file hashes despite identical acoustic content.
- If one cropped clip appears in training while a sister clip appears in testing, the model can memorize background noise signatures (reverberation room impulse responses, ambient hum), producing artificially inflated generalization metrics.

To prevent this subtle data contamination, Stage 8.9.60 implemented a comprehensive duplicate and excerpt tracking protocol.

---

## 2. Duplicate Detection Results

The duplicate detection script `backend/research/stage_8_9_60/scripts/detect_audio_duplicates.py` audited all 962 acquired recordings:

| Duplicate Verification Level | Tested Entities | Duplicates Detected | Status |
| :--- | :---: | :---: | :---: |
| **Internal File SHA-256 Digest** | 962 acquired clips | **0** | **CLEAN** |
| **Internal Raw PCM SHA-256 Digest** | 962 acquired clips | **0** | **CLEAN** |
| **Historical File Hash Collisions** | vs 2,213 registry entries | **0** | **CLEAN** |
| **Historical PCM Hash Collisions** | vs 2,213 registry entries | **0** | **CLEAN** |
| **Parent Lineage Tracking** | 962 acquired clips | **117 Multi-crop Parents** | **DOCUMENTED** |

The summary status is certified as `CLEAN_ZERO_LEAKAGE` in `backend/research/stage_8_9_60/duplicate_audit_summary.json`.

---

## 3. Excerpt Lineage and Parent-Child Mapping

Of the 962 acquired recordings, **117 parent recordings** contributed more than one extracted window or event:
- All parent-child relationships, time offsets (`start_time_seconds`, `end_time_seconds`), and parent file IDs were extracted and cataloged in `backend/research/stage_8_9_60/duplicate_and_excerpt_relationships.csv`.
- **Confinement Invariant:** Every sister clip extracted from a parent recording is assigned to the exact same `source_group_id`.
- **Partition Policy:** When assembling cohorts or splits, all clips sharing a `source_group_id` are treated as an indivisible cluster. If one clip is assigned to a sealed test set, all sister excerpts are either co-located in that test set or excluded entirely from any training corpus.

---

## 4. Near-Duplicate Acoustic Energy Audit

Acoustic energy profiles across recordings from identical creators were inspected for near-identical waveforms:
- Cross-correlation analysis on downsampled 16 kHz mono waveforms showed zero unflagged near-duplicate clips.
- All clips exhibiting cross-correlation > 0.90 were confirmed to be explicitly tracked sister excerpts with shared source group IDs.

Pytest validation (`test_08_recording_id_uniqueness`, `test_09_audio_sha256_uniqueness`, `test_10_pcm_duplicate_detection`, `test_11_near_duplicate_audit`, `test_12_excerpt_parent_relationships`) confirms that excerpt confinement and duplicate elimination are 100% verified.

