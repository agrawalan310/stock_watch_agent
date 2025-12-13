# Stock Watch Agent

A Python-based personal stock monitoring assistant that accepts plain English notes about stocks, extracts structured information using LLM, stores monitoring rules, fetches real-time prices, and triggers console alerts when conditions are met.

## Features

- 📝 Accept free-form text notes about stock actions and monitoring rules
- 🤖 Use LLM to extract structured data (symbol, action type, prices, conditions)
- 💾 Store notes in SQLite database with timestamps
- 📊 Fetch real-time stock prices using yfinance
- 🔔 Evaluate price-based and time-based conditions
- 🚨 Display bold/highlighted console alerts when conditions are met
- ⚡ Simple CLI interface for adding notes and checking conditions

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key (default, recommended):
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key-here"

# Windows CMD
set GEMINI_API_KEY=your-gemini-api-key-here

# Linux/Mac
export GEMINI_API_KEY="your-gemini-api-key-here"
```

Get your free Gemini API key from: https://makersuite.google.com/app/apikey

**Optional: Use OpenAI instead of Gemini:**
```bash
# Set provider to OpenAI
$env:LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="your-openai-api-key-here"
$env:OPENAI_API_BASE="https://api.openai.com/v1"
$env:OPENAI_MODEL="gpt-4o-mini"
```

## Usage

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

