# Swedish Anki Card Generator - Project Context

## Project Overview
A desktop application (Electron + Flask) that helps create Anki flashcards for Swedish vocabulary learning. The app parses the Folkets Lexikon Swedish-English dictionary, enriches it with multiple data sources, and provides a streamlined UI for creating forward (word→translation) and reverse (image→word) flashcards.

## Tech Stack
- **Backend**: Flask (Python 3.9+)
- **Frontend**: Electron with React
- **Dictionary Data**: Folkets Lexikon XML + Wiktionary JSONL
- **APIs Used**: 
  - Anthropic Claude API (Haiku 4.5) for translation improvement and definition generation
  - Forvo API for audio pronunciation
  - Serper API for Google Images search
- **Anki Integration**: AnkiConnect plugin

## Project Structure
```
anki_swedish/
├── app.py                  # Flask backend with REST API
├── lexicon.py             # Dictionary parsing and lookup
├── translation.py         # Claude-powered translation improvement
├── audio.py              # Forvo audio download with caching
├── images.py             # Wikimedia + Serper image search
├── anki.py               # AnkiConnect card creation
├── config.py             # Environment variables and settings
├── requirements.txt      # Python dependencies
├── data/
│   ├── folkets_sv_en_public.xml
│   └── kaikki.org-dictionary-Swedish.jsonl
└── electron/
    ├── main.js           # Electron main process (hotkey, clipboard)
    ├── preload.js        # IPC bridge
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── index.html
        ├── index.jsx
        ├── styles.css    # Dark Scandinavian theme
        └── components/
            ├── App.jsx
            ├── WordHeader.jsx
            ├── DefinitionList.jsx
            ├── InflectionList.jsx
            ├── ImagePicker.jsx
            └── CardCreator.jsx
```

## Key Features

### Dictionary System
- **36,602 words** with 41,699 inflections from Folkets Lexikon
- **Inflection map**: Look up any word form (e.g., `hundar` → `hund`)
- **Gender detection**: Uses Wiktionary data to determine `en`/`ett` for nouns
- **Compound word handling**: Words like `riks|dag` → `riksdag`
- **Multiple definitions**: Words with multiple senses (e.g., `lag` = law/team/layer/marinade)

### Data Sources Hierarchy
1. **Folkets Lexikon XML** (primary): Swedish definitions, translations, examples, synonyms, inflections
2. **Wiktionary JSONL** (enrichment): Gender tags, IPA, additional audio
3. **Claude API** (fallback): 
   - Improves poor translations on demand
   - Generates Swedish definitions when missing
4. **Forvo API**: Audio pronunciation (cached locally)
5. **Serper API**: Image search (5 results + custom search)

### Card Creation
**Forward Cards** (`word-card`, `forward-card`):
- Front: Word with article (e.g., `en hund` or `måste, ett måste` for mixed noun/verb)
- Back: All definitions numbered with translations, Swedish definitions, examples, synonyms, phonetic, audio, up to 4 images

**Reverse Cards** (`word-card`, `reverse-card`):
- Front: Up to 4 images + collapsible hint with all Swedish definitions
- Back: Word with article, phonetic, audio

**Tags**: `swedish`, `word-card`, `forward-card`/`reverse-card`, plus word classes (`substantiv`, `verb`, etc.)

### UI/UX Features
- **Global hotkey**: `Cmd+Shift+S` copies word from clipboard and opens window
- **Dark theme**: Scandinavian-inspired with Swedish blue (#006AA7) and yellow (#FECC02)
- **Swedish labels**: `sök`, `välj bilder`, `böjningar`, `skapa kort`
- **Multi-image selection**: Pick up to 4 images (shown as 2×2 grid on card)
- **Custom image search**: Override automatic results with custom Serper query
- **Default deck**: Saved to localStorage, persists across sessions
- **Reverse cards**: Checked by default
- **Auto-hide**: Window hides after card creation (1.5s delay)

## API Endpoints (Flask)

```
GET  /health                    # Status check
GET  /lookup/<word>             # Look up word (handles inflections)
POST /improve-translation       # Improve translation with Claude
GET  /audio/<word>              # Download Forvo audio
GET  /images/<word>             # Get 5 images (Wikimedia + Serper)
POST /create-card               # Create Anki card(s)
GET  /decks                     # List Anki decks
```

## Important Implementation Details

### Audio Handling
- Audio files saved to `ANKI_MEDIA_DIR` (set in .env to Anki's `collection.media` folder)
- **Caching**: Only downloads if file doesn't exist
- **Playback**: Uses macOS `afplay` via IPC (not HTML5 Audio due to Electron security)
- Card format: `[sound:hund.mp3]` (filename only, not full path)

### Image Handling
- **Automatic search**: Queries word directly via Serper (Swedish locale `gl=se`, `hl=sv`)
- **Custom search**: User can input own query (e.g., "dog photo" vs "hund")
- **Storage**: URLs embedded directly in cards (not downloaded)
- **Layout**: 1 image = centered, 2 = side-by-side, 3-4 = 2×2 grid

### Translation Improvement
- Only called on demand via `✦ improve` button
- Updates immediately in UI via callback
- Persists improved translation alongside original in backend
- Cost: ~$0.00015 per call (Haiku 4.5)

### Definition Generation
- Automatically triggered when Folkets has no Swedish definition
- Prompt includes: word, class, translation, synonyms, examples
- Max 15 words, avoids using the word itself or inflections
- Used for both forward and reverse cards

### Card Front Logic (Mixed Word Classes)
```python
has_noun = any(d.get('class') == 'substantiv' for d in definitions)
has_non_noun = any(d.get('class') != 'substantiv' for d in definitions)

if has_noun and has_non_noun and article:
    front_word = f'{word}, {article}'  # e.g., "måste, ett måste"
elif article:
    front_word = article               # e.g., "en hund"
else:
    front_word = word                  # e.g., "förklara"
```

## Environment Variables (.env)
```bash
ANTHROPIC_API_KEY=sk-...
FORVO_API_KEY=...
SERPER_API_KEY=...
ANKI_MEDIA_DIR=/Users/.../Anki2/User 1/collection.media
FOLKETS_XML_PATH=data/folkets_sv_en_public.xml
KAIKKI_JSONL_PATH=data/kaikki.org-dictionary-Swedish.jsonl
```

## Running the App

**Terminal 1 - Flask:**
```bash
cd anki_swedish
python app.py
```

**Terminal 2 - Vite:**
```bash
cd anki_swedish/electron
npm run dev:vite
```

**Terminal 3 - Electron:**
```bash
cd anki_swedish/electron
npm run dev
```

**Prerequisites:**
- Anki running with AnkiConnect plugin installed (code: `2055492159`)
- Python 3.9+ with dependencies: `pip install -r requirements.txt`
- Node.js 16+ with dependencies: `npm install`

## Known Issues & Solutions

### React Import Errors
All `.jsx` files must import React explicitly:
```javascript
import React from 'react'
```

### Python Type Hints (3.9 compatibility)
Use `Optional[str]` instead of `str | None`:
```python
from typing import Optional
def func(arg: Optional[str]) -> Optional[dict]:
```

### Audio Path Issues
- Must be absolute paths
- Use `os.path.abspath()` in `audio.py`
- Use `os.path.basename()` when embedding in card

### Vite Hot Reload
Sometimes requires full restart if React components don't update:
```bash
Ctrl+C (both Vite and Electron)
npm run dev:vite
npm run dev  # in separate terminal
```

## Future Enhancement Ideas
- AI image generation button (Flux/DALL-E) as fallback
- Sentence cards (fill-in-the-blank)
- Grammar cards
- Browser extension version
- Export/import custom vocabulary lists
- Spaced repetition analytics

## Design Philosophy
- **All definitions on one card**: Better context than separate cards per sense
- **Reverse cards by default**: Most effective for recall
- **Multi-image support**: Different contexts aid memory
- **Swedish-first UI**: Immersive language learning experience
- **Minimal friction**: Global hotkey → card created in 3 clicks

## Key Files to Reference

**Backend Logic:**
- `lexicon.py` - All dictionary parsing, word lookup, inflection mapping
- `anki.py` - Card HTML generation and AnkiConnect calls
- `translation.py` - Claude integration

**Frontend Components:**
- `App.jsx` - Main state management and lookup flow
- `DefinitionList.jsx` - Display all definitions with improve buttons
- `ImagePicker.jsx` - Multi-select with custom search
- `CardCreator.jsx` - Deck selection, reverse toggle, localStorage

**Electron IPC:**
- `main.js` - Global hotkey, clipboard, all API calls to Flask
- `preload.js` - Secure bridge exposing `window.api.*`

## Common Modification Patterns

**Adding a new data source:**
1. Create new module (e.g., `newsource.py`)
2. Add API key to `config.py`
3. Create endpoint in `app.py`
4. Add IPC handler in `main.js`
5. Expose in `preload.js`
6. Call from React component

**Changing card layout:**
- Edit `add_card()` and `add_reverse_card()` in `anki.py`
- HTML/CSS is inline in Python strings
- Test in Anki card browser after changes

**Adding new UI component:**
1. Create in `electron/src/components/`
2. Import in `App.jsx`
3. Pass necessary props (word, definitions, etc.)
4. Use `window.api.*` for backend calls
