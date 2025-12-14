"""Helper functions for managing API keys securely."""
import os
import getpass
from pathlib import Path
from typing import Optional

import config


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key, prompting user if not set."""
    api_key = config.GEMINI_API_KEY
    
    if not api_key:
        print("\n" + "="*60)
        print("Gemini API Key not found!")
        print("="*60)
        print("You can get a free API key from: https://makersuite.google.com/app/apikey")
        print("\nOptions:")
        print("1. Set environment variable: $env:GEMINI_API_KEY='your-key'")
        print("2. Create a .env file with: GEMINI_API_KEY=your-key")
        print("3. Enter it now (will not be saved)")
        print("\n" + "-"*60)
        
        choice = input("Enter API key now? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
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
                    # Temporarily set it for this session
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
    
    return api_key


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key, prompting user if not set."""
    api_key = config.OPENAI_API_KEY
    
    if not api_key:
        print("\n" + "="*60)
        print("OpenAI API Key not found!")
        print("="*60)
        print("You can get an API key from: https://platform.openai.com/api-keys")
        print("\nOptions:")
        print("1. Set environment variable: $env:OPENAI_API_KEY='your-key'")
        print("2. Create a .env file with: OPENAI_API_KEY=your-key")
        print("3. Enter it now (will not be saved)")
        print("\n" + "-"*60)
        
        choice = input("Enter API key now? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
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
                    # Temporarily set it for this session
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
    
    return api_key


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

