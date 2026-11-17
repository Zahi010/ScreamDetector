import { useState, useCallback, useEffect } from 'react'
import { useDetectorSocket } from './hooks/useDetectorSocket'
import { Header } from './components/Header'
import { AlertBanner } from './components/AlertBanner'
import { LiveMonitor } from './components/LiveMonitor'
import { MetricsGrid } from './components/MetricsGrid'
import { EventHistory } from './components/EventHistory'
import { SettingsModal } from './components/SettingsModal'
import { ReviewStudio } from './components/ReviewStudio/ReviewStudio'
import { ExperimentalShowcase } from './components/ExperimentalShowcase'
import { MultiModelLiveLab } from './components/MultiModelLiveLab'
import { Stage8_9_22_Dashboard } from './components/Stage8_9_22_Dashboard'
import { ResearchDemoDashboard } from './components/ResearchDemo/ResearchDemoDashboard'

export default function App() {
  const {
    connectionStatus,
    detectorStatus,
    metrics,
    windowTelemetry,
    activeAlert,
    dismissAlert,
    reconcileState,
  } = useDetectorSocket()

  const [activeTab, setActiveTab] = useState(() => {
    return localStorage.getItem('active_dashboard_tab') || 'live'
  })
  const [isPresentationMode, setIsPresentationMode] = useState(() => {
    return localStorage.getItem('is_presentation_mode') === 'true'
  })
  const [pendingReviewCount, setPendingReviewCount] = useState(0)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  // Persist active tab
  const handleSelectTab = (tab) => {
    setActiveTab(tab)
    localStorage.setItem('active_dashboard_tab', tab)
  }

  // Toggle Presentation Mode
  const handleTogglePresentationMode = useCallback(() => {
    setIsPresentationMode((prev) => {
      const next = !prev
      localStorage.setItem('is_presentation_mode', String(next))
      return next
    })
  }, [])

  // Fetch pending review count periodically for header badge
  useEffect(() => {
    let isMounted = true
    const fetchPending = async () => {
      try {
        const res = await fetch('/api/review/summary')
        if (res.ok) {
          const data = await res.json()
          if (isMounted) setPendingReviewCount(data.pending_review || 0)
        }
      } catch {
        // Silently ignore network errors for header badge
      }
    }
    fetchPending()
    const timer = setInterval(fetchPending, 15000)
    return () => {
      isMounted = false
      clearInterval(timer)
    }
  }, [])


  // Handle Event Acknowledgment
  const handleAcknowledge = useCallback(async (eventId, operatorNote) => {
    try {
      const res = await fetch(`/api/events/${eventId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ operator_note: operatorNote }),
      })
      if (!res.ok) throw new Error(`HTTP error ${res.status}`)
      await reconcileState()
    } catch (err) {
      console.error('Failed to acknowledge event:', err)
      alert(`Error acknowledging event: ${err.message}`)
    }
  }, [reconcileState])

  // Handle Config Updates
  const handleUpdateConfig = useCallback(async (configUpdates) => {
    try {
      const res = await fetch('/api/config', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configUpdates),
      })
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()
      await reconcileState()
      return { success: true, config: data }
    } catch (err) {
      console.error('Failed to update config:', err)
      return { success: false, error: err.message }
    }
  }, [reconcileState])

  // Start Detector
  const handleStartDetector = useCallback(async (deviceIndex) => {
    try {
      const res = await fetch('/api/detector/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_index: deviceIndex }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await reconcileState()
    } catch (err) {
      console.error('Failed to start detector:', err)
      alert(`Error starting detector: ${err.message}`)
    }
  }, [reconcileState])

  // Stop Detector
  const handleStopDetector = useCallback(async () => {
    try {
      const res = await fetch('/api/detector/stop', {
        method: 'POST',
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await reconcileState()
    } catch (err) {
      console.error('Failed to stop detector:', err)
      alert(`Error stopping detector: ${err.message}`)
    }
  }, [reconcileState])

  return (
    <div className={`app-container ${isPresentationMode ? 'presentation-mode-active' : ''}`}>
      {/* Header Bar with Tab Navigation */}
      <Header
        connectionStatus={connectionStatus}
        detectorStatus={detectorStatus}
        onOpenSettings={() => setIsSettingsOpen(true)}
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        pendingReviewCount={pendingReviewCount}
        isPresentationMode={isPresentationMode}
        onTogglePresentationMode={handleTogglePresentationMode}
      />

      {/* Main View: Live Detection vs Multi-Model Live Lab vs Model Showcase vs Dataset Review */}
      {activeTab === 'live' ? (
        <>
          {/* High-Visibility Alert Banner (Advisory) */}
          <AlertBanner
            alert={activeAlert}
            onAcknowledge={handleAcknowledge}
            onDismiss={dismissAlert}
          />

          {/* Main Monitoring Panels Grid */}
          <main className="dashboard-grid">
            <LiveMonitor
              detectorStatus={detectorStatus}
              telemetry={windowTelemetry}
            />

            <MetricsGrid
              metrics={metrics}
            />

            <EventHistory
              onAcknowledgeEvent={handleAcknowledge}
            />
          </main>
        </>
      ) : activeTab === 'live-lab' ? (
        <main className="livelab-main-wrapper">
          <MultiModelLiveLab />
        </main>
      ) : activeTab === 'showcase' ? (
        <main className="showcase-main-wrapper">
          <ExperimentalShowcase
            isPresentationMode={isPresentationMode}
            onTogglePresentationMode={handleTogglePresentationMode}
          />
        </main>
      ) : activeTab === 'sddfr' ? (
        <main className="sddfr-main-wrapper">
          <Stage8_9_22_Dashboard />
        </main>
      ) : activeTab === 'research' ? (
        <main className="research-demo-main-wrapper" style={{ padding: '1rem', maxWidth: '1600px', margin: '0 auto' }}>
          <ResearchDemoDashboard />
        </main>
      ) : (
        <main className="review-main-wrapper">
          <ReviewStudio />
        </main>
      )}

      {/* Settings & Device Configuration Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        detectorStatus={detectorStatus}
        onUpdateConfig={handleUpdateConfig}
        onStartDetector={handleStartDetector}
        onStopDetector={handleStopDetector}
      />

      {/* System Footer & Mandatory Engineering Disclaimers */}
      <footer className="app-footer">
        <div>
          <span>Festival Scream Detector — Stage 8 Real-Time Operational Interface</span>
          <span style={{ margin: '0 0.5rem' }}>•</span>
          <span>Google YAMNet + Stage 5 LR Classifier (Threshold: 0.35)</span>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span>Notice: Stage 6 contains 0 approved new hard negatives (real festival robustness unverified).</span>
          <br />
          <span>Stage 7 benchmark latency: 79.06 ms. Possible scream detections are advisory and require human verification.</span>
        </div>
      </footer>
    </div>
  )
}
