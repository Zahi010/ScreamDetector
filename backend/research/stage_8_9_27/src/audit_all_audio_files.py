import os
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
    print("=== DEEP FORENSIC AUDIT OF ALL AUDIO FILES ON DISK ===")
    
    # 1. Load 2,804 splits
    df_splits = pd.read_csv('backend/experiments/stage8_9_17_automated_dataset_reconstruction/data/manifests/source_group_splits.csv')
    print(f"Loaded 2,804 splits. Columns: {list(df_splits.columns)}")
    
    split_hashes = set(df_splits['content_hash'])
    split_file_ids = set(df_splits['file_id'])
    split_stems = set(os.path.splitext(os.path.basename(p))[0] for p in df_splits['filename'])
    split_source_groups = set(df_splits['source_group_id'].dropna())
    
    print(f"Unique hashes in splits: {len(split_hashes)}")
    print(f"Unique file_ids in splits: {len(split_file_ids)}")
    print(f"Unique source groups in splits: {len(split_source_groups)}")

    # 2. Find every .wav file in repo
    all_wavs = glob.glob('backend/**/*.wav', recursive=True)
    all_wavs = [os.path.normpath(w) for w in all_wavs]
    print(f"\nTotal wav files in backend: {len(all_wavs)}")

    records = []
    for idx, wav_path in enumerate(all_wavs):
        rel_path = os.path.relpath(wav_path, '.').replace('\\', '/')
        stem = os.path.splitext(os.path.basename(wav_path))[0]
        file_sha256 = compute_sha256(wav_path)
        
        # Audio metadata
        try:
            info = sf.info(wav_path)
            duration = info.duration
            sr = info.samplerate
            channels = info.channels
        except Exception as e:
            duration = -1.0
            sr = -1
            channels = -1

        in_splits_hash = file_sha256 in split_hashes
        in_splits_stem = stem in split_stems or any(stem in s or s in stem for s in split_stems if len(stem) > 8)

        records.append({
            'file_path': rel_path,
            'filename': os.path.basename(wav_path),
            'stem': stem,
            'sha256': file_sha256,
            'duration': duration,
            'samplerate': sr,
            'channels': channels,
            'in_splits_hash': in_splits_hash,
            'in_splits_stem': in_splits_stem
        })

    df_all = pd.DataFrame(records)
    print(f"\nAudit complete. Total analyzed: {len(df_all)}")
    print(f"Files matching split hashes: {df_all['in_splits_hash'].sum()}")
    print(f"Files with NEW hashes: {(~df_all['in_splits_hash']).sum()}")

    # Breakdown of files with NEW hashes by directory
    df_new = df_all[~df_all['in_splits_hash']]
    df_new['dir'] = df_new['file_path'].apply(lambda p: os.path.dirname(p))
    print("\nNew hash files by directory:")
    print(df_new['dir'].value_counts())

    # Save summary
    df_all.to_csv('backend/research/stage_8_9_27/src/workspace_audio_census.csv', index=False)
    print("Saved workspace_audio_census.csv")

if __name__ == '__main__':
    main()
