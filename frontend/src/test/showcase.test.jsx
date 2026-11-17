import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Header } from '../components/Header'
import { ExperimentalShowcase } from '../components/ExperimentalShowcase'

describe('Stage 8.9.14 Experimental Showcase Tests', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        model_id: 'D_v4_plus_Family_A',
        model_name: 'D_v4 + Family A (Stage 8.9.14 Acoustic Discriminability Model)',
        model_badge: 'EXPERIMENTAL DEMONSTRATION MODEL — NOT PRODUCTION CERTIFIED',
        selection_rationale:
          'Selected because it provides the strongest reported balance of event recall (90.83%), hard-negative control (7.07%), shouting rejection (9.52%), crowd rejection (11.63%), and edge streaming latency (15.40 ms) among all evaluated candidates.',
        production_model_status: 'STRICTLY FROZEN (Stage 5 Logistic Regression, Threshold: 0.3500)',
        last_evaluation_stage: 'Stage 8.9.14 (Stage 8.9.15 candidates rejected)',
        live_inference_notice:
          'Live microphone streaming executes on the verified Production Baseline (Threshold: 0.3500). Experimental benchmark metrics are shown separately for evaluation.',
        safety_notice:
          'Possible scream detected — requires human auditory verification. Automated acoustic alerts do not confirm an emergency.',
        reported_metrics: {
          event_recall_pct: 90.83,
          hard_negative_fpr_pct: 7.07,
          shouted_speech_fpr_pct: 9.52,
          crowd_fpr_pct: 11.63,
          short_scream_recall_pct: 100.0,
          short_screams_detected_vs_total: '5/5',
          brief_scream_recall_1_5s_pct: 92.31,
          brief_screams_detected_vs_total: '24/26',
          pr_auc: 0.9231,
          roc_auc: 0.957,
          precision: 0.8761,
          f1_score: 0.8919,
          median_latency_ms: 15.4,
          p95_latency_ms: 19.24,
          operating_threshold: 0.42,
        },
        acceptance_gates: [
          {
            gate_name: 'Event-Level Scream Recall',
            metric_target: '>= 96.0%',
            reported_value: '90.83%',
            gate_status: 'FAIL',
            notes: 'Misses 10 out of 109 scream events on held-out test split.',
          },
          {
            gate_name: 'Short-Scream Recall (< 1.0s)',
            metric_target: '>= 90.0%',
            reported_value: '100.0% (5/5)',
            gate_status: 'PRELIMINARY_UNCONFIRMED',
            notes: 'Cohort size N=5 is critically small and does not constitute certified proof.',
          },
          {
            gate_name: 'Hard-Negative Event FPR',
            metric_target: '<= 5.0%',
            reported_value: '7.07%',
            gate_status: 'FAIL',
            notes: '14 false alarms out of 198 hard negatives.',
          },
          {
            gate_name: 'Shouted-Speech FPR',
            metric_target: '<= 15.0%',
            reported_value: '9.52%',
            gate_status: 'PASS',
            notes: '4 false alarms out of 42 shouting/speech files.',
          },
          {
            gate_name: 'End-to-End Latency',
            metric_target: '<= 25.0 ms',
            reported_value: '15.40 ms (p95: 19.24 ms)',
            gate_status: 'PASS',
            notes: '60.8% of available 25.0 ms edge streaming budget consumed.',
          },
        ],
        model_comparison: [
          {
            model_id: 'D_v4_plus_Family_A',
            model_name: 'D_v4 + Family A (Turbulence)',
            architecture_type: 'Linear Logistic Regression (3,080 dims)',
            operating_threshold: 0.42,
            event_recall_pct: 90.83,
            hard_negative_fpr_pct: 7.07,
            shouted_speech_fpr_pct: 9.52,
            crowd_fpr_pct: 11.63,
            latency_ms: 15.4,
            p95_latency_ms: 19.24,
            short_scream_recall_pct: 100.0,
            pr_auc: 0.9231,
            is_recommended_demo: true,
            verdict: 'REJECTED — ACCEPTANCE CRITERIA NOT MET',
          },
          {
            model_id: 'D_v4_plus_Family_B',
            model_name: 'D_v4 + Family B (Spectral Dynamics)',
            architecture_type: 'Linear Logistic Regression (3,080 dims)',
            operating_threshold: 0.65,
            event_recall_pct: 81.65,
            hard_negative_fpr_pct: 4.55,
            shouted_speech_fpr_pct: 7.14,
            crowd_fpr_pct: 4.65,
            latency_ms: 15.4,
            p95_latency_ms: 19.24,
            short_scream_recall_pct: 80.0,
            pr_auc: 0.9229,
            is_recommended_demo: false,
            verdict: 'REJECTED — ACCEPTANCE CRITERIA NOT MET',
          },
          {
            model_id: 'F_v6_Acoustic_Full',
            model_name: 'F_v6 Acoustic Full (30 Acoustic Features)',
            architecture_type: 'Linear Logistic Regression (3,102 dims)',
            operating_threshold: 0.36,
            event_recall_pct: 87.16,
            hard_negative_fpr_pct: 6.57,
            shouted_speech_fpr_pct: 9.52,
            crowd_fpr_pct: 6.98,
            latency_ms: 15.4,
            p95_latency_ms: 19.24,
            short_scream_recall_pct: 80.0,
            pr_auc: 0.9134,
            is_recommended_demo: false,
            verdict: 'REJECTED — ACCEPTANCE CRITERIA NOT MET',
          },
          {
            model_id: 'Stage_8_9_15_Temporal_CNN',
            model_name: 'Stage 8.9.15 Temporal Dilated CNN',
            architecture_type: 'Deep 1D Dilated Residual CNN (70x1024 + 30 ac)',
            operating_threshold: 0.61,
            event_recall_pct: 94.5,
            hard_negative_fpr_pct: 17.17,
            shouted_speech_fpr_pct: 21.43,
            crowd_fpr_pct: 25.58,
            latency_ms: 55.63,
            p95_latency_ms: 71.23,
            short_scream_recall_pct: 80.0,
            pr_auc: 0.8992,
            is_recommended_demo: false,
            verdict: 'REJECTED — ACCEPTANCE CRITERIA NOT MET',
          },
          {
            model_id: 'Production_Baseline',
            model_name: 'Production Baseline (Stage 5)',
            architecture_type: 'Linear Logistic Regression (1,024 dims)',
            operating_threshold: 0.35,
            event_recall_pct: 87.16,
            hard_negative_fpr_pct: 10.1,
            shouted_speech_fpr_pct: 16.67,
            crowd_fpr_pct: 13.95,
            latency_ms: 16.62,
            p95_latency_ms: 20.15,
            short_scream_recall_pct: 80.0,
            pr_auc: 0.8845,
            is_recommended_demo: false,
            verdict: 'FROZEN PRODUCTION MODEL',
          },
        ],
        confusion_matrix: {
          true_positives: 99,
          false_negatives: 10,
          false_positives: 14,
          true_negatives: 184,
          total_eval_samples: 307,
          precision_pct: 87.61,
          specificity_pct: 92.93,
          f1_pct: 89.19,
          derivation_note:
            'Derived from Stage 8.9.14 single-shot held-out test evaluation cohort (109 screams, 198 hard negatives at threshold 0.4200).',
        },
        dataset_cohort: {
          total_held_out: 307,
          scream_events: 109,
          hard_negatives: 198,
          short_screams_under_1s: 5,
          short_screams_recall_pct: 100.0,
          brief_screams_up_to_1_5s: 26,
          brief_screams_recall_pct: 92.31,
          provenance_license: 'Strictly isolated source groups; CC0, CC BY, and cleared academic sources only.',
          environment_disclaimer:
            'Reported evaluation reflects curated dataset distributions; real-world festival acoustic variability remains uncertified.',
        },
        stage_history: [
          {
            stage_id: 'Stage 8.9.14',
            stage_title: 'Acoustic Discriminability Research',
            status: 'COMPLETED',
            summary:
              'D_v4 + Family A identified as the strongest balanced candidate model (90.83% recall, 7.07% FPR, 15.40 ms latency). All candidates failed simultaneous acceptance criteria.',
          },
          {
            stage_id: 'Stage 8.9.15',
            stage_title: 'Hierarchical Phonation Discrimination',
            status: 'COMPLETED (REJECTED)',
            summary:
              'Investigated 2-stage distress gating and temporal dilated CNN. All candidates rejected due to 152.97 ms latency breach, crowd FPR surge to 20.93%, and short-scream recall drop to 80.0%.',
          },
          {
            stage_id: 'Stage 8.9.16',
            stage_title: 'Lightweight Event-Aware Research',
            status: 'PENDING_AUTHORIZATION',
            summary:
              'Not started. Production classifier and threshold remain strictly frozen awaiting explicit team direction.',
          },
        ],
        what_system_can_demonstrate: [
          'Acoustic Scream Detection: 90.83% event recall on held-out test split.',
          'Shouting Rejection: Shouted-speech FPR controlled to 9.52% (passing the <= 15% gate).',
          'Crowd-Noise Discrimination: Crowd chanting and cheering FPR benchmarked at 11.63%.',
          'Short-Event Sensitivity: 100.0% recall on initial 5-example short-scream test cohort (< 1.0s).',
          'Sub-20 ms Real-Time Streaming Latency: 15.40 ms median, 19.24 ms p95 (passing the <= 25 ms gate).',
        ],
        current_limitations: [
          'Event recall remains at 90.83%, failing the >= 96.0% safety-critical target.',
          'Hard-negative event FPR remains at 7.07%, failing the <= 5.0% operational false-alarm target.',
          'Short-scream test cohort is critically small (N=5 test examples); 100% recall is preliminary and uncertified.',
          'High-pitch shouting (F0 > 700 Hz with subharmonic bifurcation) remains an irreducible acoustic false-positive mode.',
          'Real-world festival environment performance with extreme crowd reverberation and pyrotechnics is not yet certified.',
        ],
      }),
    })
  })

  it('renders top status header strip and Model Showcase navigation button', () => {
    const handleSelectTab = vi.fn()
    const handleTogglePresent = vi.fn()

    render(
      <Header
        connectionStatus="connected"
        detectorStatus={{ is_running: true, mic_status: 'active' }}
        activeTab="showcase"
        onSelectTab={handleSelectTab}
        isPresentationMode={false}
        onTogglePresentationMode={handleTogglePresent}
      />
    )

    // Verify top status strip per Section 3.A
    expect(screen.getByText('FESTIVAL SCREAM DETECTION SYSTEM')).toBeInTheDocument()
    expect(screen.getByText('AI Acoustic Monitoring')).toBeInTheDocument()
    expect(screen.getByText('EXPERIMENTAL DEMONSTRATION MODE')).toBeInTheDocument()
    expect(screen.getByText('D_v4 + Family A')).toBeInTheDocument()
    expect(screen.getByText('Frozen (0.3500)')).toBeInTheDocument()
    expect(screen.getByText('Stage 8.9.14')).toBeInTheDocument()

    // Verify navigation tabs
    const showcaseTab = screen.getByText('Model Showcase')
    expect(showcaseTab).toBeInTheDocument()
    fireEvent.click(showcaseTab)
    expect(handleSelectTab).toHaveBeenCalledWith('showcase')

    // Verify Presentation Mode toggle
    const presentBtn = screen.getByText('Present')
    expect(presentBtn).toBeInTheDocument()
    fireEvent.click(presentBtn)
    expect(handleTogglePresent).toHaveBeenCalled()
  })

  it('renders experimental warning banner and disclaimer clearly', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(
        screen.getByText('EXPERIMENTAL DEMONSTRATION MODEL — NOT PRODUCTION CERTIFIED')
      ).toBeInTheDocument()
    })

    expect(
      screen.getByText(/OFFLINE BENCHMARK NOTICE:/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/The live inference pipeline remains frozen on the Stage 5 production baseline/i)
    ).toBeInTheDocument()
  })

  it('renders performance overview cards with exact reported values and pass/fail gate statuses', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(screen.getAllByText('90.83%').length).toBeGreaterThanOrEqual(1)
    })

    // Metric values in cards and comparison table
    expect(screen.getAllByText('7.07%').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('9.52%').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('11.63%').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('15.40 ms')).toBeInTheDocument()
    expect(screen.getByText('19.24 ms')).toBeInTheDocument()

    // Pass / Fail status badges
    const failBadges = screen.getAllByText('FAIL')
    expect(failBadges.length).toBeGreaterThanOrEqual(2) // Recall and Hard-negative FPR fail

    const passBadges = screen.getAllByText('PASS')
    expect(passBadges.length).toBeGreaterThanOrEqual(2) // Shouting FPR and Latency pass

    expect(screen.getByText(/OVERALL STATUS: REJECTED/i)).toBeInTheDocument()
  })

  it('renders model comparison table for all candidate models and selection rationale', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText(/Candidate Architecture Comparison/i)).toBeInTheDocument()
    })

    // 5 candidate models
    expect(screen.getByText('D_v4 + Family A (Turbulence)')).toBeInTheDocument()
    expect(screen.getByText('D_v4 + Family B (Spectral Dynamics)')).toBeInTheDocument()
    expect(screen.getByText('F_v6 Acoustic Full (30 Acoustic Features)')).toBeInTheDocument()
    expect(screen.getByText('Stage 8.9.15 Temporal Dilated CNN')).toBeInTheDocument()
    expect(screen.getByText('Production Baseline (Stage 5)')).toBeInTheDocument()

    // Candidate recommended badge
    expect(screen.getByText('★ RECOMMENDED DEMO')).toBeInTheDocument()

    // Selection rationale callout
    expect(screen.getByText(/Technical Rationale for Showcase Selection:/i)).toBeInTheDocument()
    expect(screen.getByText(/balanced performance, rather than maximum recall alone/i)).toBeInTheDocument()
  })

  it('renders confusion matrix derived from the held-out evaluation cohort', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText(/Held-Out Test Confusion Matrix/i)).toBeInTheDocument()
    })

    // Exact derived values: TP: 99, FN: 10, FP: 14, TN: 184
    expect(screen.getByText('99')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('14')).toBeInTheDocument()
    expect(screen.getByText('184')).toBeInTheDocument()

    // Summary statistics
    expect(screen.getByText('87.61%')).toBeInTheDocument() // Precision
    expect(screen.getByText('92.93%')).toBeInTheDocument() // Specificity
    expect(screen.getByText('89.19%')).toBeInTheDocument() // F1-score
  })

  it('renders dataset cohort breakdown with explicit small sample caveat for short screams', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText(/Evaluation Cohort & Duration Breakdown/i)).toBeInTheDocument()
    })

    expect(screen.getByText('307')).toBeInTheDocument()
    expect(screen.getByText('109')).toBeInTheDocument()
    expect(screen.getByText('198')).toBeInTheDocument()
    expect(screen.getByText('5 / 5 (100%)')).toBeInTheDocument()
    expect(screen.getByText('24 / 26 (92.3%)')).toBeInTheDocument()
    expect(screen.getByText(/STATISTICAL SAMPLE SIZE NOTE:/i)).toBeInTheDocument()
    expect(screen.getByText(/reflects exactly 5 test examples/i)).toBeInTheDocument()
  })

  it('renders research stage history showing Stage 8.9.15 rejection and Stage 8.9.16 pending', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText(/Research & Model Evolution Timeline/i)).toBeInTheDocument()
    })

    expect(screen.getByText(/Stage 8.9.14: Acoustic Discriminability Research/i)).toBeInTheDocument()
    expect(screen.getByText(/Stage 8.9.15: Hierarchical Phonation Discrimination/i)).toBeInTheDocument()
    expect(screen.getByText(/Stage 8.9.16: Lightweight Event-Aware Research/i)).toBeInTheDocument()

    expect(screen.getByText('COMPLETED (REJECTED)')).toBeInTheDocument()
    expect(screen.getByText('PENDING_AUTHORIZATION')).toBeInTheDocument()
  })

  it('renders presentation spotlight: capabilities vs limitations', async () => {
    render(<ExperimentalShowcase isPresentationMode={false} onTogglePresentationMode={() => {}} />)

    await waitFor(() => {
      expect(screen.getByText('What the System Can Currently Demonstrate')).toBeInTheDocument()
    })

    expect(screen.getByText('Current Engineering Limitations & Open Gates')).toBeInTheDocument()
    expect(screen.getByText(/High-pitch shouting \(F0 > 700 Hz/i)).toBeInTheDocument()
    expect(screen.getByText(/Event recall remains at 90.83%, failing the >= 96.0% safety-critical target/i)).toBeInTheDocument()
  })
})
