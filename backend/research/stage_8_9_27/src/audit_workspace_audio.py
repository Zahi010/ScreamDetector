import os
import glob
import hashlib
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
    print("=== AUDITING AUDIO FILES IN WORKSPACE ===")
    
    # 1. Load known 2804 file IDs and source groups from stage8_9_17
    f17_path = 'backend/experiments/stage8_9_17_automated_dataset_reconstruction/data/features_stage8_9_17.npz'
    if os.path.exists(f17_path):
        f17 = np.load(f17_path, allow_pickle=True)
        file_ids_2804 = set(f17['file_ids'])
        print(f"Loaded 2,804 historical dataset IDs from {f17_path}")
    else:
        file_ids_2804 = set()
        print("Warning: stage8_9_17 features not found!")

    # 2. Check source group splits manifest
    splits_csv = 'backend/experiments/stage8_9_17_automated_dataset_reconstruction/manifests/source_group_splits.csv'
    if os.path.exists(splits_csv):
        df_splits = pd.read_csv(splits_csv)
        print(f"Loaded {len(df_splits)} records from source_group_splits.csv")
        print("Splits counts by label:")
        print(df_splits['label'].value_counts())
        print("Splits counts by split:")
        print(df_splits['split'].value_counts())
    else:
        df_splits = pd.DataFrame()

    # 3. Find all WAV files in backend/ and subdirs
    all_wavs = glob.glob('backend/**/*.wav', recursive=True)
    print(f"\nTotal .wav files found across backend: {len(all_wavs)}")
    
    # Group by directory
    dir_counts = {}
    for w in all_wavs:
        d = os.path.dirname(w).replace('\\', '/')
        dir_counts[d] = dir_counts.get(d, 0) + 1
    
    print("\nDirectory breakdown:")
    for d, c in sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {d}: {c} files")

    # 4. Check candidates database
    db_path = 'backend/database/stage8_9_reviews.db'
    if os.path.exists(db_path):
        import sqlite3
        conn = sqlite3.connect(db_path)
        df_db = pd.read_sql_query("SELECT * FROM candidates", conn)
        conn.close()
        print(f"\nCandidates DB ({db_path}): {len(df_db)} records")
        print(f"DB columns: {list(df_db.columns)}")
        for col in ['candidate_category', 'category', 'review_status', 'label']:
            if col in df_db.columns:
                print(f"DB Col {col}:")
                print(df_db[col].value_counts())

    # 5. Check stage8_8_manifest.csv
    s88_manifest = 'backend/dataset/stage8_8_hard_negatives/stage8_8_manifest.csv'
    if os.path.exists(s88_manifest):
        df_88 = pd.read_csv(s88_manifest)
        print(f"\nStage 8.8 manifest: {len(df_88)} records")
        print(f"Manifest 8.8 columns: {list(df_88.columns)}")
        for col in ['category', 'source', 'status']:
            if col in df_88.columns:
                print(f"Manifest Col {col}:")
                print(df_88[col].value_counts())

if __name__ == '__main__':
    main()
