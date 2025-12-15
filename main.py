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
        
        # Validate parsed symbol before creating the note
        parsed_symbol = parsed.get("symbol")
        if not parsed_symbol:
            print("\n✗ Error: Could not extract a valid stock symbol from the note. Please include a valid ticker (e.g., AAPL, NVDA).")
            return

        # Validate that the symbol resolves to market data
        try:
            market_data = MarketData()
            price_info = market_data.get_price_info(parsed_symbol)
        except Exception as md_err:
            print(f"\n✗ Error validating symbol: {md_err}")
            return

        if not price_info:
            print(f"\n✗ Error: Symbol '{parsed_symbol}' not found or has no market data. Please check the ticker and try again.")
            return

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


def view_mode(include_inactive: bool = False, note_id: Optional[str] = None):
    """Handle 'view' command - view database contents."""
    try:
        storage = Storage()
        
        if note_id:
            # View specific note
            note = storage.get_note_by_id(note_id)
            if not note:
                print(f"Note with ID '{note_id}' not found.")
                return
            
            notes = [note]
        else:
            # View all notes
            notes = storage.get_all_notes(include_inactive=include_inactive)
        
        if not notes:
            print("No notes found in database.")
            return
        
        # Use rich if available for better formatting
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            from rich import box
            console = Console()
            use_rich = True
        except ImportError:
            use_rich = False
        
        if use_rich:
            # Display summary table
            table = Table(title="Stock Notes Database", box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", width=36)
            table.add_column("Symbol", style="yellow", width=10)
            table.add_column("Action", style="green", width=10)
            table.add_column("Buy Price", style="blue", width=12)
            table.add_column("Created", style="dim", width=19)
            table.add_column("Status", style="bold", width=8)
            
            for note in notes:
                status = "✓ Active" if note.active else "✗ Inactive"
                status_style = "green" if note.active else "red"
                buy_price_str = f"${note.buy_price:.2f}" if note.buy_price else "N/A"
                created_str = note.created_at.strftime("%Y-%m-%d %H:%M:%S")
                
                table.add_row(
                    note.id[:8] + "...",
                    note.symbol or "N/A",
                    note.action_type or "N/A",
                    buy_price_str,
                    created_str,
                    Text(status, style=status_style)
                )
            
            console.print(table)
            console.print()
            
            # Display detailed information for each note
            for i, note in enumerate(notes, 1):
                content = Text()
                content.append(f"Note {i} of {len(notes)}\n\n", style="bold")
                content.append("ID: ", style="bold")
                content.append(f"{note.id}\n", style="cyan")
                content.append("Raw Text: ", style="bold")
                content.append(f"{note.raw_text}\n\n", style="white")
                
                if note.symbol:
                    content.append("Symbol: ", style="bold")
                    content.append(f"{note.symbol}\n", style="yellow")
                if note.action_type:
                    content.append("Action Type: ", style="bold")
                    content.append(f"{note.action_type}\n", style="green")
                if note.buy_price:
                    content.append("Buy Price: ", style="bold")
                    content.append(f"${note.buy_price:.2f}\n", style="blue")
                
                if note.conditions:
                    content.append("\nConditions:\n", style="bold")
                    for key, value in note.conditions.items():
                        if value is not None:
                            content.append(f"  • {key}: {value}\n", style="white")
                
                if note.user_opinion:
                    content.append("\nUser Opinion: ", style="bold")
                    content.append(f"{note.user_opinion}\n", style="italic dim")
                
                content.append(f"\nCreated: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
                if note.last_checked:
                    content.append(f"Last Checked: {note.last_checked.strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
                content.append(f"Status: ", style="bold")
                status_text = "Active" if note.active else "Inactive"
                status_style = "green" if note.active else "red"
                content.append(status_text, style=status_style)
                
                panel = Panel(
                    content,
                    title=f"[bold]Note Details[/bold]",
                    border_style="blue",
                    box=box.ROUNDED,
                    padding=(1, 2)
                )
                console.print(panel)
                console.print()
        else:
            # Plain text output
            print(f"\n{'='*80}")
            print(f"STOCK NOTES DATABASE - {len(notes)} note(s) found")
            print(f"{'='*80}\n")
            
            for i, note in enumerate(notes, 1):
                print(f"{'─'*80}")
                print(f"Note {i} of {len(notes)}")
                print(f"{'─'*80}")
                print(f"ID: {note.id}")
                print(f"Status: {'✓ Active' if note.active else '✗ Inactive'}")
                print(f"Symbol: {note.symbol or 'N/A'}")
                print(f"Action Type: {note.action_type or 'N/A'}")
                print(f"Buy Price: ${note.buy_price:.2f}" if note.buy_price else "Buy Price: N/A")
                print(f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if note.last_checked:
                    print(f"Last Checked: {note.last_checked.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"\nRaw Text:")
                print(f"  {note.raw_text}")
                
                if note.conditions:
                    print(f"\nConditions:")
                    for key, value in note.conditions.items():
                        if value is not None:
                            print(f"  • {key}: {value}")
                
                if note.user_opinion:
                    print(f"\nUser Opinion: {note.user_opinion}")
                
                print()
            
            print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def activate_mode(note_id: Optional[str] = None, symbol: Optional[str] = None,
                   all_inactive: bool = False):
    """Handle 'activate' command - activate notes in database."""
    try:
        storage = Storage()
        
        if all_inactive:
            # Activate all inactive notes
            inactive_notes = storage.get_all_notes(include_inactive=True)
            inactive_notes = [n for n in inactive_notes if not n.active]
            
            if not inactive_notes:
                print("\nNo inactive notes found.")
                return
            
            for note in inactive_notes:
                storage.activate_note(note.id)
            
            print(f"\n✓ Successfully activated {len(inactive_notes)} note(s).")
            return
        
        if symbol:
            # Activate notes by symbol
            all_notes = storage.get_all_notes(include_inactive=True)
            matching_notes = [n for n in all_notes if n.symbol and n.symbol.upper() == symbol.upper() and not n.active]
            
            if not matching_notes:
                print(f"\nNo inactive notes found for symbol '{symbol}'.")
                return
            
            for note in matching_notes:
                storage.activate_note(note.id)
            
            print(f"\n✓ Successfully activated {len(matching_notes)} note(s) for symbol '{symbol}'.")
            return
        
        if note_id:
            # Activate specific note by ID
            note = storage.get_note_by_id(note_id)
            if not note:
                print(f"\nNote with ID '{note_id}' not found.")
                return
            
            if note.active:
                print(f"\nNote '{note_id}' is already active.")
                return
            
            storage.activate_note(note_id)
            print(f"\n✓ Successfully activated note '{note_id}'.")
            return
        
        # If no specific option provided, show help
        print("\nError: Please specify what to activate.")
        print("Options:")
        print("  --id <note-id>        Activate a specific note by ID")
        print("  --symbol <SYMBOL>     Activate all inactive notes for a symbol")
        print("  --all-inactive        Activate all inactive notes")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def delete_mode(note_id: Optional[str] = None, symbol: Optional[str] = None, 
                all_inactive: bool = False, all_notes: bool = False, 
                confirm: bool = False):
    """Handle 'delete' command - delete notes from database."""
    try:
        storage = Storage()
        
        if all_notes:
            # Delete all notes
            if not confirm:
                response = input("\n⚠️  WARNING: This will delete ALL notes. Are you sure? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Deletion cancelled.")
                    return
            
            count = storage.delete_all_notes()
            if count > 0:
                print(f"\n✓ Successfully deleted {count} note(s).")
            else:
                print("\nNo notes found to delete.")
            return
        
        if all_inactive:
            # Delete all inactive notes
            if not confirm:
                response = input("\n⚠️  This will delete all inactive notes. Continue? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Deletion cancelled.")
                    return
            
            count = storage.delete_all_inactive()
            if count > 0:
                print(f"\n✓ Successfully deleted {count} inactive note(s).")
            else:
                print("\nNo inactive notes found.")
            return
        
        if symbol:
            # Delete notes by symbol
            notes = storage.get_all_notes(include_inactive=True)
            matching_notes = [n for n in notes if n.symbol and n.symbol.upper() == symbol.upper()]
            
            if not matching_notes:
                print(f"\nNo notes found for symbol '{symbol}'.")
                return
            
            if not confirm:
                print(f"\nFound {len(matching_notes)} note(s) for symbol '{symbol}':")
                for note in matching_notes:
                    print(f"  - {note.id[:8]}... | {note.raw_text[:50]}...")
                response = input(f"\nDelete these {len(matching_notes)} note(s)? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Deletion cancelled.")
                    return
            
            count = storage.delete_notes_by_symbol(symbol)
            if count > 0:
                print(f"\n✓ Successfully deleted {count} note(s) for symbol '{symbol}'.")
            else:
                print(f"\nNo notes deleted for symbol '{symbol}'.")
            return
        
        if note_id:
            # Delete specific note by ID
            note = storage.get_note_by_id(note_id)
            if not note:
                print(f"\nNote with ID '{note_id}' not found.")
                return
            
            if not confirm:
                print(f"\nNote to delete:")
                print(f"  ID: {note.id}")
                print(f"  Symbol: {note.symbol or 'N/A'}")
                print(f"  Text: {note.raw_text[:100]}...")
                response = input("\nDelete this note? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Deletion cancelled.")
                    return
            
            if storage.delete_note(note_id):
                print(f"\n✓ Successfully deleted note '{note_id}'.")
            else:
                print(f"\n✗ Error deleting note '{note_id}'.")
            return
        
        # If no specific option provided, show help
        print("\nError: Please specify what to delete.")
        print("Options:")
        print("  --id <note-id>        Delete a specific note by ID")
        print("  --symbol <SYMBOL>     Delete all notes for a symbol")
        print("  --all-inactive        Delete all inactive notes")
        print("  --all                 Delete all notes (use with caution!)")
        print("  --confirm             Skip confirmation prompt")
        
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
        
        # Update last_checked timestamps and deactivate notes that triggered alerts
        for note in notes:
            storage.update_last_checked(note.id)
        
        # Deactivate notes that triggered alerts
        if alerts:
            for alert in alerts:
                storage.deactivate_note(alert['note_id'])
                print(f"Note {alert['note_id'][:8]}... has been deactivated after alert.")
        
        if alerts:
            print(f"\n✓ Checked {len(notes)} note(s), {len(alerts)} alert(s) triggered.")
            print(f"  {len(alerts)} note(s) have been deactivated.")
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
    
    # View command
    view_parser = subparsers.add_parser("view", help="View all notes in the database")
    view_parser.add_argument(
        "--all",
        action="store_true",
        help="Include inactive notes (default: only active notes)"
    )
    view_parser.add_argument(
        "--id",
        type=str,
        help="View a specific note by ID"
    )
    
    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Activate notes in the database")
    activate_group = activate_parser.add_mutually_exclusive_group(required=False)
    activate_group.add_argument(
        "--id",
        type=str,
        dest="activate_id",
        help="Activate a specific note by ID"
    )
    activate_group.add_argument(
        "--symbol",
        type=str,
        help="Activate all inactive notes for a specific symbol"
    )
    activate_group.add_argument(
        "--all-inactive",
        action="store_true",
        help="Activate all inactive notes"
    )
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete notes from the database")
    delete_group = delete_parser.add_mutually_exclusive_group(required=False)
    delete_group.add_argument(
        "--id",
        type=str,
        dest="delete_id",
        help="Delete a specific note by ID"
    )
    delete_group.add_argument(
        "--symbol",
        type=str,
        help="Delete all notes for a specific symbol"
    )
    delete_group.add_argument(
        "--all-inactive",
        action="store_true",
        help="Delete all inactive notes"
    )
    delete_group.add_argument(
        "--all",
        action="store_true",
        dest="delete_all",
        help="Delete ALL notes (use with caution!)"
    )
    delete_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
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
    elif args.command == "view":
        view_mode(include_inactive=args.all, note_id=args.id)
    elif args.command == "activate":
        activate_mode(
            note_id=getattr(args, 'activate_id', None),
            symbol=getattr(args, 'symbol', None),
            all_inactive=getattr(args, 'all_inactive', False)
        )
    elif args.command == "delete":
        # Handle delete command arguments
        delete_mode(
            note_id=getattr(args, 'delete_id', None),
            symbol=getattr(args, 'symbol', None),
            all_inactive=getattr(args, 'all_inactive', False),
            all_notes=getattr(args, 'delete_all', False),
            confirm=getattr(args, 'confirm', False)
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

