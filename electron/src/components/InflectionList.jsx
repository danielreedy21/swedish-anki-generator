import React from 'react'
import { SectionLabel } from './DefinitionList'

export default function InflectionList({ definitions }) {
  // collect all inflections across all definitions, deduplicated
  const inflections = [...new Set(
    definitions.flatMap(def => def.inflections || [])
  )]

  if (!inflections.length) return null

  return (
    <div style={{ marginBottom: '16px' }}>
      <SectionLabel text="böjningar" />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {inflections.map((inflection, i) => (
          <span key={i} style={{
            fontFamily: 'var(--font-serif)',
            fontStyle: 'italic',
            fontWeight: 300,
            fontSize: '13px',
            color: 'var(--text)',
            background: 'var(--bg-2)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '3px 10px',
          }}>
            {inflection}
          </span>
        ))}
      </div>
    </div>
  )
}