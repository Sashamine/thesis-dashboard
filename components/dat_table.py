"""
DAT Universe Table Component
Displays sortable table of all DAT companies with key metrics
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from config import DAT_COMPANIES
from data import (
    fetch_eth_price,
    fetch_stock_data,
    fetch_eth_staking_stats,
    calculate_nav,
    calculate_nav_per_share,
    calculate_nav_discount,
    calculate_eth_per_share,
    determine_dat_phase,
    format_large_number,
    format_eth_amount,
    format_percentage,
)


def build_dat_dataframe(eth_price: float, staking_apy: float = 0.035) -> pd.DataFrame:
    """Build DataFrame with all DAT company metrics"""
    rows = []

    for ticker, company in DAT_COMPANIES.items():
        # Fetch stock data
        stock = fetch_stock_data(ticker)

        eth_holdings = company["eth_holdings"]
        staking_pct = company.get("staking_pct", 0)
        staking_method = company.get("staking_method", "N/A")
        stock_price = stock.get("price", 0) or 0
        shares_outstanding = stock.get("shares_outstanding", 0) or 0
        market_cap = stock.get("market_cap", 0) or 0

        # Calculate metrics
        nav = calculate_nav(eth_holdings, eth_price)
        nav_per_share = calculate_nav_per_share(eth_holdings, eth_price, shares_outstanding)
        nav_discount = calculate_nav_discount(stock_price, nav_per_share) if nav_per_share else None
        eth_per_share = calculate_eth_per_share(eth_holdings, shares_outstanding)
        phase, phase_desc = determine_dat_phase(nav_discount, False, stock.get("pe_ratio"), None)

        # Calculate staking yield
        staked_eth = eth_holdings * staking_pct
        annual_yield_eth = staked_eth * staking_apy
        annual_yield_usd = annual_yield_eth * eth_price

        rows.append({
            "Ticker": ticker,
            "Company": company["name"],
            "Tier": company["tier"],
            "ETH Holdings": eth_holdings,
            "Staked %": staking_pct,
            "Staked ETH": staked_eth,
            "Staking Method": staking_method,
            "Annual Yield ETH": annual_yield_eth,
            "Annual Yield USD": annual_yield_usd,
            "Treasury Value": nav,
            "Stock Price": stock_price,
            "Market Cap": market_cap,
            "NAV/Share": nav_per_share,
            "NAV Discount": nav_discount,
            "ETH/Share": eth_per_share,
            "Phase": phase,
            "Leader": company["leader"],
        })

    return pd.DataFrame(rows)


def render_dat_table() -> None:
    """Render the DAT universe table"""
    st.subheader("ETH DAT Universe")

    # Fetch ETH price and staking stats
    eth_data = fetch_eth_price()
    eth_price = eth_data.get("price", 0) or 0
    staking_stats = fetch_eth_staking_stats()
    staking_apy = staking_stats.get("estimated_apy", 0.035)

    if not eth_price:
        st.error("Unable to fetch ETH price")
        return

    st.caption(f"ETH Price: ${eth_price:,.2f} | Network Staking APY: {staking_apy*100:.2f}%")

    # Build and display dataframe
    with st.spinner("Loading DAT data..."):
        df = build_dat_dataframe(eth_price, staking_apy)

    # Format columns for display
    display_df = df.copy()
    display_df["ETH Holdings"] = display_df["ETH Holdings"].apply(
        lambda x: f"{x:,.0f}" if x else "N/A"
    )
    display_df["Treasury Value"] = display_df["Treasury Value"].apply(
        lambda x: format_large_number(x) if x else "N/A"
    )
    display_df["Stock Price"] = display_df["Stock Price"].apply(
        lambda x: f"${x:.2f}" if x else "N/A"
    )
    display_df["Market Cap"] = display_df["Market Cap"].apply(
        lambda x: format_large_number(x) if x else "N/A"
    )
    display_df["NAV/Share"] = display_df["NAV/Share"].apply(
        lambda x: f"${x:.2f}" if x else "N/A"
    )
    display_df["NAV Discount"] = display_df["NAV Discount"].apply(
        lambda x: format_percentage(x) if x is not None else "N/A"
    )
    display_df["ETH/Share"] = display_df["ETH/Share"].apply(
        lambda x: f"{x:.4f}" if x else "N/A"
    )

    # Sorting options
    col1, col2 = st.columns([1, 3])
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            options=["ETH Holdings", "Tier", "Treasury Value", "NAV Discount", "Ticker"],
            index=0,
        )

    # Sort the original df for proper sorting
    if sort_by == "NAV Discount":
        # Sort by absolute discount
        df_sorted = df.copy()
        df_sorted["sort_val"] = df_sorted["NAV Discount"].fillna(0)
        df_sorted = df_sorted.sort_values("sort_val", ascending=True)
        display_df = display_df.loc[df_sorted.index]
    elif sort_by == "Tier":
        display_df = display_df.sort_values("Tier")
    elif sort_by == "ETH Holdings":
        display_df = display_df.sort_values(
            display_df.columns[display_df.columns.get_loc("ETH Holdings")],
            key=lambda x: df["ETH Holdings"],
            ascending=False,
        )
    else:
        display_df = display_df.sort_values(sort_by)

    # Display columns
    columns_to_show = [
        "Ticker", "Company", "Tier", "ETH Holdings", "Treasury Value",
        "Stock Price", "Market Cap", "NAV Discount", "ETH/Share", "Phase"
    ]

    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        hide_index=True,
    )

    # Summary stats
    st.markdown("---")
    st.subheader("Universe Summary")

    col1, col2, col3, col4 = st.columns(4)

    total_eth = df["ETH Holdings"].sum()
    total_treasury = df["Treasury Value"].sum()
    total_market_cap = df["Market Cap"].sum()

    with col1:
        st.metric("Total ETH Holdings", format_eth_amount(total_eth))

    with col2:
        st.metric("Total Treasury Value", format_large_number(total_treasury))

    with col3:
        st.metric("Total Market Cap", format_large_number(total_market_cap))

    with col4:
        # Average NAV discount
        valid_discounts = df["NAV Discount"].dropna()
        avg_discount = valid_discounts.mean() if len(valid_discounts) > 0 else None
        st.metric(
            "Avg NAV Discount",
            format_percentage(avg_discount) if avg_discount is not None else "N/A"
        )

    # Tier breakdown
    st.markdown("---")
    st.subheader("By Tier")

    tier1 = df[df["Tier"] == 1]
    tier2 = df[df["Tier"] == 2]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Tier 1 (>100k ETH)**")
        st.caption(f"{len(tier1)} companies | {format_eth_amount(tier1['ETH Holdings'].sum())}")
        for _, row in tier1.iterrows():
            st.caption(f"• {row['Ticker']}: {format_eth_amount(row['ETH Holdings'])}")

    with col2:
        st.markdown("**Tier 2 (10k-100k ETH)**")
        st.caption(f"{len(tier2)} companies | {format_eth_amount(tier2['ETH Holdings'].sum())}")
        for _, row in tier2.iterrows():
            st.caption(f"• {row['Ticker']}: {format_eth_amount(row['ETH Holdings'])}")

    # Company Productivity Section
    st.markdown("---")
    st.subheader("Company Yield vs Pure Staking")
    st.caption(f"Benchmark: {staking_apy*100:.2f}% APY if you staked ETH directly")

    # Calculate productivity metrics for each company
    productivity_data = []
    for _, row in df.iterrows():
        eth_holdings = row["ETH Holdings"]
        staked_pct = row["Staked %"]
        staked_eth = row["Staked ETH"]
        annual_yield_eth = row["Annual Yield ETH"]

        # What you'd earn if you just staked 100% of the ETH yourself
        benchmark_yield = eth_holdings * staking_apy

        # Effective yield rate for this company
        effective_yield_rate = (annual_yield_eth / eth_holdings) if eth_holdings > 0 else 0

        # Productivity vs benchmark (positive = better than staking yourself)
        yield_vs_benchmark = annual_yield_eth - benchmark_yield
        productivity_ratio = effective_yield_rate / staking_apy if staking_apy > 0 else 0

        productivity_data.append({
            "Ticker": row["Ticker"],
            "Company": row["Company"],
            "ETH Holdings": eth_holdings,
            "Staked %": staked_pct,
            "Staking Method": row["Staking Method"],
            "Annual Yield (ETH)": annual_yield_eth,
            "Effective APY": effective_yield_rate,
            "Benchmark Yield": benchmark_yield,
            "vs Benchmark": yield_vs_benchmark,
            "Productivity": productivity_ratio,
        })

    prod_df = pd.DataFrame(productivity_data)

    # Display as table
    display_prod = prod_df.copy()
    display_prod["ETH Holdings"] = display_prod["ETH Holdings"].apply(lambda x: f"{x:,.0f}")
    display_prod["Staked %"] = display_prod["Staked %"].apply(lambda x: f"{x*100:.0f}%")
    display_prod["Annual Yield (ETH)"] = display_prod["Annual Yield (ETH)"].apply(lambda x: f"{x:,.0f}")
    display_prod["Effective APY"] = display_prod["Effective APY"].apply(lambda x: f"{x*100:.2f}%")
    display_prod["Benchmark Yield"] = display_prod["Benchmark Yield"].apply(lambda x: f"{x:,.0f}")
    display_prod["vs Benchmark"] = display_prod["vs Benchmark"].apply(
        lambda x: f"+{x:,.0f}" if x >= 0 else f"{x:,.0f}"
    )
    display_prod["Productivity"] = display_prod["Productivity"].apply(
        lambda x: f"{x:.0%}" if x >= 1 else f"{x:.0%}"
    )

    st.dataframe(
        display_prod[["Ticker", "ETH Holdings", "Staked %", "Staking Method",
                      "Annual Yield (ETH)", "Effective APY", "vs Benchmark", "Productivity"]],
        use_container_width=True,
        hide_index=True,
    )

    st.caption("""
    **Effective APY** = Annual yield / ETH holdings (accounts for % actually staked)
    **vs Benchmark** = Yield difference vs staking 100% yourself
    **Productivity** = Effective APY / Network APY (100% = same as staking yourself, >100% = outperforming)
    """)


def render_add_dat_form() -> None:
    """Render form to add a new DAT company"""
    st.subheader("Add New DAT Company")

    with st.form("add_dat_form"):
        col1, col2 = st.columns(2)

        with col1:
            ticker = st.text_input("Ticker Symbol", placeholder="e.g., NEWDAT")
            name = st.text_input("Company Name", placeholder="e.g., New DAT Inc.")
            eth_holdings = st.number_input("ETH Holdings", min_value=0, step=1000)

        with col2:
            tier = st.selectbox("Tier", options=[1, 2], index=1)
            leader = st.text_input("Key Leader", placeholder="e.g., John Doe")
            strategy = st.text_area("Strategy", placeholder="Investment strategy...")

        submitted = st.form_submit_button("Add Company")

        if submitted:
            if ticker and name and eth_holdings > 0:
                st.success(f"Added {ticker} - {name} to tracking list")
                st.info("Note: In production, this would save to a database/config file")
            else:
                st.error("Please fill in all required fields")
