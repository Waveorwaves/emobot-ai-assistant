"""
Configuration settings for the emobot personal assistant.
"""
import os
import logging
from pathlib import Path

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using environment variables directly.")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data storage paths
DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory"
USER_DATA_DIR = DATA_DIR / "user_data"

# Ensure directories exist
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# API Keys and tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")  # Default to 1.5 if not specified

# Paths for Gmail service, loaded from environment variables
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")

# Bot settings
BOT_NAME = "Emobot"
BOT_VERSION = "0.1.0"
DEFAULT_LANGUAGE = "en"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure logging
def setup_logging():
    """Configure the logging system."""
    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
    )
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()

# Voice processing settings
STT_ENGINE = "google"  # Options: google, whisper, etc.
TTS_ENGINE = "google"  # Options: google, elevenlabs, etc.

# Search settings
SEARCH_COOLDOWN = 2  # seconds between searches