import React, { useState, useEffect } from 'react'
import { SectionLabel } from './DefinitionList'

export default function CardCreator({ onCreateCard, disabled, cardStatus }) {
  const [decks, setDecks]       = useState([])
  const [selectedDeck, setSelectedDeck] = useState('Swedish')
  const [createReverse, setCreateReverse] = useState(true)  // checked by default
  const [creating, setCreating] = useState(false)
  const [ankiError, setAnkiError] = useState(null)

  // load available Anki decks and restore saved default
  useEffect(() => {
    window.api.getDecks().then(d => {
      if (d?.length) {
        setDecks(d)
        // restore saved default deck from localStorage
        const savedDeck = localStorage.getItem('defaultAnkiDeck')
        if (savedDeck && d.includes(savedDeck)) {
          setSelectedDeck(savedDeck)
        } else if (d.includes('Swedish')) {
          setSelectedDeck('Swedish')
        } else {
          setSelectedDeck(d[0])
        }
      }
    }).catch(() => {
      setAnkiError('Anki is not running — open Anki to create cards')
    })
  }, [])

  // save deck selection as new default when changed
  const handleDeckChange = (deck) => {
    setSelectedDeck(deck)
    localStorage.setItem('defaultAnkiDeck', deck)
  }

  const handleCreate = async () => {
    setCreating(true)
    setAnkiError(null)
    await onCreateCard(selectedDeck, createReverse)
    setCreating(false)
  }

  const isSuccess = cardStatus === 'success'
  const isError = cardStatus?.startsWith('error:')
  const errorMessage = isError ? cardStatus.replace('error:', '') : null

  return (
    <div style={{ marginTop: '4px' }}>
      <SectionLabel text="skapa kort" />

      {ankiError && (
        <div style={{
          fontSize: '11px',
          color: 'var(--danger)',
          marginBottom: '8px',
          fontStyle: 'italic',
        }}>
          {ankiError}
        </div>
      )}

      {/* deck selector */}
      {decks.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <select
            value={selectedDeck}
            onChange={e => handleDeckChange(e.target.value)}
            style={{
              background: 'var(--bg-2)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              padding: '5px 8px',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
              width: '100%',
              cursor: 'pointer',
            }}
          >
            {decks.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <div style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            marginTop: '4px',
          }}>
            sparas som standard
          </div>
        </div>
      )}

      {/* reverse card toggle */}
      <label style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '10px',
        fontSize: '11px',
        color: 'var(--text-muted)',
        cursor: 'pointer',
      }}>
        <input
          type="checkbox"
          checked={createReverse}
          onChange={e => setCreateReverse(e.target.checked)}
          style={{ cursor: 'pointer' }}
        />
        skapa också omvänt kort (bild → ord)
      </label>

      {/* create button */}
      <button
        onClick={handleCreate}
        disabled={disabled || creating || isSuccess || !!ankiError}
        style={{
          width: '100%',
          padding: '10px',
          background: isSuccess
            ? 'var(--success)'
            : isError
            ? 'var(--danger)'
            : 'var(--accent)',
          color: '#fff',
          fontSize: '12px',
          letterSpacing: '0.05em',
          borderRadius: 'var(--radius)',
          opacity: (disabled || !!ankiError) ? 0.4 : 1,
          cursor: (disabled || !!ankiError) ? 'not-allowed' : 'pointer',
        }}
      >
        {creating  ? 'skapar...'
        : isSuccess ? '✓ kortet skapat'
        : isError   ? '✗ försök igen'
        : '+ skapa anki-kort'}
      </button>

      {/* error detail */}
      {errorMessage && (
        <div style={{
          marginTop: '6px',
          fontSize: '11px',
          color: 'var(--danger)',
          fontStyle: 'italic',
        }}>
          {errorMessage}
        </div>
      )}
    </div>
  )
}