import { useState, useEffect } from 'react'

export function ExperimentalShowcase({ isPresentationMode, onTogglePresentationMode }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeChartMetric, setActiveChartMetric] = useState('all')

  useEffect(() => {
    let isMounted = true
    const fetchDemoMetrics = async () => {
      try {
        setLoading(true)
        const res = await fetch('/api/experimental/demo-metrics')
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to load demonstration metrics`)
        const json = await res.json()
        if (isMounted) {
          setData(json)
          setError(null)
        }
      } catch (err) {
        console.error('Error fetching demonstration metrics:', err)
        if (isMounted) setError(err.message)
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    fetchDemoMetrics()
    return () => {
      isMounted = false
    }
  }, [])

  // Static fallback data matching reported Stage 8.9.14 evaluation exactly
  const demoData = data || {
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
  }

  const { reported_metrics: m, acceptance_gates: gates, model_comparison: models, confusion_matrix: cm, dataset_cohort: dc } = demoData

  return (
    <div className={`showcase-container ${isPresentationMode ? 'presentation-mode' : ''}`}>
      {/* Top Warning Banner */}
      <div className="showcase-warning-banner">
        <div className="warning-icon-wrapper">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>
        <div className="warning-text-content">
          <div className="warning-title-row">
            <span className="warning-badge-pill">{demoData.model_badge}</span>
            <span className="warning-status-pill">{demoData.production_model_status}</span>
            <button
              type="button"
              className={`btn-presentation-toggle ${isPresentationMode ? 'active' : ''}`}
              onClick={onTogglePresentationMode}
              title="Toggle Presentation Mode (uncluttered, high-contrast display for team demonstration)"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <line x1="8" y1="21" x2="16" y2="21"></line>
                <line x1="12" y1="17" x2="12" y2="21"></line>
              </svg>
              <span>{isPresentationMode ? 'Exit Presentation Mode' : 'Presentation Mode'}</span>
            </button>
          </div>
          <p className="warning-description">
            <strong>OFFLINE BENCHMARK NOTICE:</strong> The metrics below are authoritative offline evaluation results from Stage 8.9.14 on a curated held-out test cohort (307 recordings). They do <strong>not</strong> represent guaranteed live microphone accuracy in live festival spaces. The live inference pipeline remains frozen on the Stage 5 production baseline.
          </p>
        </div>
      </div>

      {/* Presentation Spotlight: What it demonstrates vs Current Limitations */}
      <section className="presentation-spotlight-grid">
        <div className="card spotlight-card capabilities-card">
          <div className="card-header">
            <h2 className="card-title text-emerald">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              What the System Can Currently Demonstrate
            </h2>
            <span className="badge-pass font-mono text-xs">STAGE 8.9.14 VALIDATED</span>
          </div>
          <ul className="spotlight-list">
            {demoData.what_system_can_demonstrate.map((item, idx) => (
              <li key={idx} className="spotlight-list-item">
                <span className="spotlight-bullet bullet-emerald">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card spotlight-card limitations-card">
          <div className="card-header">
            <h2 className="card-title text-amber">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              Current Engineering Limitations & Open Gates
            </h2>
            <span className="badge-fail font-mono text-xs">UNRESOLVED CHALLENGES</span>
          </div>
          <ul className="spotlight-list">
            {demoData.current_limitations.map((item, idx) => (
              <li key={idx} className="spotlight-list-item">
                <span className="spotlight-bullet bullet-amber">⚠</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Performance Overview Metric Cards */}
      <section className="overview-metrics-section">
        <div className="section-title-row">
          <div>
            <h2 className="section-title">Model Performance Overview — {demoData.model_name}</h2>
            <p className="section-subtitle">
              Evaluating D_v4 + Family A against pre-registered safety-critical acceptance gates (Operating Threshold: {m.operating_threshold.toFixed(2)})
            </p>
          </div>
          <div className="overall-verdict-tag tag-rejected">
            OVERALL STATUS: REJECTED (GATES UNMET)
          </div>
        </div>

        <div className="metrics-grid-6">
          {/* Card 1: Event Recall */}
          <div className="metric-card card-gate-fail">
            <div className="metric-card-top">
              <span className="metric-label">Event-Level Scream Recall</span>
              <span className="gate-badge gate-fail">FAIL</span>
            </div>
            <div className="metric-number-row">
              <span className="metric-number text-fail">{m.event_recall_pct.toFixed(2)}%</span>
              <span className="metric-delta">Target: ≥ 96.0%</span>
            </div>
            <div className="metric-progress-wrapper">
              <div className="metric-progress-track">
                <div className="metric-progress-fill fill-fail" style={{ width: `${m.event_recall_pct}%` }}></div>
                <div className="metric-target-line" style={{ left: '96%' }} title="Target: 96%"></div>
              </div>
            </div>
            <span className="metric-sub font-mono">99 / 109 scream events detected</span>
          </div>

          {/* Card 2: Hard-Negative FPR */}
          <div className="metric-card card-gate-fail">
            <div className="metric-card-top">
              <span className="metric-label">Hard-Negative Event FPR</span>
              <span className="gate-badge gate-fail">FAIL</span>
            </div>
            <div className="metric-number-row">
              <span className="metric-number text-fail">{m.hard_negative_fpr_pct.toFixed(2)}%</span>
              <span className="metric-delta">Target: ≤ 5.0%</span>
            </div>
            <div className="metric-progress-wrapper">
              <div className="metric-progress-track">
                <div className="metric-progress-fill fill-fail" style={{ width: `${Math.min(100, m.hard_negative_fpr_pct * 4)}%` }}></div>
                <div className="metric-target-line" style={{ left: '20%' }} title="Target: 5% (scaled)"></div>
              </div>
            </div>
            <span className="metric-sub font-mono">14 / 198 hard negatives false alarmed</span>
          </div>

          {/* Card 3: Shouting FPR */}
          <div className="metric-card card-gate-pass">
            <div className="metric-card-top">
              <span className="metric-label">Shouted-Speech FPR</span>
              <span className="gate-badge gate-pass">PASS</span>
            </div>
            <div className="metric-number-row">
              <span className="metric-number text-pass">{m.shouted_speech_fpr_pct.toFixed(2)}%</span>
              <span className="metric-delta">Target: ≤ 15.0%</span>
            </div>
            <div className="metric-progress-wrapper">
              <div className="metric-progress-track">
                <div className="metric-progress-fill fill-pass" style={{ width: `${(m.shouted_speech_fpr_pct / 15) * 60}%` }}></div>
                <div className="metric-target-line" style={{ left: '60%' }} title="Target: 15%"></div>
              </div>
            </div>
            <span className="metric-sub font-mono">4 / 42 shouting files triggered false alarms</span>
          </div>

          {/* Card 4: Crowd FPR */}
          <div className="metric-card card-gate-info">
            <div className="metric-card-top">
              <span className="metric-label">Crowd Chant & Cheer FPR</span>
              <span className="gate-badge gate-info">MONITORED</span>
            </div>
            <div className="metric-number-row">
              <span className="metric-number text-cyan">{m.crowd_fpr_pct.toFixed(2)}%</span>
              <span className="metric-delta">Stage 8.9.14 Baseline</span>
            </div>
            <div className="metric-progress-wrapper">
              <div className="metric-progress-track">
                <div className="metric-progress-fill fill-cyan" style={{ width: `${m.crowd_fpr_pct * 3}%` }}></div>
              </div>
            </div>
            <span className="metric-sub font-mono">5 / 43 stadium/cheering files triggered</span>
          </div>

          {/* Card 5: Median Latency */}
          <div className="metric-card card-gate-pass">
            <div className="metric-card-top">
              <span className="metric-label">Median End-to-End Latency</span>
              <span className="gate-badge gate-pass">PASS</span>
            </div>
            <div className="metric-number-row">
              <span className="metric-number text-pass">{m.median_latency_ms.toFixed(2)} ms</span>
              <span className="metric-delta">Budget: ≤ 25.0 ms</span>
            </div>
            <div className="metric-progress-wrapper">
              <div className="metric-progress-track">
                <div className="metric-progress-fill fill-pass" style={{ width: `${(m.median_latency_ms / 25) * 100}%` }}></div>
                <div className="metric-target-line" style={{ left: '100%' }} title="Budget: 25.0 ms"></div>
              </div>
            </div>
            <span className="metric-sub font-mono">61.6% of 25 ms edge budget consumed</span>
          </div>

          {/* Card 6: 95th Percentile Latency */}
          <div className="metric-card card-gate-pass">
            <div className="metric-card-top">
              <span className="metric-label">95th Percentile (p95) Latency</span>
              <span className="gate-badge gate-pass">PASS</span>
            </div>
            <div className="metric-number-row">
              <span className="metric-number text-pass">{m.p95_latency_ms.toFixed(2)} ms</span>
              <span className="metric-delta">Budget: ≤ 25.0 ms</span>
            </div>
            <div className="metric-progress-wrapper">
              <div className="metric-progress-track">
                <div className="metric-progress-fill fill-pass" style={{ width: `${(m.p95_latency_ms / 25) * 100}%` }}></div>
                <div className="metric-target-line" style={{ left: '100%' }} title="Budget: 25.0 ms"></div>
              </div>
            </div>
            <span className="metric-sub font-mono">77.0% of 25 ms edge budget consumed</span>
          </div>
        </div>
      </section>

      {/* Model Performance Comparison Section */}
      <section className="card comparison-section">
        <div className="card-header comparison-header">
          <div>
            <h2 className="card-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
              Candidate Architecture Comparison & Trade-Off Analysis
            </h2>
            <p className="card-subtitle">
              Evaluating why <strong>D_v4 + Family A</strong> is selected for demonstration: balanced performance, rather than maximum recall alone.
            </p>
          </div>
          <div className="chart-metric-filters">
            <button
              type="button"
              className={`filter-btn ${activeChartMetric === 'all' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('all')}
            >
              All Metrics
            </button>
            <button
              type="button"
              className={`filter-btn ${activeChartMetric === 'recall' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('recall')}
            >
              Recall
            </button>
            <button
              type="button"
              className={`filter-btn ${activeChartMetric === 'fpr' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('fpr')}
            >
              Hard-Neg FPR
            </button>
            <button
              type="button"
              className={`filter-btn ${activeChartMetric === 'shouting' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('shouting')}
            >
              Shouting FPR
            </button>
            <button
              type="button"
              className={`filter-btn ${activeChartMetric === 'latency' ? 'active' : ''}`}
              onClick={() => setActiveChartMetric('latency')}
            >
              Latency
            </button>
          </div>
        </div>

        {/* Visual Comparison Chart / Cards */}
        <div className="comparison-table-wrapper">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Candidate Architecture</th>
                <th>Threshold</th>
                <th>Event Recall</th>
                <th>Hard-Neg FPR</th>
                <th>Shouting FPR</th>
                <th>Crowd FPR</th>
                <th>Median Latency</th>
                <th>PR-AUC</th>
                <th>Demo Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((mod) => {
                const isSelected = mod.model_id === 'D_v4_plus_Family_A'
                return (
                  <tr key={mod.model_id} className={`comparison-row ${isSelected ? 'row-selected' : ''}`}>
                    <td>
                      <div className="model-name-cell">
                        <span className="font-semibold text-primary">{mod.model_name}</span>
                        <span className="model-arch-sub text-muted font-mono">{mod.architecture_type}</span>
                      </div>
                    </td>
                    <td className="font-mono text-secondary">{mod.operating_threshold.toFixed(2)}</td>
                    <td>
                      <div className="bar-cell">
                        <div className="bar-track">
                          <div
                            className={`bar-fill ${mod.event_recall_pct >= 96 ? 'fill-pass' : 'fill-fail'}`}
                            style={{ width: `${mod.event_recall_pct}%` }}
                          ></div>
                        </div>
                        <span className="bar-value font-mono">{mod.event_recall_pct.toFixed(2)}%</span>
                      </div>
                    </td>
                    <td>
                      <div className="bar-cell">
                        <div className="bar-track">
                          <div
                            className={`bar-fill ${mod.hard_negative_fpr_pct <= 5 ? 'fill-pass' : 'fill-fail'}`}
                            style={{ width: `${Math.min(100, mod.hard_negative_fpr_pct * 4)}%` }}
                          ></div>
                        </div>
                        <span className="bar-value font-mono">{mod.hard_negative_fpr_pct.toFixed(2)}%</span>
                      </div>
                    </td>
                    <td>
                      <span className={`status-pill-small ${mod.shouted_speech_fpr_pct <= 15 ? 'pill-pass' : 'pill-fail'} font-mono`}>
                        {mod.shouted_speech_fpr_pct.toFixed(2)}%
                      </span>
                    </td>
                    <td>
                      <span className="text-secondary font-mono">{mod.crowd_fpr_pct.toFixed(2)}%</span>
                    </td>
                    <td>
                      <span className={`status-pill-small ${mod.latency_ms <= 25 ? 'pill-pass' : 'pill-fail'} font-mono`}>
                        {mod.latency_ms.toFixed(1)} ms
                      </span>
                    </td>
                    <td className="font-mono text-secondary">{mod.pr_auc.toFixed(4)}</td>
                    <td>
                      {isSelected ? (
                        <span className="badge-demo-selected">
                          ★ RECOMMENDED DEMO
                        </span>
                      ) : (
                        <span className="badge-not-promoted font-mono">
                          {mod.model_id === 'Production_Baseline' ? 'FROZEN PROD' : 'REJECTED'}
                        </span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Narrative Callout: Why D_v4 + Family A was chosen */}
        <div className="rationale-callout-box">
          <div className="callout-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <div className="callout-text">
            <h4 className="callout-title font-semibold text-primary">Technical Rationale for Showcase Selection:</h4>
            <p className="callout-body text-secondary text-sm">
              {demoData.selection_rationale} While the <strong>Stage 8.9.15 Temporal CNN</strong> achieved higher scream recall (94.50%), it caused severe crowd false alarms (25.58%), high shouting false alarms (21.43%), and consumed 55.63 ms latency (exceeding edge limits). Conversely, <strong>D_v4 + Family B</strong> cut FPR to 4.55% but dropped scream recall down to 81.65%. <strong>D_v4 + Family A</strong> delivers the highest overall F1 score (0.8919) and PR-AUC (0.9231) while maintaining sub-20 ms streaming speed.
            </p>
          </div>
        </div>
      </section>

      {/* Grid: Confusion Matrix & Dataset Cohort Breakdown */}
      <section className="two-column-details-grid">
        {/* Left Card: Confusion Matrix */}
        <div className="card cm-card">
          <div className="card-header">
            <h2 className="card-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="12" y1="3" x2="12" y2="21"></line>
              </svg>
              Held-Out Test Confusion Matrix (D_v4 + Family A)
            </h2>
            <span className="font-mono text-xs text-muted">N = {cm.total_eval_samples} Recordings</span>
          </div>

          <div className="cm-grid-container">
            <div className="cm-row-header-wrapper">
              <div className="cm-axis-title-y">ACTUAL GROUND TRUTH</div>
            </div>
            <div className="cm-matrix-body">
              <div className="cm-axis-title-x">PREDICTED CLASSIFICATION</div>
              <div className="cm-quadrant-grid">
                {/* True Positive */}
                <div className="cm-cell cell-tp" title="True Positives: Correctly detected screams">
                  <span className="cm-cell-label">True Positive (TP)</span>
                  <span className="cm-cell-count">{cm.true_positives}</span>
                  <span className="cm-cell-sub">Screams Detected ({((cm.true_positives / (cm.true_positives + cm.false_negatives)) * 100).toFixed(1)}%)</span>
                </div>

                {/* False Negative */}
                <div className="cm-cell cell-fn" title="False Negatives: Missed screams">
                  <span className="cm-cell-label">False Negative (FN)</span>
                  <span className="cm-cell-count text-fail">{cm.false_negatives}</span>
                  <span className="cm-cell-sub">Missed Screams ({((cm.false_negatives / (cm.true_positives + cm.false_negatives)) * 100).toFixed(1)}%)</span>
                </div>

                {/* False Positive */}
                <div className="cm-cell cell-fp" title="False Positives: Hard negatives flagged as screams">
                  <span className="cm-cell-label">False Positive (FP)</span>
                  <span className="cm-cell-count text-fail">{cm.false_positives}</span>
                  <span className="cm-cell-sub">False Alarms ({((cm.false_positives / (cm.false_positives + cm.true_negatives)) * 100).toFixed(1)}%)</span>
                </div>

                {/* True Negative */}
                <div className="cm-cell cell-tn" title="True Negatives: Correctly rejected non-screams">
                  <span className="cm-cell-label">True Negative (TN)</span>
                  <span className="cm-cell-count">{cm.true_negatives}</span>
                  <span className="cm-cell-sub">Correct Rejections ({((cm.true_negatives / (cm.false_positives + cm.true_negatives)) * 100).toFixed(1)}%)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="cm-summary-stats-row">
            <div className="cm-stat-item">
              <span className="text-muted text-xs">Precision:</span>
              <span className="font-mono font-semibold text-primary">{cm.precision_pct.toFixed(2)}%</span>
            </div>
            <div className="cm-stat-item">
              <span className="text-muted text-xs">Specificity:</span>
              <span className="font-mono font-semibold text-primary">{cm.specificity_pct.toFixed(2)}%</span>
            </div>
            <div className="cm-stat-item">
              <span className="text-muted text-xs">F1-Score:</span>
              <span className="font-mono font-semibold text-primary">{cm.f1_pct.toFixed(2)}%</span>
            </div>
          </div>
          <p className="text-muted text-xs font-mono mt-2">{cm.derivation_note}</p>
        </div>

        {/* Right Card: Dataset Cohort & Short-Scream Analysis */}
        <div className="card cohort-card">
          <div className="card-header">
            <h2 className="card-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" strokeWidth="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
              Evaluation Cohort & Duration Breakdown
            </h2>
            <span className="font-mono text-xs text-muted">Strict Source-Disjoint Split</span>
          </div>

          <div className="cohort-stats-grid">
            <div className="cohort-stat-box">
              <span className="stat-label">Total Held-Out Test Set</span>
              <span className="stat-value font-mono">{dc.total_held_out}</span>
              <span className="stat-sub">126 Unseen Source Groups</span>
            </div>
            <div className="cohort-stat-box">
              <span className="stat-label">True Scream Recordings</span>
              <span className="stat-value font-mono text-cyan">{dc.scream_events}</span>
              <span className="stat-sub">35.5% Prevalence in Test</span>
            </div>
            <div className="cohort-stat-box">
              <span className="stat-label">Hard Negative Recordings</span>
              <span className="stat-value font-mono text-amber">{dc.hard_negatives}</span>
              <span className="stat-sub">Shouting, Crowds, Sirens, SFX</span>
            </div>
            <div className="cohort-stat-box">
              <span className="stat-label">Short Screams (&lt; 1.0s)</span>
              <span className="stat-value font-mono text-emerald">5 / 5 (100%)</span>
              <span className="stat-sub text-amber font-semibold">⚠ Preliminary (Small N=5)</span>
            </div>
            <div className="cohort-stat-box">
              <span className="stat-label">Brief Screams (≤ 1.5s)</span>
              <span className="stat-value font-mono text-emerald">24 / 26 (92.3%)</span>
              <span className="stat-sub">High Brief Transient Sensitivity</span>
            </div>
            <div className="cohort-stat-box">
              <span className="stat-label">Sustained Screams (&gt; 1.5s)</span>
              <span className="stat-value font-mono text-primary">75 / 83 (90.4%)</span>
              <span className="stat-sub">Long Scream Phonation</span>
            </div>
          </div>

          <div className="cohort-disclaimer-box">
            <p className="text-secondary text-xs">
              <strong>STATISTICAL SAMPLE SIZE NOTE:</strong> The 100% recall result on short screams under 1 second reflects exactly 5 test examples. As required by evaluation governance, this cannot be represented as certified proof of real-world short-scream robustness.
            </p>
          </div>
        </div>
      </section>

      {/* Stage History Timeline */}
      <section className="card history-timeline-section">
        <div className="card-header">
          <h2 className="card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Research & Model Evolution Timeline
          </h2>
          <span className="font-mono text-xs text-muted">Audited Research Stages</span>
        </div>

        <div className="timeline-items-wrapper">
          {demoData.stage_history.map((stg, i) => {
            const isRejected = stg.status.includes('REJECTED')
            const isPending = stg.status.includes('PENDING')
            return (
              <div key={stg.stage_id} className="timeline-node">
                <div className={`timeline-dot ${isRejected ? 'dot-rejected' : isPending ? 'dot-pending' : 'dot-completed'}`}>
                  {i + 1}
                </div>
                <div className="timeline-content">
                  <div className="timeline-title-row">
                    <span className="font-semibold text-primary">{stg.stage_id}: {stg.stage_title}</span>
                    <span className={`timeline-status-pill ${isRejected ? 'status-rejected' : isPending ? 'status-pending' : 'status-completed'} font-mono`}>
                      {stg.status}
                    </span>
                  </div>
                  <p className="timeline-summary text-secondary text-sm">{stg.summary}</p>
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
