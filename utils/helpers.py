"""
Utility functions and helpers
"""
from datetime import datetime, timedelta
from typing import Optional


def days_until(date_str: str) -> int:
    """Calculate days until a future date"""
    target = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now()
    delta = target - today
    return max(0, delta.days)


def format_date(date_str: str, format_str: str = "%B %d, %Y") -> str:
    """Format a date string"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime(format_str)
    except:
        return date_str


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: float
) -> Optional[float]:
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or years <= 0:
        return None
    return (end_value / start_value) ** (1 / years) - 1


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Safely divide two numbers"""
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def format_currency(value: float, decimals: int = 2) -> str:
    """Format a number as currency"""
    if value is None:
        return "N/A"
    return f"${value:,.{decimals}f}"


def get_trend_indicator(current: float, previous: float) -> str:
    """Get trend indicator emoji"""
    if current > previous * 1.01:
        return "📈"
    elif current < previous * 0.99:
        return "📉"
    else:
        return "➡️"


def truncate_string(s: str, max_length: int = 50) -> str:
    """Truncate a string with ellipsis"""
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."
