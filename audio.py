import os
import requests
from typing import Optional
from config import FORVO_API_KEY, ANKI_MEDIA_DIR


def get_forvo_audio(word: str) -> Optional[str]:
    """
    Fetch the best-rated Swedish pronunciation from Forvo and save it
    directly to the Anki media directory.
    Returns the file path, or None if no pronunciation was found.

    Note: Forvo audio URLs expire after 2 hours — always download immediately.
    """
    url = (
        f'https://apifree.forvo.com/key/{FORVO_API_KEY}'
        f'/format/json/action/word-pronunciations'
        f'/word/{word}/language/sv'
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f'Forvo API error for "{word}": {e}')
        return None

    items = data.get('items', [])
    if not items:
        print(f'No Forvo pronunciation found for "{word}"')
        return None

    # items are sorted by vote count — first is best
    best = items[0]
    mp3_url = best.get('pathmp3')
    if not mp3_url:
        return None

    try:
        audio_response = requests.get(mp3_url, timeout=10)
        audio_response.raise_for_status()
    except Exception as e:
        print(f'Failed to download audio for "{word}": {e}')
        return None

    os.makedirs(ANKI_MEDIA_DIR, exist_ok=True)
    filepath = os.path.abspath(os.path.join(ANKI_MEDIA_DIR, f'{word}.mp3'))

    if os.path.exists(filepath):
        print(f'Audio already cached: {filepath}')
        return filepath

    with open(filepath, 'wb') as f:
        f.write(audio_response.content)

    print(f'Audio saved: {filepath}')
    return filepath
