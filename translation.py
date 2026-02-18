import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def improve_translation(word: str, definition_entry: dict) -> dict:
    """
    Call Claude Haiku to improve the Folkets translation for a single definition.
    Adds 'improved_translation' key alongside the existing 'translation'.
    Returns the updated definition_entry.
    """
    word_class = definition_entry.get('class', '')
    folkets_translation = definition_entry.get('translation', 'none')
    swedish_definition = definition_entry.get('definition', '')
    synonyms = ', '.join(definition_entry.get('synonyms', []))

    prompt = (
        f'You are a Swedish to English dictionary assistant.\n'
        f'Word: "{word}"\n'
        f'Part of speech: {word_class}\n'
        f'Swedish definition: "{swedish_definition}"\n'
        f'Swedish synonyms: "{synonyms}"\n'
        f'Folkets Lexikon translation: "{folkets_translation}"\n\n'
        f'Give the most natural English translation for this specific sense of the word. '
        f'Reply with only the translation, no explanation.'
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{'role': 'user', 'content': prompt}]
    )

    definition_entry['improved_translation'] = response.content[0].text.strip()
    return definition_entry


def get_translation(definition_entry: dict) -> str:
    """
    Return the best available translation for a definition —
    improved if it exists, otherwise fall back to Folkets.
    """
    return (
        definition_entry.get('improved_translation')
        or definition_entry.get('translation')
        or ''
    )


def generate_definition(word: str, definition_entry: dict) -> str:
    """
    Generate a Swedish definition when one is missing, using Claude Haiku.
    Uses the translation, word class, and any synonyms/examples as context.
    """
    word_class = definition_entry.get('class', '')
    translation = get_translation(definition_entry)
    synonyms = ', '.join(definition_entry.get('synonyms', []))
    example = definition_entry.get('example', '')

    prompt = (
        f'You are a Swedish dictionary editor.\n'
        f'Word: "{word}"\n'
        f'Part of speech: {word_class}\n'
        f'English translation: "{translation}"\n'
    )

    if synonyms:
        prompt += f'Swedish synonyms: "{synonyms}"\n'
    if example:
        prompt += f'Example usage: "{example}"\n'

    prompt += (
        f'\nWrite a concise Swedish definition (max 15 words) that explains what this word means. '
        f'Do not include the word itself or any of its inflections in the definition. '
        f'Reply with only the definition in Swedish, no explanation.'
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[{'role': 'user', 'content': prompt}]
    )

    return response.content[0].text.strip()