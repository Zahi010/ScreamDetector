# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.77 Adjudication Status Builder
Builds: adjudication_status.csv (26 rows staged for review)
"""

import os
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE76_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76")

def build_adjudication_status():
    prov_path = os.path.join(STAGE76_DIR, "acquisition_provenance.csv")
    df_prov = pd.read_csv(prov_path)
    
    st76_manifest = os.path.join(STAGE76_DIR, "annotation_assignment_manifest.csv")
    df_tasks = pd.read_csv(st76_manifest)
    
    # Map recording_id to rater tasks
    task_map = {}
    for _, row in df_tasks.iterrows():
        rec_id = row["recording_id"]
        rater = row["assigned_rater_id"]
        tid = row["assignment_id"]
        if rec_id not in task_map:
            task_map[rec_id] = {}
        task_map[rec_id][rater] = tid
        
    records = []
    for idx, row in df_prov.iterrows():
        rec_id = row["recording_id"]
        adj_id = f"ADJ_{idx+1:04d}"
        t_a = task_map.get(rec_id, {}).get("RATER_A", "")
        t_b = task_map.get(rec_id, {}).get("RATER_B", "")
        
        records.append({
            "adjudication_id": adj_id,
            "recording_id": rec_id,
            "rater_a_task_id": t_a,
            "rater_b_task_id": t_b,
            "rater_a_binary_label": None,
            "rater_b_binary_label": None,
            "binary_concordance": "PENDING",
            "rater_a_primary_label": None,
            "rater_b_primary_label": None,
            "category_concordance": "PENDING",
            "adjudication_required": "PENDING_REVIEW_SUBMISSION",
            "adjudication_status": "AWAITING_INITIAL_HUMAN_RATINGS",
            "adjudicator_id": None,
            "final_adjudicated_binary": None,
            "final_adjudicated_primary": None,
            "final_adjudicated_subcategory": None,
            "adjudication_notes": "Staged for adjudication upon completion of dual human reviews."
        })
        
    df_out = pd.DataFrame(records)
    out_path = os.path.join(STAGE_DIR, "adjudication_status.csv")
    df_out.to_csv(out_path, index=False)
    print(f"[OK] Wrote {out_path} ({len(df_out)} rows)")
    print("Adjudication status breakdown:")
    print(df_out["adjudication_status"].value_counts())

if __name__ == "__main__":
    build_adjudication_status()

