"""
Individual DAT Company Detail Pages
Displays comprehensive metrics and charts for each company
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
from config import DAT_COMPANIES, PERSONAL_POSITIONS, PHASES
from data import (
    fetch_eth_price,
    fetch_stock_data,
    fetch_stock_history,
    calculate_nav,
    calculate_nav_per_share,
    calculate_nav_discount,
    calculate_eth_per_share,
    determine_dat_phase,
    format_large_number,
    format_eth_amount,
    format_percentage,
)


def render_price_chart(ticker: str, period: str = "1y") -> None:
    """Render stock price chart"""
    hist = fetch_stock_history(ticker, period)

    if hist.empty:
        st.warning("No historical data available")
        return

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
        name=ticker,
    ))

    fig.update_layout(
        title=f"{ticker} Price History",
        yaxis_title="Price ($)",
        xaxis_title="Date",
        height=400,
        xaxis_rangeslider_visible=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_volume_chart(ticker: str, period: str = "1y") -> None:
    """Render volume chart"""
    hist = fetch_stock_history(ticker, period)

    if hist.empty:
        return

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist["Volume"],
        name="Volume",
        marker_color="rgba(100, 100, 255, 0.6)",
    ))

    fig.update_layout(
        title="Trading Volume",
        yaxis_title="Volume",
        height=200,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_nav_comparison_chart(
    stock_price: float,
    nav_per_share: float,
    ticker: str
) -> None:
    """Render NAV vs Stock Price comparison"""
    if not nav_per_share:
        return

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Stock Price", "NAV/Share"],
        y=[stock_price, nav_per_share],
        marker_color=["#636EFA", "#00CC96"],
    ))

    discount = calculate_nav_discount(stock_price, nav_per_share)
    discount_text = format_percentage(discount) if discount else "N/A"

    fig.update_layout(
        title=f"Stock Price vs NAV ({discount_text} {'premium' if discount and discount > 0 else 'discount'})",
        yaxis_title="Price ($)",
        height=300,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_dat_detail_page(ticker: str) -> None:
    """Render complete detail page for a DAT company"""
    if ticker not in DAT_COMPANIES:
        st.error(f"Company {ticker} not found")
        return

    company = DAT_COMPANIES[ticker]

    # Header
    st.title(f"{company['name']} ({ticker})")
    st.caption(f"Tier {company['tier']} | {company['strategy']}")

    if company["leader"]:
        st.caption(f"**Leadership:** {company['leader']}")

    # Fetch data
    eth_data = fetch_eth_price()
    eth_price = eth_data.get("price", 0) or 0

    stock = fetch_stock_data(ticker)
    stock_price = stock.get("price", 0) or 0
    shares_outstanding = stock.get("shares_outstanding", 0) or 0
    market_cap = stock.get("market_cap", 0) or 0

    eth_holdings = company["eth_holdings"]

    # Calculate metrics
    nav = calculate_nav(eth_holdings, eth_price)
    nav_per_share = calculate_nav_per_share(eth_holdings, eth_price, shares_outstanding)
    nav_discount = calculate_nav_discount(stock_price, nav_per_share) if nav_per_share else None
    eth_per_share = calculate_eth_per_share(eth_holdings, shares_outstanding)
    phase, phase_desc = determine_dat_phase(nav_discount, False, stock.get("pe_ratio"), None)

    # Key Metrics Row
    st.markdown("---")
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Stock Price", f"${stock_price:.2f}" if stock_price else "N/A")
        st.metric("Market Cap", format_large_number(market_cap))

    with col2:
        st.metric("ETH Holdings", format_eth_amount(eth_holdings))
        st.metric("Treasury Value", format_large_number(nav))

    with col3:
        st.metric("NAV/Share", f"${nav_per_share:.2f}" if nav_per_share else "N/A")
        st.metric(
            "NAV Discount/Premium",
            format_percentage(nav_discount) if nav_discount is not None else "N/A"
        )

    with col4:
        st.metric("ETH/Share", f"{eth_per_share:.6f}" if eth_per_share else "N/A")
        st.metric("Shares Outstanding", f"{shares_outstanding:,.0f}" if shares_outstanding else "N/A")

    # Phase Status
    st.markdown("---")
    st.subheader("Phase Status")

    phase_info = PHASES.get(phase, {})

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"**Current Phase:** {phase_info.get('name', phase)}")
        st.caption(phase_info.get("description", ""))

    with col2:
        if phase == "accumulation":
            st.progress(0.33, text="Accumulation → Transition → Terminal")
        elif phase == "transition":
            st.progress(0.66, text="Accumulation → Transition → Terminal")
        else:
            st.progress(1.0, text="Accumulation → Transition → Terminal")

    # Charts
    st.markdown("---")
    st.subheader("Charts")

    # Period selector
    period = st.selectbox(
        "Time Period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
    )

    render_price_chart(ticker, period)
    render_volume_chart(ticker, period)

    if nav_per_share:
        render_nav_comparison_chart(stock_price, nav_per_share, ticker)

    # Personal Position (if applicable)
    if ticker in PERSONAL_POSITIONS:
        st.markdown("---")
        st.subheader("Your Position")

        position = PERSONAL_POSITIONS[ticker]
        shares = position.get("shares", 0)
        cost_basis = position.get("cost_basis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Shares Owned", f"{shares:,}")

        with col2:
            position_value = shares * stock_price if stock_price else 0
            st.metric("Position Value", format_large_number(position_value))

        with col3:
            if cost_basis:
                pnl = (stock_price - cost_basis) * shares
                pnl_pct = (stock_price - cost_basis) / cost_basis
                st.metric(
                    "P&L",
                    format_large_number(pnl),
                    delta=format_percentage(pnl_pct),
                )

    # Accumulation Metrics
    st.markdown("---")
    st.subheader("Accumulation Metrics (Phase 6a)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**What to Track:**")
        st.caption("• ETH holdings growth quarter over quarter")
        st.caption("• ETH per share trend (should be growing)")
        st.caption("• NAV discount trend (should be narrowing)")
        st.caption("• Dilution rate (should be declining)")

    with col2:
        st.markdown("**Data Sources:**")
        st.caption("• Company IR announcements (weekly updates)")
        st.caption("• SEC filings (10-Q, 10-K)")
        st.caption("• CoinGecko treasury tracker")
        st.caption("• ethereumtreasuries.net")

    # Company Notes
    if company.get("notes"):
        st.markdown("---")
        st.subheader("Notes")
        st.info(company["notes"])


def render_dat_selector() -> Optional[str]:
    """Render DAT company selector and return selected ticker"""
    tickers = list(DAT_COMPANIES.keys())
    names = [f"{t} - {DAT_COMPANIES[t]['name']}" for t in tickers]

    selected = st.selectbox(
        "Select Company",
        options=range(len(tickers)),
        format_func=lambda i: names[i],
    )

    return tickers[selected]
