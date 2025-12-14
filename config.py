"""Configuration settings for stock_watch_agent."""
import os
from pathlib import Path

def reload_env():
    """Reload environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)  # override=True ensures it reloads
        return True
    except ImportError:
        # python-dotenv not installed, skip .env loading
        return False

# Load environment variables from .env file if it exists
reload_env()

# Database configuration
DB_PATH = Path(__file__).parent / "stock_watch.db"

# LLM API configuration
# Default to Google Gemini, but can be switched to OpenAI
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "openai"

# Google Gemini configuration (default)
# API key should be set via environment variable or .env file
# Never commit your API key to the repository!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Common working models: "gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash-latest"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# OpenAI configuration (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Console output configuration
USE_RICH = True  # Use rich library for better console output

