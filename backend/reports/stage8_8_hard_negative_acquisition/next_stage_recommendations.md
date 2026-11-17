# Next-Stage Recommendations & Retraining Gate Protocol (Post-Stage 8.8)

## 1. Current State & Immediate Action Items
Stage 8.8 has automated discovery, licensing classification, deduplication, and quality control.
The candidate review queue has been generated in `review_queue.csv` with 370 tracked records.

### Next Command to Resume or Inspect:
```bash
# To view prioritized review queue:
python scripts/review_hard_negatives_queue.py --list

# To approve a candidate as verified non-scream after human listening:
python scripts/review_hard_negatives_queue.py --approve perm_whistle_01 --note "Verified referee whistle, no scream"

# To resume API acquisition once FREESOUND_API_KEY is configured in .env:
python scripts/download_hard_negatives.py --source freesound --resume
```

---

## 2. Hard Retraining Gate Requirements
Do NOT retrain the classifier until the following gate conditions are met:
1. **Minimum Reviewed Negatives**: At least 25 unique, human-approved non-scream recordings in Category 1 (Whistles/Squeaks), Category 2 (Crowd Cheering), and Category 3 (EDM Synthesizers).
2. **Acoustic Isolation**: Verify that no source-group collisions exist between newly approved negatives and the historical Stage 4 validation/test splits.
3. **No Mislabeled Screams**: Every newly added negative clip must be listened to by an operator to verify that enthusiastic cheering does not conceal an actual distress vocalization.
4. **Commercial Safety**: Only recordings with `CC0_VERIFIED` or `CC_BY_VERIFIED` status may be transferred to the training split. Non-commercial (`CC BY-NC`) recordings must be permanently segregated.

---

## 3. Recommended Roadmap for Stage 9 (Classifier Retraining & Calibration)
1. **Controlled Fine-Tuning**:
   - Add approved hard negatives into the training set only.
   - Maintain the frozen Stage 4 test set completely separate to benchmark true generalization.
2. **Evaluation Metrics**:
   - Measure whether the rave whistle false-alarm rate drops from ~90% down to < 5% while maintaining recall >= 88% at the 0.35 threshold.
3. **Threshold Calibration**:
   - Re-evaluate ROC-AUC, PR-AUC, and optimal operating threshold on the expanded validation set.
