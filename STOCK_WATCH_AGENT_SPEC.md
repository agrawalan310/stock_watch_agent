# STOCK_WATCH_AGENT_SPEC.md

## Project Name
stock_watch_agent

## Objective
Build a Python-based application called stock_watch_agent that acts as a personal stock monitoring assistant.

The app accepts plain English stock-related notes, uses an LLM to extract structured intent, stores the data with timestamps, fetches real-time stock prices, evaluates conditions, and triggers console-based alerts when conditions are met.

This is not an auto-trading app. It is a thinking, monitoring, and reminding agent.

## Key Requirements
1. Accept free-form user text related to stock actions, opinions, and monitoring rules
2. Use an LLM to extract structured data from the text
3. Store raw input, structured output, and timestamps
4. Fetch real-time stock prices
5. Evaluate price-based and time-based conditions
6. Show notifications as bold/highlighted console alerts
7. Allow manual execution (later schedulable)

## Tech Stack
- Python 3.10+
- SQLite
- yfinance
- LLM API (OpenAI-compatible)
- rich or colorama for console alerts

## Project Structure
stock_watch_agent/
├── main.py
├── llm_parser.py
├── storage.py
├── market_data.py
├── evaluator.py
├── notifier.py
├── models.py
├── config.py
└── README.md

## Data Model
SQLite table: stock_notes

Fields:
- id (uuid)
- raw_text
- symbol
- action_type
- buy_price
- conditions (JSON)
- user_opinion
- created_at
- last_checked
- active

## LLM Responsibilities
- Extract intent only
- Output valid JSON
- Missing values must be null
- Normalize stock symbols

## Examples
- I bought NVIDIA at 170$. Keep a note of the price and inform me if it crosses 200$
- I bought NIKE at 70$ today.
I want to hold it for around 6 months.
If it goes below 65$, remind me to sell.
- I had put a trailing stop loss on Tesla at 300.
It went below and my shares got sold.
Now if Tesla trades between 300 and 310 in a month, notify me.
- I bought Archer Aviation at around 8$.
If the stock is up after a month, notify me so I can invest more.
- Remind me in 3 months to review Apple stock.
- I am holding Microsoft for long term.
Alert me if it falls more than 15% from today.
- Keep an eye on Amazon and notify me if it crosses 2000.


## Execution Flow
Add mode:
1. Accept user text
2. Parse via LLM
3. Validate JSON
4. Store in SQLite

Check mode:
1. Load active rules
2. Fetch prices
3. Evaluate conditions
4. Trigger alerts
5. Update timestamps

## CLI
python main.py add
python main.py check

## Non-Goals
- No trading
- No brokerage integration
- No background scheduler (v1)

## Future Enhancements
- Cron / scheduler
- Notifications via email / Telegram
- Portfolio analytics
- Multi-agent architecture
