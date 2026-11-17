# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.77 Audio Integrity Auditor
Audits the 26 downloaded WAV recordings in backend/research/stage_8_9_76/audio/
Generates: stage76_audio_integrity_audit.csv
"""

import os
import glob
import hashlib
import pandas as pd
import soundfile as sf
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76", "audio")
PROV_PATH = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76", "acquisition_provenance.csv")

def audit_audio_files():
    df_prov = pd.read_csv(PROV_PATH)
    prov_map = {row["recording_id"]: row for _, row in df_prov.iterrows()}
    
    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "*.wav")))
    print(f"Auditing {len(audio_files)} audio files in {AUDIO_DIR}...")
    
    audit_rows = []
    for fpath in audio_files:
        fname = os.path.basename(fpath)
        cand_id = os.path.splitext(fname)[0]
        
        # Read raw file bytes for file SHA-256
        with open(fpath, "rb") as f:
            file_bytes = f.read()
        file_sha256 = hashlib.sha256(file_bytes).hexdigest()
        
        # Decode audio
        decodable = False
        sr = None
        channels = None
        num_samples = None
        dur_sec = None
        decoded_pcm_sha256 = None
        try:
            data, sr = sf.read(fpath, dtype="float32")
            decodable = True
            channels = 1 if data.ndim == 1 else data.shape[1]
            num_samples = len(data)
            dur_sec = round(num_samples / sr, 4)
            # Standard PCM representation hash
            pcm_int16 = (data * 32767.0).astype(np.int16)
            decoded_pcm_sha256 = hashlib.sha256(pcm_int16.tobytes()).hexdigest()
        except Exception as e:
            print(f"[ERROR] Failed to decode {fname}: {e}")
            
        # Cross-reference with provenance
        prov_record = prov_map.get(cand_id, {})
        expected_sha = prov_record.get("file_sha256", None)
        recorded_harvest_pcm = prov_record.get("pcm_sha256", None)
        sha_match = (file_sha256 == expected_sha) if expected_sha else False
        
        # Validate criteria: decodable, sr==16000, channels==1, dur >= 0.2, dur <= 30.0, sha_match
        is_valid = (
            decodable and 
            sr == 16000 and 
            channels == 1 and 
            dur_sec >= 0.2 and 
            dur_sec <= 30.0 and 
            sha_match
        )
        
        verdict = "VERIFIED_AUDIO_INTEGRITY_PASS" if is_valid else "INTEGRITY_FAIL"
        
        audit_rows.append({
            "candidate_id": cand_id,
            "filename": fname,
            "source_sound_id": prov_record.get("source_sound_id", ""),
            "creator_uploader": prov_record.get("creator_uploader", ""),
            "license": prov_record.get("license", ""),
            "target_category": prov_record.get("target_category", ""),
            "sample_rate": sr,
            "channels": channels,
            "num_samples": num_samples,
            "duration_seconds": dur_sec,
            "file_sha256": file_sha256,
            "expected_file_sha256": expected_sha,
            "file_sha256_match": 1 if sha_match else 0,
            "recorded_harvest_pcm_sha256": recorded_harvest_pcm,
            "decoded_pcm_sha256": decoded_pcm_sha256,
            "audio_format": "WAV_16KHZ_MONO_PCM16",
            "decodable": 1 if decodable else 0,
            "integrity_verdict": verdict
        })
        
    df_audit = pd.DataFrame(audit_rows)
    out_path = os.path.join(STAGE_DIR, "stage76_audio_integrity_audit.csv")
    df_audit.to_csv(out_path, index=False)
    print(f"[OK] Wrote {out_path} ({len(df_audit)} rows)")
    
    pass_count = (df_audit["integrity_verdict"] == "VERIFIED_AUDIO_INTEGRITY_PASS").sum()
    print(f"Audio Integrity Audit Results: {pass_count}/{len(df_audit)} PASSED")

if __name__ == "__main__":
    audit_audio_files()
