from flask import Flask, jsonify, request
from flask_cors import CORS

from lexicon import word_data, inflection_map, lookup_word
from translation import improve_translation, get_translation, generate_definition
from audio import get_forvo_audio
from images import get_images
from anki import add_card, add_reverse_card, get_decks, is_anki_running

app = Flask(__name__)
CORS(app)  # allow Electron frontend to call the API


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'words_loaded': len(word_data),
        'inflections_loaded': len(inflection_map),
        'anki_running': is_anki_running(),
    })


# ---------------------------------------------------------------------------
# Word lookup
# ---------------------------------------------------------------------------

@app.route('/lookup/<word>')
def lookup(word):
    """
    Look up a word by its base form or any inflected form.
    Returns the base word and all its definitions.
    """
    result = lookup_word(
        word=word.lower().strip(),
        word_data=word_data,
        inflection_map=inflection_map
    )

    if not result:
        return jsonify({'error': f'"{word}" not found'}), 404

    return jsonify(result)


# ---------------------------------------------------------------------------
# Translation improvement
# ---------------------------------------------------------------------------

@app.route('/improve-translation', methods=['POST'])
def improve():
    """
    Improve the Folkets translation for a specific definition using Claude.
    Expects JSON: { "word": "sträckning", "definition_index": 0 }
    Updates word_data in place and returns the improved definition.
    """
    data = request.get_json()
    word = data.get('word')
    definition_index = data.get('definition_index', 0)

    if word not in word_data:
        return jsonify({'error': f'"{word}" not found'}), 404

    definitions = word_data[word]['definitions']

    if definition_index >= len(definitions):
        return jsonify({'error': 'definition_index out of range'}), 400

    updated = improve_translation(
        word=word,
        definition_entry=definitions[definition_index]
    )

    # update in place so subsequent lookups return the improved translation
    word_data[word]['definitions'][definition_index] = updated

    return jsonify(updated)


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

@app.route('/audio/<word>')
def audio(word):
    """
    Download the Forvo pronunciation for a word and save it to Anki media dir.
    Returns the file path.
    """
    path = get_forvo_audio(word)

    if not path:
        return jsonify({'error': f'No audio found for "{word}"'}), 404

    return jsonify({'path': path, 'filename': path.split('/')[-1]})


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------

@app.route('/images/<word>')
def images(word):
    """
    Return up to 5 image URLs for a word (Wikimedia first, then Serper).
    """
    num = request.args.get('num', 5, type=int)
    urls = get_images(word=word, num=num)

    if not urls:
        return jsonify({'error': f'No images found for "{word}"'}), 404

    return jsonify({'images': urls})


# ---------------------------------------------------------------------------
# Anki card creation
# ---------------------------------------------------------------------------

@app.route('/create-card', methods=['POST'])
def create_card():
    """
    Create an Anki card via AnkiConnect.
    Expects JSON with word details and the user's chosen image URL.

    Required fields: word, word_class, translation, definition
    Optional fields: article, example, synonyms, phonetic,
                     audio_path, image_url, deck
    """
    data = request.get_json()

    required = ['word', 'definitions']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    definitions = data['definitions']
    if not definitions:
        return jsonify({'error': 'No definitions provided'}), 400

    # generate definitions for any entries missing them
    for i, def_entry in enumerate(definitions):
        if not def_entry.get('definition'):
            print(f'Generating definition for "{data["word"]}" sense {i+1}...')
            definitions[i]['definition'] = generate_definition(data['word'], def_entry)

    # collect all word classes for tags
    word_classes = list(set(d.get('class', '') for d in definitions if d.get('class')))

    if not is_anki_running():
        return jsonify({'error': 'Anki is not running or AnkiConnect is not installed'}), 503

    try:
        note_id = add_card(
            word=data['word'],
            article=data.get('article'),
            definitions=definitions,
            word_classes=word_classes,
            audio_path=data.get('audio_path'),
            image_urls=data.get('image_urls', []),
            deck=data.get('deck', 'Swedish'),
        )

        result = {'success': True, 'note_id': note_id}

        # create reverse card if requested - use all definitions and images
        if data.get('create_reverse'):
            # use first definition's phonetic (they're usually the same across senses)
            first_phonetic = definitions[0].get('phonetic') if definitions else None
            reverse_id = add_reverse_card(
                word=data['word'],
                article=data.get('article'),
                definitions=definitions,
                phonetic=first_phonetic,
                audio_path=data.get('audio_path'),
                image_urls=data.get('image_urls', []),
                deck=data.get('deck', 'Swedish'),
            )
            result['reverse_note_id'] = reverse_id

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Anki utilities
# ---------------------------------------------------------------------------

@app.route('/decks')
def decks():
    """Return all Anki deck names so the frontend can let the user pick one."""
    if not is_anki_running():
        return jsonify({'error': 'Anki is not running'}), 503
    return jsonify({'decks': get_decks()})


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(port=5000, debug=False)