"""Helper functions for managing API keys securely.

This module prefers environment variables, then Streamlit `st.secrets` when
available (useful for Streamlit Cloud deployments), and only falls back to an
interactive prompt when running in a terminal.
"""
import os
import getpass
import sys
from pathlib import Path
from typing import Optional

import config


def _lookup_streamlit_secret(key: str) -> Optional[str]:
    """Try to read a key from Streamlit secrets without requiring Streamlit UI.

    Returns the secret value or None if not available.
    """
    try:
        import streamlit as _st
        secrets = _st.secrets
        if not secrets:
            return None
        # secrets can be dict-like; check several common keys/nesting patterns
        if isinstance(secrets, dict):
            # Top-level direct key
            if key in secrets:
                return secrets.get(key)
            # Lowercase variant
            lower = key.lower()
            if lower in secrets:
                return secrets.get(lower)
            # Nested under provider name, e.g. {"GEMINI": {"API_KEY": "..."}}
            provider = key.split("_")[0]
            if provider in secrets and isinstance(secrets.get(provider), dict):
                # Try common nested keys
                for nested in ("API_KEY", "GEMINI_API_KEY", "api_key", "key"):
                    val = secrets.get(provider).get(nested)
                    if val:
                        return val
        else:
            # Some versions of Streamlit return Secrets object supporting dict-like access
            try:
                if secrets.get(key):
                    return secrets.get(key)
            except Exception:
                pass
    except Exception:
        # Streamlit not installed or not running; ignore
        return None

    return None


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from env, Streamlit secrets, or prompt if interactive.

    In non-interactive environments (e.g. Streamlit Cloud), this will NOT prompt
    the user and will return None if the key is not found.
    """
    # Prefer explicit environment variable first
    api_key = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
    if api_key:
        return api_key

    # Try Streamlit secrets (useful for Streamlit Cloud deployments)
    secret_key = _lookup_streamlit_secret("GEMINI_API_KEY")
    if secret_key:
        os.environ["GEMINI_API_KEY"] = secret_key
        return secret_key

    # If running in a real terminal, prompt the user interactively
    try:
        if sys.stdin is not None and sys.stdin.isatty():
            print("\n" + "=" * 60)
            print("Gemini API Key not found!")
            print("=" * 60)
            print("You can get a free API key from: https://makersuite.google.com/app/apikey")
            print("\nOptions:")
            print("1. Set environment variable: $env:GEMINI_API_KEY='your-key'")
            print("2. Create a .env file with: GEMINI_API_KEY=your-key")
            print("3. Enter it now (will not be saved)")
            print("\n" + "-" * 60)

            choice = input("Enter API key now? (y/n): ").strip().lower()
            if choice in ["y", "yes"]:
                print("\nInput options:")
                print("1. Hidden input (secure, recommended)")
                print("2. Visible input (less secure, but you can see what you type)")
                input_choice = input("Choose option (1/2, default=1): ").strip() or "1"
                try:
                    if input_choice == "2":
                        print("\n⚠️  Warning: Your API key will be visible as you type!")
                        api_key = input("Enter your Gemini API key: ").strip()
                    else:
                        print("\n⚠️  Note: Your input will be hidden for security (you can still type, it just won't show)")
                        print("   Or press Ctrl+C to cancel and use .env file or environment variable instead.\n")
                        api_key = getpass.getpass("Enter your Gemini API key: ").strip()

                    if api_key:
                        os.environ["GEMINI_API_KEY"] = api_key
                        print("✓ API key received and set for this session.")
                        return api_key
                    else:
                        print("No API key provided.")
                        return None
                except KeyboardInterrupt:
                    print("\n\nCancelled. Please set your API key using .env file or environment variable.")
                    return None
            else:
                print("\nPlease set your API key using one of the methods above.")
                return None
    except Exception:
        # If any error occurs (non-interactive environment), do not prompt
        return None

    return None


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key, prompting user if not set."""
    api_key = os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY
    if api_key:
        return api_key

    # Try Streamlit secrets
    secret_key = _lookup_streamlit_secret("OPENAI_API_KEY")
    if secret_key:
        os.environ["OPENAI_API_KEY"] = secret_key
        return secret_key

    # If running in a terminal, prompt; otherwise return None for non-interactive
    try:
        if sys.stdin is not None and sys.stdin.isatty():
            print("\n" + "=" * 60)
            print("OpenAI API Key not found!")
            print("=" * 60)
            print("You can get an API key from: https://platform.openai.com/api-keys")
            print("\nOptions:")
            print("1. Set environment variable: $env:OPENAI_API_KEY='your-key'")
            print("2. Create a .env file with: OPENAI_API_KEY=your-key")
            print("3. Enter it now (will not be saved)")
            print("\n" + "-" * 60)

            choice = input("Enter API key now? (y/n): ").strip().lower()
            if choice in ["y", "yes"]:
                print("\nInput options:")
                print("1. Hidden input (secure, recommended)")
                print("2. Visible input (less secure, but you can see what you type)")
                input_choice = input("Choose option (1/2, default=1): ").strip() or "1"
                try:
                    if input_choice == "2":
                        print("\n⚠️  Warning: Your API key will be visible as you type!")
                        api_key = input("Enter your OpenAI API key: ").strip()
                    else:
                        print("\n⚠️  Note: Your input will be hidden for security (you can still type, it just won't show)")
                        print("   Or press Ctrl+C to cancel and use .env file or environment variable instead.\n")
                        api_key = getpass.getpass("Enter your OpenAI API key: ").strip()

                    if api_key:
                        os.environ["OPENAI_API_KEY"] = api_key
                        print("✓ API key received and set for this session.")
                        return api_key
                    else:
                        print("No API key provided.")
                        return None
                except KeyboardInterrupt:
                    print("\n\nCancelled. Please set your API key using .env file or environment variable.")
                    return None
            else:
                print("\nPlease set your API key using one of the methods above.")
                return None
    except Exception:
        return None

    return None


def setup_api_key_interactive():
    """Interactive setup for API keys."""
    provider = config.LLM_PROVIDER.lower()
    
    if provider == "gemini":
        api_key = get_gemini_api_key()
        if api_key:
            print("\n✓ API key set for this session.")
            print("To make it permanent, create a .env file or set environment variable.")
        return api_key
    elif provider == "openai":
        api_key = get_openai_api_key()
        if api_key:
            print("\n✓ API key set for this session.")
            print("To make it permanent, create a .env file or set environment variable.")
        return api_key
    else:
        print(f"Unknown provider: {provider}")
        return None

