import React, { useState, useEffect, useCallback } from 'react'
import WordHeader from './WordHeader'
import DefinitionList from './DefinitionList'
import InflectionList from './InflectionList'
import ImagePicker from './ImagePicker'
import CardCreator from './CardCreator'

export default function App() {
  const [query, setQuery]               = useState('')
  const [wordData, setWordData]         = useState(null)  // { word, details }
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState(null)
  const [selectedDef, setSelectedDef]   = useState(0)
  const [images, setImages]             = useState([])
  const [selectedImage, setSelectedImage] = useState([])
  const [audioPath, setAudioPath]       = useState(null)
  const [cardStatus, setCardStatus]     = useState(null) // 'success' | 'error' | null
  const [step, setStep]                 = useState('lookup') // 'lookup' | 'images' | 'done'

  // ---------------------------------------------------------------------------
  // Lookup
  // ---------------------------------------------------------------------------

  const lookupWord = useCallback(async (word) => {
    if (!word?.trim()) return
    const w = word.trim().toLowerCase()
    setQuery(w)
    setLoading(true)
    setError(null)
    setWordData(null)
    setImages([])
    setSelectedImage([])
    setAudioPath(null)
    setCardStatus(null)
    setSelectedDef(0)
    setStep('lookup')

    try {
      const result = await window.api.lookupWord(w)
      if (!result) {
        setError(`"${w}" not found in dictionary`)
        return
      }
      const [baseWord, details] = Object.entries(result)[0]
      setWordData({ word: baseWord, details })

      // fetch images and audio in parallel, don't block the UI
      window.api.getImages(baseWord).then(imgs => {
        setImages(imgs || [])
        if (imgs?.length) setStep('images')
      })
      window.api.getAudio(baseWord).then(audio => {
        setAudioPath(audio?.path || null)
      })
    } catch (e) {
      setError('Could not connect to backend — is Flask running?')
    } finally {
      setLoading(false)
    }
  }, [])

  // listen for hotkey-triggered lookups from main process
  useEffect(() => {
    const cleanup = window.api.onLookupWord((word) => {
      lookupWord(word)
    })
    return cleanup
  }, [lookupWord])

  // ---------------------------------------------------------------------------
  // Card creation
  // ---------------------------------------------------------------------------

  const handleCreateCard = async (deck, createReverse) => {
    if (!wordData) return

    const cardData = {
      word: wordData.word,
      article: wordData.details['word with article'],
      definitions: wordData.details.definitions,  // pass all definitions
      audio_path: audioPath,
      image_urls: selectedImage,  // now an array
      deck,
      create_reverse: createReverse,
    }

    const result = await window.api.createCard(cardData)

    if (result?.success) {
      setCardStatus('success')
      setStep('done')
      // auto-hide after 1.5s
      setTimeout(() => window.api.hideWindow(), 1500)
    } else {
      setCardStatus(`error:${result?.error || 'Unknown error'}`)
    }
  }

  // ---------------------------------------------------------------------------
  // Improve translation
  // ---------------------------------------------------------------------------

  const handleImproveTranslation = async () => {
    if (!wordData) return
    const improved = await window.api.improveTranslation(wordData.word, selectedDef)
    if (improved) {
      setWordData(prev => {
        const defs = [...prev.details.definitions]
        defs[selectedDef] = improved
        return { ...prev, details: { ...prev.details, definitions: defs } }
      })
    }
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const def = wordData?.details?.definitions?.[selectedDef]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg)' }}>

      {/* drag region */}
      <div className="titlebar" />

      {/* search bar */}
      <SearchBar
        query={query}
        onChange={setQuery}
        onSubmit={() => lookupWord(query)}
      />

      <div className="scroll" style={{ flex: 1, padding: '0 16px 16px' }}>

        {loading && <StatusMessage text="søker..." />}
        {error && <StatusMessage text={error} isError />}

        {wordData && !loading && (
          <div className="fade-up">

            <WordHeader
              word={wordData.word}
              article={wordData.details['word with article']}
              phonetic={def?.phonetic}
              audioPath={audioPath}
            />

            <DefinitionList
              definitions={wordData.details.definitions}
              selectedIndex={selectedDef}
              onSelect={setSelectedDef}
              onImprove={handleImproveTranslation}
            />

            <InflectionList
              definitions={wordData.details.definitions}
            />

            {images.length > 0 && (
              <ImagePicker
                images={images}
                selected={selectedImage}
                onSelect={setSelectedImage}
                word={wordData.word}
              />
            )}

            <CardCreator
              onCreateCard={handleCreateCard}
              disabled={!def}
              cardStatus={cardStatus}
            />

          </div>
        )}

        {step === 'done' && cardStatus === 'success' && (
          <div className="fade-up" style={{ textAlign: 'center', padding: '24px', color: 'var(--success)' }}>
            ✓ card created
          </div>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Search bar
// ---------------------------------------------------------------------------

function SearchBar({ query, onChange, onSubmit }) {
  return (
    <div style={{
      padding: '8px 16px 12px',
      borderBottom: '1px solid var(--border)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        background: 'var(--bg-2)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '6px 10px',
        gap: '8px',
      }}>
        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>sök</span>
        <input
          value={query}
          onChange={e => onChange(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && onSubmit()}
          placeholder="skriv ett ord..."
          style={{
            flex: 1,
            background: 'transparent',
            color: 'var(--text)',
            fontSize: '13px',
            caretColor: 'var(--accent-2)',
          }}
          autoFocus
        />
        {query && (
          <button
            onClick={onSubmit}
            style={{
              background: 'var(--accent)',
              color: '#fff',
              fontSize: '11px',
              padding: '2px 8px',
              borderRadius: '3px',
            }}
          >
            →
          </button>
        )}
      </div>
    </div>
  )
}

function StatusMessage({ text, isError }) {
  return (
    <div style={{
      padding: '24px 0',
      color: isError ? 'var(--danger)' : 'var(--text-muted)',
      fontStyle: 'italic',
      textAlign: 'center',
    }}>
      {text}
    </div>
  )
}