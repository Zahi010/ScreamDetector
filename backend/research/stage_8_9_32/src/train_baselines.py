import os
import csv
import json
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    recall_score, precision_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, accuracy_score
)

def evaluate_predictions(y_true, y_prob, threshold=0.35):
    y_pred = (y_prob >= threshold).astype(int)
    rec = recall_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc_auc = 0.5
    try:
        pr_auc = average_precision_score(y_true, y_prob)
    except Exception:
        pr_auc = 0.0
    
    # Specificity and FPR
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    spec = tn / (tn + fp + 1e-9)
    fpr = fp / (fp + tn + 1e-9)
    
    return {
        'recall': rec,
        'precision': prec,
        'f1': f1,
        'accuracy': acc,
        'specificity': spec,
        'fpr': fpr,
        'roc_auc': roc_auc,
        'pr_auc': pr_auc,
        'tp': int(tp),
        'fp': int(fp),
        'fn': int(fn),
        'tn': int(tn)
    }

def main():
    print("=== STAGE 8.9.32 - PHASE 4: BASELINE RESEARCH MODELS ===")
    os.makedirs('backend/research/stage_8_9_32/models/baselines', exist_ok=True)
    os.makedirs('backend/research/stage_8_9_32/experiments', exist_ok=True)
    
    # Load dataset
    data_path = 'backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz'
    data = np.load(data_path, allow_pickle=True)
    
    file_ids = data['file_ids']
    splits = data['splits']
    binary_labels = data['binary_labels']
    categories = data['categories']
    source_groups = data['source_groups']
    X = data['features_mean'] # 1024-dim mean-pooled YAMNet embeddings
    
    # Filter ambiguous
    valid_idx = np.where(binary_labels != 'ambiguous')[0]
    file_ids = file_ids[valid_idx]
    splits = splits[valid_idx]
    binary_labels = binary_labels[valid_idx]
    categories = categories[valid_idx]
    source_groups = source_groups[valid_idx]
    X = X[valid_idx]
    
    y = np.array([1 if b == 'scream' else 0 for b in binary_labels])
    
    train_mask = (splits == 'train')
    val_mask = (splits == 'val')
    test_mask = (splits == 'test')
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_val, y_val = X[val_mask], y[val_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print(f"Dataset Partitions:")
    print(f"  Train: {len(X_train)} samples ({sum(y_train)} screams, {len(y_train)-sum(y_train)} hard negatives)")
    print(f"  Val:   {len(X_val)} samples ({sum(y_val)} screams, {len(y_val)-sum(y_val)} hard negatives)")
    print(f"  Test:  {len(X_test)} samples ({sum(y_test)} screams, {len(y_test)-sum(y_test)} hard negatives)")
    
    # Define baselines
    models = {
        'Baseline_A_LogisticRegression': LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        'Baseline_B_ClassWeighted_LR': LogisticRegression(C=1.0, class_weight='balanced', max_iter=1000, random_state=42),
        'Baseline_C_RandomForest': RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        'Baseline_D_MLP': MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=250, random_state=42, early_stopping=True)
    }
    
    comparison_rows = []
    registry_rows = []
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        # Save model
        save_path = f"backend/research/stage_8_9_32/models/baselines/{name}.joblib"
        joblib.dump(model, save_path)
        
        # Evaluate on Val
        val_probs = model.predict_proba(X_val)[:, 1]
        val_metrics = evaluate_predictions(y_val, val_probs, threshold=0.35)
        
        # Evaluate on Test
        test_probs = model.predict_proba(X_test)[:, 1]
        test_metrics = evaluate_predictions(y_test, test_probs, threshold=0.35)
        
        # Compute category specific FPRs on test set
        test_cats = categories[test_mask]
        cheer_idx = np.where((test_cats == 'crowd_chant_cheering'))[0]
        crying_idx = np.where((test_cats == 'infant_crying'))[0]
        shout_idx = np.where((test_cats == 'shouting_and_speech'))[0]
        
        cheer_fpr = float(np.mean(test_probs[cheer_idx] >= 0.35)) if len(cheer_idx) > 0 else 0.0
        crying_fpr = float(np.mean(test_probs[crying_idx] >= 0.35)) if len(crying_idx) > 0 else 0.0
        shout_fpr = float(np.mean(test_probs[shout_idx] >= 0.35)) if len(shout_idx) > 0 else 0.0
        
        print(f"  Test Recall: {test_metrics['recall']*100:.2f}%, FPR: {test_metrics['fpr']*100:.2f}%, Cheering FPR: {cheer_fpr*100:.2f}%, Crying FPR: {crying_fpr*100:.2f}%, ROC-AUC: {test_metrics['roc_auc']:.4f}")
        
        comparison_rows.append({
            'model_name': name,
            'val_recall_pct': f"{val_metrics['recall']*100:.2f}%",
            'val_fpr_pct': f"{val_metrics['fpr']*100:.2f}%",
            'val_f1': f"{val_metrics['f1']:.4f}",
            'val_roc_auc': f"{val_metrics['roc_auc']:.4f}",
            'test_recall_pct': f"{test_metrics['recall']*100:.2f}%",
            'test_precision_pct': f"{test_metrics['precision']*100:.2f}%",
            'test_fpr_pct': f"{test_metrics['fpr']*100:.2f}%",
            'test_f1': f"{test_metrics['f1']:.4f}",
            'test_roc_auc': f"{test_metrics['roc_auc']:.4f}",
            'test_pr_auc': f"{test_metrics['pr_auc']:.4f}",
            'test_cheering_fpr_pct': f"{cheer_fpr*100:.2f}%",
            'test_crying_fpr_pct': f"{crying_fpr*100:.2f}%",
            'test_shouting_fpr_pct': f"{shout_fpr*100:.2f}%",
            'artifact_path': save_path
        })
        
        registry_rows.append({
            'model_name': name,
            'architecture': str(model.__class__.__name__),
            'input_feature_dim': 1024,
            'decision_threshold': 0.35,
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'artifact_path': save_path
        })
    
    # Save baseline_model_comparison.csv
    p_comp = 'backend/research/stage_8_9_32/experiments/baseline_model_comparison.csv'
    with open(p_comp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(comparison_rows[0].keys()))
        w.writeheader()
        w.writerows(comparison_rows)
    print(f"\nSaved {p_comp}")
    
    # Save baseline_experiment_registry.csv
    p_reg = 'backend/research/stage_8_9_32/experiments/baseline_experiment_registry.csv'
    with open(p_reg, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(registry_rows[0].keys()))
        w.writeheader()
        w.writerows(registry_rows)
    print(f"Saved {p_reg}")

if __name__ == '__main__':
    main()
