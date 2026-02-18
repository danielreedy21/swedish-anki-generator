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


def add_card(
    word: str,
    article: Optional[str],
    word_class: str,
    translation: str,
    definition: str,
    example: Optional[str],
    synonyms: list,
    phonetic: Optional[str],
    audio_path: Optional[str],
    image_url: Optional[str],
    deck: str = ANKI_DECK_NAME,
) -> int:
    """
    Create an Anki card via AnkiConnect.
    Returns the new note ID.

    Front: the word with article (if noun), e.g. 'en hund'
    Back:  translation, definition, example, synonyms, audio, image
    """
    front_word = f'{article}' if article else word

    # build back of card
    back_parts = [f'<b>{translation}</b>']

    if definition:
        back_parts.append(f'<i>{definition}</i>')

    if example:
        back_parts.append(f'Exempel: {example}')

    if synonyms:
        back_parts.append(f'Synonymer: {", ".join(synonyms)}')

    if phonetic:
        back_parts.append(f'[{phonetic}]')

    if audio_path:
        filename = os.path.basename(audio_path)
        back_parts.append(f'[sound:{filename}]')

    if image_url:
        back_parts.append(f'<img src="{image_url}">')

    back = '<br><br>'.join(back_parts)

    note_id = _ankiconnect(
        'addNote',
        note={
            'deckName': deck,
            'modelName': ANKI_MODEL_NAME,
            'fields': {
                'Front': front_word,
                'Back': back,
            },
            'tags': ['swedish', word_class.lower()],
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
    definition: str,
    phonetic: Optional[str],
    audio_path: Optional[str],
    image_url: Optional[str],
    deck: str = ANKI_DECK_NAME,
) -> int:
    """
    Create a reverse Anki card (image + definition → word).
    The front shows the image with a collapsible definition hint.
    The back shows the Swedish word with phonetic and audio.
    """
    front_word = f'{article}' if article else word

    # front: image and collapsible definition
    front_parts = []
    if image_url:
        front_parts.append(f'<img src="{image_url}" style="max-width: 300px; border-radius: 8px;">')
    
    if definition:
        # collapsible definition using <details> HTML tag
        front_parts.append(f'''
            <details style="margin-top: 12px; cursor: pointer;">
                <summary style="color: #7a7570; font-size: 11px;">💡 visa ledtråd</summary>
                <div style="margin-top: 8px; font-style: italic; color: #e8e4dd;">
                    {definition}
                </div>
            </details>
        ''')
    
    front = '<br>'.join(front_parts) if front_parts else 'no context available'

    # back: word with phonetic and audio
    back_parts = [f'<span style="font-size: 24px; font-style: italic;">{front_word}</span>']
    
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
            'tags': ['swedish', 'reverse'],
            'options': {
                'allowDuplicate': False,
                'duplicateScope': 'deck',
            }
        }
    )

    return note_id