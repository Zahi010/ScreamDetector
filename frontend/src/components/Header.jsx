import { useState, useEffect } from 'react'

export function Header({
  connectionStatus,
  detectorStatus,
  onOpenSettings,
  activeTab = 'live',
  onSelectTab,
  pendingReviewCount,
  isPresentationMode = false,
  onTogglePresentationMode,
}) {
  const [timeStr, setTimeStr] = useState('')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setTimeStr(now.toLocaleTimeString())
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  const getConnectionBadge = () => {
    switch (connectionStatus) {
      case 'connected':
        return (
          <span className="status-badge badge-connected" title="Real-time WebSocket streaming active">
            <span className="status-dot pulse-dot" /> Connected
          </span>
        )
      case 'reconnecting':
        return (
          <span className="status-badge badge-reconnecting" title="Attempting reconnection...">
            <span className="status-dot pulse-dot" /> Reconnecting
          </span>
        )
      default:
        return (
          <span className="status-badge badge-disconnected" title="WebSocket disconnected">
            <span className="status-dot" /> Disconnected
          </span>
        )
    }
  }

  const getDetectorBadge = () => {
    if (detectorStatus.is_running) {
      return (
        <span className="status-badge badge-running" title="Audio engine processing live stream">
          <span className="status-dot pulse-dot" />
          {detectorStatus.mic_status === 'active' ? 'Detector Active (Mic)' : 'Detector Active (Buffer)'}
        </span>
      )
    }
    return (
      <span className="status-badge badge-stopped" title="Detection engine idle">
        <span className="status-dot" /> Detector Stopped
      </span>
    )
  }

  return (
    <header className="app-header-container">
      {/* Top Status Header Bar - Required Section 3.A */}
      <div className="header-status-strip">
        <div className="strip-left">
          <span className="strip-item strip-title font-semibold">
            FESTIVAL SCREAM DETECTION SYSTEM
          </span>
          <span className="strip-sep">•</span>
          <span className="strip-item strip-monitoring">AI Acoustic Monitoring</span>
          <span className="strip-sep">•</span>
          <span className="strip-item badge-experimental-strip">
            EXPERIMENTAL DEMONSTRATION MODE
          </span>
        </div>
        <div className="strip-right font-mono">
          <span className="strip-item">
            Selected: <strong className="text-cyan">D_v4 + Family A</strong>
          </span>
          <span className="strip-sep">|</span>
          <span className="strip-item">
            Production: <strong className="text-amber">Frozen (0.3500)</strong>
          </span>
          <span className="strip-sep">|</span>
          <span className="strip-item">
            Last Eval: <strong className="text-secondary">Stage 8.9.14</strong>
          </span>
        </div>
      </div>

      {/* Main Navigation and Brand Bar */}
      <div className="app-header">
        <div className="brand-section">
          <div className="brand-logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5v14M7 9v6M22 10v4M2 10v4" />
            </svg>
          </div>
          <div>
            <h1 className="brand-title">Festival Scream Detector</h1>
            <div className="brand-subtitle">AI Acoustic Security & Surveillance Engine</div>
          </div>
        </div>

        {/* Main Tab Navigation */}
        <nav className="header-nav-tabs" aria-label="Main Navigation">
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'live' ? 'active' : ''}`}
            onClick={() => onSelectTab && onSelectTab('live')}
            title="Switch to Real-Time Scream Detection Dashboard"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            <span>Live Detection</span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'live-lab' ? 'active' : ''}`}
            onClick={() => onSelectTab && onSelectTab('live-lab')}
            title="Multi-Model Live Audio Testing Lab (Evaluate 7 Models on Shared Audio Stream)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M2 13a2 2 0 0 0 2-2V7a2 2 0 0 1 4 0v4a2 2 0 0 0 4 0V4a2 2 0 0 1 4 0v7a2 2 0 0 0 4 0V8a2 2 0 0 1 4 0v5a10 10 0 0 1-20 0Z"></path>
            </svg>
            <span>Multi-Model Live Lab</span>
            <span className="nav-badge-lab font-mono" title="Live Testing 7 Models Simultaneously">
              LIVE 7-MODEL
            </span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'showcase' ? 'active' : ''}`}
            onClick={() => onSelectTab && onSelectTab('showcase')}
            title="View Stage 8.9.14 Model Showcase & Candidate Benchmark Comparison"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            <span>Model Showcase</span>
            <span className="nav-badge-showcase font-mono" title="Showcasing D_v4 + Family A">
              D_v4+A
            </span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'sddfr' ? 'active' : ''}`}
            onClick={() => onSelectTab && onSelectTab('sddfr')}
            title="Stage 8.9.22 Signal-Driven Dynamic Feature Routing (SDDFR) Research Dashboard"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20V10M18 20V4M6 20v-4" />
            </svg>
            <span>SDDFR (8.9.22)</span>
            <span className="nav-badge-showcase font-mono" style={{ backgroundColor: '#701a75', color: '#f5d0fe' }} title="Stage 8.9.22 Research Architecture">
              RESEARCH
            </span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'research' ? 'active' : ''}`}
            onClick={() => onSelectTab && onSelectTab('research')}
            title="Stage 8.9.80 Candidate 71-D Live Microphone Demonstration Dashboard"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="22" />
            </svg>
            <span>Live Mic Demo (71-D)</span>
            <span className="nav-badge-showcase font-mono" style={{ backgroundColor: '#0284c7', color: '#e0f2fe' }} title="Stage 8.9.80 Live Microphone Integration">
              71-D LIVE
            </span>
          </button>

          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'review' ? 'active' : ''}`}
            onClick={() => onSelectTab && onSelectTab('review')}
            title="Switch to Human Review Studio"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18V5l12-2v13"></path>
              <circle cx="6" cy="18" r="3"></circle>
              <circle cx="18" cy="16" r="3"></circle>
            </svg>
            <span>Dataset Review</span>
            {pendingReviewCount !== undefined && pendingReviewCount > 0 && (
              <span className="nav-badge-pending font-mono" title={`${pendingReviewCount} candidates pending review`}>
                {pendingReviewCount}
              </span>
            )}
          </button>
        </nav>

        <div className="header-meta">
          {onTogglePresentationMode && (
            <button
              type="button"
              className={`btn-presentation-header ${isPresentationMode ? 'active' : ''}`}
              onClick={onTogglePresentationMode}
              title={isPresentationMode ? 'Exit Presentation Mode' : 'Enter Presentation Mode (Clean, High-Contrast Team View)'}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <line x1="8" y1="21" x2="16" y2="21"></line>
                <line x1="12" y1="17" x2="12" y2="21"></line>
              </svg>
              <span>{isPresentationMode ? 'Presenting' : 'Present'}</span>
            </button>
          )}
          {getConnectionBadge()}
          {getDetectorBadge()}
          <div className="clock-display" title="Current Local Time">
            {timeStr || '--:--:--'}
          </div>
          <button
            className="btn-secondary"
            onClick={onOpenSettings}
            title="Configure detection settings and audio input"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            Settings
          </button>
        </div>
      </div>
    </header>
  )
}

