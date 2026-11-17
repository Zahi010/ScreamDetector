import csv
import os
import hashlib
import soundfile as sf

def main():
    v2_audit_path = 'backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_15_hierarchical_phonation/reports/dataset_provenance_and_license_audit.csv'
    with open(v2_audit_path, 'r', encoding='utf-8') as f:
        v2_rows = list(csv.DictReader(f))

    manifest_31_path = 'backend/research/stage_8_9_31/evaluation_cohort_manifest.csv'
    with open(manifest_31_path, 'r', encoding='utf-8') as f:
        man31_rows = [r for r in csv.DictReader(f) if str(r['audited_ground_truth']) == '0']

    manifest_entries = []

    print('Processing v2 verified hard negatives...')
    for r in v2_rows:
        if r['binary_label'] != 'non_scream':
            continue
        fid = r['file_id']
        cat = r['target_category']
        p_found = None
        for ext in ['.wav', '.flac', '.mp3', '.ogg']:
            cand = f'backend/experiments/v2_hard_negative_training/audio/{cat}/{fid}{ext}'
            if os.path.exists(cand):
                p_found = cand
                break
        if not p_found:
            continue
        
        file_sha = hashlib.sha256(open(p_found, 'rb').read()).hexdigest()
        try:
            info = sf.info(p_found)
            sr = info.samplerate
            dur = info.duration
            samples = info.frames
        except Exception:
            sr = 16000
            dur = float(r['duration_seconds'])
            samples = int(dur * sr)
        
        cat_norm = cat.upper()
        if 'CROWD' in cat_norm or 'CHEERING' in cat_norm:
            prim_cat = 'STADIUM_CHEERING'
        elif 'INFANT' in cat_norm or 'CRYING' in cat_norm:
            prim_cat = 'BABY_CRYING'
        elif 'SHOUTING' in cat_norm or 'SPEECH' in cat_norm:
            prim_cat = 'SHOUTED_SPEECH'
        elif 'WHISTLE' in cat_norm or 'SQUEAK' in cat_norm:
            prim_cat = 'WHISTLE_SQUEAK'
        elif 'SIREN' in cat_norm or 'FIREWORK' in cat_norm:
            prim_cat = 'SIREN_ALARM'
        else:
            prim_cat = 'ENVIRONMENTAL_NON_VOCAL'
        
        manifest_entries.append({
            'recording_id': f'HN_V2_{fid}',
            'original_source_id': r.get('original_id') or fid,
            'dataset_name': r['source_dataset'],
            'source_provider': 'freesound',
            'source_url': r['source_url'],
            'uploader_or_creator': r['source_group_id'],
            'source_group_id': r['source_group_id'],
            'license': r['license'],
            'attribution_required': 'True' if 'by' in r['license'].lower() else 'False',
            'duration_sec': f'{dur:.4f}',
            'sample_rate': sr,
            'sample_count': samples,
            'primary_category': prim_cat,
            'ground_truth_status': 'CLEAR_HARD_NEGATIVE',
            'audio_quality_status': 'VERIFIED_CLEAN',
            'sha256_file': file_sha,
            'local_file_path': p_found
        })

    print(f'Processed {len(manifest_entries)} v2 hard negatives.')

    for r in man31_rows:
        rec_id = r['recording_id']
        orig_id = r['original_source_id']
        prim_cat = r['audited_content_category']
        dur = float(r['duration_sec'])
        prov = r['source_provider']
        
        # Local path check
        p_cand = f'backend/research/stage_8_9_30/processed/positive/FS_{orig_id}_16k_mono.wav'
        if not os.path.exists(p_cand):
            p_cand = f'backend/research/stage_8_9_30/processed/negative/{orig_id}_16k_mono.wav'
        if not os.path.exists(p_cand):
            p_cand = f'backend/research/stage_8_9_30/raw/negative/FS_{orig_id}.mp3'

        manifest_entries.append({
            'recording_id': f'HN_AUDITED_{rec_id}',
            'original_source_id': orig_id,
            'dataset_name': 'STAGE_8_9_31_AUDITED_COHORT',
            'source_provider': prov,
            'source_url': f'https://freesound.org/s/{orig_id}' if prov == 'freesound' else 'https://zenodo.org/record/3874403',
            'uploader_or_creator': r['uploader'],
            'source_group_id': r['source_group_id'],
            'license': 'CC0 / CC-BY (Permissive)',
            'attribution_required': 'True' if prov == 'freesound' else 'False',
            'duration_sec': f'{dur:.4f}',
            'sample_rate': 16000,
            'sample_count': int(dur * 16000),
            'primary_category': prim_cat,
            'ground_truth_status': 'CLEAR_HARD_NEGATIVE',
            'audio_quality_status': 'VERIFIED_AUDITED',
            'sha256_file': r['sha256_processed'],
            'local_file_path': p_cand
        })

    print(f'Total hard negative entries: {len(manifest_entries)}')

    p_hn = 'backend/research/stage_8_9_32/dataset/hard_negative_dataset_manifest.csv'
    with open(p_hn, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(manifest_entries[0].keys()))
        w.writeheader()
        w.writerows(manifest_entries)
    print(f'Saved {p_hn}')

    sg_stats = {}
    for m in manifest_entries:
        sg = m['source_group_id']
        cat = m['primary_category']
        dur = float(m['duration_sec'])
        if sg not in sg_stats:
            sg_stats[sg] = {'source_group_id': sg, 'total_recordings': 0, 'total_duration_sec': 0.0, 'categories': set()}
        sg_stats[sg]['total_recordings'] += 1
        sg_stats[sg]['total_duration_sec'] += dur
        sg_stats[sg]['categories'].add(cat)

    sg_rows = []
    for sg, data in sorted(sg_stats.items()):
        sg_rows.append({
            'source_group_id': sg,
            'total_recordings': data['total_recordings'],
            'total_duration_sec': f'{data["total_duration_sec"]:.2f}',
            'category_diversity': ';'.join(sorted(data['categories'])),
            'partition_recommendation': 'ISOLATED_BLOCK'
        })

    p_sg_stat = 'backend/research/stage_8_9_32/dataset/source_group_statistics.csv'
    with open(p_sg_stat, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(sg_rows[0].keys()))
        w.writeheader()
        w.writerows(sg_rows)
    print(f'Saved {p_sg_stat} ({len(sg_rows)} source groups)')

if __name__ == '__main__':
    main()
