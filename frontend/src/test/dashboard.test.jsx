import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Header } from '../components/Header'
import { AlertBanner } from '../components/AlertBanner'
import { LiveMonitor } from '../components/LiveMonitor'
import { MetricsGrid } from '../components/MetricsGrid'
import { EventHistory } from '../components/EventHistory'
import { SettingsModal } from '../components/SettingsModal'

describe('Header Component', () => {
  it('renders branding and connected status badge', () => {
    render(
      <Header
        connectionStatus="connected"
        detectorStatus={{ is_running: true, mic_status: 'active' }}
        onOpenSettings={() => {}}
      />
    )
    expect(screen.getByText('Festival Scream Detector')).toBeInTheDocument()
    expect(screen.getByText(/Connected/i)).toBeInTheDocument()
    expect(screen.getByText(/Detector Active/i)).toBeInTheDocument()
  })

  it('renders disconnected state when socket loses connection', () => {
    render(
      <Header
        connectionStatus="disconnected"
        detectorStatus={{ is_running: false }}
        onOpenSettings={() => {}}
      />
    )
    expect(screen.getByText(/Disconnected/i)).toBeInTheDocument()
    expect(screen.getByText(/Detector Stopped/i)).toBeInTheDocument()
  })
})

describe('AlertBanner Component', () => {
  const mockAlert = {
    event_id: 'evt_20261024_test',
    peak_probability: 0.884,
    duration_seconds: 1.46,
    window_count: 3,
    start_wall_time_iso: '2026-10-24T12:00:00Z',
    acknowledged: false,
  }

  it('renders alert headline, confidence, and human verification advisory', () => {
    render(
      <AlertBanner
        alert={mockAlert}
        onAcknowledge={() => {}}
        onDismiss={() => {}}
      />
    )
    expect(screen.getByText(/POSSIBLE SCREAM EVENT DETECTED/i)).toBeInTheDocument()
    expect(screen.getByText(/88.4%/i)).toBeInTheDocument()
    expect(screen.getByText(/Requires human auditory verification/i)).toBeInTheDocument()
    expect(screen.getByText(/Acknowledge Alert/i)).toBeInTheDocument()
  })

  it('handles operator acknowledgment submission', async () => {
    const handleAck = vi.fn().mockResolvedValue({})
    render(
      <AlertBanner
        alert={mockAlert}
        onAcknowledge={handleAck}
        onDismiss={() => {}}
      />
    )
    const ackBtn = screen.getByText(/Acknowledge Alert/i)
    fireEvent.click(ackBtn)

    const submitBtn = screen.getByText(/Submit Acknowledgment/i)
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(handleAck).toHaveBeenCalledWith('evt_20261024_test', expect.any(String))
    })
  })
})

describe('LiveMonitor Component', () => {
  it('renders state badge, raw score, smoothed score, and real RMS audio activity', () => {
    render(
      <LiveMonitor
        detectorStatus={{ state: 'CANDIDATE', threshold: 0.35 }}
        telemetry={{
          window_index: 42,
          raw_probability: 0.725,
          smoothed_probability: 0.610,
          audio_rms: 0.0452,
          priors: [{ class_name: 'Screaming', score: 0.85 }],
        }}
      />
    )
    expect(screen.getByText('CANDIDATE')).toBeInTheDocument()
    expect(screen.getByText(/72.5%/i)).toBeInTheDocument()
    expect(screen.getByText(/61.0%/i)).toBeInTheDocument()
    expect(screen.getByText(/RMS: 0.0452/i)).toBeInTheDocument()
    expect(screen.getByText(/Screaming/i)).toBeInTheDocument()
  })
})

describe('MetricsGrid Component', () => {
  it('displays real latency numbers and processed window counters', () => {
    const mockMetrics = {
      windows_processed: 1250,
      total_alerts_emitted: 4,
      total_alerts_suppressed: 2,
      latency_metrics_ms: { mean: 79.1, min: 65.0, max: 95.0, p95: 84.5 },
      inference_errors: 0,
      dropped_samples: 0,
      session_uptime_seconds: 610,
    }
    render(<MetricsGrid metrics={mockMetrics} />)
    expect(screen.getByText('1,250')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
    expect(screen.getByText('79.1 ms')).toBeInTheDocument()
    expect(screen.getByText(/P95: 84.5 ms/i)).toBeInTheDocument()
  })
})

describe('EventHistory Component', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('renders empty state when no events exist in log', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ total: 0, events: [] }),
    })

    render(<EventHistory onAcknowledgeEvent={() => {}} />)
    await waitFor(() => {
      expect(screen.getByText(/No detection events recorded/i)).toBeInTheDocument()
    })
  })

  it('renders populated events table when events are returned', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total: 1,
        events: [
          {
            event_id: 'evt_history_01',
            peak_probability: 0.81,
            duration_seconds: 1.95,
            window_count: 4,
            alert_emitted: true,
            acknowledged: true,
            operator_note: 'Verified in crowd zone B',
          },
        ],
      }),
    })

    render(<EventHistory onAcknowledgeEvent={() => {}} />)
    await waitFor(() => {
      expect(screen.getByText('evt_history_01')).toBeInTheDocument()
      expect(screen.getByText('81.0%')).toBeInTheDocument()
      expect(screen.getByText(/Verified in crowd zone B/i)).toBeInTheDocument()
    })
  })
})

describe('SettingsModal Component', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ devices: [{ device_index: 0, name: 'Built-in Mic', host_api: 'MME' }] }),
    })
  })

  it('renders threshold slider, start/stop detector controls, and device dropdown', async () => {
    render(
      <SettingsModal
        isOpen={true}
        onClose={() => {}}
        detectorStatus={{ is_running: false, threshold: 0.35, cooldown_seconds: 3.0 }}
        onUpdateConfig={() => {}}
        onStartDetector={() => {}}
        onStopDetector={() => {}}
      />
    )
    await waitFor(() => {
      expect(screen.getByText('Detector Settings & Audio Control')).toBeInTheDocument()
    })
    expect(screen.getByText('0.35')).toBeInTheDocument()
    expect(screen.getByText('Start Live Detector')).toBeInTheDocument()
  })

  it('shows confirmation prompt before stopping active detector', async () => {
    render(
      <SettingsModal
        isOpen={true}
        onClose={() => {}}
        detectorStatus={{ is_running: true, threshold: 0.35 }}
        onUpdateConfig={() => {}}
        onStartDetector={() => {}}
        onStopDetector={() => {}}
      />
    )
    await waitFor(() => {
      expect(screen.getByText('Stop Detector')).toBeInTheDocument()
    })
    const stopBtn = screen.getByText('Stop Detector')
    fireEvent.click(stopBtn)
    expect(screen.getByText('Confirm Stop?')).toBeInTheDocument()
  })
})
