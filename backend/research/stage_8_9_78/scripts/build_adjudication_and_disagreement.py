# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
Stage 8.9.78 Adjudication & Disagreement Builder
Generates:
1. disagreement_analysis.csv (0 disagreements currently flagged)
2. adjudication_status.csv (26 rows staged for review)
"""

import os
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE77_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_77")
STAGE76_DIR = os.path.join(PROJECT_ROOT, "backend", "research", "stage_8_9_76")

def build_adjudication_and_disagreement():
    # 1. Build disagreement_analysis.csv (schema with 0 active disagreements)
    disagree_cols = [
        "disagreement_id", "recording_id", "rater_a_task_id", "rater_b_task_id",
        "rater_a_primary_label", "rater_b_primary_label", "rater_a_binary", "rater_b_binary",
        "disagreement_type", "adjudication_status", "escalation_timestamp", "notes"
    ]
    df_disagree = pd.DataFrame(columns=disagree_cols)
    disagree_path = os.path.join(STAGE_DIR, "disagreement_analysis.csv")
    df_disagree.to_csv(disagree_path, index=False)
    print(f"[OK] Wrote {disagree_path} (0 active disagreements)")
    
    # 2. Build adjudication_status.csv (26 staged items)
    prov_path = os.path.join(STAGE76_DIR, "acquisition_provenance.csv")
    df_prov = pd.read_csv(prov_path)
    
    assign_path = os.path.join(STAGE77_DIR, "annotation_assignment_status.csv")
    df_assign = pd.read_csv(assign_path)
    
    rec_to_a = {r["recording_id"]: r["assignment_id"] for _, r in df_assign[df_assign["assigned_rater"] == "RATER_A"].iterrows()}
    rec_to_b = {r["recording_id"]: r["assignment_id"] for _, r in df_assign[df_assign["assigned_rater"] == "RATER_B"].iterrows()}
    
    adj_rows = []
    for idx, row in df_prov.iterrows():
        rec_id = row["recording_id"]
        adj_id = f"ADJ_{idx+1:04d}"
        
        adj_rows.append({
            "adjudication_id": adj_id,
            "recording_id": rec_id,
            "rater_a_task_id": rec_to_a.get(rec_id),
            "rater_b_task_id": rec_to_b.get(rec_id),
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
        
    df_adj = pd.DataFrame(adj_rows)
    adj_path = os.path.join(STAGE_DIR, "adjudication_status.csv")
    df_adj.to_csv(adj_path, index=False)
    print(f"[OK] Wrote {adj_path} ({len(df_adj)} rows)")

if __name__ == "__main__":
    build_adjudication_and_disagreement()

