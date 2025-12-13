"""Console notification system for stock alerts."""
from typing import List, Dict, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

import config


class Notifier:
    """Handles console-based notifications."""

    def __init__(self):
        """Initialize notifier."""
        if config.USE_RICH and RICH_AVAILABLE:
            self.console = Console()
            self.use_rich = True
        else:
            self.use_rich = False

    def show_alert(self, alert: Dict[str, Any]):
        """
        Display a single alert in the console.
        
        Args:
            alert: Dictionary with alert information from evaluator
        """
        if self.use_rich:
            self._show_rich_alert(alert)
        else:
            self._show_plain_alert(alert)

    def _show_rich_alert(self, alert: Dict[str, Any]):
        """Display alert using rich library."""
        symbol = alert.get("symbol", "UNKNOWN")
        current_price = alert.get("current_price", 0)
        buy_price = alert.get("buy_price")
        
        # Build alert text
        title = Text(f"🚨 STOCK ALERT: {symbol}", style="bold red")
        price_text = Text(f"Current Price: ${current_price:.2f}", style="bold yellow")
        
        if buy_price:
            change = current_price - buy_price
            percent = (change / buy_price) * 100
            change_text = Text(
                f"Buy Price: ${buy_price:.2f} | Change: ${change:+.2f} ({percent:+.2f}%)",
                style="cyan"
            )
        else:
            change_text = Text("", style="cyan")
        
        reasons = alert.get("reasons", [])
        reasons_text = "\n".join([f"• {reason}" for reason in reasons])
        
        content = Text()
        content.append(title)
        content.append("\n\n")
        content.append(price_text)
        if buy_price:
            content.append("\n")
            content.append(change_text)
        content.append("\n\n")
        content.append("Conditions Met:\n", style="bold")
        content.append(reasons_text, style="white")
        
        if alert.get("user_opinion"):
            content.append("\n\n")
            content.append("Note: ", style="italic")
            content.append(alert["user_opinion"], style="italic dim")
        
        panel = Panel(
            content,
            title="[bold red]ALERT[/bold red]",
            border_style="red",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")

    def _show_plain_alert(self, alert: Dict[str, Any]):
        """Display alert using plain text."""
        symbol = alert.get("symbol", "UNKNOWN")
        current_price = alert.get("current_price", 0)
        buy_price = alert.get("buy_price")
        
        print("\n" + "=" * 60)
        print(f"🚨 STOCK ALERT: {symbol}")
        print("=" * 60)
        print(f"Current Price: ${current_price:.2f}")
        
        if buy_price:
            change = current_price - buy_price
            percent = (change / buy_price) * 100
            print(f"Buy Price: ${buy_price:.2f} | Change: ${change:+.2f} ({percent:+.2f}%)")
        
        print("\nConditions Met:")
        for reason in alert.get("reasons", []):
            print(f"  • {reason}")
        
        if alert.get("user_opinion"):
            print(f"\nNote: {alert['user_opinion']}")
        
        print("=" * 60 + "\n")

    def show_alerts(self, alerts: List[Dict[str, Any]]):
        """
        Display multiple alerts.
        
        Args:
            alerts: List of alert dictionaries
        """
        if not alerts:
            if self.use_rich:
                self.console.print("[green]✓[/green] No alerts at this time.")
            else:
                print("✓ No alerts at this time.")
            return
        
        if self.use_rich:
            self.console.print(f"\n[bold yellow]Found {len(alerts)} alert(s):[/bold yellow]\n")
        
        for alert in alerts:
            self.show_alert(alert)

