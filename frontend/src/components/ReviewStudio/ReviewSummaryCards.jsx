import { useState } from 'react'

export function ReviewSummaryCards({
  summary,
  onApplyPreset,
  onTriggerEvaluation,
  isEvaluating,
  onTriggerTriage,
  isTriaging,
  onOpenRecovery,
  onOpenEvaluation,
}) {

  if (!summary) {
    return (
      <div className="review-summary-skeleton">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
      </div>
    )
  }

  const triageCounts = summary.triage_counts || {
    LIKELY_NON_SCREAM: 0,
    POSSIBLE_SCREAM: 0,
    AMBIGUOUS: 0,
    REVIEW_REQUIRED: 0,
  }

  const triageCards = [
    {
      id: 'triage_likely_non_scream',
      group: 'LIKELY_NON_SCREAM',
      label: 'Likely Non-Scream',
      value: triageCounts.LIKELY_NON_SCREAM || 0,
      sub: 'Strong alt evidence, low scream score',
      theme: 'triage-card-likely',
      badge: 'RECOMMENDED FIRST',
      preset: { triage_group: 'LIKELY_NON_SCREAM', sort_by: 'triage', sort_order: 'asc' },
    },
    {
      id: 'triage_possible_scream',
      group: 'POSSIBLE_SCREAM',
      label: 'Possible Scream',
      value: triageCounts.POSSIBLE_SCREAM || 0,
      sub: 'Score ≥ 0.35 with scream tags or high prob',
      theme: 'triage-card-possible',
      badge: 'PRIORITY AUDIT',
      preset: { triage_group: 'POSSIBLE_SCREAM' },
    },
    {
      id: 'triage_ambiguous',
      group: 'AMBIGUOUS',
      label: 'Ambiguous',
      value: triageCounts.AMBIGUOUS || 0,
      sub: 'Infant crying / mixed harmonics / near 0.35',
      theme: 'triage-card-ambiguous',
      badge: 'CAREFUL LISTEN',
      preset: { triage_group: 'AMBIGUOUS' },
    },
    {
      id: 'triage_review_required',
      group: 'REVIEW_REQUIRED',
      label: 'Review Required',
      value: triageCounts.REVIEW_REQUIRED || 0,
      sub: 'Missing audio / clipping / silence / error',
      theme: 'triage-card-required',
      badge: 'QUALITY / MISSING',
      preset: { triage_group: 'REVIEW_REQUIRED' },
    },
  ]

  const statusCards = [
    {
      id: 'total',
      label: 'Total Discovered',
      value: summary.total_candidates,
      sub: 'Stage 8.8 candidates',
      type: 'neutral',
      preset: { status: 'all', score_filter: 'all', audio: 'all', triage_group: 'all' },
    },
    {
      id: 'available',
      label: 'Audio Available',
      value: summary.audio_available,
      sub: `${Math.round((summary.audio_available / (summary.total_candidates || 1)) * 100)}% on disk`,
      type: 'cyan',
      preset: { audio: 'available' },
    },
    {
      id: 'reviewed',
      label: 'Reviewed',
      value: summary.reviewed_count,
      sub: `${summary.reviewed_percentage}% completed`,
      type: 'idle',
      preset: { status: 'all' },
    },
    {
      id: 'pending',
      label: 'Pending Review',
      value: summary.pending_review,
      sub: 'Needs listening verification',
      type: 'warning',
      preset: { status: 'UNREVIEWED' },
    },
    {
      id: 'approved',
      label: 'Approved Non-Screams',
      value: summary.approved_non_scream,
      sub: 'Safe negative baseline',
      type: 'idle',
      preset: { status: 'APPROVED_NON_SCREAM' },
    },
    {
      id: 'scream',
      label: 'Scream Present',
      value: summary.scream_present,
      sub: 'Flagged or contaminated',
      type: 'alert',
      preset: { status: 'SCREAM_PRESENT' },
    },
    {
      id: 'ambiguous',
      label: 'Ambiguous Decisions',
      value: summary.ambiguous,
      sub: 'Unclear vocalizations',
      type: 'warning',
      preset: { status: 'AMBIGUOUS' },
    },
    {
      id: 'excluded',
      label: 'Excluded',
      value: summary.excluded,
      sub: 'Licence or quality issue',
      type: 'muted',
      preset: { status: 'EXCLUDED' },
    },
    {
      id: 'missing_audio',
      label: 'Missing Audio',
      value: summary.missing_audio,
      sub: 'Not downloaded to disk',
      type: 'muted',
      preset: { audio: 'missing' },
    },
    {
      id: 'missing_scores',
      label: 'Missing Scores',
      value: summary.missing_model_scores,
      sub: 'Not yet evaluated',
      type: 'warning',
      preset: { score_filter: 'missing' },
    },
  ]

  const handleExportCSV = () => {
    window.location.href = '/api/review/export.csv'
  }

  return (
    <div className="review-summary-container" data-testid="review-summary-cards">
      {/* Automated Triage Recommendations Row */}
      <div className="triage-section-wrap">
        <div className="triage-section-header">
          <div className="triage-title-block">
            <span className="triage-header-tag">STAGE 8.9.1</span>
            <h4 className="triage-heading">Automated Hard-Negative Triage Recommendations</h4>
          </div>
          <span className="triage-note">
            Advisory ordering only &bull; Never auto-approves or alters ground truth
          </span>
        </div>

        <div className="triage-cards-grid">
          {triageCards.map((card) => (
            <div
              key={card.id}
              className={`triage-card ${card.theme} clickable-card`}
              onClick={() => onApplyPreset(card.preset)}
              title={`Filter by ${card.label} (${card.sub})`}
              data-testid={card.id}
            >
              <div className="triage-card-top">
                <span className="triage-badge-pill">{card.badge}</span>
                <span className="triage-card-label">{card.label}</span>
              </div>
              <div className="triage-card-value font-mono">
                {card.value.toLocaleString()}
              </div>
              <div className="triage-card-sub">{card.sub}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 10 Queue Status Counters Grid */}
      <div className="summary-cards-grid">
        {statusCards.map((card) => (
          <div
            key={card.id}
            className={`summary-card card-${card.type} clickable-card`}
            onClick={() => onApplyPreset(card.preset)}
            title={`Filter queue by ${card.label}`}
          >
            <div className="summary-card-header">
              <span className="summary-card-label">{card.label}</span>
            </div>
            <div className="summary-card-value font-mono">
              {card.value.toLocaleString()}
            </div>
            <div className="summary-card-sub">{card.sub}</div>
          </div>
        ))}
      </div>

      {/* Action and Quick Presets Toolbar */}
      <div className="summary-toolbar">
        <div className="preset-buttons-group">
          <span className="toolbar-label">Quick Filters:</span>
          <button
            type="button"
            className="btn-preset btn-preset-highlight"
            onClick={() => onApplyPreset({ triage_group: 'LIKELY_NON_SCREAM', sort_by: 'triage', sort_order: 'asc', status: 'UNREVIEWED', audio: 'available' })}
            title="Sort and review obvious hard negatives first"
          >
            ✨ Likely Non-Screams First
          </button>
          <button
            type="button"
            className="btn-preset"
            onClick={() => onApplyPreset({ score_filter: 'high_risk', status: 'UNREVIEWED', audio: 'available' })}
            title="Inspect high-scoring candidates needing review"
          >
            🔥 High-Score Unreviewed (≥ 0.35)
          </button>
          <button
            type="button"
            className="btn-preset"
            onClick={() => onApplyPreset({ audio: 'available', status: 'UNREVIEWED' })}
            title="Show audio clips ready for listening review"
          >
            🎧 Ready for Listening
          </button>
          <button
            type="button"
            className="btn-preset btn-preset-clear"
            onClick={() => onApplyPreset({ category: 'all', source: 'all', license: 'all', status: 'all', audio: 'all', score_filter: 'all', triage_group: 'all', search: '' })}
            title="Reset all filters to default"
          >
            ↺ Clear Filters
          </button>
        </div>

        <div className="action-buttons-group">
          <button
            type="button"
            className="btn-action-triage"
            onClick={onTriggerTriage}
            disabled={isTriaging || isEvaluating}
            title="Execute YAMNet acoustic tag extraction and frozen 0.35 classifier triage"
          >
            {isTriaging ? (
              <>
                <span className="spinner-sm" /> Running Auto-Triage...
              </>
            ) : (
              <>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
                Run Auto-Triage (YAMNet + 0.35)
              </>
            )}
          </button>

          <button
            type="button"
            className="btn-action-evaluation"
            onClick={onOpenEvaluation}
            title="Inspect human-verified false positives, confusion matrix, and performance metrics"
            data-testid="btn-open-evaluation"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            False-Positive Analysis
          </button>

          <button
            type="button"
            className="btn-action-recovery"
            onClick={onOpenRecovery}
            title="Inspect missing audio audit and restore recordings from E: and Freesound"
            data-testid="btn-open-recovery"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Missing Audio Recovery
          </button>

          <button
            type="button"
            className="btn-secondary"

            onClick={handleExportCSV}
            title="Download full candidate provenance, triage groups, and review queue as CSV"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export CSV
          </button>
        </div>
      </div>
    </div>
  )
}
