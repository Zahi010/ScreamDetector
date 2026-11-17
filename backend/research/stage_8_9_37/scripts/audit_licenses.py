"""
Stage 8.9.37 - Task 9: License & Provenance Audit
Audits licensing terms for all acquired recordings according to commercial-intent policies.
CC0: Eligible (Public Domain)
CC BY: Eligible (Attribution Required)
CC BY-NC / CC BY-NC-ND: Quarantined
Generates license_audit.csv and summary statistics.
"""
import os
import pandas as pd

def audit_licenses():
    print("======================================================================")
    print("STAGE 8.9.37 - TASK 9: LICENSE & PROVENANCE AUDIT")
    print("======================================================================")
    
    in_csv = "backend/research/stage_8_9_37/manifests/acquired_recordings.csv"
    df = pd.read_csv(in_csv)
    
    audit_rows = []
    for _, r in df.iterrows():
        lic = r['license']
        if "NC" in lic or "Non-Commercial" in lic:
            status = "QUARANTINED"
            action = "Isolate in non-commercial research archive; do not include in commercial deployment manifest"
            policy_reason = "Contains NonCommercial (NC) restriction incompatible with commercial intent"
        elif "CC0" in lic or "Public Domain" in lic:
            status = "ELIGIBLE"
            action = "Approved for all splits (train/val/test/production)"
            policy_reason = "Public domain dedication allows unrestricted commercial and non-commercial research use"
        elif "CC BY" in lic:
            status = "ELIGIBLE_WITH_ATTRIBUTION"
            action = "Approved for all splits subject to creator attribution preservation"
            policy_reason = "Permissive attribution license allows commercial usage provided attribution metadata is tracked"
        else:
            status = "QUARANTINED"
            action = "Quarantined pending legal clearance"
            policy_reason = "Unknown or unverified license terms"
            
        audit_rows.append({
            "acquisition_id": r['acquisition_id'],
            "binary_label": r['binary_label'],
            "target_category": r['target_category'],
            "source_group_id": r['source_group_id'],
            "creator_id": r['creator_id'],
            "license": lic,
            "license_status": status,
            "commercial_policy_reason": policy_reason,
            "required_action": action,
            "original_url": r['original_url'],
            "sha256_checksum": r['sha256_checksum']
        })
        
    audit_df = pd.DataFrame(audit_rows)
    out_csv = "backend/research/stage_8_9_37/manifests/license_audit.csv"
    audit_df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv} ({len(audit_df)} records)")
    
    print("\nLicense Audit Distribution:")
    print(audit_df['license_status'].value_counts())
    print("\nQuarantined Records by Category:")
    quar = audit_df[audit_df['license_status'] == 'QUARANTINED']
    print(quar['target_category'].value_counts())

if __name__ == "__main__":
    audit_licenses()
