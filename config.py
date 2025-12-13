"""Configuration settings for stock_watch_agent."""
import os
from pathlib import Path

# Database configuration
DB_PATH = Path(__file__).parent / "stock_watch.db"

# LLM API configuration
# Default to Google Gemini, but can be switched to OpenAI
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "openai"

# Google Gemini configuration (default)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBJb9qjovfIZ5swj_DD1Ss7E1JbZ7hgNVU")
# Common working models: "gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash-latest"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# OpenAI configuration (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Console output configuration
USE_RICH = True  # Use rich library for better console output

