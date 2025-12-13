"""Main CLI entry point for stock_watch_agent."""
import sys
import argparse
from typing import Optional

from llm_parser import LLMParser, list_available_models
from storage import Storage
from market_data import MarketData
from evaluator import Evaluator
from notifier import Notifier
from models import StockNote


def add_mode(text: Optional[str] = None):
    """Handle 'add' command - add a new stock note."""
    if not text:
        print("Enter your stock note (press Enter twice to finish, or Ctrl+Z then Enter on Windows):")
        lines = []
        try:
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            text = "\n".join(lines[:-1])  # Remove the last empty line
        except EOFError:
            text = "\n".join(lines)
    
    if not text or not text.strip():
        print("Error: No text provided.")
        return
    
    print("\nProcessing your note...")
    
    try:
        # Parse with LLM
        parser = LLMParser()
        parsed = parser.parse(text)
        
        print(f"Parsed data:")
        print(f"  Symbol: {parsed.get('symbol') or 'N/A'}")
        print(f"  Action: {parsed.get('action_type') or 'N/A'}")
        print(f"  Buy Price: ${parsed.get('buy_price') or 'N/A'}")
        print(f"  Conditions: {parsed.get('conditions')}")
        
        # Create note
        note = StockNote.create_new(
            raw_text=text,
            symbol=parsed.get("symbol"),
            action_type=parsed.get("action_type"),
            buy_price=parsed.get("buy_price"),
            conditions=parsed.get("conditions"),
            user_opinion=parsed.get("user_opinion")
        )
        
        # Store in database
        storage = Storage()
        if storage.add_note(note):
            print(f"\n✓ Note saved successfully! (ID: {note.id})")
        else:
            print("\n✗ Error saving note to database.")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def check_mode():
    """Handle 'check' command - check all active notes and show alerts."""
    print("Checking stock conditions...\n")
    
    try:
        # Load active notes
        storage = Storage()
        notes = storage.get_active_notes()
        
        if not notes:
            print("No active notes found.")
            return
        
        print(f"Found {len(notes)} active note(s).\n")
        
        # Initialize components
        market_data = MarketData()
        evaluator = Evaluator(market_data)
        notifier = Notifier()
        
        # Evaluate all notes
        alerts = evaluator.evaluate_all(notes)
        
        # Show alerts
        notifier.show_alerts(alerts)
        
        # Update last_checked timestamps
        for note in notes:
            storage.update_last_checked(note.id)
        
        if alerts:
            print(f"\n✓ Checked {len(notes)} note(s), {len(alerts)} alert(s) triggered.")
        else:
            print(f"\n✓ Checked {len(notes)} note(s), no alerts.")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Stock Watch Agent - Monitor stocks and get alerts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new stock note")
    add_parser.add_argument(
        "--text",
        type=str,
        help="Stock note text (if not provided, will prompt for input)"
    )
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check all active notes and show alerts")
    
    # List models command
    list_models_parser = subparsers.add_parser("list-models", help="List available LLM models")
    list_models_parser.add_argument(
        "--provider",
        type=str,
        choices=["gemini", "openai"],
        help="Provider to list models for (default: uses configured provider)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "add":
        add_mode(args.text)
    elif args.command == "check":
        check_mode()
    elif args.command == "list-models":
        list_available_models(args.provider)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

