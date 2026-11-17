import { useState, useEffect } from 'react'
import { AudioPlayer } from './AudioPlayer'

export function ReviewDetailPanel({
  recording,
  history,
  onSaveDecision,
  onPrevClip,
  onNextClip,
  hasPrevClip,
  hasNextClip,
  isSaving,
  autoAdvance,
  onToggleAutoAdvance,
}) {
  const [selectedReason, setSelectedReason] = useState('')
  const [notes, setNotes] = useState('')
  const [hasUnsavedNotes, setHasUnsavedNotes] = useState(false)
  const [isHistoryExpanded, setIsHistoryExpanded] = useState(false)

  // Reason codes matching Section 4
  const reasonCodes = [
    { id: '', label: 'Select Reason Code (Optional)...' },
    { id: 'Genuine non-scream sound', label: 'Genuine non-scream sound' },
    { id: 'Scream-like vocalisation', label: 'Scream-like vocalisation' },
    { id: 'Possible scream present', label: 'Possible scream present' },
    { id: 'Overlapping or mixed sounds', label: 'Overlapping or mixed sounds' },
    { id: 'Incorrect source annotation', label: 'Incorrect source annotation' },
    { id: 'Poor audio quality', label: 'Poor audio quality' },
    { id: 'Duplicate recording', label: 'Duplicate recording' },
    { id: 'Incomplete or missing audio', label: 'Incomplete or missing audio' },
    { id: 'Other', label: 'Other' },
  ]

  // Reset form when active recording changes
  useEffect(() => {
    if (recording) {
      setNotes(recording.reviewer_notes || '')
      setSelectedReason(recording.reviewer_reason_code || '')
      setHasUnsavedNotes(false)
    } else {
      setNotes('')
      setSelectedReason('')
      setHasUnsavedNotes(false)
    }
  }, [recording?.recording_id])

  const handleNotesChange = (e) => {
    setNotes(e.target.value)
    setHasUnsavedNotes(e.target.value !== (recording?.reviewer_notes || ''))
  }

  const handleDecisionClick = (decision) => {
    if (!recording) return
    onSaveDecision(decision, selectedReason, notes)
  }

  if (!recording) {
    return (
      <aside className="review-detail-panel empty-selection" data-testid="review-detail-empty">
        <div className="empty-panel-prompt">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm1 14.93V18a1 1 0 0 1-2 0v-1.07A7 7 0 0 1 5.07 11H6a1 1 0 0 1 0-2h-.93A7 7 0 0 1 11 3.07V4a1 1 0 0 1 2 0v-.93A7 7 0 0 1 18.93 9H18a1 1 0 0 1 0 2h.93A7 7 0 0 1 13 16.93z"></path>
          </svg>
          <h3>No Recording Selected</h3>
          <p>Select a candidate from the queue to inspect audio, verify annotations, and record your review decision.</p>
        </div>
      </aside>
    )
  }

  const isReviewed = recording.review_status && recording.review_status !== 'UNREVIEWED'

  const getTriageBadge = (group) => {
    switch (group) {
      case 'LIKELY_NON_SCREAM':
        return <span className="triage-badge triage-likely">🟢 Likely Non-Scream</span>
      case 'POSSIBLE_SCREAM':
        return <span className="triage-badge triage-possible">🔴 Possible Scream</span>
      case 'AMBIGUOUS':
        return <span className="triage-badge triage-ambiguous">🟠 Ambiguous</span>
      case 'REVIEW_REQUIRED':
      default:
        return <span className="triage-badge triage-required">⚪ Review Required</span>
    }
  }

  const topClasses = recording.yamnet_top_classes || []
  const relevantTags = recording.yamnet_relevant_tags || []

  return (
    <aside className="review-detail-panel" data-testid="review-detail-panel">
      {/* Detail Header */}
      <div className="detail-header">
        <div className="detail-title-wrap">
          <div className="detail-rec-id font-mono">{recording.recording_id}</div>
          <h2 className="detail-title" title={recording.original_title_description}>
            {recording.original_title_description || recording.original_filename || 'Untitled Recording'}
          </h2>
        </div>

        <div className="detail-badges">
          {recording.has_audio ? (
            <span className="status-badge badge-connected">Audio Available</span>
          ) : (
            <span className="status-badge badge-disconnected">Audio Missing</span>
          )}
          <span className={`status-badge badge-status-${recording.review_status?.toLowerCase()}`}>
            {recording.review_status ? recording.review_status.replace(/_/g, ' ') : 'UNREVIEWED'}
          </span>
        </div>
      </div>

      {/* Embedded Audio Player */}
      <div className="detail-player-section">
        <AudioPlayer
          recordingId={recording.recording_id}
          hasAudio={recording.has_audio}
          onPrev={onPrevClip}
          onNext={onNextClip}
          hasPrev={hasPrevClip}
          hasNext={hasNextClip}
        />
      </div>

      {/* Stage 8.9.1 Automated Triage Diagnostic Section */}
      <div className="detail-triage-card" data-testid="detail-triage-card">
        <div className="triage-card-header">
          <div className="triage-header-left">
            <span className="triage-section-tag">STAGE 8.9.1 AUTO-TRIAGE</span>
            <div className="triage-group-display">
              {getTriageBadge(recording.triage_group)}
            </div>
          </div>
          <span className="triage-disclaimer-pill">Review Recommendation Only</span>
        </div>

        {/* Triage Reason */}
        <div className="triage-reason-box">
          <span className="triage-reason-label">Classification Rationale:</span>
          <p className="triage-reason-text">{recording.triage_reason || 'Pending automated acoustic triage run.'}</p>
        </div>

        {/* Side-by-Side Model Comparison Grid */}
        <div className="side-by-side-comparison">
          {/* Left: Frozen Custom Scream Classifier */}
          <div className="comparison-box classifier-box">
            <div className="box-title-row">
              <span className="box-title">Scream Classifier</span>
              <span className="box-threshold font-mono">Threshold: 0.35</span>
            </div>
            <div className="score-big-row">
              {recording.model_score !== null && recording.model_score !== undefined ? (
                <>
                  <span className={`score-value font-mono ${recording.model_score >= 0.35 ? 'text-alert' : 'text-cyan'}`}>
                    {(recording.model_score * 100).toFixed(2)}%
                  </span>
                  <span className={`eval-alert-pill ${recording.model_score >= 0.35 ? 'pill-alert' : 'pill-clear'}`}>
                    {recording.model_score >= 0.35 ? 'ALERT (≥ 0.35)' : 'CLEAR (< 0.35)'}
                  </span>
                </>
              ) : (
                <span className="score-unevaluated">Not evaluated</span>
              )}
            </div>
            <div className="box-meta-sub font-mono">
              Model Hash: ad6e428d05... [Frozen]
            </div>
          </div>

          {/* Right: Pretrained YAMNet AudioSet Prior */}
          <div className="comparison-box yamnet-box">
            <div className="box-title-row">
              <span className="box-title">YAMNet Acoustic Labels</span>
              <span className="box-threshold">521 AudioSet Classes</span>
            </div>

            {/* Relevant Sound Tags */}
            {relevantTags.length > 0 ? (
              <div className="yamnet-tags-list">
                <span className="tags-label">Detected Target Indicators:</span>
                <div className="relevant-tags-grid">
                  {relevantTags.map((tag, idx) => (
                    <div key={idx} className="relevant-tag-item">
                      <div className="tag-header">
                        <span className="tag-name" title={tag.class_name}>{tag.class_name}</span>
                        <span className="tag-score font-mono">{(tag.max_score * 100).toFixed(1)}%</span>
                      </div>
                      <div className="tag-bar-track">
                        <div
                          className={`tag-bar-fill fill-${tag.category}`}
                          style={{ width: `${Math.min(100, Math.max(5, tag.max_score * 100))}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="yamnet-tags-empty font-mono">
                No specific festival interference indicators (whistle, siren, cry, etc.) detected above threshold.
              </div>
            )}

            {/* Top Overall Classes */}
            {topClasses.length > 0 && (
              <div className="top-classes-strip">
                <span className="top-classes-label">Top Priors:</span>
                <div className="top-priors-flex">
                  {topClasses.slice(0, 3).map((c, i) => (
                    <span key={i} className="prior-pill font-mono" title={`Mean: ${c.mean_score}, Max: ${c.max_score}`}>
                      {c.class_name} ({(c.mean_score * 100).toFixed(0)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Signal Quality Indicators */}
        <div className="signal-quality-bar font-mono">
          <div className="quality-metric">
            <span className="metric-label">Duration:</span>
            <span className="metric-val">{recording.duration_seconds ? `${recording.duration_seconds.toFixed(2)}s` : '—'}</span>
          </div>
          <div className="quality-metric">
            <span className="metric-label">Clipping:</span>
            <span className={`metric-val ${recording.clipping_ratio > 0.20 ? 'metric-bad' : 'metric-good'}`}>
              {(recording.clipping_ratio * 100).toFixed(1)}%
            </span>
          </div>
          <div className="quality-metric">
            <span className="metric-label">Silence:</span>
            <span className={`metric-val ${recording.silence_ratio > 0.90 ? 'metric-bad' : 'metric-good'}`}>
              {(recording.silence_ratio * 100).toFixed(1)}%
            </span>
          </div>
          <div className="quality-metric">
            <span className="metric-label">Integrity:</span>
            <span className="metric-val text-cyan">Frozen 0.35 Validated</span>
          </div>
        </div>
      </div>

      {/* Metadata Cards */}
      <div className="detail-metadata-grid">
        <div className="meta-card">
          <span className="meta-label">Category & Source</span>
          <div className="meta-value font-bold">
            {recording.proposed_category ? recording.proposed_category.replace(/_/g, ' ') : 'Unspecified'}
          </div>
          <div className="meta-sub">
            Source: <span className="font-mono">{recording.source_provider}</span> ({recording.original_source_id || 'N/A'})
          </div>
          {recording.original_source_url && (
            <div className="meta-link-wrap">
              <a
                href={recording.original_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="meta-external-link"
              >
                View Source Webpage ↗
              </a>
            </div>
          )}
        </div>

        <div className="meta-card">
          <span className="meta-label">Licence & Provenance</span>
          <div className="meta-value font-mono">
            {recording.commercial_compatibility || 'UNKNOWN'}
          </div>
          <div className="meta-sub" title={recording.attribution_text}>
            {recording.clip_license || recording.dataset_license || 'No license string'}
          </div>
          {recording.original_creator && (
            <div className="meta-creator">
              Creator: <span className="font-mono">{recording.original_creator}</span>
            </div>
          )}
        </div>
      </div>

      {/* Original Source Annotations */}
      {recording.original_annotations && recording.original_annotations.length > 0 && (
        <div className="detail-annotations-box">
          <span className="box-label">Original Dataset Annotations / Tags:</span>
          <div className="tags-flex">
            {recording.original_annotations.map((tag, idx) => (
              <span key={idx} className="dataset-tag">{tag}</span>
            ))}
          </div>
        </div>
      )}

      {/* Human Review Decision Section */}
      <div className="decision-action-box">
        <div className="decision-header">
          <h3 className="section-heading">Human Review Decision</h3>
          <div className="auto-advance-toggle">
            <label className="checkbox-label" title="Automatically advance to the next clip after recording decision">
              <input
                type="checkbox"
                checked={autoAdvance}
                onChange={(e) => onToggleAutoAdvance(e.target.checked)}
              />
              <span>Auto-advance to next</span>
            </label>
          </div>
        </div>

        {/* Reason Code Dropdown */}
        <div className="form-field">
          <label htmlFor="reason-code-select" className="field-label">Observation Reason Code</label>
          <select
            id="reason-code-select"
            className="field-select"
            value={selectedReason}
            onChange={(e) => setSelectedReason(e.target.value)}
          >
            {reasonCodes.map((rc) => (
              <option key={rc.id} value={rc.id}>{rc.label}</option>
            ))}
          </select>
        </div>

        {/* Reviewer Notes Field */}
        <div className="form-field">
          <div className="field-label-row">
            <label htmlFor="reviewer-notes" className="field-label">Reviewer Notes</label>
            {hasUnsavedNotes && (
              <span className="unsaved-indicator font-mono">● Unsaved edits</span>
            )}
          </div>
          <textarea
            id="reviewer-notes"
            className="field-textarea"
            rows="2"
            placeholder="Document acoustic characteristics, vocal harmonics, false-alarm vulnerabilities..."
            value={notes}
            onChange={handleNotesChange}
          />
        </div>

        {/* 4 Action Buttons */}
        <div className="decision-buttons-grid">
          <button
            type="button"
            className="btn-decision btn-approve"
            onClick={() => handleDecisionClick('APPROVED_NON_SCREAM')}
            disabled={isSaving}
            title="Confirm genuine non-scream sound (Safe hard negative) [Key: 1]"
          >
            <span className="btn-key-badge font-mono">1</span>
            <span className="btn-decision-text">Approve Non-Scream</span>
          </button>

          <button
            type="button"
            className="btn-decision btn-scream"
            onClick={() => handleDecisionClick('SCREAM_PRESENT')}
            disabled={isSaving}
            title="Flag candidate: scream vocalization present [Key: 2]"
          >
            <span className="btn-key-badge font-mono">2</span>
            <span className="btn-decision-text">Scream Present</span>
          </button>

          <button
            type="button"
            className="btn-decision btn-ambiguous"
            onClick={() => handleDecisionClick('AMBIGUOUS')}
            disabled={isSaving}
            title="Mark as ambiguous vocalization / mixed sounds [Key: 3]"
          >
            <span className="btn-key-badge font-mono">3</span>
            <span className="btn-decision-text">Ambiguous</span>
          </button>

          <button
            type="button"
            className="btn-decision btn-exclude"
            onClick={() => handleDecisionClick('EXCLUDED')}
            disabled={isSaving}
            title="Exclude due to corrupt audio, licensing, or invalid format [Key: 4]"
          >
            <span className="btn-key-badge font-mono">4</span>
            <span className="btn-decision-text">Exclude</span>
          </button>
        </div>

        {/* Reopen / Reset Button (only if already reviewed) */}
        {isReviewed && (
          <div className="reopen-action-row">
            <button
              type="button"
              className="btn-reopen"
              onClick={() => onSaveDecision('UNREVIEWED', 'Reopened for re-review', notes)}
              disabled={isSaving}
              title="Reset status back to Pending Review while preserving audit history"
            >
              ↺ Reset Decision to Pending Review
            </button>
          </div>
        )}
      </div>

      {/* Immutable Audit Log History */}
      <div className="audit-history-box">
        <button
          type="button"
          className="audit-toggle-header"
          onClick={() => setIsHistoryExpanded(!isHistoryExpanded)}
          aria-expanded={isHistoryExpanded}
        >
          <div className="audit-title-left">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 8v4l3 3"></path>
              <circle cx="12" cy="12" r="10"></circle>
            </svg>
            <span>Decision Audit Trail ({history?.length || 0})</span>
          </div>
          <span className="toggle-chevron">{isHistoryExpanded ? '▲' : '▼'}</span>
        </button>

        {isHistoryExpanded && (
          <div className="audit-timeline">
            {(!history || history.length === 0) ? (
              <div className="audit-empty font-mono">No previous human reviews recorded.</div>
            ) : (
              history.map((entry) => (
                <div key={entry.id} className="timeline-item">
                  <div className="timeline-meta font-mono">
                    <span className="timeline-time">{new Date(entry.timestamp).toLocaleString()}</span>
                    <span className="timeline-reviewer">by {entry.reviewer}</span>
                  </div>
                  <div className="timeline-transition">
                    <span className="font-mono text-muted">{entry.previous_status}</span>
                    <span className="trans-arrow">➔</span>
                    <span className="font-mono text-cyan font-bold">{entry.new_status}</span>
                  </div>
                  {entry.reason_code && (
                    <div className="timeline-reason font-sans">
                      Reason: <em>{entry.reason_code}</em>
                    </div>
                  )}
                  {entry.notes && (
                    <div className="timeline-notes font-sans">
                      "{entry.notes}"
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </aside>
  )
}
