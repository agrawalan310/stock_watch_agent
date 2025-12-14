# Stock Watch Agent

A Python-based personal stock monitoring assistant that accepts plain English notes about stocks, extracts structured information using LLM, stores monitoring rules, fetches real-time prices, and triggers console alerts when conditions are met.

## Features

- 🌐 **Web UI (Streamlit)**: Beautiful, interactive web interface for all operations
- 📝 Accept free-form text notes about stock actions and monitoring rules
- 🤖 Use LLM to extract structured data (symbol, action type, prices, conditions)
- 💾 Store notes in SQLite database with timestamps
- 📊 Fetch real-time stock prices using yfinance
- 🔔 Evaluate price-based and time-based conditions
- 🚨 Display alerts when conditions are met
- ⚡ CLI interface also available for command-line usage

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key (required):

**Option 1: Using .env file (Recommended)**
```bash
# Create a .env file in the project root
# Copy the example (if provided) or create one with:
GEMINI_API_KEY=your-gemini-api-key-here
```

**Option 2: Environment variable**
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key-here"

# Windows CMD
set GEMINI_API_KEY=your-gemini-api-key-here

# Linux/Mac
export GEMINI_API_KEY="your-gemini-api-key-here"
```

**Option 3: Interactive prompt**
- When you run the app, it will prompt you to enter the API key if not set
- In Streamlit UI, you can enter it directly in the interface

**Get your free Gemini API key from:** https://makersuite.google.com/app/apikey

**⚠️ Important:** Never commit your API key to the repository! The `.env` file is already in `.gitignore`.

**Optional: Use OpenAI instead of Gemini:**
```bash
# In .env file or environment variables:
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

4. Run the Streamlit web UI (recommended):
```bash
streamlit run app.py
```

Or use the CLI interface:
```bash
python main.py add
python main.py check
```

## Usage

### Web UI (Streamlit) - Recommended

Launch the web interface:
```bash
streamlit run app.py
```

The web UI provides:
- **Home**: Dashboard with statistics and recent notes
- **Add Note**: Easy-to-use form to add stock notes with AI parsing
- **View Notes**: Interactive table and detailed view of all notes
- **Check Alerts**: One-click button to check all conditions and see alerts
- **Delete Notes**: Safe deletion interface with confirmations

### CLI Interface

### Add a Stock Note

```bash
python main.py add
```

Then enter your note when prompted. For example:
- "I bought NVIDIA at 170$. Keep a note of the price and inform me if it crosses 200$"
- "I bought NIKE at 70$ today. If it goes below 65$, remind me to sell."
- "Remind me in 3 months to review Apple stock."

You can also provide text directly:
```bash
python main.py add --text "I bought Tesla at 250$. Alert me if it goes above 300$"
```

### Check for Alerts

```bash
python main.py check
```

This will:
1. Load all active notes from the database
2. Fetch current stock prices
3. Evaluate all conditions
4. Display alerts for any conditions that are met
5. Update last_checked timestamps
6. **Automatically deactivate notes that triggered alerts** (you can reactivate them later)

### View Database Contents

```bash
# View all active notes
python main.py view

# View all notes including inactive ones
python main.py view --all

# View a specific note by ID
python main.py view --id "note-uuid-here"
```

This displays all information stored in the database including:
- Note ID, symbol, action type, buy price
- Raw text input
- Parsed conditions
- User opinion
- Creation and last checked timestamps
- Active/inactive status

### Delete Notes

```bash
# Delete a specific note by ID
python main.py delete --id "note-uuid-here"

# Delete all notes for a specific symbol
python main.py delete --symbol "AAPL"

# Delete all inactive notes
python main.py delete --all-inactive

# Delete ALL notes (use with caution!)
python main.py delete --all

# Skip confirmation prompt (use with --confirm)
python main.py delete --id "note-uuid-here" --confirm
```

**Note:** By default, delete operations will prompt for confirmation. Use `--confirm` to skip the confirmation prompt.

### Activate Notes

```bash
# Activate a specific note by ID
python main.py activate --id "note-uuid-here"

# Activate all inactive notes for a specific symbol
python main.py activate --symbol "AAPL"

# Activate all inactive notes
python main.py activate --all-inactive
```

**Note:** When alerts are triggered during `check`, notes are automatically deactivated. Use the `activate` command to reactivate them.

## Examples

The agent understands various types of stock-related notes:

**Price thresholds:**
- "I bought NVIDIA at 170$. Inform me if it crosses 200$"
- "Keep an eye on Amazon and notify me if it crosses 2000"

**Price drops:**
- "I am holding Microsoft for long term. Alert me if it falls more than 15% from today."

**Price ranges:**
- "If Tesla trades between 300 and 310 in a month, notify me."

**Time-based reminders:**
- "Remind me in 3 months to review Apple stock."
- "I bought Archer Aviation at around 8$. If the stock is up after a month, notify me so I can invest more."

**Stop losses:**
- "I had put a trailing stop loss on Tesla at 300. It went below and my shares got sold. Now if Tesla trades between 300 and 310 in a month, notify me."

## Project Structure

```
stock_watch_agent/
├── main.py              # CLI entry point
├── llm_parser.py        # LLM-based text parsing
├── storage.py           # SQLite database operations
├── market_data.py       # Stock price fetching (yfinance)
├── evaluator.py         # Condition evaluation logic
├── notifier.py          # Console alert display
├── models.py            # Data models
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Database

The application uses SQLite to store notes in a `stock_watch.db` file (created automatically). The database schema includes:

- `id`: Unique identifier (UUID)
- `raw_text`: Original user input
- `symbol`: Stock ticker symbol
- `action_type`: Type of action (buy, hold, watch, sell, review)
- `buy_price`: Purchase price if mentioned
- `conditions`: JSON object with various conditions
- `user_opinion`: User's notes or opinion
- `created_at`: Timestamp when note was created
- `last_checked`: Timestamp of last condition check
- `active`: Whether the note is active (1 or 0)

## Configuration

Edit `config.py` to customize:
- Database path
- LLM API settings
- Console output preferences

## Limitations

- This is **not** an auto-trading application
- No background scheduler (v1) - you must manually run `check` command
- No brokerage integration
- Requires internet connection for price data and LLM API

## Future Enhancements

- Cron/scheduler for automatic checking
- Email/Telegram notifications
- Portfolio analytics
- Multi-agent architecture

## License

This project is provided as-is for personal use.

