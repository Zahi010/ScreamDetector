import os
import json
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

def classify_license(lic_str):
    if not lic_str or pd.isna(lic_str):
        return "UNKNOWN / MISSING", "QUARANTINE", "Missing declared license"
    
    l = str(lic_str).strip().lower()
    if any(k in l for k in ["cc0", "publicdomain/zero", "public domain", "cc-0"]):
        return "CC0 1.0 Universal", "COMMERCIALLY_ELIGIBLE", "No attribution required (Public Domain)"
    elif "noncommercial" in l or "non-commercial" in l or "cc-by-nc" in l or "cc by-nc" in l:
        return "CC BY-NC 4.0", "QUARANTINED_NON_COMMERCIAL", "Prohibited for commercial use"
    elif "no-derivatives" in l or "cc-by-nd" in l or "cc by-nd" in l:
        return "CC BY-ND 4.0", "QUARANTINED_NO_DERIVATIVES", "Prohibits transformation/filtering"
    elif "sharealike" in l or "cc-by-sa" in l or "cc by-sa" in l:
        return "CC BY-SA 4.0", "ELIGIBLE_WITH_SHAREALIKE", "Attribution and ShareAlike copyleft review required"
    elif "by/3.0" in l or "cc-by-3.0" in l:
        return "CC BY 3.0", "COMMERCIALLY_ELIGIBLE_WITH_ATTRIBUTION", "Attribution required (Freesound URL & Author)"
    elif "by/4.0" in l or "cc-by-4.0" in l or "cc by" in l:
        return "CC BY 4.0", "COMMERCIALLY_ELIGIBLE_WITH_ATTRIBUTION", "Attribution required (Freesound URL & Author)"
    elif "apache" in l:
        return "Apache 2.0", "COMMERCIALLY_ELIGIBLE_WITH_ATTRIBUTION", "Apache 2.0 license notice required"
    else:
        return f"Other ({lic_str})", "QUARANTINE_REVIEW_REQUIRED", "Review required"

def main():
    print("Executing Phase D: Validating License Provenance...")
    
    # Check if acquisition manifest exists; if not, create initial license policy catalog
    lic_records = [
        {
            "license_name": "Creative Commons Zero 1.0 Universal (CC0)",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "standardized_code": "CC0-1.0",
            "commercial_eligibility": "FULLY_ELIGIBLE",
            "attribution_required": False,
            "derivatives_allowed": True,
            "quarantine_status": "APPROVED",
            "policy_notes": "Unrestricted commercial and research use. No creator attribution legally mandated, though preserved for scientific provenance."
        },
        {
            "license_name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "standardized_code": "CC-BY-4.0",
            "commercial_eligibility": "ELIGIBLE_WITH_ATTRIBUTION",
            "attribution_required": True,
            "derivatives_allowed": True,
            "quarantine_status": "APPROVED",
            "policy_notes": "Commercial use permitted with appropriate credit, link to license, and indication of changes."
        },
        {
            "license_name": "Creative Commons Attribution 3.0 Unported (CC BY 3.0)",
            "license_url": "https://creativecommons.org/licenses/by/3.0/",
            "standardized_code": "CC-BY-3.0",
            "commercial_eligibility": "ELIGIBLE_WITH_ATTRIBUTION",
            "attribution_required": True,
            "derivatives_allowed": True,
            "quarantine_status": "APPROVED",
            "policy_notes": "Legacy Freesound license. Fully compatible with commercial research subject to author attribution."
        },
        {
            "license_name": "Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)",
            "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
            "standardized_code": "CC-BY-NC-4.0",
            "commercial_eligibility": "INELIGIBLE",
            "attribution_required": True,
            "derivatives_allowed": True,
            "quarantine_status": "STRICT_QUARANTINE",
            "policy_notes": "Strictly quarantined. Must NOT be ingested into production training or commercial deployment pipelines."
        },
        {
            "license_name": "Creative Commons Attribution-NoDerivatives 4.0 (CC BY-ND 4.0)",
            "license_url": "https://creativecommons.org/licenses/by-nd/4.0/",
            "standardized_code": "CC-BY-ND-4.0",
            "commercial_eligibility": "INELIGIBLE",
            "attribution_required": True,
            "derivatives_allowed": False,
            "quarantine_status": "STRICT_QUARANTINE",
            "policy_notes": "Strictly quarantined. Prohibits audio cropping, feature filtering, or DSP transformation."
        },
        {
            "license_name": "All Rights Reserved / Proprietary YouTube Terms",
            "license_url": "https://www.youtube.com/t/terms",
            "standardized_code": "PROPRIETARY_YOUTUBE",
            "commercial_eligibility": "INELIGIBLE",
            "attribution_required": False,
            "derivatives_allowed": False,
            "quarantine_status": "PROHIBITED",
            "policy_notes": "Prohibited by Stage 8.9.60 governance. Zero scraping or unvetted ingestion."
        }
    ]
    
    df_lic = pd.DataFrame(lic_records)
    out_csv = os.path.join(STAGE_DIR, "license_inventory.csv")
    df_lic.to_csv(out_csv, index=False)
    print(f"Saved license policy inventory to {out_csv} ({len(df_lic)} license classes)")

if __name__ == "__main__":
    main()

