"""Streamlit web UI for Stock Watch Agent."""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from llm_parser import LLMParser
from storage import Storage
from market_data import MarketData
from evaluator import Evaluator
from notifier import Notifier
from models import StockNote
import config

# Page configuration
st.set_page_config(
    page_title="Stock Watch Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'storage' not in st.session_state:
    st.session_state.storage = Storage()
if 'parser' not in st.session_state:
    try:
        st.session_state.parser = LLMParser()
    except Exception as e:
        st.session_state.parser = None
        st.session_state.parser_error = str(e)


def main():
    """Main Streamlit app."""
    st.title("📈 Stock Watch Agent")
    st.markdown("Monitor your stocks and get alerts when conditions are met")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page",
        ["🏠 Home", "➕ Add Note", "👁️ View Notes", "🔔 Check Alerts", "🗑️ Delete Notes"]
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home()
    elif page == "➕ Add Note":
        show_add_note()
    elif page == "👁️ View Notes":
        show_view_notes()
    elif page == "🔔 Check Alerts":
        show_check_alerts()
    elif page == "🗑️ Delete Notes":
        show_delete_notes()


def show_home():
    """Display home page with statistics."""
    st.header("Welcome to Stock Watch Agent")
    
    storage = st.session_state.storage
    
    # Get statistics
    all_notes = storage.get_all_notes(include_inactive=True)
    active_notes = [n for n in all_notes if n.active]
    inactive_notes = [n for n in all_notes if not n.active]
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Notes", len(all_notes))
    with col2:
        st.metric("Active Notes", len(active_notes))
    with col3:
        st.metric("Inactive Notes", len(inactive_notes))
    with col4:
        unique_symbols = len(set([n.symbol for n in active_notes if n.symbol]))
        st.metric("Watched Symbols", unique_symbols)
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("Use the sidebar to navigate to 'Add Note'")
    
    with col2:
        st.info("Use the sidebar to navigate to 'View Notes'")
    
    with col3:
        st.info("Use the sidebar to navigate to 'Check Alerts'")
    
    # Recent notes
    if active_notes:
        st.markdown("---")
        st.subheader("Recent Active Notes")
        recent_notes = sorted(active_notes, key=lambda x: x.created_at, reverse=True)[:5]
        
        for note in recent_notes:
            with st.expander(f"{note.symbol or 'N/A'} - {note.raw_text[:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Symbol:** {note.symbol or 'N/A'}")
                    st.write(f"**Action:** {note.action_type or 'N/A'}")
                    if note.buy_price:
                        st.write(f"**Buy Price:** ${note.buy_price:.2f}")
                with col2:
                    st.write(f"**Created:** {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    if note.last_checked:
                        st.write(f"**Last Checked:** {note.last_checked.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if note.conditions:
                    st.write("**Conditions:**")
                    for key, value in note.conditions.items():
                        if value is not None:
                            st.write(f"  - {key}: {value}")


def show_add_note():
    """Display add note page."""
    st.header("➕ Add Stock Note")
    st.markdown("Enter your stock-related note in plain English. The AI will extract structured information.")
    
    # Check if parser is available
    if st.session_state.parser is None:
        error_msg = st.session_state.get('parser_error', 'Unknown error')
        st.error(f"⚠️ LLM Parser not available: {error_msg}")
        
        # Show API key setup instructions
        st.markdown("---")
        st.subheader("API Key Setup")
        
        provider = config.LLM_PROVIDER.lower()
        if provider == "gemini":
            st.markdown("""
            **To use Gemini API:**
            1. Get your free API key from: https://makersuite.google.com/app/apikey
            2. Set it using one of these methods:
               - **Environment variable:** `$env:GEMINI_API_KEY="your-key"`
               - **Create a .env file** in the project root with: `GEMINI_API_KEY=your-key`
               - **Enter it below** (temporary, for this session only)
            """)
            
            api_key_input = st.text_input("Enter Gemini API Key (optional, for this session only):", type="password")
            if st.button("Set API Key"):
                if api_key_input:
                    import os
                    os.environ["GEMINI_API_KEY"] = api_key_input
                    st.success("API key set! Please refresh the page or restart the app.")
                    st.rerun()
                else:
                    st.error("Please enter a valid API key.")
        
        elif provider == "openai":
            st.markdown("""
            **To use OpenAI API:**
            1. Get your API key from: https://platform.openai.com/api-keys
            2. Set it using one of these methods:
               - **Environment variable:** `$env:OPENAI_API_KEY="your-key"`
               - **Create a .env file** in the project root with: `OPENAI_API_KEY=your-key`
               - **Enter it below** (temporary, for this session only)
            """)
            
            api_key_input = st.text_input("Enter OpenAI API Key (optional, for this session only):", type="password")
            if st.button("Set API Key"):
                if api_key_input:
                    import os
                    os.environ["OPENAI_API_KEY"] = api_key_input
                    st.success("API key set! Please refresh the page or restart the app.")
                    st.rerun()
                else:
                    st.error("Please enter a valid API key.")
        
        return
    
    # Example notes
    with st.expander("📝 Example Notes"):
        examples = [
            "I bought NVIDIA at 170$. Keep a note of the price and inform me if it crosses 200$",
            "I bought NIKE at 70$ today. If it goes below 65$, remind me to sell.",
            "Remind me in 3 months to review Apple stock.",
            "I am holding Microsoft for long term. Alert me if it falls more than 15% from today.",
            "Keep an eye on Amazon and notify me if it crosses 2000."
        ]
        for i, example in enumerate(examples):
            if st.button(f"Use: {example[:50]}...", key=f"example_{i}"):
                st.session_state.example_text = example
                st.rerun()
    
    # Text input - use example text if selected
    default_text = st.session_state.get('example_text', '')
    if 'example_text' in st.session_state:
        del st.session_state.example_text
    
    text_input = st.text_area(
        "Enter your stock note:",
        value=default_text,
        height=150,
        placeholder="Example: I bought NVIDIA at 170$. Keep a note of the price and inform me if it crosses 200$"
    )
    
    if st.button("Process Note", type="primary"):
        if not text_input or not text_input.strip():
            st.error("Please enter a note before processing.")
            return
        
        with st.spinner("Processing your note with AI..."):
            try:
                # Parse with LLM
                parsed = st.session_state.parser.parse(text_input)

                # Validate the parsed symbol before saving. If no symbol was
                # extracted or the symbol cannot be resolved to market data,
                # show an error and don't add the note.
                parsed_symbol = parsed.get("symbol")
                if not parsed_symbol:
                    st.error("Could not extract a valid stock symbol from the note. Please include a valid ticker (e.g., AAPL, NVDA).")
                    return

                # Use MarketData to ensure the symbol exists
                try:
                    market_data = MarketData()
                    price_info = market_data.get_price_info(parsed_symbol)
                except Exception as md_err:
                    # If market data cannot be fetched (e.g., yfinance not installed), surface an error
                    st.error(f"Market data validation failed: {md_err}")
                    return

                if not price_info:
                    st.error(f"Symbol '{parsed_symbol}' not found or has no market data. Please check the ticker and try again.")
                    return
                
                # Show parsed data
                st.success("Note parsed successfully!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Parsed Information")
                    st.write(f"**Symbol:** {parsed.get('symbol') or 'N/A'}")
                    st.write(f"**Action Type:** {parsed.get('action_type') or 'N/A'}")
                    if parsed.get('buy_price'):
                        st.write(f"**Buy Price:** ${parsed.get('buy_price'):.2f}")
                    else:
                        st.write("**Buy Price:** N/A")
                    
                    if parsed.get('user_opinion'):
                        st.write(f"**User Opinion:** {parsed.get('user_opinion')}")
                
                with col2:
                    st.subheader("Conditions")
                    conditions = parsed.get('conditions', {})
                    if conditions:
                        for key, value in conditions.items():
                            if value is not None:
                                st.write(f"**{key}:** {value}")
                    else:
                        st.write("No conditions extracted")
                
                # Create note
                note = StockNote.create_new(
                    raw_text=text_input,
                    symbol=parsed.get("symbol"),
                    action_type=parsed.get("action_type"),
                    buy_price=parsed.get("buy_price"),
                    conditions=parsed.get("conditions"),
                    user_opinion=parsed.get("user_opinion")
                )
                
                # Save to database
                if st.session_state.storage.add_note(note):
                    st.success(f"✅ Note saved successfully! (ID: {note.id[:8]}...)")
                    st.balloons()
                    
                    # Clear input
                    if st.button("Add Another Note"):
                        st.rerun()
                else:
                    st.error("Failed to save note to database.")
                    
            except Exception as e:
                st.error(f"Error processing note: {e}")
                st.exception(e)


def show_view_notes():
    """Display view notes page with a list/table."""
    st.header("👁️ View Notes")
    
    storage = st.session_state.storage
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_inactive = st.checkbox("Show inactive notes", value=False)
    with col2:
        filter_symbol = st.text_input("Filter by symbol (leave empty for all)", "").upper()
    
    # Get notes
    all_notes = storage.get_all_notes(include_inactive=True)
    
    if not show_inactive:
        all_notes = [n for n in all_notes if n.active]
    
    if filter_symbol:
        all_notes = [n for n in all_notes if n.symbol and n.symbol.upper() == filter_symbol]
    
    if not all_notes:
        st.info("No notes found.")
        return
    
    st.write(f"**Found {len(all_notes)} note(s)**")
    
    # Display as table with action buttons
    st.subheader("Notes Table")
    
    # Prepare data for table
    table_data = []
    for note in all_notes:
        conditions_str = ", ".join([f"{k}: {v}" for k, v in (note.conditions or {}).items() if v is not None])
        table_data.append({
            "ID": note.id[:8] + "...",
            "Symbol": note.symbol or "N/A",
            "Action": note.action_type or "N/A",
            "Buy Price": f"${note.buy_price:.2f}" if note.buy_price else "N/A",
            "Status": "✓ Active" if note.active else "✗ Inactive",
            "Created": note.created_at.strftime("%Y-%m-%d %H:%M"),
            "Last Checked": note.last_checked.strftime("%Y-%m-%d %H:%M") if note.last_checked else "Never",
            "Conditions": conditions_str[:50] + "..." if len(conditions_str) > 50 else conditions_str or "None"
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Quick activate/deactivate section
    st.markdown("---")
    st.subheader("Quick Actions")
    
    # Separate active and inactive notes
    active_notes = [n for n in all_notes if n.active]
    inactive_notes = [n for n in all_notes if not n.active]
    
    if inactive_notes:
        st.write(f"**Inactive Notes ({len(inactive_notes)}):**")
        cols = st.columns(min(3, len(inactive_notes)))
        for idx, note in enumerate(inactive_notes[:3]):
            with cols[idx % 3]:
                if st.button(f"Activate: {note.symbol or 'N/A'}", key=f"quick_activate_{note.id}"):
                    storage.activate_note(note.id)
                    st.success(f"Note {note.symbol or note.id[:8]} activated!")
                    st.rerun()
        
        if len(inactive_notes) > 3:
            st.caption(f"... and {len(inactive_notes) - 3} more inactive notes. Use detailed view to activate them.")
    
    # Detailed view
    st.markdown("---")
    st.subheader("Detailed View")
    
    # Select note to view details
    note_options = [f"{n.symbol or 'N/A'} - {n.id[:8]}... ({'Active' if n.active else 'Inactive'})" for n in all_notes]
    selected = st.selectbox("Select a note to view details:", note_options)
    
    if selected:
        note_index = note_options.index(selected)
        note = all_notes[note_index]
        
        # Display full details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Basic Information**")
            st.write(f"**ID:** {note.id}")
            st.write(f"**Symbol:** {note.symbol or 'N/A'}")
            st.write(f"**Action Type:** {note.action_type or 'N/A'}")
            if note.buy_price:
                st.write(f"**Buy Price:** ${note.buy_price:.2f}")
            st.write(f"**Status:** {'✓ Active' if note.active else '✗ Inactive'}")
        
        with col2:
            st.write("**Timestamps**")
            st.write(f"**Created:** {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if note.last_checked:
                st.write(f"**Last Checked:** {note.last_checked.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.write("**Last Checked:** Never")
        
        st.write("**Raw Text:**")
        st.text_area("", note.raw_text, height=100, disabled=True, key=f"raw_{note.id}")
        
        if note.conditions:
            st.write("**Conditions:**")
            for key, value in note.conditions.items():
                if value is not None:
                    st.write(f"  - **{key}:** {value}")
        
        if note.user_opinion:
            st.write("**User Opinion:**")
            st.write(note.user_opinion)
        
        # Activate/Deactivate button
        st.markdown("---")
        if note.active:
            if st.button("Deactivate Note", key=f"deactivate_{note.id}"):
                storage.deactivate_note(note.id)
                st.success("Note deactivated!")
                st.rerun()
        else:
            if st.button("Activate Note", key=f"activate_{note.id}", type="primary"):
                storage.activate_note(note.id)
                st.success("Note activated!")
                st.rerun()


def show_check_alerts():
    """Display check alerts page."""
    st.header("🔔 Check Alerts")
    
    storage = st.session_state.storage
    
    if st.button("Check All Active Notes", type="primary"):
        with st.spinner("Checking stock conditions..."):
            try:
                # Load active notes
                notes = storage.get_active_notes()
                
                if not notes:
                    st.info("No active notes found.")
                    return
                
                st.write(f"Checking {len(notes)} active note(s)...")
                
                # Initialize components
                market_data = MarketData()
                evaluator = Evaluator(market_data)
                
                # Evaluate all notes
                alerts = evaluator.evaluate_all(notes)
                
                # Update last_checked timestamps and deactivate notes that triggered alerts
                for note in notes:
                    storage.update_last_checked(note.id)
                
                # Deactivate notes that triggered alerts
                deactivated_count = 0
                if alerts:
                    for alert in alerts:
                        storage.deactivate_note(alert['note_id'])
                        deactivated_count += 1
                
                # Display results
                if alerts:
                    st.success(f"🚨 Found {len(alerts)} alert(s)!")
                    st.info(f"ℹ️ {deactivated_count} note(s) have been automatically deactivated.")
                    
                    for i, alert in enumerate(alerts, 1):
                        with st.container():
                            st.markdown(f"### Alert {i}: {alert['symbol']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Current Price", f"${alert['current_price']:.2f}")
                                if alert.get('buy_price'):
                                    change = alert['current_price'] - alert['buy_price']
                                    percent = (change / alert['buy_price']) * 100
                                    st.metric("Change from Buy", f"${change:+.2f} ({percent:+.2f}%)")
                            
                            with col2:
                                st.write("**Conditions Met:**")
                                for reason in alert['reasons']:
                                    st.write(f"  • {reason}")
                            
                            st.write("**Original Note:**")
                            st.text(alert['raw_text'])
                            
                            if alert.get('user_opinion'):
                                st.write("**User Opinion:**")
                                st.write(alert['user_opinion'])
                            
                            st.markdown("---")
                    
                    st.balloons()
                else:
                    st.info(f"✓ Checked {len(notes)} note(s), no alerts at this time.")
                    
            except Exception as e:
                st.error(f"Error checking alerts: {e}")
                st.exception(e)


def show_delete_notes():
    """Display delete notes page."""
    st.header("🗑️ Delete Notes")
    st.warning("⚠️ This action cannot be undone. Please be careful.")
    
    storage = st.session_state.storage
    
    # Get all notes for selection
    all_notes = storage.get_all_notes(include_inactive=True)
    
    if not all_notes:
        st.info("No notes found in database.")
        return
    
    # Delete options
    delete_option = st.radio(
        "Delete option:",
        ["Delete by ID", "Delete by Symbol", "Delete All Inactive", "Delete All Notes"]
    )
    
    if delete_option == "Delete by ID":
        note_options = [f"{n.symbol or 'N/A'} - {n.id[:8]}... ({'Active' if n.active else 'Inactive'})" for n in all_notes]
        selected = st.selectbox("Select note to delete:", note_options)
        
        if st.button("Delete Selected Note", type="primary"):
            note_index = note_options.index(selected)
            note = all_notes[note_index]
            
            if storage.delete_note(note.id):
                st.success(f"✓ Successfully deleted note '{note.id[:8]}...'")
                st.rerun()
            else:
                st.error("Failed to delete note.")
    
    elif delete_option == "Delete by Symbol":
        symbols = sorted(set([n.symbol for n in all_notes if n.symbol]))
        selected_symbol = st.selectbox("Select symbol:", symbols)
        
        matching_notes = [n for n in all_notes if n.symbol == selected_symbol]
        st.write(f"**Found {len(matching_notes)} note(s) for {selected_symbol}**")
        
        if st.button(f"Delete All Notes for {selected_symbol}", type="primary"):
            count = storage.delete_notes_by_symbol(selected_symbol)
            if count > 0:
                st.success(f"✓ Successfully deleted {count} note(s) for {selected_symbol}")
                st.rerun()
            else:
                st.error("Failed to delete notes.")
    
    elif delete_option == "Delete All Inactive":
        inactive_notes = [n for n in all_notes if not n.active]
        st.write(f"**Found {len(inactive_notes)} inactive note(s)**")
        
        if st.button("Delete All Inactive Notes", type="primary"):
            count = storage.delete_all_inactive()
            if count > 0:
                st.success(f"✓ Successfully deleted {count} inactive note(s)")
                st.rerun()
            else:
                st.info("No inactive notes to delete.")
    
    elif delete_option == "Delete All Notes":
        st.error(f"⚠️ This will delete ALL {len(all_notes)} note(s)!")
        confirm = st.text_input("Type 'DELETE ALL' to confirm:")
        
        if st.button("Delete All Notes", type="primary"):
            if confirm == "DELETE ALL":
                count = storage.delete_all_notes()
                st.success(f"✓ Successfully deleted {count} note(s)")
                st.rerun()
            else:
                st.error("Confirmation text does not match. Deletion cancelled.")


if __name__ == "__main__":
    main()

