import React, { useState } from 'react'
import { SectionLabel } from './DefinitionList'

export default function ImagePicker({ images, selected, onSelect, word }) {
  const [customQuery, setCustomQuery] = useState('')
  const [customImages, setCustomImages] = useState([])
  const [searching, setSearching] = useState(false)

  const handleCustomSearch = async () => {
    if (!customQuery.trim()) return
    setSearching(true)
    const results = await window.api.getImages(customQuery.trim())
    setCustomImages(results || [])
    setSearching(false)
  }

  const allImages = [...images, ...customImages]

  // selected is now an array of URLs
  const selectedArray = Array.isArray(selected) ? selected : []

  const toggleImage = (url) => {
    if (selectedArray.includes(url)) {
      // deselect
      onSelect(selectedArray.filter(u => u !== url))
    } else {
      // select (max 4)
      if (selectedArray.length < 4) {
        onSelect([...selectedArray, url])
      }
    }
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      <SectionLabel text={`välj bild${selectedArray.length > 0 ? `er (${selectedArray.length}/4)` : 'er'}`} />

      {/* main image grid */}
      {images.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr)',
          gap: '6px',
          marginBottom: '12px',
        }}>
          {images.map((url, i) => (
            <ImageThumb
              key={i}
              url={url}
              isSelected={selectedArray.includes(url)}
              onSelect={() => toggleImage(url)}
              disabled={!selectedArray.includes(url) && selectedArray.length >= 4}
            />
          ))}
          <NoneThumb 
            isSelected={selectedArray.length === 0} 
            onSelect={() => onSelect([])} 
          />
        </div>
      )}

      {/* custom search */}
      <div style={{
        background: 'var(--bg-2)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '10px',
      }}>
        <div style={{
          fontSize: '10px',
          color: 'var(--text-muted)',
          marginBottom: '6px',
          letterSpacing: '0.05em',
        }}>
          EGEN SÖKNING
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <input
            value={customQuery}
            onChange={e => setCustomQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCustomSearch()}
            placeholder={`försök "dog photo" eller "swedish flag"`}
            style={{
              flex: 1,
              background: 'var(--bg-3)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              padding: '5px 8px',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
            }}
          />
          <button
            onClick={handleCustomSearch}
            disabled={searching || !customQuery.trim()}
            style={{
              background: 'var(--accent)',
              color: '#fff',
              fontSize: '11px',
              padding: '5px 12px',
              borderRadius: 'var(--radius)',
              opacity: (searching || !customQuery.trim()) ? 0.5 : 1,
              cursor: (searching || !customQuery.trim()) ? 'not-allowed' : 'pointer',
            }}
          >
            {searching ? '...' : 'sök'}
          </button>
        </div>

        {/* custom results */}
        {customImages.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(5, 1fr)',
            gap: '6px',
            marginTop: '10px',
          }}>
            {customImages.map((url, i) => (
              <ImageThumb
                key={`custom-${i}`}
                url={url}
                isSelected={selectedArray.includes(url)}
                onSelect={() => toggleImage(url)}
                disabled={!selectedArray.includes(url) && selectedArray.length >= 4}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ImageThumb({ url, isSelected, onSelect, disabled }) {
  return (
    <div
      onClick={disabled ? undefined : onSelect}
      style={{
        aspectRatio: '1',
        borderRadius: 'var(--radius)',
        overflow: 'hidden',
        border: `2px solid ${isSelected ? 'var(--accent-2)' : 'transparent'}`,
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'border-color 0.15s, transform 0.1s, opacity 0.15s',
        transform: isSelected ? 'scale(1.04)' : 'scale(1)',
        background: 'var(--bg-3)',
        position: 'relative',
        opacity: disabled ? 0.4 : 1,
      }}
    >
      <img
        src={url}
        alt=""
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block',
        }}
        onError={e => { e.target.style.display = 'none' }}
      />
      {isSelected && (
        <div style={{
          position: 'absolute',
          bottom: '3px',
          right: '3px',
          background: 'var(--accent-2)',
          color: '#000',
          fontSize: '9px',
          borderRadius: '2px',
          padding: '1px 3px',
          fontWeight: 'bold',
        }}>
          ✓
        </div>
      )}
    </div>
  )
}

function NoneThumb({ isSelected, onSelect }) {
  return (
    <div
      onClick={onSelect}
      style={{
        aspectRatio: '1',
        borderRadius: 'var(--radius)',
        border: `2px solid ${isSelected ? 'var(--accent-2)' : 'var(--border)'}`,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-muted)',
        fontSize: '10px',
        transition: 'border-color 0.15s',
        background: 'var(--bg-2)',
      }}
    >
      ingen
    </div>
  )
}