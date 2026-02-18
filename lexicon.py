import json
import xml.etree.ElementTree as ET
from typing import Optional
from config import FOLKETS_XML_PATH, KAIKKI_JSONL_PATH

# ---------------------------------------------------------------------------
# Class definitions
# ---------------------------------------------------------------------------

CLASS_DEFINITIONS = {
    'ab': 'adverb',
    'abbrev': 'förkortning',
    'article': 'artikel',
    'hp': 'frågepronomen',
    'ie': 'infinitivmärke',
    'in': 'interjektion',
    'jj': 'adjektiv',
    'kn': 'konjunktion',
    'nn': 'substantiv',
    'pm': 'egennamn',
    'pn': 'pronomen',
    'pp': 'preposition',
    'prefix': 'förled',
    'ps': 'possessivt pronomen',
    'rg': 'grundtal',
    'sn': 'subjunktion',
    'suffix': 'efterled',
    'vb': 'verb',
    '': 'okategoriserad',
    None: 'okategoriserad',
}

# ---------------------------------------------------------------------------
# XML parsing
# ---------------------------------------------------------------------------

def parse_element(element):
    """Recursively parse an XML element into a dict."""
    entry = {'tag': element.tag}
    entry.update(element.attrib)

    if element.text and element.text.strip():
        entry['text'] = element.text.strip()

    children = [parse_element(child) for child in element]
    if children:
        entry['children'] = children

    return entry


def build_lexicon(xml_path: str) -> dict:
    """Parse the Folkets XML and return the raw lexicon dict."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    lexicon = {}

    for word in root.findall('word'):
        swedish = word.get('value')
        is_compound = '|' in swedish
        compound_delineated = swedish if is_compound else None

        if is_compound:
            swedish = swedish.replace('|', '')

        word_data = {
            'attributes': dict(word.attrib),
            'children': [parse_element(child) for child in word]
        }

        if is_compound:
            word_data['children'].append({
                'tag': 'compound delineation',
                'value': compound_delineated
            })

        if swedish in lexicon:
            lexicon[swedish].append(word_data)
        else:
            lexicon[swedish] = [word_data]

    return lexicon


# ---------------------------------------------------------------------------
# Kaikki / Wiktionary noun senses
# ---------------------------------------------------------------------------

def build_noun_senses(jsonl_path: str) -> dict:
    """Parse the Wiktionary JSONL and return noun gender senses."""
    noun_senses = {}

    with open(jsonl_path, 'r') as f:
        for line in f:
            entry = json.loads(line)

            if entry.get('pos') != 'noun':
                continue

            word = entry.get('word')

            for sense in entry.get('senses', []):
                tags = sense.get('tags', [])
                glosses = sense.get('glosses', [])

                if 'neuter' in tags:
                    article = 'ett'
                elif 'common-gender' in tags or 'masculine' in tags or 'feminine' in tags:
                    article = 'en'
                else:
                    article = None

                for gloss in glosses:
                    if word not in noun_senses:
                        noun_senses[word] = []
                    noun_senses[word].append({
                        'gloss': gloss,
                        'article': article
                    })

    return noun_senses


# ---------------------------------------------------------------------------
# Word detail extraction
# ---------------------------------------------------------------------------

def get_noun_article(word: str, noun_senses: dict) -> Optional[str]:
    """Return 'en word', 'ett word', 'en/ett word', or None."""
    if word not in noun_senses:
        return None

    articles = {sense['article'] for sense in noun_senses[word]}

    if 'en' in articles and 'ett' in articles:
        return f'en/ett {word}'
    elif 'en' in articles:
        return f'en {word}'
    elif 'ett' in articles:
        return f'ett {word}'
    return None


def get_word_details(word: str, lexicon: dict, noun_senses: dict) -> dict:
    """Extract a clean details dict for a single word from the raw lexicon."""
    word_elements = lexicon[word]
    word_definitions = []

    for word_element in word_elements:
        definition_dict = {}
        word_class = word_element.get('attributes', {}).get('class')
        definition_dict['class'] = CLASS_DEFINITIONS.get(word_class, 'okategoriserad')

        synonyms = []
        inflections = []

        for tag in word_element['children']:
            t = tag['tag']
            if t == 'compound delineation':
                definition_dict['compound_delineation'] = tag['value']
            elif t == 'definition':
                definition_dict['definition'] = tag.get('value', '')
            elif t == 'translation':
                definition_dict['translation'] = tag.get('value', '')
            elif t == 'phonetic':
                definition_dict['phonetic'] = tag.get('value', '')
            elif t == 'example':
                definition_dict['example'] = tag.get('value', '')
            elif t == 'synonym':
                synonyms.append(tag.get('value', ''))
            elif t == 'paradigm':
                for child in tag.get('children', []):
                    inflections.append(child.get('value', ''))

        definition_dict['synonyms'] = synonyms
        definition_dict['inflections'] = inflections
        word_definitions.append(definition_dict)

    return {
        'word with article': get_noun_article(word=word, noun_senses=noun_senses),
        'definitions': word_definitions,
    }


def build_word_data(lexicon: dict, noun_senses: dict) -> dict:
    """Build the full word_data dict for every word in the lexicon."""
    word_data = {}
    for word in lexicon.keys():
        word_data[word] = get_word_details(
            word=word,
            lexicon=lexicon,
            noun_senses=noun_senses
        )
    return word_data


def build_inflection_map(word_data: dict) -> dict:
    """Build a map of inflected form -> base word."""
    inflection_map = {}
    for word, data in word_data.items():
        for definition in data['definitions']:
            for inflection in definition.get('inflections', []):
                inflection_map[inflection] = word
    return inflection_map


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def lookup_word(word: str, word_data: dict, inflection_map: dict) -> Optional[dict]:
    """
    Look up a word by its base form or any inflected form.
    Returns {base_word: word_details} or None if not found.
    """
    if word in word_data:
        return {word: word_data[word]}
    elif word in inflection_map:
        base_word = inflection_map[word]
        return {base_word: word_data[base_word]}
    return None


# ---------------------------------------------------------------------------
# Module-level data — loaded once at import time
# ---------------------------------------------------------------------------

print('Loading lexicon...')
_lexicon = build_lexicon(FOLKETS_XML_PATH)

print('Loading noun senses...')
_noun_senses = build_noun_senses(KAIKKI_JSONL_PATH)

print('Building word data...')
word_data = build_word_data(_lexicon, _noun_senses)

print('Building inflection map...')
inflection_map = build_inflection_map(word_data)

print(f'Lexicon ready: {len(word_data)} words, {len(inflection_map)} inflections')
