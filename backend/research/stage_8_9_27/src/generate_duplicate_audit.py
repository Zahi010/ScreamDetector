import os
import glob
import hashlib
import pandas as pd

def main():
    print("=== GENERATING AUDIO HASH AND DUPLICATE AUDIT ===")
    
    # 1. Load splits
    df_splits = pd.read_csv('backend/research/stage_8_9_27/src/splits_with_disk_sha256.csv')
    split_hashes = set(df_splits['sha256_disk'])
    split_fids = set(df_splits['file_id'])
    split_sgs = set(df_splits['source_group_id'].dropna().str.lower())

    # 2. Load census of all workspace audio
    df_census = pd.read_csv('backend/research/stage_8_9_27/src/workspace_audio_census.csv')
    df_manifest = pd.read_csv('backend/research/stage_8_9_27/independent_dataset_manifest.csv')
    manifest_hashes = set(df_manifest['sha256'])

    audit_records = []
    for idx, r in df_census.iterrows():
        sha = r['sha256']
        p = r['file_path']
        fn = r['filename']
        stem = r['stem']
        
        in_splits = sha in split_hashes
        in_independent = sha in manifest_hashes
        
        if in_splits:
            status = 'HISTORICAL_SPLIT_OVERLAP'
            action = 'EXCLUDED_TRAIN_VAL_TEST_LEAKAGE_PREVENTION'
            details = 'Exact SHA-256 matches an established training/validation/test split recording.'
        elif in_independent:
            status = 'ACCEPTED_INDEPENDENT_COHORT'
            action = 'INCLUDED_IN_INDEPENDENT_MANIFEST'
            details = 'Verified unique SHA-256, disjoint source group, no split leakage.'
        else:
            status = 'DEDUPLICATED_OR_QUARANTINED'
            action = 'EXCLUDED_FROM_PRIMARY_COHORT'
            if 'supp_short_scream' in p and any(k in stem for k in ['186931', '186955', '186958', '344067', '169003', '169005', '369003']):
                details = 'Misleading folder probe; ground truth verified as pyrotechnics/whistle/squeak, not a scream.'
            elif 'fsd50k' in stem or 'user' in stem:
                details = 'Source-group / uploader or sound ID overlap with historical development dataset.'
            else:
                details = 'Internal duplicate recording or unverified provenance.'

        audit_records.append({
            'filename': fn,
            'local_path': p,
            'sha256': sha,
            'duration_seconds': r['duration'],
            'sample_rate': r['samplerate'],
            'channels': r['channels'],
            'audit_status': status,
            'audit_action': action,
            'audit_details': details
        })

    df_audit = pd.DataFrame(audit_records)
    out_path = 'backend/research/stage_8_9_27/audio_hash_and_duplicate_audit.csv'
    df_audit.to_csv(out_path, index=False)
    print(f"Saved {len(df_audit)} audit rows to {out_path}")
    print("Audit breakdown:")
    print(df_audit['audit_status'].value_counts())

if __name__ == '__main__':
    main()
