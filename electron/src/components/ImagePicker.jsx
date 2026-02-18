import React from 'react'
import { SectionLabel } from './DefinitionList'

export default function ImagePicker({ images, selected, onSelect }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <SectionLabel text="välj bild" />

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: '6px',
      }}>
        {images.map((url, i) => (
          <ImageThumb
            key={i}
            url={url}
            isSelected={url === selected}
            onSelect={() => onSelect(url === selected ? null : url)} // toggle off if clicked again
          />
        ))}

        {/* 'none' option */}
        <NoneThumb isSelected={selected === null} onSelect={() => onSelect(null)} />
      </div>
    </div>
  )
}

function ImageThumb({ url, isSelected, onSelect }) {
  return (
    <div
      onClick={onSelect}
      style={{
        aspectRatio: '1',
        borderRadius: 'var(--radius)',
        overflow: 'hidden',
        border: `2px solid ${isSelected ? 'var(--accent-2)' : 'transparent'}`,
        cursor: 'pointer',
        transition: 'border-color 0.15s, transform 0.1s',
        transform: isSelected ? 'scale(1.04)' : 'scale(1)',
        background: 'var(--bg-3)',
        position: 'relative',
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