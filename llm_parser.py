"""LLM-based parser for extracting structured data from user text."""
import json
import re
import os
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

import config


def list_available_models(provider: Optional[str] = None) -> None:
    """
    List all available models for the specified provider.
    
    Args:
        provider: "gemini" or "openai". If None, uses config.LLM_PROVIDER
    """
    if provider is None:
        provider = config.LLM_PROVIDER.lower()
    else:
        provider = provider.lower()
    
    print(f"\nListing available models for {provider.upper()}...\n")
    
    if provider == "gemini":
        if not GEMINI_AVAILABLE:
            print("Error: google-generativeai package not installed.")
            print("Install it with: pip install google-generativeai")
            return
        
        if not config.GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY not set.")
            return
        
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            models = genai.list_models()
            
            print("Available Gemini models that support generateContent:\n")
            models_found = False
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    models_found = True
                    model_name = model.name.replace('models/', '')
                    print(f"  ✓ {model_name}")
                    if hasattr(model, 'display_name') and model.display_name:
                        print(f"    Display Name: {model.display_name}")
                    if hasattr(model, 'description') and model.description:
                        print(f"    Description: {model.description}")
                    print()
            
            if not models_found:
                print("  No models found that support generateContent.")
            
            print("\nTo use a model, set GEMINI_MODEL environment variable or update config.py")
            print(f"Example: $env:GEMINI_MODEL=\"{model_name}\"")
            
        except Exception as e:
            print(f"Error listing models: {e}")
            import traceback
            traceback.print_exc()
    
    elif provider == "openai":
        if not OPENAI_AVAILABLE:
            print("Error: openai package not installed.")
            print("Install it with: pip install openai")
            return
        
        if not config.OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY not set.")
            return
        
        try:
            client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_BASE)
            models = client.models.list()
            
            print("Available OpenAI models:\n")
            for model in models.data:
                model_id = model.id
                # Filter to show common GPT models
                if any(x in model_id.lower() for x in ['gpt', 'text', 'davinci', 'curie', 'babbage', 'ada']):
                    print(f"  ✓ {model_id}")
                    if hasattr(model, 'created') and model.created:
                        from datetime import datetime
                        created = datetime.fromtimestamp(model.created)
                        print(f"    Created: {created.strftime('%Y-%m-%d')}")
                    print()
            
            print("\nTo use a model, set OPENAI_MODEL environment variable or update config.py")
            print(f"Example: $env:OPENAI_MODEL=\"gpt-4o-mini\"")
            
        except Exception as e:
            print(f"Error listing models: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print(f"Unknown provider: {provider}. Use 'gemini' or 'openai'.")


class LLMParser:
    """Parses user text using LLM to extract structured stock information."""

    def __init__(self):
        """Initialize LLM parser."""
        # Reload .env file to pick up any changes
        config.reload_env()
        # Reload the API key from environment
        import importlib
        importlib.reload(config)
        
        self.provider = config.LLM_PROVIDER.lower()
        
        if self.provider == "gemini":
            # Get fresh API key after reload
            api_key = os.getenv("GEMINI_API_KEY", "") or config.GEMINI_API_KEY
            
            if not api_key:
                # Try to get API key interactively
                try:
                    from api_key_helper import get_gemini_api_key
                    api_key = get_gemini_api_key()
                    if api_key:
                        config.GEMINI_API_KEY = api_key
                        os.environ["GEMINI_API_KEY"] = api_key
                    else:
                        raise ValueError("GEMINI_API_KEY not set. Please set GEMINI_API_KEY environment variable or create a .env file.")
                except ImportError:
                    raise ValueError("GEMINI_API_KEY not set. Please set GEMINI_API_KEY environment variable or create a .env file.")
            else:
                # Update config with the reloaded key
                config.GEMINI_API_KEY = api_key
            
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai package not installed. Install it with: pip install google-generativeai")
            
            # Configure with the API key and validate it immediately so
            # authentication errors surface at startup instead of later.
            genai.configure(api_key=api_key)

            # Validate the API key by making a lightweight call. This
            # will raise on invalid/unauthorized keys and surface a clear
            # error to the caller (Streamlit UI or CLI) during parser init.
            try:
                genai.list_models()
            except Exception as e:
                raise ValueError(f"Gemini API key validation failed: {e}")

            self.model_name = config.GEMINI_MODEL
            
            # Try to create the model and handle errors gracefully
            try:
                self.client = genai.GenerativeModel(self.model_name)
                self.use_gemini = True
            except Exception as e:
                # If model not found, try common alternatives
                print(f"Warning: Model '{self.model_name}' not available. Trying alternatives...")
                alternative_models = ["gemini-pro", "gemini-1.5-pro", "models/gemini-pro"]
                model_found = False
                for alt_model in alternative_models:
                    try:
                        self.client = genai.GenerativeModel(alt_model)
                        self.model_name = alt_model
                        self.use_gemini = True
                        model_found = True
                        print(f"Using model: {alt_model}")
                        break
                    except:
                        continue
                
                if not model_found:
                    # List available models
                    print("\n" + "="*60)
                    print("Could not initialize the specified model.")
                    print("="*60)
                    try:
                        list_available_models("gemini")
                    except:
                        pass
                    raise ValueError(f"Could not initialize Gemini model '{self.model_name}'. Error: {e}")
            
        elif self.provider == "openai":
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set. Please set OPENAI_API_KEY environment variable.")
            
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Install it with: pip install openai")
            
            self.client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_API_BASE
            )
            self.model_name = config.OPENAI_MODEL
            self.use_gemini = False
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}. Use 'gemini' or 'openai'.")

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse user text and extract structured data.
        
        Returns a dictionary with:
        - symbol: Stock ticker symbol (normalized, e.g., "NVDA", "AAPL")
        - action_type: One of "buy", "hold", "watch", "sell", "review", "unknown"
        - buy_price: Purchase price if mentioned (float or None)
        - conditions: Dictionary of conditions (price thresholds, time periods, etc.)
        - user_opinion: User's opinion or notes (string or None)
        """
        prompt = f"""You are a stock monitoring assistant. Extract structured information from the following user text about stocks.

User text: "{text}"

Extract and return ONLY valid JSON with the following structure:
{{
    "symbol": "TICKER_SYMBOL" or null,
    "action_type": "buy" | "hold" | "watch" | "sell" | "review" | "unknown" or null,
    "buy_price": number or null,
    "conditions": {{
        "price_above": number or null,
        "price_below": number or null,
        "price_between": {{"min": number, "max": number}} or null,
        "percent_change": number or null,
        "percent_drop": number or null,
        "percent_above_buy": number or null,
        "time_period_days": number or null,
        "reminder_days": number or null,
        "trailing_stop": number or null
    }},
    "user_opinion": "string" or null
}}

Rules:
1. Normalize stock symbols to uppercase (e.g., "nvidia" -> "NVDA", "Apple" -> "AAPL")
2. Extract buy_price if user mentions purchasing price
3. Extract conditions from phrases like:
   - "crosses 200$" or "above 200$" -> price_above: 200
   - "goes below 65$" or "below 65$" -> price_below: 65
   - "between 300 and 310" -> price_between: {{"min": 300, "max": 310}}
   - "falls more than 15%" or "drops 15%" -> percent_drop: 15
   - "10% above buy price" or "10% above this price" -> percent_above_buy: 10
   - "rises 20% from buy" -> percent_above_buy: 20
   - "in 3 months" -> reminder_days: 90
   - "after a month" -> time_period_days: 30
   - "trailing stop loss at 300" -> trailing_stop: 300
4. For percentage above buy price: If user says "10% above buy price" or "10% above this price", use percent_above_buy: 10 (NOT price_above)
5. Set missing values to null (not empty strings or empty objects)
6. Return ONLY valid JSON, no additional text or markdown formatting
7. Ensure all JSON is properly closed with matching braces and brackets

JSON:"""

        content = None
        try:
            if self.use_gemini:
                # Reload .env file in case it was updated
                config.reload_env()
                # Get fresh API key
                fresh_api_key = os.getenv("GEMINI_API_KEY", "") or config.GEMINI_API_KEY
                if fresh_api_key and fresh_api_key != config.GEMINI_API_KEY:
                    # API key changed, reconfigure
                    genai.configure(api_key=fresh_api_key)
                    config.GEMINI_API_KEY = fresh_api_key
                    # Recreate client with new key
                    self.client = genai.GenerativeModel(self.model_name)
                
                # Use Gemini API
                full_prompt = f"""You are a helpful assistant that extracts structured data from stock-related text. Always return valid JSON only.

{prompt}"""
                
                response = self.client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 500,
                    }
                )
                content = response.text.strip()
            else:
                # Use OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts structured data from stock-related text. Always return valid JSON only. Do not include any explanatory text before or after the JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                content = response.choices[0].message.content.strip()
            
            if not content:
                print("Error: Empty response from LLM API")
                return self._default_result()
            
            # Remove markdown code blocks if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            # Try to extract JSON if there's extra text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            # Try to fix common JSON issues before parsing
            # Remove trailing commas before closing braces/brackets
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            # Remove any text after the closing brace
            brace_pos = content.rfind('}')
            if brace_pos > 0:
                content = content[:brace_pos + 1]
            
            # Parse JSON
            result = json.loads(content)
            
            # Validate and normalize
            return self._normalize_result(result)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM JSON response: {e}")
            if content:
                print(f"Full response was:")
                print("=" * 60)
                print(content)
                print("=" * 60)
                print(f"Response length: {len(content)} characters")
                # Try to fix common JSON issues
                try:
                    # Remove trailing commas before closing braces/brackets
                    fixed_content = re.sub(r',(\s*[}\]])', r'\1', content)
                    result = json.loads(fixed_content)
                    print("Fixed JSON parsing issue (trailing comma)")
                    return self._normalize_result(result)
                except:
                    pass
            return self._default_result()
        except Exception as e:
            error_msg = str(e)
            # Check if it's an API key error
            if any(keyword in error_msg.lower() for keyword in ["api key", "401", "403", "invalid", "unauthorized", "authentication", "permission denied"]):
                print(f"\n❌ Invalid or expired API key detected!")
                print(f"Error: {error_msg[:200]}")
                print("\nPlease check your .env file and ensure your API key is correct.")
                print("The .env file will be reloaded on the next API call.")
                # Clear the cached key to force reload
                if self.use_gemini:
                    config.GEMINI_API_KEY = ""
                    os.environ.pop("GEMINI_API_KEY", None)
            else:
                print(f"Error calling LLM API: {e}")
                import traceback
                traceback.print_exc()
            return self._default_result()

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate the parsed result."""
        normalized = {
            "symbol": self._normalize_symbol(result.get("symbol")),
            "action_type": result.get("action_type"),
            "buy_price": self._safe_float(result.get("buy_price")),
            "conditions": result.get("conditions") or {},
            "user_opinion": result.get("user_opinion")
        }
        
        # Ensure conditions is a dict
        if not isinstance(normalized["conditions"], dict):
            normalized["conditions"] = {}
        
        # Normalize condition values
        conditions = normalized["conditions"]
        for key in ["price_above", "price_below", "percent_change", "percent_drop", 
                   "percent_above_buy", "time_period_days", "reminder_days", "trailing_stop"]:
            if key in conditions:
                conditions[key] = self._safe_float(conditions[key])
        
        return normalized

    def _normalize_symbol(self, symbol: Optional[str]) -> Optional[str]:
        """Normalize stock symbol to uppercase."""
        if not symbol:
            return None
        # Remove common prefixes/suffixes and normalize
        symbol = symbol.upper().strip()
        # Remove $ if present
        symbol = symbol.replace("$", "")
        return symbol if symbol else None

    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _default_result(self) -> Dict[str, Any]:
        """Return default result when parsing fails."""
        return {
            "symbol": None,
            "action_type": None,
            "buy_price": None,
            "conditions": {},
            "user_opinion": None
        }

