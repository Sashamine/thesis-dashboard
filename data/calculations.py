"""
Calculation functions for DAT metrics
NAV, ETH per share, drawdowns, phase detection, health status
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


def calculate_nav(eth_holdings: float, eth_price: float) -> float:
    """Calculate Net Asset Value of ETH treasury"""
    return eth_holdings * eth_price


def calculate_nav_per_share(
    eth_holdings: float, eth_price: float, shares_outstanding: float
) -> Optional[float]:
    """Calculate NAV per share"""
    if not shares_outstanding or shares_outstanding <= 0:
        return None
    nav = calculate_nav(eth_holdings, eth_price)
    return nav / shares_outstanding


def calculate_nav_discount(
    stock_price: float, nav_per_share: float
) -> Optional[float]:
    """
    Calculate NAV discount/premium
    Negative = discount (stock trading below NAV)
    Positive = premium (stock trading above NAV)
    """
    if not nav_per_share or nav_per_share <= 0:
        return None
    return (stock_price - nav_per_share) / nav_per_share


def calculate_eth_per_share(
    eth_holdings: float, shares_outstanding: float
) -> Optional[float]:
    """Calculate ETH holdings per share"""
    if not shares_outstanding or shares_outstanding <= 0:
        return None
    return eth_holdings / shares_outstanding


def calculate_drawdown(current_price: float, high_price: float) -> float:
    """Calculate drawdown from high"""
    if high_price <= 0:
        return 0
    return (current_price - high_price) / high_price


def calculate_dilution_rate(
    current_shares: float, previous_shares: float, period_years: float = 1.0
) -> Optional[float]:
    """Calculate annualized dilution rate"""
    if not previous_shares or previous_shares <= 0:
        return None
    growth = (current_shares - previous_shares) / previous_shares
    return growth / period_years


def calculate_treasury_value_change(
    current_eth: float,
    previous_eth: float,
    current_price: float,
    previous_price: float,
) -> Dict[str, float]:
    """Calculate treasury value change decomposition"""
    current_value = current_eth * current_price
    previous_value = previous_eth * previous_price

    total_change = current_value - previous_value
    pct_change = total_change / previous_value if previous_value > 0 else 0

    # Decompose into price effect and accumulation effect
    price_effect = previous_eth * (current_price - previous_price)
    accumulation_effect = (current_eth - previous_eth) * current_price

    return {
        "total_change": total_change,
        "pct_change": pct_change,
        "price_effect": price_effect,
        "accumulation_effect": accumulation_effect,
    }


def determine_dat_phase(
    nav_discount: Optional[float],
    has_dividend: bool,
    pe_ratio: Optional[float],
    ops_cost_ratio: Optional[float],  # Operational costs / treasury income
) -> Tuple[str, str]:
    """
    Determine which phase a DAT company is in
    Returns (phase_code, phase_description)
    """
    # Phase 6c: Terminal - Has established P/E, paying dividends
    if has_dividend and pe_ratio and pe_ratio > 20:
        return ("terminal", "Phase 6c: Terminal - Earnings-driven valuation")

    # Phase 6b: Transition - Starting to show earnings characteristics
    if has_dividend or (nav_discount and abs(nav_discount) < 0.10):
        return ("transition", "Phase 6b: Transition - Moving toward earnings focus")

    # Phase 6a: Accumulation - NAV-driven
    return ("accumulation", "Phase 6a: Accumulation - NAV discount/premium driven")


def calculate_position_value(
    shares: int, stock_price: float
) -> float:
    """Calculate position value"""
    return shares * stock_price


def calculate_portfolio_metrics(
    positions: Dict[str, Dict[str, Any]],
    stock_data: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculate aggregate portfolio metrics"""
    total_value = 0
    total_cost = 0
    position_values = {}

    for ticker, position in positions.items():
        shares = position.get("shares", 0)
        cost_basis = position.get("cost_basis")

        stock = stock_data.get(ticker, {})
        price = stock.get("price", 0) or 0

        value = shares * price
        position_values[ticker] = {
            "shares": shares,
            "price": price,
            "value": value,
            "drawdown": stock.get("drawdown_from_ath"),
        }
        total_value += value

        if cost_basis:
            total_cost += shares * cost_basis

    return {
        "total_value": total_value,
        "total_cost": total_cost if total_cost > 0 else None,
        "total_pnl": total_value - total_cost if total_cost > 0 else None,
        "positions": position_values,
    }


def get_health_status(
    value: float,
    warning_threshold: float,
    critical_threshold: float,
    higher_is_better: bool = True,
) -> str:
    """
    Determine health status based on thresholds
    Returns: 'healthy', 'warning', or 'critical'
    """
    if higher_is_better:
        if value >= warning_threshold:
            return "healthy"
        elif value >= critical_threshold:
            return "warning"
        else:
            return "critical"
    else:
        if value <= warning_threshold:
            return "healthy"
        elif value <= critical_threshold:
            return "warning"
        else:
            return "critical"


def check_precondition_health(
    eth_dominance: Optional[float],
    eth_staking_apy: Optional[float],
    deficit_gdp_ratio: Optional[float],
) -> Dict[str, Dict[str, Any]]:
    """
    Check health of all thesis preconditions
    Returns status for each precondition
    """
    results = {}

    # ETH Dominance (Thesis 4 precondition)
    if eth_dominance is not None:
        if eth_dominance >= 0.50:
            status = "healthy"
        elif eth_dominance >= 0.40:
            status = "warning"
        else:
            status = "critical"
        results["eth_dominance"] = {
            "value": eth_dominance,
            "status": status,
            "label": f"{eth_dominance:.1%} ETH ecosystem TVL share",
            "threshold": "Invalidation below 40% for 2+ years",
        }
    else:
        results["eth_dominance"] = {"status": "unknown", "label": "Data unavailable"}

    # ETH Staking Yield (Thesis 4 precondition)
    if eth_staking_apy is not None:
        if eth_staking_apy >= 0.03:
            status = "healthy"
        elif eth_staking_apy >= 0.02:
            status = "warning"
        else:
            status = "critical"
        results["eth_yield"] = {
            "value": eth_staking_apy,
            "status": status,
            "label": f"{eth_staking_apy:.2%} staking APY",
            "threshold": "Invalidation below 1% for 2+ years",
        }
    else:
        results["eth_yield"] = {"status": "unknown", "label": "Data unavailable"}

    # Macro Backdrop (Thesis 1 precondition)
    if deficit_gdp_ratio is not None:
        # For fiscal dominance thesis, sustained deficits confirm the thesis
        if deficit_gdp_ratio < -3:  # Deficit (negative is deficit)
            status = "healthy"  # Confirms fiscal dominance thesis
        elif deficit_gdp_ratio < 0:
            status = "warning"
        else:
            status = "critical"  # Surplus would refute thesis
        results["macro_backdrop"] = {
            "value": deficit_gdp_ratio,
            "status": status,
            "label": f"{deficit_gdp_ratio:.1f}% deficit/GDP",
            "threshold": "Thesis confirmed by continued deficits",
        }
    else:
        results["macro_backdrop"] = {"status": "unknown", "label": "Data unavailable"}

    return results


def count_transition_signals(
    has_dividend: bool,
    ops_costs_declining: bool,
    analyst_narrative_shift: bool,
    nav_discount_narrowing: bool,
    options_market_exists: bool,
) -> Tuple[int, int]:
    """
    Count how many Phase 6b transition signals are present
    Returns (signals_present, total_signals)
    """
    signals = [
        has_dividend,
        ops_costs_declining,
        analyst_narrative_shift,
        nav_discount_narrowing,
        options_market_exists,
    ]
    return sum(signals), len(signals)


def format_large_number(value: float, decimals: int = 2) -> str:
    """Format large numbers with K, M, B suffixes"""
    if value is None:
        return "N/A"

    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value >= 1_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000:.{decimals}f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}${abs_value / 1_000_000:.{decimals}f}M"
    elif abs_value >= 1_000:
        return f"{sign}${abs_value / 1_000:.{decimals}f}K"
    else:
        return f"{sign}${abs_value:.{decimals}f}"


def format_eth_amount(value: float) -> str:
    """Format ETH amounts"""
    if value is None:
        return "N/A"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M ETH"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K ETH"
    else:
        return f"{value:.4f} ETH"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage values"""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"
