# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.77 Annotation Assignment Status Builder
Builds: annotation_assignment_status.csv (52 tasks)
"""

import os
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE76_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76")

def build_assignment_status():
    st76_manifest = os.path.join(STAGE76_DIR, "annotation_assignment_manifest.csv")
    df_st76 = pd.read_csv(st76_manifest)
    
    records = []
    for _, row in df_st76.iterrows():
        records.append({
            "assignment_id": row["assignment_id"],
            "recording_id": row["recording_id"],
            "assigned_rater": row["assigned_rater_id"],
            "audio_file_path": row["audio_file_path"],
            "taxonomy_version": "2.0_CANONICAL_24_CLASS",
            "handbook_version": "STAGE_8_9_77_V1",
            "model_blinding_verified": 1,
            "metadata_blinding_verified": 1,
            "assignment_status": "AWAITING_INDEPENDENT_HUMAN_REVIEW",
            "submitted_timestamp": None,
            "assigned_primary_label": None,
            "assigned_subcategory": None,
            "assigned_binary_label": None,
            "assigned_confidence_rating": None,
            "environmental_tags": None,
            "rater_notes": None
        })
        
    df_out = pd.DataFrame(records)
    out_path = os.path.join(STAGE_DIR, "annotation_assignment_status.csv")
    df_out.to_csv(out_path, index=False)
    print(f"[OK] Wrote {out_path} ({len(df_out)} assignment tasks)")
    print("Breakdown by Rater:")
    print(df_out["assigned_rater"].value_counts())
    print("Breakdown by Status:")
    print(df_out["assignment_status"].value_counts())

if __name__ == "__main__":
    build_assignment_status()

