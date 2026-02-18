import requests
from config import SERPER_DEV_API_KEY

WIKIMEDIA_API = 'https://en.wikipedia.org/api/rest_v1/page/summary'
SERPER_API = 'https://google.serper.dev/images'


def get_wikimedia_images(word: str) -> list[str]:
    """
    Try to get an image from Wikipedia for the given word.
    Returns a list with one URL if found, empty list otherwise.
    """
    try:
        response = requests.get(f'{WIKIMEDIA_API}/{word}', timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()
        thumbnail = data.get('thumbnail', {}).get('source')
        return [thumbnail] if thumbnail else []
    except Exception as e:
        print(f'Wikimedia error for "{word}": {e}')
        return []


def get_serper_images(word: str, num: int = 5) -> list[str]:
    """
    Search Google Images via Serper for the given word.
    Uses Swedish locale for more relevant results.
    Returns a list of image URLs.
    """
    try:
        response = requests.post(
            SERPER_API,
            headers={
                'X-API-KEY': SERPER_DEV_API_KEY,
                'Content-Type': 'application/json'
            },
            json={
                'q': word + 'bild',
                'gl': 'se',   # Swedish locale
                'hl': 'sv',   # Swedish language
                'num': num
            },
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get('images', [])
        return [r['imageUrl'] for r in results if 'imageUrl' in r]
    except Exception as e:
        print(f'Serper error for "{word}": {e}')
        return []


def get_images(word: str, num: int = 5) -> list[str]:
    """
    Waterfall image search:
    1. Try Wikimedia (free, no rate limits)
    2. Fall back to Serper (paid, broader coverage)
    Returns up to `num` image URLs.
    """
    images = get_wikimedia_images(word)

    # if Wikimedia only gave us 1, top up with Serper results
    if len(images) < num:
        serper_images = get_serper_images(word, num=num)
        # deduplicate while preserving order
        seen = set(images)
        for img in serper_images:
            if img not in seen:
                images.append(img)
                seen.add(img)

    return images[:num]
