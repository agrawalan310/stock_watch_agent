"""Market data fetching using yfinance."""
from typing import Optional, Dict
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    yf = None


class MarketData:
    """Fetches real-time stock market data."""

    def __init__(self):
        """Initialize market data fetcher."""
        if yf is None:
            raise ImportError("yfinance package not installed. Install it with: pip install yfinance")

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price for a symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "NVDA")
            
        Returns:
            Current price as float, or None if symbol not found or error occurs
        """
        if not symbol:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Try to get current price from various fields
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            
            if current_price:
                return float(current_price)
            
            # Fallback: get latest close price from history
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                return float(hist["Close"].iloc[-1])
            
            return None
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def get_price_info(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive price information for a symbol.
        
        Returns:
            Dictionary with price, previous_close, and other info, or None
        """
        if not symbol:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose")
            
            if current_price is None:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    current_price = float(hist["Close"].iloc[-1])
                    previous_close = float(hist["Close"].iloc[0]) if len(hist) > 1 else current_price
            
            if current_price is None:
                return None
            
            return {
                "current_price": float(current_price),
                "previous_close": float(previous_close) if previous_close else None,
                "symbol": symbol,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            print(f"Error fetching price info for {symbol}: {e}")
            return None

