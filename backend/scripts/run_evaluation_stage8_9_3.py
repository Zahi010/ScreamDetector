"""Script to evaluate frozen scream classifier against all 343 reviewed recordings (Stage 8.9.3).

Executes resumable inference on the 14 previously unscored recordings and
computes full binary classification metrics on human-reviewed ground truth.
"""

import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from src.dataset.false_positive_analyzer import get_false_positive_analyzer

def main():
    print("=" * 60)
    print("STAGE 8.9.3: RUNNING FROZEN CLASSIFIER INFERENCE ON REVIEWED RECORDINGS")
    print("=" * 60)

    analyzer = get_false_positive_analyzer()

    # Step 1: Run resumable inference on reviewed recordings with audio
    print("\n[Step 1] Checking and evaluating unscored reviewed recordings...")
    res = analyzer.run_inference_on_reviewed(force_reevaluate=False)
    print(f"  Inference evaluated : {res['evaluated_count']}")
    print(f"  Inference failures  : {res['failed_count']}")
    print(f"  Model alerts at 0.35: {res['alerts_count']}")

    # Step 2: Compute full evaluation report
    print("\n[Step 2] Generating Human-Verified Evaluation Report...")
    report = analyzer.compute_evaluation_report()

    meta = report["model_metadata"]
    print(f"\nModel Hash Verified : {meta['artifacts_verified']}")
    print(f"Classifier SHA-256  : {meta['classifier_hash']}")
    print(f"Decision Threshold  : {meta['operating_threshold']}")

    audit = report["dataset_audit"]
    print(f"\nTotal Candidates        : {audit['total_candidates']}")
    print(f"Audio Available         : {audit['audio_available']}")
    print(f"Total Human Decisions   : {audit['total_human_decisions']}")
    print(f"  - APPROVED_NON_SCREAM : {audit['decision_counts']['APPROVED_NON_SCREAM']}")
    print(f"  - SCREAM_PRESENT      : {audit['decision_counts']['SCREAM_PRESENT']}")
    print(f"  - AMBIGUOUS           : {audit['decision_counts']['AMBIGUOUS']}")
    print(f"  - EXCLUDED            : {audit['decision_counts']['EXCLUDED']}")
    print(f"  - UNREVIEWED (No audio): {audit['unreviewed_count']}")
    print(f"Missing Model Scores    : {audit['missing_model_scores']} (Expected: exactly the 27 unacquired clips)")
    print(f"Reviewed Missing Scores : {audit['reviewed_missing_scores_count']}")

    binary = report["binary_evaluation"]
    cm = binary["confusion_matrix"]
    m = binary["metrics"]

    print("\n" + "=" * 60)
    print("BINARY CLASSIFICATION METRICS (HUMAN GROUND TRUTH ONLY)")
    print("=" * 60)
    print(f"Total Binary Evaluated  : {binary['total_binary_evaluated']}")
    print(f"Negative Class (Approved): {binary['negative_count_approved']}")
    print(f"Positive Class (Screams) : {binary['positive_count_scream']}")
    print(f"Excluded Ambiguous      : {binary['excluded_ambiguous_count']}")
    print(f"Excluded Other          : {binary['excluded_other_count']}")

    print("\nConfusion Matrix:")
    print(f"  True Positives  (TP)  : {cm['true_positives']}")
    print(f"  False Positives (FP)  : {cm['false_positives']}")
    print(f"  True Negatives  (TN)  : {cm['true_negatives']}")
    print(f"  False Negatives (FN)  : {cm['false_negatives']}")

    print("\nPerformance Rates:")
    print(f"  Accuracy              : {m['accuracy'] * 100:.2f}%")
    print(f"  Precision             : {m['precision'] * 100:.2f}%")
    print(f"  Recall (Sensitivity)  : {m['recall_sensitivity'] * 100:.2f}%")
    print(f"  Specificity           : {m['specificity'] * 100:.2f}%")
    print(f"  False Positive Rate   : {m['false_positive_rate'] * 100:.2f}%")
    print(f"  False Negative Rate   : {m['false_negative_rate'] * 100:.2f}%")
    print(f"  F1 Score              : {m['f1_score']:.4f}")
    print(f"  ROC-AUC               : {m['roc_auc'] if m['roc_auc'] is not None else 'N/A'}")
    print(f"  PR-AUC                : {m['pr_auc'] if m['pr_auc'] is not None else 'N/A'}")

    lim = binary["statistical_limitation"]
    if lim["flagged"]:
        print(f"\n[STATISTICAL LIMITATION FLAG]\n  {lim['message']}")

    print("\n" + "=" * 60)
    print("FALSE POSITIVE BREAKDOWN BY SOUND CATEGORY")
    print("=" * 60)
    for cat in report["category_breakdown"]:
        print(f"  {cat['category']:<28}: Total={cat['total_evaluated']:<3} FP={cat['false_positives']:<3} TN={cat['true_negatives']:<3} FPR={cat['false_positive_rate']*100:.1f}% MeanScore={cat['mean_score']:.3f} MaxScore={cat['max_score']:.3f}")

    print("\n" + "=" * 60)
    print("FALSE POSITIVE BREAKDOWN BY SOURCE")
    print("=" * 60)
    for src in report["source_breakdown"]:
        print(f"  {src['source']:<15}: Total={src['total_evaluated']:<3} FP={src['false_positives']:<3} TN={src['true_negatives']:<3} FPR={src['false_positive_rate']*100:.1f}%")

    print("\n" + "=" * 60)
    print(f"TOP FALSE POSITIVES ({len(report['false_positives'])} total):")
    print("=" * 60)
    for fp in report["false_positives"][:10]:
        title_safe = fp['original_title'][:40].encode('ascii', errors='replace').decode('ascii')
        print(f"  [{fp['recording_id']}] Score: {fp['model_score']:.4f} | Cat: {fp['proposed_category']} | Src: {fp['source_provider']} | Title: {title_safe}")

    print("\n" + "=" * 60)
    print(f"FALSE NEGATIVES ({len(report['false_negatives'])} total):")
    print("=" * 60)
    for fn in report["false_negatives"]:
        title_safe = fn['original_title'][:40].encode('ascii', errors='replace').decode('ascii')
        print(f"  [{fn['recording_id']}] Score: {fn['model_score']:.4f} | Cat: {fn['proposed_category']} | Title: {title_safe}")

    print("\n" + "=" * 60)
    print("TRUE POSITIVES (1 total):")
    print("=" * 60)
    for tp in report.get("binary_evaluation", {}).get("confusion_matrix", {}):
        pass
    with analyzer.store._get_connection() as conn:
        tp_rows = conn.execute("SELECT recording_id, model_score, proposed_category, original_title_description FROM candidates WHERE review_status = 'SCREAM_PRESENT' AND model_score >= 0.35").fetchall()
        for tp in tp_rows:
            title_safe = (tp['original_title_description'] or '')[:40].encode('ascii', errors='replace').decode('ascii')
            print(f"  [{tp['recording_id']}] Score: {tp['model_score']:.4f} | Cat: {tp['proposed_category']} | Title: {title_safe}")

if __name__ == "__main__":
    main()
