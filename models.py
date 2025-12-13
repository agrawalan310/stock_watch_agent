"""Data models for stock_watch_agent."""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ActionType(str, Enum):
    """Types of stock actions."""
    BUY = "buy"
    HOLD = "hold"
    WATCH = "watch"
    SELL = "sell"
    REVIEW = "review"
    UNKNOWN = "unknown"


@dataclass
class StockNote:
    """Represents a stock monitoring note."""
    id: str
    raw_text: str
    symbol: Optional[str]
    action_type: Optional[str]
    buy_price: Optional[float]
    conditions: Optional[Dict[str, Any]]
    user_opinion: Optional[str]
    created_at: datetime
    last_checked: Optional[datetime]
    active: bool

    @classmethod
    def create_new(cls, raw_text: str, symbol: Optional[str] = None,
                   action_type: Optional[str] = None,
                   buy_price: Optional[float] = None,
                   conditions: Optional[Dict[str, Any]] = None,
                   user_opinion: Optional[str] = None) -> "StockNote":
        """Create a new StockNote with generated ID and timestamp."""
        return cls(
            id=str(uuid.uuid4()),
            raw_text=raw_text,
            symbol=symbol,
            action_type=action_type,
            buy_price=buy_price,
            conditions=conditions or {},
            user_opinion=user_opinion,
            created_at=datetime.now(),
            last_checked=None,
            active=True
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "raw_text": self.raw_text,
            "symbol": self.symbol,
            "action_type": self.action_type,
            "buy_price": self.buy_price,
            "conditions": json.dumps(self.conditions) if self.conditions else None,
            "user_opinion": self.user_opinion,
            "created_at": self.created_at.isoformat(),
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "active": 1 if self.active else 0
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockNote":
        """Create StockNote from database dictionary."""
        conditions = None
        if data.get("conditions"):
            try:
                conditions = json.loads(data["conditions"])
            except (json.JSONDecodeError, TypeError):
                conditions = {}

        return cls(
            id=data["id"],
            raw_text=data["raw_text"],
            symbol=data["symbol"],
            action_type=data["action_type"],
            buy_price=data["buy_price"],
            conditions=conditions,
            user_opinion=data["user_opinion"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_checked=datetime.fromisoformat(data["last_checked"]) if data.get("last_checked") else None,
            active=bool(data["active"])
        )

