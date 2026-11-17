# AudioSet Source Assessment & Legal Usability Report

**Project:** AI-Powered Festival Scream Detection System (`festival-scream-detector`)  
**Date:** October 24, 2026  
**Author:** Senior Machine Learning & Audio Data Licensing Specialist  
**Deliverable:** Stage 8.7 — Existing Dataset Coverage Audit and AudioSet Source Investigation  

---

> [!IMPORTANT]
> **EXECUTIVE LEGAL & ARCHITECTURAL SUMMARY**  
> Google’s AudioSet **DOES NOT DISTRIBUTE RAW PLAYABLE AUDIO (WAV/MP3)**. It distributes only metadata (YouTube video IDs, timestamp offsets, and class labels) and precomputed 128-dimensional VGGish feature vectors.  
> 
> Acquiring playable audio requires scraping YouTube, which introduces severe link rot (~35–45% of videos from 2017 are permanently deleted), violates YouTube Terms of Service Section 5.B without a download license, and carries third-party copyright claims. Any commercial or field deployment of models trained on scraped YouTube audio is legally high-risk and **REQUIRES LEGAL REVIEW**.  
> 
> By contrast, **Freesound.org** (via Stage 6) and **Local Microphone Capture** (via Stage 8.6) provide direct, high-fidelity, legally permissive (CC0, CC BY, or operator-consented) WAV recordings with zero YouTube dependency.

---

## 1. What Google AudioSet Actually Distributes

Google Research released AudioSet in 2017 as a foundational benchmark for audio event research. The official distribution endpoints ([AudioSet Download Page](https://research.google.com/audioset/download.html)) contain exclusively the following assets:

| Asset Name | Format | Content | Playable Audio Included? | License |
| :--- | :--- | :--- | :---: | :--- |
| **`ontology.json`** | JSON | 632 audio classes organized in a directed acyclic graph (MID, name, description, children) | **NO** | CC BY 4.0 |
| **`balanced_train_segments.csv`** | CSV | ~22,176 segments (~10 per class) with YouTube ID (`YTID`), start time, end time, and labels | **NO** | CC BY 4.0 |
| **`eval_segments.csv`** | CSV | ~20,371 segments for held-out evaluation | **NO** | CC BY 4.0 |
| **`unbalanced_train_segments.csv`** | CSV | ~2,042,985 segment entries across all 632 classes | **NO** | CC BY 4.0 |
| **Precomputed Audio Features** | TFRecord | Pre-extracted 128-dimensional VGGish embeddings per 1-second segment | **NO** (Embeddings only) | CC BY 4.0 |

```
Google AudioSet Release:
[YouTube IDs & Timestamps] + [128-dim VGGish Embeddings] ---> NO WAV FILES DISTRIBUTED!
                                                                  |
                                                                  v
                                      Must Scrape YouTube (High Risk & Degraded)
```

### Critical Technical Distinction: Precomputed Features vs. Our Pipeline
- AudioSet's precomputed feature files contain **128-dimensional VGGish features** trained on YouTube-8M.
- Our scream detection pipeline uses **Google YAMNet**, which produces **1,024-dimensional embeddings** from 16 kHz raw waveforms.
- Therefore, AudioSet’s precomputed TFRecord embeddings **cannot be directly fed into our Stage 5 Logistic Regression classifier** (which strictly expects 1,024-dimensional max-pooled YAMNet vectors). Playable 16 kHz audio would be required to extract YAMNet embeddings.

---

## 2. Technical Hurdles & Availability Degradation (Link Rot)

If a team attempts to reconstruct raw audio from AudioSet metadata, the following engineering blockers arise:

1. **Severe Link Rot (~35% to 45% Missing Audio):**  
   Because AudioSet was indexed in 2017, empirical evaluations across the MIR (Music Information Retrieval) and DCASE research communities show that between 35% and 45% of the original YouTube videos are now gone:
   - Videos deleted by original uploaders.
   - Channels terminated or banned for copyright violations.
   - Videos set to "Private" or "Unlisted".
   - Geographic blocking and regional restrictions.
   - Any collection pipeline attempting to download AudioSet in 2026 will fail on over a third of candidate clips.
2. **YouTube Anti-Scraping Defenses & Tooling Breakage:**  
   Downloading audio using tools such as `yt-dlp` or `youtube-dl` triggers YouTube rate-limiting, IP throttling, and Cloudflare/reCAPTCHA bot defenses. Maintaining an automated scraping pipeline requires proxy rotation and constant maintenance.
3. **Severe Multi-Label Acoustic Contamination:**  
   YouTube videos are unconstrained, naturalistic uploads. An AudioSet segment labeled "Whistle" or "Cheering" almost always contains loud background commercial music, shouting vloggers, wind rumble, and heavy Opus/AAC lossy compression artifacts. This makes single-label hard-negative isolation noisy and unreliable without intensive human manual cleaning.

---

## 3. Legal and Licensing Audit

| Dimension | AudioSet Metadata Asset | Underlying YouTube Audio Recordings |
| :--- | :--- | :--- |
| **Asset Type** | CSV files and JSON ontology | Actual audiovisual streams hosted on YouTube |
| **Governing License** | Creative Commons Attribution 4.0 (`CC BY 4.0`) | Third-Party Uploader Copyright (Standard YouTube License) |
| **Redistribution Rights** | Permitted with attribution | **PROHIBITED** without explicit creator authorization |
| **Commercial Exploitation** | Permitted for metadata | **UNRESOLVED / REQUIRES LEGAL REVIEW** |
| **Terms of Service Compliance** | Compliant | **POTENTIAL VIOLATION** of YouTube ToS Section 5.B |

### Detailed Legal Findings
1. **Metadata vs. Content Separation:**  
   Google’s `CC BY 4.0` license applies *strictly to the annotation files created by Google researchers*. Google does not hold, grant, or sublicense rights to the underlying YouTube videos.
2. **YouTube Terms of Service:**  
   YouTube’s Terms of Service state:
   > *"You shall not download any Content unless you see a 'download' or similar link displayed by YouTube on the Service for that Content."*  
   Automated scraping of thousands of clips using headless extractors violates YouTube’s terms of use.
3. **Commercial Deployment Risk:**  
   If our festival scream detector is deployed commercially (e.g. licensed to event organizers, security providers, or festival venues), incorporating audio scraped from YouTube uploaders without commercial licensing creates copyright liability.  
   **Legal Status:** **REQUIRES LEGAL REVIEW**.

---

## 4. Alternative Lawful Audio Sources Comparison

| Acoustic Sound Source | Playable Audio Available? | Licensing Clarity | Festival Acoustic Relevance | Acquisition Friction | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Google AudioSet (YouTube)** | **NO** (Metadata only) | **REQUIRES LEGAL REVIEW** (Third-party YouTube copyright) | Moderate (Noisy, multi-label) | Very High (Link rot, IP throttling) | **REJECT for bulk downloads** |
| **Freesound.org (Stage 6)** | **YES** (Direct WAV/FLAC) | **PERMISSIVE** (CC0, CC BY with author attribution) | High (Clean isolated sound events) | Low (Direct REST API / batch download) | **PRIMARY RECOMMENDED EXTERNAL SOURCE** |
| **Stage 8.6 Local Mic Capture** | **YES** (Direct 16kHz WAV) | **PERMISSIVE** (Consented operator/participants) | Maximum (Target microphone & hardware) | Zero (Built-in script ready) | **PRIMARY RECOMMENDED DOMESTIC SOURCE** |
| **Royalty-Free Music Stems** | **YES** (Direct WAV) | **PERMISSIVE** (Commercial license / CC0) | High (EDM drops, synth risers) | Low (Curated music asset libraries) | **RECOMMENDED FOR EDM & SYNTHS** |

---

## 5. Candidate AudioSet Categories Shortlist (For Reference Only)

If specific AudioSet categories are ever investigated for reference or targeted lawful retrieval, the following MIDs represent our critical hard-negative gaps:

| AudioSet Class Name | Machine ID (`mid`) | YAMNet Index | Primary Acoustic Gap Addressed |
| :--- | :--- | :---: | :--- |
| **Whistle** | `/m/0l156k` | 396 | Rave whistles, slide whistles (Stage 5 FP remediation) |
| **Cheering** | `/m/053hz1` | 61 | Crowd cheering at festival stage climaxes |
| **Applause** | `/m/028ght` | 62 | Stadium clapping and audience appreciation |
| **Crowd** | `/m/03qtwd` | 64 | General festival audience murmur and roar |
| **Synthesizer** | `/m/0l14qv` | 153 | Sawtooth leads and frequency-modulated EDM risers |
| **Electronic Music** | `/m/02lkt` | — | General electronic festival music backdrop |
| **Squeak** | `/m/07q6cd_` | 355 | Squeaky toys (Stage 5 FP remediation) |
| **Shout** | `/m/07p6fty` | 6 | Human vocal shouting over loud music |
| **Yell** | `/m/07sr1lc` | 9 | Excited non-distress crowd vocalizations |
| **Baby cry, infant cry** | `/t/dd00002` | 20 | High-intensity infant crying (Stage 5 FP remediation) |
| **Fireworks** | `/m/0g6b5` | 426 | Stage pyrotechnics and aerial whistling fireworks |
| **Wind noise (microphone)**| `/t/dd00092` | 279 | Outdoor microphone capsule wind turbulence |

---

## 6. Recommended Lawful Acquisition Procedure

Rather than attempting mass scraping of AudioSet, the project should adhere to the following lawful three-tier acquisition policy:

1. **Tier 1 (Zero-Risk Local Capture):**  
   Use Stage 8.6 [`record_evaluation_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/record_evaluation_audio.py) to capture physical whistles, party horns, squeaky toys, fan wind noise, and consented human shouting directly on target laptop/embedded hardware.
2. **Tier 2 (Permissive Creative Commons Audio via Freesound):**  
   Curate 25–50 specific recordings from Freesound.org carrying explicit `CC0 1.0` (Public Domain) or `CC BY 4.0` (Attribution) licenses for EDM risers, cheering crowds, and fireworks. Feed these into the existing Stage 6 [`ingest_hard_negatives.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/ingest_hard_negatives.py) pipeline.
3. **Tier 3 (AudioSet Contingency Protocol):**  
   If an acoustic category cannot be sourced via Tier 1 or Tier 2, identify specific Creative Commons licensed YouTube videos from AudioSet segment lists, manually verify CC BY licensing on YouTube, extract only the designated 10-second window, and document creator attribution in sidecar metadata.
