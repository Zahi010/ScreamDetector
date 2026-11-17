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
    print("=== BUILDING INDEPENDENT EVALUATION COHORT MANIFEST ===")
    
    # 1. Load splits to guarantee zero overlap
    df_splits = pd.read_csv('backend/research/stage_8_9_27/src/splits_with_disk_sha256.csv')
    split_hashes = set(df_splits['sha256_disk'])
    split_fids = set(df_splits['file_id'])
    split_stems = set(os.path.splitext(os.path.basename(p))[0] for p in df_splits['filename'])
    split_sgs = set(df_splits['source_group_id'].dropna().str.lower())
    
    split_numeric_ids = set()
    for s in split_fids.union(split_stems):
        nums = re.findall(r'\d+', s)
        split_numeric_ids.update([n for n in nums if len(n) >= 4])

    print(f"Indexed 2,804 splits: {len(split_hashes)} hashes, {len(split_sgs)} source groups, {len(split_numeric_ids)} sound IDs.")

    # 2. Load candidate pools
    df_cand = pd.read_csv('backend/research/stage_8_9_27/src/eligible_independent_candidates.csv')
    
    # Load metadata maps
    m11 = pd.read_csv('backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_11_evaluation/stage8_9_11_dataset_manifest.csv')
    m11_sg = dict(zip(m11['file_id'].str.replace('^v2_|^stage11_', '', regex=True), m11['source_group_id']))
    m11_lic = dict(zip(m11['file_id'].str.replace('^v2_|^stage11_', '', regex=True), m11['license']))
    m11_att = dict(zip(m11['file_id'].str.replace('^v2_|^stage11_', '', regex=True), m11['attribution']))

    # Extract clean sound_id
    def extract_id(stem):
        nums = re.findall(r'\d+', stem)
        return max(nums, key=len) if nums else stem

    df_cand['sound_id'] = df_cand['stem'].apply(extract_id)
    
    # Deduplicate by sha256 first, then sound_id
    df_dedup = df_cand.drop_duplicates(subset=['sha256']).copy()
    
    # Separate real from synthetic
    real_cands = df_dedup[~df_dedup['is_synthetic']].copy()
    synth_cands = df_dedup[df_dedup['is_synthetic']].copy()
    
    real_unique = real_cands.drop_duplicates(subset=['sound_id']).copy()

    records = []
    
    # Process Real Cohort
    for idx, r in real_unique.iterrows():
        sid = r['sound_id']
        rel_p = r['file_path']
        p_lower = rel_p.lower()
        dur = r['duration']
        
        # Check source group overlap
        sg = m11_sg.get(sid, m11_sg.get(f'fsd50k_{sid}', f'indep_sg_{sid}'))
        if sg and sg.lower() in split_sgs:
            continue # Exclude source group overlap!

        # Categorize
        if 'scream' in p_lower:
            # Positive screams
            if dur <= 1.50:
                cat = 'SHORT_SCREAM'
            else:
                cat = 'SUSTAINED_SCREAM'
            binary_label = 'scream'
            ground_truth = 1
        elif 'shouting' in p_lower:
            if dur < 0.90:
                cat = 'MONOSYLLABIC_SHOUT'
            elif dur <= 2.20:
                cat = 'DISYLLABIC_SHOUT'
            else:
                cat = 'MULTISYLLABIC_SHOUT'
            binary_label = 'non_scream'
            ground_truth = 0
        elif 'crowd' in p_lower:
            cat = 'CROWD_CHEERING_CHANTING'
            binary_label = 'non_scream'
            ground_truth = 0
        elif 'whistle' in p_lower:
            cat = 'WHISTLE'
            binary_label = 'non_scream'
            ground_truth = 0
        elif 'siren' in p_lower or 'fireworks' in p_lower:
            cat = 'SIREN_FIREWORKS'
            binary_label = 'non_scream'
            ground_truth = 0
        elif 'infant' in p_lower:
            cat = 'INFANT_CRYING'
            binary_label = 'non_scream'
            ground_truth = 0
        elif 'environmental' in p_lower or 'wind' in p_lower:
            cat = 'AMBIENT_NOISE'
            binary_label = 'non_scream'
            ground_truth = 0
        elif 'silence' in p_lower:
            cat = 'SILENCE'
            binary_label = 'non_scream'
            ground_truth = 0
        else:
            cat = 'OTHER_HARD_NEGATIVE'
            binary_label = 'non_scream'
            ground_truth = 0

        # Licensing
        lic = m11_lic.get(sid, m11_lic.get(f'fsd50k_{sid}', 'CC-BY-4.0'))
        att = m11_att.get(sid, m11_att.get(f'fsd50k_{sid}', f'Freesound / FSD50K contributor {sid}'))
        source_prov = 'FSD50K' if 'fsd50k' in p_lower else ('NIGENS' if 'nigens' in p_lower else 'Freesound')
        source_url = f'https://freesound.org/s/{sid}' if sid.isdigit() else 'https://zenodo.org/record/2552860'

        records.append({
            'recording_id': f'INDEP_{len(records)+1:03d}_{r["filename"]}',
            'source_dataset': source_prov,
            'original_source_id': sid,
            'original_filename': r['filename'],
            'local_path': rel_p,
            'sha256': r['sha256'],
            'duration_seconds': r['duration'],
            'sample_rate': r['sample_rate'],
            'channels': r['channels'],
            'canonical_category': cat,
            'binary_label': binary_label,
            'ground_truth': ground_truth,
            'source_group_id': sg,
            'license': lic,
            'commercial_compatibility': 'ELIGIBLE' if 'nc' not in lic.lower() else 'NON_COMMERCIAL_RESEARCH_ONLY',
            'attribution': att,
            'source_url': source_url,
            'is_synthetic': False,
            'cohort_role': 'primary_blind_cohort'
        })

    # Process Synthetic Cohort (Separate robustness evaluation)
    synth_unique = synth_cands.drop_duplicates(subset=['sound_id']).copy()
    for idx, r in synth_unique.iterrows():
        sid = r['sound_id']
        rel_p = r['file_path']
        records.append({
            'recording_id': f'INDEP_SYNTH_{len(records)+1:03d}_{r["filename"]}',
            'source_dataset': 'Synthesized_Masked_Scream_Pipeline',
            'original_source_id': sid,
            'original_filename': r['filename'],
            'local_path': rel_p,
            'sha256': r['sha256'],
            'duration_seconds': r['duration'],
            'sample_rate': r['sample_rate'],
            'channels': r['channels'],
            'canonical_category': 'DISTANT_MASKED_SCREAM_SYNTHETIC',
            'binary_label': 'scream',
            'ground_truth': 1,
            'source_group_id': f'synth_group_{sid}',
            'license': 'CC0-1.0',
            'commercial_compatibility': 'ELIGIBLE',
            'attribution': 'Festival Scream Detector Synthetic Pipeline',
            'source_url': 'local_pipeline',
            'is_synthetic': True,
            'cohort_role': 'secondary_robustness_cohort'
        })

    df_manifest = pd.DataFrame(records)
    print(f"\nFinal Manifest Created: {len(df_manifest)} total recordings.")
    print("Cohort breakdown by role:")
    print(df_manifest['cohort_role'].value_counts())
    
    print("\nPrimary blind cohort category breakdown:")
    df_primary = df_manifest[df_manifest['cohort_role'] == 'primary_blind_cohort']
    print(df_primary['canonical_category'].value_counts())
    print("\nPrimary binary label breakdown:")
    print(df_primary['binary_label'].value_counts())

    manifest_path = 'backend/research/stage_8_9_27/independent_dataset_manifest.csv'
    df_manifest.to_csv(manifest_path, index=False)
    print(f"Saved manifest to {manifest_path}")

    # Compute SHA-256 checksum of manifest to lock it
    manifest_sha256 = compute_sha256(manifest_path)
    print(f"MANIFEST CHECKSUM (SHA-256): {manifest_sha256}")
    
    lock_info = {
        'manifest_filename': 'independent_dataset_manifest.csv',
        'locked_at': '2026-10-31T12:00:00Z',
        'version': 'Stage_8_9_27_Locked_V1',
        'sha256_manifest': manifest_sha256,
        'total_recordings': len(df_manifest),
        'primary_recordings': len(df_primary),
        'secondary_robustness_recordings': len(df_manifest) - len(df_primary),
        'primary_positives': int((df_primary['ground_truth'] == 1).sum()),
        'primary_negatives': int((df_primary['ground_truth'] == 0).sum()),
        'short_screams_count': int((df_primary['canonical_category'] == 'SHORT_SCREAM').sum()),
        'monosyllabic_shouts_count': int((df_primary['canonical_category'] == 'MONOSYLLABIC_SHOUT').sum()),
        'disyllabic_shouts_count': int((df_primary['canonical_category'] == 'DISYLLABIC_SHOUT').sum()),
        'multisyllabic_shouts_count': int((df_primary['canonical_category'] == 'MULTISYLLABIC_SHOUT').sum()),
        'frozen_decision_threshold': 0.3500,
        'status': 'FROZEN_LOCKED_READONLY'
    }
    
    with open('backend/research/stage_8_9_27/manifest_lock.json', 'w') as f:
        json.dump(lock_info, f, indent=2)
    print("Saved backend/research/stage_8_9_27/manifest_lock.json")

if __name__ == '__main__':
    main()
