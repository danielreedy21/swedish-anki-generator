import React from 'react'

export default function WordHeader({ word, article, phonetic, audioPath }) {
  const playAudio = () => {
    if (!audioPath) return
    window.api.playAudio(audioPath)
  }

  return (
    <div style={{
      padding: '20px 0 16px',
      borderBottom: '1px solid var(--border)',
      marginBottom: '16px',
    }}>

      {/* article badge */}
      {article && (
        <div style={{
          fontSize: '11px',
          color: 'var(--accent-2)',
          fontFamily: 'var(--font-mono)',
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          marginBottom: '4px',
        }}>
          {article.split(' ')[0]}  {/* just 'en' or 'ett' or 'en/ett' */}
        </div>
      )}

      {/* word */}
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        gap: '12px',
      }}>
        <h1 style={{
          fontFamily: 'var(--font-serif)',
          fontWeight: 300,
          fontSize: '32px',
          color: 'var(--text)',
          lineHeight: 1.1,
          fontStyle: 'italic',
        }}>
          {word}
        </h1>

        {/* audio button */}
        {audioPath && (
          <button
            onClick={playAudio}
            title="play pronunciation"
            style={{
              background: 'none',
              color: 'var(--text-muted)',
              fontSize: '16px',
              padding: '2px',
              lineHeight: 1,
            }}
          >
            ♪
          </button>
        )}
      </div>

      {/* phonetic */}
      {phonetic && (
        <div style={{
          marginTop: '4px',
          color: 'var(--text-muted)',
          fontSize: '12px',
          fontFamily: 'var(--font-mono)',
        }}>
          [{phonetic}]
        </div>
      )}
    </div>
  )
}