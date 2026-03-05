import os
import requests
from typing import Optional
from config import ANKI_CONNECT_URL, ANKI_DECK_NAME, ANKI_MODEL_NAME


def _ankiconnect(action: str, **params):
    """Send a request to the AnkiConnect plugin."""
    payload = {'action': action, 'version': 6, 'params': params}
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()
        if result.get('error'):
            raise Exception(result['error'])
        return result.get('result')
    except requests.exceptions.ConnectionError:
        raise Exception(
            'Could not connect to AnkiConnect. '
            'Make sure Anki is running and the AnkiConnect plugin is installed.'
        )


def is_anki_running() -> bool:
    """Check whether Anki is open and AnkiConnect is reachable."""
    try:
        _ankiconnect('version')
        return True
    except Exception:
        return False


def _build_inflections_html(definitions: list) -> str:
    """
    Build an HTML block showing inflections for all definitions.
    Groups inflections by word class when there are multiple definition senses.
    Returns an empty string if no inflections exist.
    """
    groups = []
    for def_entry in definitions:
        inflections = def_entry.get('inflections', [])
        if not inflections:
            continue
        word_class = def_entry.get('class', '')
        groups.append((word_class, inflections))

    if not groups:
        return ''

    chip_style = (
        'display: inline-block;'
        'background: rgba(255,255,255,0.08);'
        'border: 1px solid rgba(255,255,255,0.15);'
        'border-radius: 4px;'
        'padding: 2px 8px;'
        'margin: 2px 3px;'
        'font-size: 13px;'
        'color: #c8c4be;'
    )

    label_style = (
        'font-size: 10px;'
        'color: #7a7570;'
        'text-transform: uppercase;'
        'letter-spacing: 0.05em;'
        'margin-right: 4px;'
    )

    parts = []

    if len(groups) == 1:
        _, inflections = groups[0]
        chips = ''.join(f'<span style="{chip_style}">{inf}</span>' for inf in inflections)
        parts.append(f'<div style="margin-top: 10px;">{chips}</div>')
    else:
        for word_class, inflections in groups:
            chips = ''.join(f'<span style="{chip_style}">{inf}</span>' for inf in inflections)
            label = f'<span style="{label_style}">{word_class}:</span>' if word_class else ''
            parts.append(f'<div style="margin-top: 6px;">{label}{chips}</div>')

    return ''.join(parts)


def _build_images_html(image_urls: list) -> str:
    """
    Build a responsive image block for up to 4 images, optimized for mobile.
    - 1 image: centered, max 600px wide, scales down on smaller screens
    - 2-4 images: 2-column grid, each image constrained and cropped to uniform height
    """
    if not image_urls:
        return ''

    num_images = len(image_urls)

    single_img_style = (
        'max-width: 600px;'
        'width: 100%;'
        'height: auto;'
        'border-radius: 8px;'
        'display: block;'
        'margin: 0 auto;'
    )

    grid_cell_style = (
        'width: 48%;'
        'display: inline-block;'
        'margin: 1%;'
        'vertical-align: top;'
    )

    grid_img_style = (
        'width: 100%;'
        'height: 160px;'
        'object-fit: cover;'
        'border-radius: 8px;'
        'display: block;'
    )

    if num_images == 1:
        return f'<img src="{image_urls[0]}" style="{single_img_style}">'
    else:
        cells = ''.join(
            f'<span style="{grid_cell_style}"><img src="{url}" style="{grid_img_style}" class="anki-grid-img"></span>'
            for url in image_urls
        )
        # Media query bumps grid image height to 260px on wider screens (desktop)
        responsive_style = (
            '<style>'
            '@media (min-width: 600px) { .anki-grid-img { height: 260px !important; } }'
            '</style>'
        )
        return (
            f'{responsive_style}'
            f'<div style="max-width: 600px; margin: 0 auto; font-size: 0;">'
            f'{cells}'
            f'</div>'
        )


def add_card(
    word: str,
    article: Optional[str],
    definitions: list,
    word_classes: list,
    audio_path: Optional[str],
    image_urls: list,
    deck: str = ANKI_DECK_NAME,
) -> int:
    """
    Create an Anki card with all definitions for a word.
    Each definition is numbered and includes its translation, Swedish definition,
    examples, and synonyms. Supports up to 4 images.
    """
    has_noun = any(d.get('class') == 'substantiv' for d in definitions)
    has_non_noun = any(d.get('class') != 'substantiv' for d in definitions)

    if has_noun and has_non_noun and article:
        front_word = f'{word}, {article}'
    elif article:
        front_word = article
    else:
        front_word = word

    front = f'<div style="font-size: 28px; font-weight: bold;">{front_word}</div>'

    back_parts = []

    for i, def_entry in enumerate(definitions, 1):
        def_parts = []

        word_class = def_entry.get('class', '')
        translation = def_entry.get('improved_translation') or def_entry.get('translation', '')

        header = f'<b>{i}. {word_class}'
        if translation:
            header += f' — {translation}'
        header += '</b>'
        def_parts.append(header)

        definition = def_entry.get('definition')
        if definition:
            def_parts.append(f'<i>{definition}</i>')

        example = def_entry.get('example')
        if example:
            def_parts.append(f'<span style="font-size: 90%;">ex: {example}</span>')

        synonyms = def_entry.get('synonyms', [])
        if synonyms:
            def_parts.append(f'<span style="font-size: 90%;">synonymer: {", ".join(synonyms)}</span>')

        if i == 1:
            phonetic = def_entry.get('phonetic')
            if phonetic:
                def_parts.append(f'<span style="font-size: 90%; color: #999;">[{phonetic}]</span>')

        inflections = def_entry.get('inflections', [])
        if inflections:
            chip_style = (
                'display: inline-block;'
                'background: rgba(255,255,255,0.08);'
                'border: 1px solid rgba(255,255,255,0.15);'
                'border-radius: 4px;'
                'padding: 2px 8px;'
                'margin: 2px 3px;'
                'font-size: 13px;'
                'color: #c8c4be;'
            )
            chips = ''.join(f'<span style="{chip_style}">{inf}</span>' for inf in inflections)
            def_parts.append(f'<div style="margin-top: 4px;">{chips}</div>')

        back_parts.append('<br>'.join(def_parts))

    if audio_path:
        filename = os.path.basename(audio_path)
        back_parts.append(f'[sound:{filename}]')

    images_html = _build_images_html(image_urls)
    if images_html:
        back_parts.append(images_html)

    back = '<br><br>'.join(back_parts)

    note_id = _ankiconnect(
        'addNote',
        note={
            'deckName': deck,
            'modelName': ANKI_MODEL_NAME,
            'fields': {
                'Front': front,
                'Back': back,
            },
            'tags': ['swedish', 'word-card', 'forward-card'] + [wc.lower() for wc in word_classes if wc],
            'options': {
                'allowDuplicate': False,
                'duplicateScope': 'deck',
            }
        }
    )

    return note_id


def get_decks() -> list[str]:
    """Return all deck names from Anki."""
    return _ankiconnect('deckNames')


def add_reverse_card(
    word: str,
    article: Optional[str],
    definitions: list,
    phonetic: Optional[str],
    audio_path: Optional[str],
    image_urls: list,
    deck: str = ANKI_DECK_NAME,
) -> int:
    """
    Create a reverse Anki card (images + definitions → word).
    The front shows up to 4 images with collapsible definition hints.
    The back shows the Swedish word with phonetic, audio, and inflections.
    """
    has_noun = any(d.get('class') == 'substantiv' for d in definitions)
    has_non_noun = any(d.get('class') != 'substantiv' for d in definitions)

    if has_noun and has_non_noun and article:
        back_word = f'{word}, {article}'
    elif article:
        back_word = article
    else:
        back_word = word

    front_parts = []

    images_html = _build_images_html(image_urls)
    if images_html:
        front_parts.append(images_html)

    if definitions:
        def_lines = []
        for i, def_entry in enumerate(definitions, 1):
            definition = def_entry.get('definition', '')
            if definition:
                word_class = def_entry.get('class', '')
                def_lines.append(f'{i}. {word_class} — <i>{definition}</i>')

        if def_lines:
            definitions_html = '<br>'.join(def_lines)
            front_parts.append(f'''
                <details style="margin-top: 12px; cursor: pointer;">
                    <summary style="color: #7a7570; font-size: 11px;">💡 visa ledtråd</summary>
                    <div style="margin-top: 8px; font-size: 12px; color: #e8e4dd;">
                        {definitions_html}
                    </div>
                </details>
            ''')

    front = '<br>'.join(front_parts) if front_parts else 'no context available'

    inflections_html = _build_inflections_html(definitions)

    back_parts = [f'<div style="font-size: 24px; font-style: italic;">{back_word}</div>']

    if inflections_html:
        back_parts.append(inflections_html)

    if phonetic:
        back_parts.append(f'<div style="color: #7a7570; font-size: 13px; margin-top: 6px;">[{phonetic}]</div>')

    if audio_path:
        filename = os.path.basename(audio_path)
        back_parts.append(f'[sound:{filename}]')

    back = ''.join(back_parts)

    note_id = _ankiconnect(
        'addNote',
        note={
            'deckName': deck,
            'modelName': ANKI_MODEL_NAME,
            'fields': {
                'Front': front,
                'Back': back,
            },
            'tags': ['swedish', 'word-card', 'reverse-card'],
            'options': {
                'allowDuplicate': False,
                'duplicateScope': 'deck',
            }
        }
    )

    return note_id