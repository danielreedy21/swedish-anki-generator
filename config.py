import os
from dotenv import load_dotenv
load_dotenv()

# --- API Keys ---
# set these as environment variables, or replace directly for local dev
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
FORVO_API_KEY = os.getenv('FORVO_API_KEY')
SERPER_DEV_API_KEY = os.getenv('SERPER_DEV_API_KEY')

# --- Data Paths ---
FOLKETS_XML_PATH = os.getenv('FOLKETS_XML_PATH', 'data/folkets_sv_en_public.xml')
KAIKKI_JSONL_PATH = os.getenv('KAIKKI_JSONL_PATH', 'data/kaikki.org-dictionary-Swedish.jsonl')

# --- Audio ---
AUDIO_DIR = os.getenv('AUDIO_DIR', 'audio')
ANKI_MEDIA_DIR = os.getenv('ANKI_MEDIA_DIR', '/Users/danielreedy/Library/Application Support/Anki2/User 1/collection.media')

# --- Anki ---
ANKI_CONNECT_URL = 'http://localhost:8765'
ANKI_DECK_NAME = 'Swedish'
ANKI_MODEL_NAME = 'Basic'

# --- Claude ---
CLAUDE_MODEL = 'claude-haiku-4-5-20251001'
CLAUDE_MAX_TOKENS = 50
