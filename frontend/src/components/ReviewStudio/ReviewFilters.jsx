export function ReviewFilters({
  filters,
  onChangeFilter,
  onResetFilters,
  totalMatching,
}) {
  const categories = [
    { id: 'all', label: 'All Categories' },
    { id: 'whistles_and_squeaks', label: 'Whistles & Squeaks' },
    { id: 'crowd_cheering_applause', label: 'Crowd Cheering & Applause' },
    { id: 'edm_and_synthesizers', label: 'EDM & Synthesizer Risers' },
    { id: 'shouting_and_speech', label: 'Shouting & Excited Speech' },
    { id: 'vuvuzelas_and_horns', label: 'Vuvuzelas & Stadium Horns' },
    { id: 'fireworks_pyrotechnics', label: 'Fireworks & Pyrotechnics' },
    { id: 'wind_and_mic_noise', label: 'Wind Noise & Mic Handling' },
    { id: 'infant_crying_archival', label: 'Infant Crying (Archival)' },
    { id: 'sfx_sirens_ringing', label: 'Sirens, Bells & Ringing' },
  ]

  const sources = [
    { id: 'all', label: 'All Sources' },
    { id: 'fsd50k', label: 'FSD50K' },
    { id: 'freesound', label: 'Freesound' },
    { id: 'curated_permissive', label: 'Curated Permissive' },
    { id: 'audioset', label: 'AudioSet (Metadata)' },
  ]

  const licenses = [
    { id: 'all', label: 'All Licences' },
    { id: 'CC0_VERIFIED', label: 'CC0 Verified' },
    { id: 'CC_BY_VERIFIED', label: 'CC BY Verified' },
    { id: 'NONCOMMERCIAL_ONLY', label: 'Non-Commercial Only' },
    { id: 'RESTRICTED', label: 'Restricted / Copyright' },
  ]

  const statuses = [
    { id: 'all', label: 'All Review States' },
    { id: 'UNREVIEWED', label: 'Pending Review' },
    { id: 'APPROVED_NON_SCREAM', label: 'Approved Non-Scream' },
    { id: 'SCREAM_PRESENT', label: 'Scream Present' },
    { id: 'AMBIGUOUS', label: 'Ambiguous' },
    { id: 'EXCLUDED', label: 'Excluded' },
  ]

  const triageGroups = [
    { id: 'all', label: 'All Triage Recommendations' },
    { id: 'LIKELY_NON_SCREAM', label: '🟢 Likely Non-Scream (Strong Alt Evid)' },
    { id: 'POSSIBLE_SCREAM', label: '🔴 Possible Scream (Score ≥ 0.35)' },
    { id: 'AMBIGUOUS', label: '🟠 Ambiguous / Conflicting' },
    { id: 'REVIEW_REQUIRED', label: '⚪ Review Required (Missing / Error)' },
  ]

  const scoreOptions = [
    { id: 'all', label: 'All Scores' },
    { id: 'high_risk', label: 'High Risk (Score ≥ 0.35)' },
    { id: 'low_risk', label: 'Low Risk (Score < 0.35)' },
    { id: 'missing', label: 'Not Evaluated' },
  ]

  return (
    <aside className="review-filters-panel" data-testid="review-filters-panel">
      <div className="filters-header">
        <div className="filters-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
          </svg>
          <h3>Queue Filters</h3>
        </div>
        <button
          type="button"
          className="btn-filter-reset"
          onClick={onResetFilters}
          title="Reset all filters to defaults"
        >
          Reset
        </button>
      </div>

      <div className="filter-count-badge">
        <span className="font-mono">{totalMatching}</span> recordings matched
      </div>

      {/* Search Input */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-search">Search Candidates</label>
        <div className="search-input-wrap">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            id="filter-search"
            type="text"
            className="filter-search-input"
            placeholder="ID, title, filename..."
            value={filters.search || ''}
            onChange={(e) => onChangeFilter('search', e.target.value)}
          />
          {filters.search && (
            <button
              type="button"
              className="btn-clear-search"
              onClick={() => onChangeFilter('search', '')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Triage Group Filter */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-triage">Triage Group</label>
        <select
          id="filter-triage"
          className="filter-select"
          value={filters.triage_group || 'all'}
          onChange={(e) => onChangeFilter('triage_group', e.target.value)}
        >
          {triageGroups.map((tg) => (
            <option key={tg.id} value={tg.id}>{tg.label}</option>
          ))}
        </select>
      </div>

      {/* Review Status Filter */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-status">Review Decision</label>
        <select
          id="filter-status"
          className="filter-select"
          value={filters.status || 'all'}
          onChange={(e) => onChangeFilter('status', e.target.value)}
        >
          {statuses.map((s) => (
            <option key={s.id} value={s.id}>{s.label}</option>
          ))}
        </select>
      </div>

      {/* Sound Category Filter */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-category">Sound Category</label>
        <select
          id="filter-category"
          className="filter-select"
          value={filters.category || 'all'}
          onChange={(e) => onChangeFilter('category', e.target.value)}
        >
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.label}</option>
          ))}
        </select>
      </div>

      {/* Audio Availability Radio Filter */}
      <div className="filter-group">
        <label className="filter-label">Audio Availability</label>
        <div className="filter-radio-group">
          {[
            { id: 'all', label: 'All' },
            { id: 'available', label: 'On Disk' },
            { id: 'missing', label: 'Missing' },
          ].map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`btn-radio-toggle ${filters.audio === opt.id ? 'active' : ''}`}
              onClick={() => onChangeFilter('audio', opt.id)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Model Score Range Filter */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-score">Model Score (Threshold: 0.35)</label>
        <select
          id="filter-score"
          className="filter-select"
          value={filters.score_filter || 'all'}
          onChange={(e) => onChangeFilter('score_filter', e.target.value)}
        >
          {scoreOptions.map((opt) => (
            <option key={opt.id} value={opt.id}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Source Provider Filter */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-source">Source Dataset</label>
        <select
          id="filter-source"
          className="filter-select"
          value={filters.source || 'all'}
          onChange={(e) => onChangeFilter('source', e.target.value)}
        >
          {sources.map((src) => (
            <option key={src.id} value={src.id}>{src.label}</option>
          ))}
        </select>
      </div>

      {/* License Status Filter */}
      <div className="filter-group">
        <label className="filter-label" htmlFor="filter-license">Licence Classification</label>
        <select
          id="filter-license"
          className="filter-select"
          value={filters.license || 'all'}
          onChange={(e) => onChangeFilter('license', e.target.value)}
        >
          {licenses.map((lic) => (
            <option key={lic.id} value={lic.id}>{lic.label}</option>
          ))}
        </select>
      </div>
    </aside>
  )
}
