"""Evaluates stock conditions and determines if alerts should be triggered."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models import StockNote
from market_data import MarketData


class Evaluator:
    """Evaluates conditions for stock notes."""

    def __init__(self, market_data: MarketData):
        """Initialize evaluator with market data fetcher."""
        self.market_data = market_data

    def evaluate_note(self, note: StockNote) -> Optional[Dict[str, Any]]:
        """
        Evaluate a single stock note and return alert info if conditions are met.
        
        Returns:
            Dictionary with alert information if conditions are met, None otherwise
        """
        if not note.symbol:
            return None
        
        if not note.active:
            return None
        
        # Get current price
        price_info = self.market_data.get_price_info(note.symbol)
        print(f"Price info: {price_info}")
        if not price_info:
            print(f"No price info found for {note.symbol}")
            return None
        
        current_price = price_info["current_price"]
        conditions = note.conditions or {}
        
        # Check various conditions
        alert_reasons = []
        
        # Price above threshold
        if conditions.get("price_above") and current_price >= conditions["price_above"]:
            alert_reasons.append(f"Price crossed above ${conditions['price_above']:.2f}")
        
        # Price below threshold
        if conditions.get("price_below") and current_price <= conditions["price_below"]:
            alert_reasons.append(f"Price fell below ${conditions['price_below']:.2f}")
        
        # Price between range
        if conditions.get("price_between"):
            price_range = conditions["price_between"]
            if isinstance(price_range, dict):
                min_price = price_range.get("min")
                max_price = price_range.get("max")
                if min_price and max_price and min_price <= current_price <= max_price:
                    alert_reasons.append(f"Price is between ${min_price:.2f} and ${max_price:.2f}")
        
        # Percentage drop from buy price
        if conditions.get("percent_drop") and note.buy_price:
            drop_threshold = conditions["percent_drop"]
            percent_change = ((current_price - note.buy_price) / note.buy_price) * 100
            if percent_change <= -drop_threshold:
                alert_reasons.append(f"Price dropped {abs(percent_change):.2f}% from buy price ${note.buy_price:.2f}")
        
        # Percentage change from today (if we have previous close)
        if conditions.get("percent_change") and price_info.get("previous_close"):
            change_threshold = conditions["percent_change"]
            percent_change = ((current_price - price_info["previous_close"]) / price_info["previous_close"]) * 100
            if abs(percent_change) >= abs(change_threshold):
                direction = "up" if percent_change > 0 else "down"
                alert_reasons.append(f"Price changed {abs(percent_change):.2f}% {direction} from previous close")
        
        # Time-based reminders
        if conditions.get("reminder_days"):
            days_elapsed = (datetime.now() - note.created_at).days
            if days_elapsed >= conditions["reminder_days"]:
                alert_reasons.append(f"Reminder: {conditions['reminder_days']} days have passed")
        
        # Time period check (e.g., "after a month")
        if conditions.get("time_period_days"):
            days_elapsed = (datetime.now() - note.created_at).days
            if days_elapsed >= conditions["time_period_days"]:
                # Check if price is up (for conditions like "if stock is up after a month")
                if note.buy_price:
                    percent_change = ((current_price - note.buy_price) / note.buy_price) * 100
                    if percent_change > 0:
                        alert_reasons.append(f"Time period reached ({conditions['time_period_days']} days) and price is up {percent_change:.2f}%")
                else:
                    alert_reasons.append(f"Time period reached ({conditions['time_period_days']} days)")
        
        # Trailing stop loss
        if conditions.get("trailing_stop") and note.buy_price:
            stop_price = conditions["trailing_stop"]
            if current_price <= stop_price:
                alert_reasons.append(f"Price hit trailing stop at ${stop_price:.2f}")
        
        if alert_reasons:
            return {
                "note_id": note.id,
                "symbol": note.symbol,
                "current_price": current_price,
                "buy_price": note.buy_price,
                "reasons": alert_reasons,
                "raw_text": note.raw_text,
                "user_opinion": note.user_opinion
            }
        
        return None

    def evaluate_all(self, notes: List[StockNote]) -> List[Dict[str, Any]]:
        """
        Evaluate all notes and return list of alerts.
        
        Args:
            notes: List of StockNote objects to evaluate
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        for note in notes:
            alert = self.evaluate_note(note)
            if alert:
                alerts.append(alert)
        return alerts

