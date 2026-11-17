import os
import re
import glob
import hashlib
import json
import numpy as np
import pandas as pd
import soundfile as sf

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=== SEARCHING FOR INDEPENDENT CANDIDATE AUDIO FILES ===")
    
    # 1. Load splits
    df_splits = pd.read_csv('backend/research/stage_8_9_27/src/splits_with_disk_sha256.csv')
    split_hashes = set(df_splits['sha256_disk'])
    split_fids = set(df_splits['file_id'])
    split_stems = set(os.path.splitext(os.path.basename(p))[0] for p in df_splits['filename'])
    split_source_groups = set(df_splits['source_group_id'].dropna().str.lower())
    split_orig_ids = set(df_splits['original_id'].dropna().astype(str))
    
    split_numeric_ids = set()
    for s in split_fids.union(split_stems):
        nums = re.findall(r'\d+', s)
        split_numeric_ids.update([n for n in nums if len(n) >= 4]) # 4+ digits

    print(f"Loaded {len(df_splits)} splits. Indexed {len(split_hashes)} hashes, {len(split_source_groups)} source groups, {len(split_numeric_ids)} sound IDs.")

    # 2. Check candidate pools
    all_wavs = glob.glob('backend/**/*.wav', recursive=True)
    all_wavs = [os.path.normpath(w) for w in all_wavs]

    print(f"Total wavs on disk: {len(all_wavs)}")

    candidates = []
    excluded = []

    for wav_path in all_wavs:
        rel_path = os.path.relpath(wav_path, '.').replace('\\', '/')
        basename = os.path.basename(wav_path)
        stem = os.path.splitext(basename)[0]
        
        # Audio hash
        sha256 = compute_sha256(wav_path)
        
        # Exact hash match?
        if sha256 in split_hashes:
            excluded.append((rel_path, "EXACT_SHA256_MATCH_SPLIT"))
            continue
            
        # Check numeric ID overlap
        nums = [n for n in re.findall(r'\d+', stem) if len(n) >= 4]
        overlap_nums = [n for n in nums if n in split_numeric_ids]
        if overlap_nums:
            excluded.append((rel_path, f"NUMERIC_SOUND_ID_OVERLAP_{overlap_nums[0]}"))
            continue

        # Check stem overlap
        clean_stem = re.sub(r'^(v2_|v3_|stage11_|supp_short_scream_\d+_)', '', stem)
        if clean_stem in split_stems:
            excluded.append((rel_path, f"STEM_MATCH_{clean_stem}"))
            continue

        # Check synthetic status
        is_synthetic = "synth" in stem.lower() or "generated_silence" in rel_path.lower()
        
        try:
            info = sf.info(wav_path)
            dur = info.duration
            sr = info.samplerate
            ch = info.channels
        except Exception as e:
            excluded.append((rel_path, f"CORRUPT_AUDIO_{e}"))
            continue

        candidates.append({
            'file_path': rel_path,
            'filename': basename,
            'stem': stem,
            'sha256': sha256,
            'duration': round(dur, 4),
            'sample_rate': sr,
            'channels': ch,
            'is_synthetic': is_synthetic
        })

    df_cand = pd.DataFrame(candidates)
    df_excl = pd.DataFrame(excluded, columns=['file_path', 'reason'])

    print(f"\nFiltered candidates: {len(df_cand)} eligible, {len(df_excl)} excluded.")
    print("Excluded reasons breakdown:")
    print(df_excl['reason'].apply(lambda r: r.split('_')[0]).value_counts())

    if len(df_cand) > 0:
        print("\nEligible candidates by directory:")
        df_cand['dir'] = df_cand['file_path'].apply(lambda p: os.path.dirname(p))
        print(df_cand['dir'].value_counts())
        
        print("\nSynthetic vs Real in eligible candidates:")
        print(df_cand['is_synthetic'].value_counts())

    df_cand.to_csv('backend/research/stage_8_9_27/src/eligible_independent_candidates.csv', index=False)
    df_excl.to_csv('backend/research/stage_8_9_27/src/excluded_audio_audit.csv', index=False)
    print("Saved eligible_independent_candidates.csv and excluded_audio_audit.csv")

if __name__ == '__main__':
    main()
