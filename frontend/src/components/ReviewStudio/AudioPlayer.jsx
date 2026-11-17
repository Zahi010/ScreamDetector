import { useState, useRef, useEffect, useCallback } from 'react'

export function AudioPlayer({
  recordingId,
  hasAudio,
  onPrev,
  onNext,
  hasPrev,
  hasNext,
}) {
  const audioRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(0.85)
  const [playbackRate, setPlaybackRate] = useState(1.0)
  const [isLoading, setIsLoading] = useState(false)
  const [audioError, setAudioError] = useState(null)

  const audioSrc = recordingId && hasAudio ? `/api/review/recordings/${recordingId}/audio` : null

  // Reset player state when recording changes
  useEffect(() => {
    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    setAudioError(null)

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      if (audioSrc) {
        setIsLoading(true)
        audioRef.current.load()
      }
    }
  }, [audioSrc, recordingId])

  // Apply volume and playback speed
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume
      audioRef.current.playbackRate = playbackRate
    }
  }, [volume, playbackRate])

  const togglePlay = useCallback(() => {
    if (!audioRef.current || !audioSrc) return

    if (isPlaying) {
      audioRef.current.pause()
      setIsPlaying(false)
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true)
      }).catch(err => {
        console.warn('Playback error:', err)
        setAudioError('Failed to play audio stream')
        setIsPlaying(false)
      })
    }
  }, [isPlaying, audioSrc])

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration || 0)
      setIsLoading(false)
    }
  }

  const handleEnded = () => {
    setIsPlaying(false)
    setCurrentTime(0)
  }

  const handleSeek = (e) => {
    const newTime = parseFloat(e.target.value)
    setCurrentTime(newTime)
    if (audioRef.current) {
      audioRef.current.currentTime = newTime
    }
  }

  const handleVolumeChange = (e) => {
    const newVol = parseFloat(e.target.value)
    setVolume(newVol)
  }

  const handleSpeedChange = (rate) => {
    setPlaybackRate(rate)
    if (audioRef.current) {
      audioRef.current.playbackRate = rate
    }
  }

  const formatTime = (secs) => {
    if (isNaN(secs) || secs < 0) return '0:00'
    const m = Math.floor(secs / 60)
    const s = Math.floor(secs % 60)
    return `${m}:${s < 10 ? '0' : ''}${s}`
  }

  if (!hasAudio) {
    return (
      <div className="audio-player-missing" data-testid="audio-player-missing">
        <div className="audio-missing-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="1" y1="1" x2="23" y2="23"></line>
            <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
            <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
        </div>
        <div className="audio-missing-text">
          <strong>Audio File Unavailable Locally</strong>
          <span>This candidate metadata exists in manifest, but audio has not been downloaded to local disk.</span>
        </div>
      </div>
    )
  }

  return (
    <div className="review-audio-player" data-testid="review-audio-player">
      <audio
        ref={audioRef}
        src={audioSrc}
        preload="metadata"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        onError={() => {
          setIsLoading(false)
          setAudioError('Error loading audio stream')
        }}
      />

      {/* Top Playback Controls */}
      <div className="player-top-controls">
        <div className="nav-buttons-group">
          <button
            type="button"
            className="btn-player-nav"
            onClick={onPrev}
            disabled={!hasPrev}
            title="Previous Clip [Arrow Left]"
            aria-label="Previous recording"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="19 20 9 12 19 4 19 20"></polygon>
              <line x1="5" y1="19" x2="5" y2="5"></line>
            </svg>
          </button>

          <button
            type="button"
            className={`btn-player-play ${isPlaying ? 'is-playing' : ''}`}
            onClick={togglePlay}
            disabled={isLoading || !audioSrc}
            title={isPlaying ? 'Pause [Space]' : 'Play [Space]'}
            aria-label={isPlaying ? 'Pause recording' : 'Play recording'}
          >
            {isLoading ? (
              <span className="spinner-sm" />
            ) : isPlaying ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            )}
          </button>

          <button
            type="button"
            className="btn-player-nav"
            onClick={onNext}
            disabled={!hasNext}
            title="Next Clip [Arrow Right]"
            aria-label="Next recording"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polygon points="5 4 15 12 5 20 5 4"></polygon>
              <line x1="19" y1="5" x2="19" y2="19"></line>
            </svg>
          </button>
        </div>

        {/* Time Display */}
        <div className="player-time-display font-mono">
          <span>{formatTime(currentTime)}</span>
          <span className="time-sep">/</span>
          <span>{formatTime(duration)}</span>
        </div>

        {/* Speed Controls */}
        <div className="speed-selector">
          {[0.75, 1.0, 1.25, 1.5].map((rate) => (
            <button
              key={rate}
              type="button"
              className={`btn-speed ${playbackRate === rate ? 'active' : ''}`}
              onClick={() => handleSpeedChange(rate)}
              title={`Playback speed ${rate}x`}
            >
              {rate}x
            </button>
          ))}
        </div>

        {/* Volume Control */}
        <div className="player-volume-control">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          </svg>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
            aria-label="Volume slider"
          />
        </div>
      </div>

      {/* Seek Progress Bar */}
      <div className="player-seek-container">
        <input
          type="range"
          min="0"
          max={duration || 100}
          step="0.05"
          value={currentTime}
          onChange={handleSeek}
          className="player-seek-bar"
          aria-label="Audio timeline position"
          disabled={!duration}
        />
      </div>

      {/* Error or shortcut banner */}
      {audioError ? (
        <div className="audio-error-msg">{audioError}</div>
      ) : (
        <div className="player-shortcuts-hint">
          <span className="kbd-hint"><kbd>Space</kbd> Play/Pause</span>
          <span className="kbd-hint"><kbd>←</kbd> Prev</span>
          <span className="kbd-hint"><kbd>→</kbd> Next</span>
          <span className="kbd-hint"><kbd>1</kbd>–<kbd>4</kbd> Review Actions</span>
        </div>
      )}
    </div>
  )
}
