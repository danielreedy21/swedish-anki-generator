import React, { useState } from 'react'

export default function DefinitionList({ definitions, word, onImprove }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <SectionLabel text="definitioner" />

      {definitions.map((def, i) => (
        <DefinitionCard
          key={i}
          def={def}
          index={i}
          word={word}
          definitionIndex={i}
          onImprove={onImprove}
        />
      ))}
    </div>
  )
}

function DefinitionCard({ def, index, word, definitionIndex, onImprove }) {
  const [improving, setImproving] = useState(false)
  const translation = def.improved_translation || def.translation

  const handleImprove = async () => {
    setImproving(true)
    const improvedDef = await window.api.improveTranslation(word, definitionIndex)
    if (improvedDef && onImprove) {
      onImprove(definitionIndex, improvedDef)
    }
    setImproving(false)
  }

  return (
    <div
      style={{
        background: 'var(--bg-2)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '12px',
        marginBottom: '8px',
      }}
    >
      {/* header row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>

        {/* index */}
        <span style={{
          fontSize: '10px',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)',
          minWidth: '16px',
        }}>
          {index + 1}.
        </span>

        {/* word class badge */}
        <span style={{
          fontSize: '10px',
          color: 'var(--accent)',
          border: '1px solid var(--accent)',
          borderRadius: '3px',
          padding: '1px 5px',
          opacity: 0.8,
        }}>
          {def.class}
        </span>

        {/* translation */}
        <span style={{
          flex: 1,
          fontFamily: 'var(--font-serif)',
          fontSize: '15px',
          fontWeight: 300,
          color: 'var(--text)',
        }}>
          {translation || <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>no translation</span>}
        </span>

        {/* improve button */}
        <button
          onClick={handleImprove}
          disabled={improving}
          title="improve translation with Claude"
          style={{
            fontSize: '10px',
            color: improving ? 'var(--text-muted)' : 'var(--accent-2)',
            background: 'none',
            padding: '2px 4px',
            opacity: improving ? 0.5 : 1,
          }}
        >
          {improving ? '...' : '✦ improve'}
        </button>
      </div>

      {/* Swedish definition */}
      {def.definition && (
        <div style={{
          fontSize: '12px',
          color: 'var(--text-muted)',
          marginBottom: def.example || def.synonyms?.length ? '6px' : 0,
          paddingLeft: '24px',
          lineHeight: 1.5,
        }}>
          {def.definition}
        </div>
      )}

      {/* example */}
      {def.example && (
        <div style={{
          fontSize: '11px',
          color: 'var(--text-muted)',
          fontStyle: 'italic',
          paddingLeft: '24px',
          marginBottom: def.synonyms?.length ? '4px' : 0,
        }}>
          ex. {def.example}
        </div>
      )}

      {/* synonyms */}
      {def.synonyms?.length > 0 && (
        <div style={{ paddingLeft: '24px', marginTop: '4px', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
          {def.synonyms.map((s, i) => (
            <span key={i} style={{
              fontSize: '10px',
              color: 'var(--text-muted)',
              background: 'var(--bg)',
              border: '1px solid var(--border)',
              borderRadius: '3px',
              padding: '1px 5px',
            }}>
              {s}
            </span>
          ))}
        </div>
      )}

      {/* show if translation was improved */}
      {def.improved_translation && (
        <div style={{
          paddingLeft: '24px',
          marginTop: '6px',
          fontSize: '10px',
          color: 'var(--success)',
        }}>
          ✦ improved · original: {def.translation}
        </div>
      )}
    </div>
  )
}

export function SectionLabel({ text }) {
  return (
    <div style={{
      fontSize: '10px',
      color: 'var(--text-muted)',
      letterSpacing: '0.1em',
      textTransform: 'uppercase',
      marginBottom: '8px',
    }}>
      {text}
    </div>
  )
}