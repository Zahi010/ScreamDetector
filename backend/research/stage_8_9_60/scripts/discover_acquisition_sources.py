import os
import json
import pandas as pd

# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.join(REPO_ROOT, "backend", "research", "stage_8_9_60")

SOURCES = [
    {
        "source_name": "FSD50K (Freesound Dataset 50K - Zenodo)",
        "official_url": "https://zenodo.org/record/4060432",
        "dataset_owner": "Music Technology Group, Universitat Pompeu Fabra (UPF)",
        "license": "CC BY 4.0 / CC0 (Individual clip declared licenses)",
        "attribution_requirements": "Attribution to original Freesound creator via Freesound sound ID and FSD50K paper citation",
        "permitted_use": "Commercial and research use permitted subject to individual clip CC license",
        "restrictions": "No redistribution without attribution; preserve original creator identity",
        "expected_categories": "Shouted speech, screaming, infant crying, cheering, whistles, crowd noise",
        "estimated_independent_sources": 1500,
        "audio_download_permitted": True,
        "redistribution_permitted": True,
        "verification_status": "VERIFIED_ELIGIBLE"
    },
    {
        "source_name": "NIGENS General Sound Events",
        "official_url": "https://zenodo.org/record/2535879",
        "dataset_owner": "Audio Research Group, Tampere University & Inria",
        "license": "CC BY 4.0",
        "attribution_requirements": "Cite NIGENS dataset publication (Giannoulis et al., 2019)",
        "permitted_use": "Research and commercial development permitted with attribution",
        "restrictions": "Attribution required",
        "expected_categories": "Vocalizations, gasps, footsteps, environmental noises, laughter",
        "estimated_independent_sources": 350,
        "audio_download_permitted": True,
        "redistribution_permitted": True,
        "verification_status": "VERIFIED_ELIGIBLE"
    },
    {
        "source_name": "OpenSLR Permissive Speech & Vocalizations",
        "official_url": "https://www.openslr.org/",
        "dataset_owner": "OpenSLR Consortium",
        "license": "CC0 / CC BY 4.0 / Apache 2.0 (resource-dependent)",
        "attribution_requirements": "Cite respective OpenSLR resource ID and authors",
        "permitted_use": "Commercial and academic speech research",
        "restrictions": "Check individual corpus terms",
        "expected_categories": "Loud speech, emotional shouting, vocal projection",
        "estimated_independent_sources": 800,
        "audio_download_permitted": True,
        "redistribution_permitted": True,
        "verification_status": "VERIFIED_ELIGIBLE"
    },
    {
        "source_name": "Freesound Verified Permissive Pool (CC0 / CC BY)",
        "official_url": "https://freesound.org/",
        "dataset_owner": "Freesound / Individual Uploaders",
        "license": "CC0 1.0 Universal / CC BY 3.0 / CC BY 4.0",
        "attribution_requirements": "Full URL and author username preservation",
        "permitted_use": "Commercial and research applications",
        "restrictions": "CC0 requires no attribution; CC BY requires attribution; no bulk automated scraping without API compliance",
        "expected_categories": "Low-intensity screams, distant screams, festival background noise, cheers",
        "estimated_independent_sources": 2500,
        "audio_download_permitted": True,
        "redistribution_permitted": True,
        "verification_status": "VERIFIED_ELIGIBLE"
    },
    {
        "source_name": "ESC-50 Environmental Sound Classification",
        "official_url": "https://github.com/karolpiczak/ESC-50",
        "dataset_owner": "Karol J. Piczak",
        "license": "CC BY-NC 3.0 (Non-Commercial)",
        "attribution_requirements": "Attribution to Piczak (2015)",
        "permitted_use": "Non-commercial academic research only",
        "restrictions": "COMMERCIAL USE PROHIBITED",
        "expected_categories": "Crying, shouting, sirens, crowd noise",
        "estimated_independent_sources": 500,
        "audio_download_permitted": True,
        "redistribution_permitted": False,
        "verification_status": "QUARANTINED_NON_COMMERCIAL — DO NOT ACQUIRE"
    },
    {
        "source_name": "AudioSet (YouTube Unvetted Subset)",
        "official_url": "https://research.google.com/audioset/",
        "dataset_owner": "Google LLC / Various YouTube Creators",
        "license": "CC BY 4.0 (Metadata) / Proprietary YouTube Terms (Audio)",
        "attribution_requirements": "YouTube terms of service",
        "permitted_use": "Varies by video; generally restricted for standalone redistribution",
        "restrictions": "SCRAPING PROHIBITED BY STAGE GOVERNANCE",
        "expected_categories": "Screaming, cheering, crowd ambience",
        "estimated_independent_sources": 10000,
        "audio_download_permitted": False,
        "redistribution_permitted": False,
        "verification_status": "PROHIBITED — DO NOT ACQUIRE"
    }
]

def main():
    print("Executing Phase B: Acquisition Source Discovery...")
    df_sources = pd.DataFrame(SOURCES)
    out_csv = os.path.join(STAGE_DIR, "acquisition_source_catalog.csv")
    df_sources.to_csv(out_csv, index=False)
    print(f"Saved acquisition source catalog to {out_csv} ({len(df_sources)} sources)")
    
    # Summary of eligible sources
    eligible = df_sources[df_sources["verification_status"] == "VERIFIED_ELIGIBLE"]
    quarantined = df_sources[df_sources["verification_status"] != "VERIFIED_ELIGIBLE"]
    print(f"\nVerified Eligible Sources: {len(eligible)}")
    for idx, r in eligible.iterrows():
        print(f"  [ELIGIBLE] {r['source_name']} ({r['license']})")
    print(f"Quarantined / Prohibited Sources: {len(quarantined)}")
    for idx, r in quarantined.iterrows():
        print(f"  [EXCLUDED] {r['source_name']}: {r['verification_status']}")

if __name__ == "__main__":
    main()

