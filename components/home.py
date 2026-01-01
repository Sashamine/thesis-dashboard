"""
Home/Summary Page Component
Displays precondition health, phase progression, position health, and invalidation watch
"""
import streamlit as st
from typing import Dict, Any
from config import (
    DAT_COMPANIES,
    PERSONAL_POSITIONS,
    HEALTH_STATUS,
    INVALIDATION_THRESHOLDS,
    FRED_API_KEY,
)
from data import (
    fetch_eth_price,
    fetch_defi_tvl,
    fetch_eth_staking_stats,
    fetch_stock_data,
    fetch_deficit_gdp_ratio,
    check_precondition_health,
    calculate_nav,
    calculate_nav_per_share,
    calculate_nav_discount,
    calculate_portfolio_metrics,
    format_large_number,
    format_percentage,
)


def render_health_indicator(status: str, label: str) -> None:
    """Render a health status indicator"""
    config = HEALTH_STATUS.get(status, HEALTH_STATUS["unknown"])
    st.markdown(f"{config['emoji']} **{label}**")


def render_precondition_health() -> None:
    """Render precondition health section"""
    st.subheader("Precondition Health")

    # Fetch data
    defi_data = fetch_defi_tvl()
    staking_data = fetch_eth_staking_stats()

    eth_dominance = defi_data.get("eth_dominance") if "error" not in defi_data else None
    eth_apy = staking_data.get("estimated_apy") if "error" not in staking_data else None

    # Fetch macro data from FRED
    deficit_gdp = None
    if FRED_API_KEY:
        deficit_data = fetch_deficit_gdp_ratio(FRED_API_KEY)
        deficit_gdp = deficit_data.get("value") if "error" not in deficit_data else None

    # Check health
    health = check_precondition_health(
        eth_dominance=eth_dominance,
        eth_staking_apy=eth_apy,
        deficit_gdp_ratio=deficit_gdp,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        status = health["eth_dominance"]["status"]
        label = health["eth_dominance"]["label"]
        config = HEALTH_STATUS.get(status, HEALTH_STATUS["unknown"])
        st.metric(
            label="ETH Dominance",
            value=config["emoji"],
            delta=label,
        )
        if status == "critical":
            st.caption("⚠️ " + health["eth_dominance"].get("threshold", ""))

    with col2:
        status = health["eth_yield"]["status"]
        label = health["eth_yield"]["label"]
        config = HEALTH_STATUS.get(status, HEALTH_STATUS["unknown"])
        st.metric(
            label="ETH Yield",
            value=config["emoji"],
            delta=label,
        )

    with col3:
        status = health["macro_backdrop"]["status"]
        label = health["macro_backdrop"]["label"]
        config = HEALTH_STATUS.get(status, HEALTH_STATUS["unknown"])
        st.metric(
            label="Macro Backdrop",
            value=config["emoji"],
            delta=label,
        )
        if status == "unknown":
            st.caption("Add FRED API key for macro data")


def render_phase_progression() -> None:
    """Render phase progression section"""
    st.subheader("Phase Progression")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Current Phase:** Accumulation (6a)")
        st.progress(0.33, text="Accumulation → Transition → Terminal")

    with col2:
        # Count transition signals (simplified - these would come from real data)
        signals_present = 0
        total_signals = 5
        st.markdown(f"**Transition Signals:** {signals_present}/{total_signals} triggered")

        signals = [
            ("Dividend announced", False),
            ("Ops costs declining", False),
            ("Analyst narrative shift", False),
            ("NAV discount < 10%", False),
            ("Options market exists", False),
        ]

        for signal, triggered in signals:
            icon = "✅" if triggered else "⬜"
            st.caption(f"{icon} {signal}")


def render_position_health() -> None:
    """Render position health section"""
    st.subheader("Position Health")

    # Fetch ETH price
    eth_data = fetch_eth_price()
    eth_price = eth_data.get("price", 0) or 0

    # Fetch stock data for positions
    stock_data = {}
    for ticker in PERSONAL_POSITIONS.keys():
        if ticker != "ETH":
            stock_data[ticker] = fetch_stock_data(ticker)

    # Calculate portfolio metrics
    portfolio = calculate_portfolio_metrics(PERSONAL_POSITIONS, stock_data)

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Portfolio NAV",
            value=format_large_number(portfolio["total_value"]),
        )

    with col2:
        bmnr = portfolio["positions"].get("BMNR", {})
        bmnr_value = bmnr.get("value", 0)
        bmnr_drawdown = bmnr.get("drawdown")
        st.metric(
            label="BMNR Position",
            value=format_large_number(bmnr_value),
            delta=format_percentage(bmnr_drawdown) if bmnr_drawdown else None,
            delta_color="inverse" if bmnr_drawdown and bmnr_drawdown < 0 else "normal",
        )

    with col3:
        sbet = portfolio["positions"].get("SBET", {})
        sbet_value = sbet.get("value", 0)
        sbet_drawdown = sbet.get("drawdown")
        st.metric(
            label="SBET Position",
            value=format_large_number(sbet_value),
            delta=format_percentage(sbet_drawdown) if sbet_drawdown else None,
            delta_color="inverse" if sbet_drawdown and sbet_drawdown < 0 else "normal",
        )

    # ETH price
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        eth_change = eth_data.get("change_24h", 0)
        st.metric(
            label="ETH Price",
            value=f"${eth_price:,.2f}" if eth_price else "N/A",
            delta=f"{eth_change:.2f}%" if eth_change else None,
        )


def render_invalidation_watch() -> None:
    """Render invalidation watch section"""
    st.subheader("Invalidation Watch")

    # Count active invalidation signals
    active_signals = 0
    total_signals = len(INVALIDATION_THRESHOLDS)

    st.markdown(f"**{active_signals}/{total_signals} triggers active**")

    for key, config in INVALIDATION_THRESHOLDS.items():
        metric = config.get("metric", key)
        meaning = config.get("meaning", "")
        threshold = config.get("threshold", "")

        # Check if triggered (simplified - would need real data)
        triggered = False

        icon = "🔴" if triggered else "🟢"
        st.caption(f"{icon} {metric}: {meaning}")


def render_home_page() -> None:
    """Render the complete home page"""
    st.title("Thesis Tracking Dashboard")
    st.markdown("*Monitoring the path to ETH royalty companies*")

    # Quick stats row
    eth_data = fetch_eth_price()
    eth_price = eth_data.get("price", 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ETH Price", f"${eth_price:,.2f}" if eth_price else "N/A")
    with col2:
        # Total DAT ETH holdings
        total_eth = sum(c["eth_holdings"] for c in DAT_COMPANIES.values())
        total_value = total_eth * eth_price if eth_price else 0
        st.metric("DAT Universe Value", format_large_number(total_value))
    with col3:
        st.metric("Companies Tracked", len(DAT_COMPANIES))
    with col4:
        st.metric("Theses Tracked", "13")

    st.markdown("---")

    # Main content sections
    render_precondition_health()
    st.markdown("---")

    render_phase_progression()
    st.markdown("---")

    render_position_health()
    st.markdown("---")

    render_invalidation_watch()
