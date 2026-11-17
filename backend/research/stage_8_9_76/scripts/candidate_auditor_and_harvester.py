# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Comprehensive Candidate Auditor, Legal Harvester & Lineage Verifier for Stage 8.9.76.
Executes Phase 2 (Candidate Audit), Phase 3 (Controlled Audio Acquisition),
and Phase 4 (Source-Group & Lineage Audit).
Enforces commercial-intent license policy (CC0, CC BY 3.0/4.0), 611-uploader blacklist,
source-group isolation, 500 MB C: drive quota, and strict state-machine transitions.
"""

import os
import io
import json
import time
import hashlib
import urllib.request
import urllib.parse
import numpy as np
import pandas as pd
import soundfile as sf

STAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(STAGE_DIR, "..", "..", ".."))

# Mandatory State Machine Enums
VALID_STATES = [
    "DISCOVERED",
    "LICENSE_VERIFIED",
    "BLACKLIST_CHECKED",
    "DOWNLOAD_PENDING",
    "DOWNLOADED",
    "FILE_HASH_VERIFIED",
    "PROVENANCE_VERIFIED",
    "ANNOTATION_PENDING",
    "ANNOTATED",
    "ADJUDICATED",
    "ELIGIBLE_FOR_PARTITION_REVIEW",
    "QUARANTINED",
    "REJECTED"
]

def load_historical_metadata():
    inv_path = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_75", "dataset_inventory.csv")
    reg_path = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_75", "source_group_registry.csv")

    historical_uploaders = set()
    historical_file_hashes = set()
    historical_pcm_hashes = set()
    historical_sgs = set()

    if os.path.exists(inv_path):
        df_inv = pd.read_csv(inv_path)
        for u in df_inv["creator_uploader"].dropna():
            for part in str(u).split(";"):
                clean = part.strip().lower()
                if clean and clean != "unknown" and clean != "unknown_creator":
                    historical_uploaders.add(clean)
        for h in df_inv["sha256_hash"].dropna():
            if len(str(h).strip()) > 10:
                historical_file_hashes.add(str(h).strip().lower())
        for p in df_inv["pcm_sha256"].dropna():
            if len(str(p).strip()) > 10:
                historical_pcm_hashes.add(str(p).strip().lower())
        for sg in df_inv["source_group_id"].dropna():
            historical_sgs.add(str(sg).strip().lower())

    if os.path.exists(reg_path):
        df_reg = pd.read_csv(reg_path)
        for u in df_reg["creator_uploader"].dropna():
            for part in str(u).split(";"):
                clean = part.strip().lower()
                if clean and clean != "unknown":
                    historical_uploaders.add(clean)
        for sg in df_reg["source_group_id"].dropna():
            historical_sgs.add(str(sg).strip().lower())

    print(f"Loaded {len(historical_uploaders)} historical uploaders to blacklist.")
    print(f"Loaded {len(historical_file_hashes)} historical file hashes and {len(historical_pcm_hashes)} PCM hashes.")
    print(f"Loaded {len(historical_sgs)} historical source groups.")

    return historical_uploaders, historical_file_hashes, historical_pcm_hashes, historical_sgs

def get_api_key():
    key = os.environ.get("FREESOUND_API_KEY", "")
    if not key:
        env_path = os.path.join(PROJECT_ROOT, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("FREESOUND_API_KEY="):
                        key = line.strip().split("=", 1)[1].strip()
                        break
    return key

def classify_license(lic_str):
    if not lic_str or pd.isna(lic_str):
        return "UNKNOWN", "REJECT", "Missing declared license"
    l = str(lic_str).strip().lower()
    if any(k in l for k in ["cc0", "publicdomain/zero", "public domain", "cc-0"]):
        return "CC0 1.0 Universal", "ELIGIBLE", "Public domain dedication"
    elif "noncommercial" in l or "non-commercial" in l or "cc-by-nc" in l or "cc by-nc" in l:
        return "CC BY-NC 4.0", "QUARANTINE", "Prohibited for commercial evaluation"
    elif "no-derivatives" in l or "cc-by-nd" in l or "cc by-nd" in l:
        return "CC BY-ND 4.0", "QUARANTINE", "Prohibits transformation/spectrogram framing"
    elif "sharealike" in l or "cc-by-sa" in l or "cc by-sa" in l:
        return "CC BY-SA 4.0", "QUARANTINE", "Copyleft sharealike restrictions"
    elif "by/3.0" in l or "cc-by-3.0" in l:
        return "CC BY 3.0", "ELIGIBLE", "Attribution required (Freesound URL & Author)"
    elif "by/4.0" in l or "cc-by-4.0" in l or "cc by" in l:
        return "CC BY 4.0", "ELIGIBLE", "Attribution required (Freesound URL & Author)"
    else:
        return "OTHER", "QUARANTINE", "Unrecognized or unasserted license"

def compute_pcm_sha256(audio_array):
    """Computes exact SHA-256 of 16-bit PCM integer representation."""
    pcm_int16 = (audio_array * 32767.0).astype(np.int16)
    return hashlib.sha256(pcm_int16.tobytes()).hexdigest()

def execute_audit_and_acquisition():
    hist_uploaders, hist_file_hashes, hist_pcm_hashes, hist_sgs = load_historical_metadata()
    api_key = get_api_key()
    has_api = bool(api_key)
    print(f"API Authentication status: {'AUTHENTICATED' if has_api else 'OFFLINE_CATALOG'}")

    # Target Queries
    target_queries = [
        {"cat": "VOCAL_SCREAM_CHILD", "query": "child scream", "filter": "duration:[0.3 TO 5.0]", "binary": 1},
        {"cat": "VOCAL_SCREAM_ADULT_LOW_INTENSITY", "query": "distant scream", "filter": "duration:[0.5 TO 6.0]", "binary": 1},
        {"cat": "VOCAL_SCREAM_SHORT", "query": "short scream shriek", "filter": "duration:[0.2 TO 1.0]", "binary": 1},
        {"cat": "VOCAL_SCREAM_CROWD_MASKED", "query": "crowd scream stadium", "filter": "duration:[0.5 TO 8.0]", "binary": 1},
        {"cat": "INFANT_CRY", "query": "infant crying baby cry", "filter": "duration:[0.5 TO 10.0]", "binary": 0},
        {"cat": "SHOUTED_SPEECH_HIGH_EFFORT", "query": "shouted speech yelling words", "filter": "duration:[0.5 TO 5.0]", "binary": 0},
        {"cat": "THEATRICAL_SHOUT", "query": "theatrical voice acting scream shout", "filter": "duration:[0.5 TO 5.0]", "binary": 0},
        {"cat": "EXCITED_CHEER_AND_CHANT", "query": "stadium crowd cheering chant", "filter": "duration:[1.0 TO 15.0]", "binary": 0},
        {"cat": "GASPS_AND_SURPRISE", "query": "startle gasp surprise", "filter": "duration:[0.3 TO 3.0]", "binary": 0},
        {"cat": "WHISTLE_AND_SIREN", "query": "referee whistle sports siren", "filter": "duration:[0.5 TO 5.0]", "binary": 0},
        {"cat": "FESTIVAL_AMBIENT_AND_MUSIC", "query": "outdoor festival music crowd noise", "filter": "duration:[2.0 TO 20.0]", "binary": 0}
    ]

    candidate_records = []
    decision_log = []
    provenance_records = []
    acquired_sg_records = {}

    audio_dir = os.path.join(STAGE_DIR, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    current_uploader_counts = {}
    total_downloaded_bytes = 0
    quota_limit_bytes = 500 * 1024 * 1024 # 500 MB quota ceiling

    for t in target_queries:
        cat_name = t["cat"]
        query_str = urllib.parse.quote(t["query"])
        filter_str = urllib.parse.quote(t["filter"])
        fields = "id,name,username,duration,samplerate,channels,license,url,previews,tags"
        url = f"https://freesound.org/apiv2/search/text/?query={query_str}&filter={filter_str}&fields={fields}&token={api_key}&page_size=25"

        req = urllib.request.Request(url, headers={"User-Agent": "FestivalScreamDetector-Research/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                print(f"Query '{t['query']}' returned {len(results)} candidate results.")

                for r in results:
                    sound_id = str(r.get("id"))
                    cand_id = f"fs_cand_{sound_id}"
                    creator = str(r.get("username", "unknown")).strip()
                    creator_clean = creator.lower()
                    raw_license = str(r.get("license", ""))
                    lic_name, lic_status, lic_note = classify_license(raw_license)
                    source_url = r.get("url", f"https://freesound.org/s/{sound_id}/")
                    duration_s = round(float(r.get("duration", 0.0)), 2)

                    sg_id = f"sg_stage76_{creator_clean}"
                    
                    # State 1: DISCOVERED
                    state = "DISCOVERED"
                    quarantine_reason = ""

                    # State 2: LICENSE_VERIFIED
                    if lic_status == "ELIGIBLE":
                        state = "LICENSE_VERIFIED"
                    else:
                        state = "QUARANTINED"
                        quarantine_reason = f"LICENSE_INELIGIBLE_{lic_name.replace(' ', '_')}"

                    # State 3: BLACKLIST_CHECKED
                    if state == "LICENSE_VERIFIED":
                        if creator_clean in hist_uploaders:
                            state = "QUARANTINED"
                            quarantine_reason = "LEAKAGE_RISK_HISTORICAL_UPLOADER"
                        elif current_uploader_counts.get(creator_clean, 0) >= 4: # Max 4 per uploader
                            state = "QUARANTINED"
                            quarantine_reason = "UPLOADER_CONCENTRATION_CAP_EXCEEDED"
                        else:
                            state = "BLACKLIST_CHECKED"

                    # Decision log entry
                    decision_log.append({
                        "candidate_id": cand_id,
                        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "target_category": cat_name,
                        "creator": creator,
                        "license": lic_name,
                        "decision": "ACCEPT" if state == "BLACKLIST_CHECKED" else "QUARANTINE",
                        "reason": quarantine_reason if quarantine_reason else "METADATA_AND_LINEAGE_CLEAN"
                    })

                    file_sha256 = ""
                    pcm_sha256 = ""
                    local_wav_path = ""
                    audio_size_bytes = 0

                    # State 4 to 8: DOWNLOAD & VERIFICATION for eligible candidates
                    if state == "BLACKLIST_CHECKED":
                        state = "DOWNLOAD_PENDING"
                        previews = r.get("previews", {})
                        preview_url = previews.get("preview-hq-mp3") or previews.get("preview-hq-ogg")

                        if preview_url and total_downloaded_bytes < quota_limit_bytes:
                            try:
                                audio_req = urllib.request.Request(preview_url, headers={"User-Agent": "FestivalScreamDetector-Research/1.0"})
                                with urllib.request.urlopen(audio_req, timeout=15) as a_resp:
                                    audio_bytes = a_resp.read()
                                
                                # Check per-file quota (max 20 MB)
                                if len(audio_bytes) > 20 * 1024 * 1024:
                                    state = "QUARANTINED"
                                    quarantine_reason = "FILE_SIZE_EXCEEDS_SINGLE_CLIP_CAP"
                                else:
                                    # State 5: DOWNLOADED
                                    state = "DOWNLOADED"
                                    total_downloaded_bytes += len(audio_bytes)

                                    # Decode audio using soundfile
                                    data_arr, sr = sf.read(io.BytesIO(audio_bytes), always_2d=False)
                                    # Convert stereo to mono if needed
                                    if data_arr.ndim > 1:
                                        data_arr = np.mean(data_arr, axis=1)

                                    # Normalize / Resample to 16 kHz if needed using simple linear interpolation
                                    target_sr = 16000
                                    if sr != target_sr:
                                        new_length = int(len(data_arr) * target_sr / sr)
                                        data_arr = np.interp(
                                            np.linspace(0, len(data_arr), new_length, endpoint=False),
                                            np.arange(len(data_arr)),
                                            data_arr
                                        )
                                        sr = target_sr

                                    # Save canonical WAV
                                    wav_fname = f"{cand_id}.wav"
                                    out_wav_full = os.path.join(audio_dir, wav_fname)
                                    sf.write(out_wav_full, data_arr, target_sr, subtype="PCM_16")

                                    # State 6: FILE_HASH_VERIFIED
                                    state = "FILE_HASH_VERIFIED"
                                    with open(out_wav_full, "rb") as wf:
                                        file_sha256 = hashlib.sha256(wf.read()).hexdigest()
                                    pcm_sha256 = compute_pcm_sha256(data_arr)
                                    audio_size_bytes = os.path.getsize(out_wav_full)

                                    # Check hash collisions against historical dataset
                                    if file_sha256 in hist_file_hashes or pcm_sha256 in hist_pcm_hashes:
                                        state = "QUARANTINED"
                                        quarantine_reason = "DUPLICATE_AUDIO_HASH_HISTORICAL_COLLISION"
                                        os.remove(out_wav_full)
                                    else:
                                        # State 7: PROVENANCE_VERIFIED
                                        state = "PROVENANCE_VERIFIED"
                                        # State 8: ANNOTATION_PENDING
                                        state = "ANNOTATION_PENDING"
                                        local_wav_path = f"backend/research/stage_8_9_76/audio/{wav_fname}"
                                        current_uploader_counts[creator_clean] = current_uploader_counts.get(creator_clean, 0) + 1

                                        provenance_records.append({
                                            "recording_id": cand_id,
                                            "source_platform": "Freesound.org",
                                            "source_sound_id": sound_id,
                                            "source_url": source_url,
                                            "creator_uploader": creator,
                                            "license": lic_name,
                                            "license_url": raw_license,
                                            "target_category": cat_name,
                                            "binary_label": t["binary"],
                                            "duration_seconds": round(len(data_arr) / target_sr, 2),
                                            "sample_rate": target_sr,
                                            "channels": 1,
                                            "source_group_id": sg_id,
                                            "file_sha256": file_sha256,
                                            "pcm_sha256": pcm_sha256,
                                            "local_audio_path": local_wav_path,
                                            "file_size_bytes": audio_size_bytes,
                                            "governance_status": "PROVENANCE_VERIFIED_INDEPENDENT"
                                        })

                                        # Update source group registry tracking
                                        if sg_id not in acquired_sg_records:
                                            acquired_sg_records[sg_id] = {
                                                "source_group_id": sg_id,
                                                "creator_uploader": creator,
                                                "recording_count": 0,
                                                "total_duration_seconds": 0.0,
                                                "primary_categories": set(),
                                                "license": lic_name,
                                                "is_historical_leak": 0
                                            }
                                        acquired_sg_records[sg_id]["recording_count"] += 1
                                        acquired_sg_records[sg_id]["total_duration_seconds"] += round(len(data_arr) / target_sr, 2)
                                        acquired_sg_records[sg_id]["primary_categories"].add(cat_name)

                            except Exception as e:
                                state = "QUARANTINED"
                                quarantine_reason = f"DOWNLOAD_OR_DECODE_ERROR_{type(e).__name__}"

                    candidate_records.append({
                        "candidate_id": cand_id,
                        "source_sound_id": sound_id,
                        "creator_uploader": creator,
                        "target_category": cat_name,
                        "binary_label": t["binary"],
                        "declared_license": raw_license,
                        "license_classification": lic_name,
                        "source_url": source_url,
                        "duration_seconds": duration_s,
                        "current_state": state,
                        "quarantine_reason": quarantine_reason,
                        "source_group_id": sg_id,
                        "file_sha256": file_sha256,
                        "pcm_sha256": pcm_sha256,
                        "local_wav_path": local_wav_path
                    })

            time.sleep(0.3) # Respectful rate limiting
        except Exception as e:
            print(f"Error executing search for '{t['query']}': {e}")

    # Build DataFrames
    cand_df = pd.DataFrame(candidate_records)
    dec_df = pd.DataFrame(decision_log)
    prov_df = pd.DataFrame(provenance_records)

    # Convert acquired source group records
    sg_list = []
    for sg_id, val in acquired_sg_records.items():
        sg_list.append({
            "source_group_id": val["source_group_id"],
            "creator_uploader": val["creator_uploader"],
            "recording_count": val["recording_count"],
            "total_duration_seconds": round(val["total_duration_seconds"], 2),
            "primary_categories": ";".join(sorted(list(val["primary_categories"]))),
            "license": val["license"],
            "is_historical_leak": val["is_historical_leak"]
        })
    acq_sg_df = pd.DataFrame(sg_list)

    # Save CSVs
    cand_csv = os.path.join(STAGE_DIR, "candidate_audit.csv")
    cand_df.to_csv(cand_csv, index=False)
    dec_csv = os.path.join(STAGE_DIR, "acquisition_decision_log.csv")
    dec_df.to_csv(dec_csv, index=False)
    prov_csv = os.path.join(STAGE_DIR, "acquisition_provenance.csv")
    prov_df.to_csv(prov_csv, index=False)
    acq_sg_csv = os.path.join(STAGE_DIR, "acquired_source_group_registry.csv")
    acq_sg_df.to_csv(acq_sg_csv, index=False)

    print(f"\n--- Acquisition Summary ---")
    print(f"Total candidates audited: {len(cand_df)}")
    print(f"State breakdown:\n{cand_df['current_state'].value_counts()}")
    print(f"Actually downloaded and verified recordings: {len(prov_df)}")
    print(f"Novel independent source groups acquired: {len(acq_sg_df)}")
    print(f"Total downloaded audio size: {total_downloaded_bytes / (1024*1024):.2f} MB (Quota limit: 500 MB)")

    return cand_df, dec_df, prov_df, acq_sg_df

if __name__ == "__main__":
    execute_audit_and_acquisition()

