import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { FalsePositiveAnalysisModal } from '../components/ReviewStudio/FalsePositiveAnalysisModal'
import { ReviewSummaryCards } from '../components/ReviewStudio/ReviewSummaryCards'

const mockEvaluationReport = {
  evaluation_stage: 'Stage 8.9.3 — Human-Verified False-Positive Analysis',
  evaluated_at: '2026-10-28T16:00:00Z',
  model_metadata: {
    operating_threshold: 0.35,
    classifier_hash: 'ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f',
    metadata_hash: '30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60',
    artifacts_verified: true,
  },
  dataset_audit: {
    total_candidates: 370,
    audio_available: 343,
    missing_audio: 27,
    missing_model_scores: 27,
    reviewed_missing_scores_count: 0,
    reviewed_missing_scores_ids: [],
    total_human_decisions: 343,
    decision_counts: {
      APPROVED_NON_SCREAM: 338,
      SCREAM_PRESENT: 2,
      AMBIGUOUS: 3,
      EXCLUDED: 0,
      UNREVIEWED: 27,
    },
    unreviewed_count: 27,
  },
  binary_evaluation: {
    total_binary_evaluated: 340,
    negative_count_approved: 338,
    positive_count_scream: 2,
    excluded_ambiguous_count: 3,
    excluded_other_count: 0,
    confusion_matrix: {
      true_positives: 1,
      false_negatives: 1,
      true_negatives: 296,
      false_positives: 42,
    },
    metrics: {
      accuracy: 0.8735,
      precision: 0.0233,
      recall_sensitivity: 0.5,
      specificity: 0.8757,
      false_positive_rate: 0.1243,
      false_negative_rate: 0.5,
      f1_score: 0.0444,
      roc_auc: 0.5947,
      pr_auc: 0.0744,
    },
    statistical_limitation: {
      flagged: true,
      positive_count: 2,
      negative_count: 338,
      message: 'CAUTION: Positive sample size in evaluated hard-negative queue is very small (N=2). While the negative sample size (N=338) provides high statistical power for Specificity and False Positive Rate, metrics relying heavily on positive samples (Recall, Precision, F1-Score, and PR-AUC) have wide confidence intervals and must be interpreted with caution.',
    },
  },
  category_breakdown: [
    {
      category: 'shouting_and_speech',
      total_evaluated: 35,
      negatives: 34,
      positives: 1,
      true_negatives: 16,
      false_positives: 18,
      true_positives: 1,
      false_negatives: 0,
      false_positive_rate: 0.5294,
      mean_score: 0.5041,
      max_score: 1.0,
    },
    {
      category: 'whistles_and_squeaks',
      total_evaluated: 43,
      negatives: 43,
      positives: 0,
      true_negatives: 33,
      false_positives: 10,
      true_positives: 0,
      false_negatives: 0,
      false_positive_rate: 0.2326,
      mean_score: 0.2125,
      max_score: 1.0,
    },
  ],
  source_breakdown: [
    {
      source: 'fsd50k',
      total_evaluated: 312,
      negatives: 310,
      positives: 2,
      true_negatives: 270,
      false_positives: 40,
      true_positives: 1,
      false_negatives: 1,
      false_positive_rate: 0.129,
      mean_score: 0.12,
      max_score: 1.0,
    },
  ],
  false_positives: [
    {
      recording_id: 'fsd50k_254476',
      source_provider: 'fsd50k',
      proposed_category: 'infant_crying_archival',
      original_title: 'marvie_screech06.flac',
      creator: 'user_1',
      license: 'CC0',
      duration_seconds: 3.2,
      model_score: 1.0,
      model_alert: true,
      predicted_label: 'SCREAM',
      human_label: 'APPROVED_NON_SCREAM',
      reviewer_notes: 'High pitch screeching cry',
      reviewer_reason_code: 'INFANT_CRY',
      classification_outcome: 'FP',
      has_audio: true,
    },
  ],
  false_negatives: [
    {
      recording_id: 'fsd50k_349401',
      source_provider: 'fsd50k',
      proposed_category: 'crowd_cheering_applause',
      original_title: 'The crowd shouted Countdown.WAV',
      creator: 'user_2',
      license: 'CC-BY',
      duration_seconds: 5.0,
      model_score: 0.0,
      model_alert: false,
      predicted_label: 'NON_SCREAM',
      human_label: 'SCREAM_PRESENT',
      reviewer_notes: 'Contains scream in crowd',
      reviewer_reason_code: 'HUMAN_SCREAM',
      classification_outcome: 'FN',
      has_audio: true,
    },
  ],
  ambiguous_records: [
    {
      recording_id: 'fsd50k_999999',
      source_provider: 'fsd50k',
      proposed_category: 'infant_crying_archival',
      original_title: 'ambiguous_sound.wav',
      creator: 'user_3',
      license: 'CC0',
      duration_seconds: 2.1,
      model_score: 0.38,
      model_alert: true,
      predicted_label: 'SCREAM',
      human_label: 'AMBIGUOUS',
      reviewer_notes: 'Could be scream or baby cry',
      reviewer_reason_code: 'AMBIGUOUS_VOCAL',
      classification_outcome: 'AMBIGUOUS',
      has_audio: true,
    },
  ],
}

describe('Stage 8.9.3 Human-Verified False-Positive Analysis UI', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn((url) => {
        if (url.includes('/api/review/evaluation/report')) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => mockEvaluationReport,
          })
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({}),
        })
      })
    )
  })

  it('renders modal when isOpen is true with title and threshold', async () => {
    render(<FalsePositiveAnalysisModal isOpen={true} onClose={() => {}} />)

    expect(screen.getByTestId('fp-analysis-modal')).toBeInTheDocument()
    expect(screen.getByText('Human-Verified False-Positive Analysis')).toBeInTheDocument()
    expect(screen.getByText(/Threshold: 0.35/i)).toBeInTheDocument()
  })

  it('displays the statistical sample size limitation banner', async () => {
    render(<FalsePositiveAnalysisModal isOpen={true} onClose={() => {}} />)

    await waitFor(() => {
      expect(screen.getByTestId('statistical-limitation-banner')).toBeInTheDocument()
      expect(screen.getByText(/Statistical Sample Size Notice:/i)).toBeInTheDocument()
      expect(screen.getByText(/Ground Truth Class Distribution/i)).toBeInTheDocument()
    })
  })

  it('renders key performance metrics (accuracy, specificity, FPR, ROC-AUC)', async () => {
    render(<FalsePositiveAnalysisModal isOpen={true} onClose={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText('87.57%')).toBeInTheDocument() // Specificity
      expect(screen.getByText('12.43%')).toBeInTheDocument() // FPR
      expect(screen.getByText('87.35%')).toBeInTheDocument() // Accuracy
      expect(screen.getByText(/0.5947/)).toBeInTheDocument() // ROC-AUC
    })
  })

  it('renders the interactive 2x2 confusion matrix grid', async () => {
    render(<FalsePositiveAnalysisModal isOpen={true} onClose={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText('True Positive (TP)')).toBeInTheDocument()
      expect(screen.getByText('False Negative (FN)')).toBeInTheDocument()
      expect(screen.getByText('False Positive (FP)')).toBeInTheDocument()
      expect(screen.getByText('True Negative (TN)')).toBeInTheDocument()

      expect(screen.getByText('296')).toBeInTheDocument() // TN
      expect(screen.getByText('42')).toBeInTheDocument()  // FP
    })
  })

  it('renders category and source breakdown tables', async () => {
    render(<FalsePositiveAnalysisModal isOpen={true} onClose={() => {}} />)

    await waitFor(() => {
      expect(screen.getAllByText('shouting and speech').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('whistles and squeaks').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('fsd50k').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('renders false-positive items with audio player button and metadata', async () => {
    render(<FalsePositiveAnalysisModal isOpen={true} onClose={() => {}} />)

    await waitFor(() => {
      expect(screen.getByTestId('fp-item-fsd50k_254476')).toBeInTheDocument()
      expect(screen.getByText('marvie_screech06.flac')).toBeInTheDocument()
      expect(screen.getAllByText('APPROVED_NON_SCREAM').length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText(/SCREAM \(100.0%\)/)).toBeInTheDocument()
    })
  })

  it('triggers onOpenEvaluation when False-Positive Analysis button is clicked in ReviewSummaryCards', () => {
    const handleOpenEval = vi.fn()
    render(
      <ReviewSummaryCards
        summary={{
          total_candidates: 370,
          audio_available: 343,
          reviewed_count: 343,
          reviewed_percentage: 92.7,
          pending_review: 27,
          approved_non_scream: 338,
          scream_present: 2,
          ambiguous: 3,
          excluded: 0,
          missing_audio: 27,
          missing_model_scores: 27,
        }}
        onApplyPreset={() => {}}
        onTriggerEvaluation={() => {}}
        isEvaluating={false}
        onTriggerTriage={() => {}}
        isTriaging={false}
        onOpenRecovery={() => {}}
        onOpenEvaluation={handleOpenEval}
      />
    )

    const btn = screen.getByTestId('btn-open-evaluation')
    expect(btn).toBeInTheDocument()
    fireEvent.click(btn)
    expect(handleOpenEval).toHaveBeenCalledTimes(1)
  })
})
