import os
import json
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_59")
STAGE54_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_54")

def classify_license(lic_str):
    if not lic_str or pd.isna(lic_str):
        return "UNKNOWN / MISSING", "QUARANTINE"
    
    l = str(lic_str).strip().lower()
    if any(k in l for k in ["cc0", "public domain", "cc-0"]):
        return "CC0 / Public Domain", "COMMERCIALLY_ELIGIBLE"
    elif "cc-by-nc" in l or "cc by-nc" in l or "non-commercial" in l or "noncommercial" in l:
        return "CC BY-NC (Non-Commercial)", "QUARANTINED_NON_COMMERCIAL"
    elif "cc-by-nd" in l or "cc by-nd" in l or "no-derivatives" in l:
        return "CC BY-ND (No Derivatives)", "QUARANTINED_NO_DERIVATIVES"
    elif "cc-by-sa" in l or "cc by-sa" in l or "sharealike" in l:
        return "CC BY-SA (ShareAlike)", "ELIGIBLE_WITH_SHAREALIKE"
    elif "cc-by" in l or "cc by" in l or "attribution" in l:
        return "CC BY (Attribution)", "COMMERCIALLY_ELIGIBLE_WITH_ATTRIBUTION"
    elif "all rights reserved" in l or "copyright" in l or "arr" in l:
        return "All Rights Reserved", "QUARANTINED_PROPRIETARY"
    else:
        return f"Other ({lic_str})", "QUARANTINE_REVIEW_REQUIRED"

def main():
    print("Executing Phase G / License Audit: Analyzing License Provenance...")
    
    manifest_p = os.path.join(STAGE54_DIR, "dataset", "partition_manifest_verified.csv")
    df = pd.read_csv(manifest_p)
    
    provenance_rows = []
    for idx, r in df.iterrows():
        lic = r["license"]
        lic_category, legal_status = classify_license(lic)
        
        # Attribution requirement
        attr_req = "None required (Public Domain / CC0)"
        if "ATTRIBUTION" in legal_status or "SHAREALIKE" in legal_status:
            attr_req = f"Attribution to creator: {r['creator']}"
        elif "QUARANTINE" in legal_status:
            attr_req = "Ineligible for commercial deployment — research quarantine"
            
        provenance_rows.append({
            "expansion_file_id": r["expansion_file_id"],
            "original_recording_id": r["original_recording_id"],
            "creator_uploader": r["creator"],
            "source_dataset": r["source_dataset"],
            "source_group_id": r["source_group_id"],
            "declared_license": lic,
            "standardized_license_class": lic_category,
            "commercial_eligibility_status": legal_status,
            "attribution_requirements": attr_req,
            "expansion_partition": r["expansion_partition"],
            "target_category": r["target_category"],
            "binary_label": r["binary_label"]
        })
        
    df_prov = pd.DataFrame(provenance_rows)
    prov_csv = os.path.join(STAGE_DIR, "license_provenance_inventory.csv")
    df_prov.to_csv(prov_csv, index=False)
    print(f"Saved license provenance inventory to {prov_csv} ({len(df_prov)} entries)")
    
    # Summary by partition and status
    print("\nLicense Breakdown by Commercial Eligibility Status:")
    print(df_prov["commercial_eligibility_status"].value_counts())
    print("\nLicense Breakdown by Standardized License Class:")
    print(df_prov["standardized_license_class"].value_counts())
    
    summary = {
        "total_recordings_audited": len(df_prov),
        "status_distribution": df_prov["commercial_eligibility_status"].value_counts().to_dict(),
        "license_class_distribution": df_prov["standardized_license_class"].value_counts().to_dict(),
        "commercial_eligible_count": int((df_prov["commercial_eligibility_status"].isin(["COMMERCIALLY_ELIGIBLE", "COMMERCIALLY_ELIGIBLE_WITH_ATTRIBUTION", "ELIGIBLE_WITH_SHAREALIKE"])).sum()),
        "quarantined_count": int((df_prov["commercial_eligibility_status"].str.startswith("QUARANTINE")).sum())
    }
    with open(os.path.join(STAGE_DIR, "license_provenance_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()

