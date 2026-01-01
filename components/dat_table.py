"""
DAT Universe Table Component
Displays sortable table of all DAT companies with key metrics
"""
import streamlit as st
import pandas as pd
from datetime import datetime
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
        quarterly_burn_usd = company.get("quarterly_burn_usd", 0)
        burn_source = company.get("burn_source", "")
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

        # Calculate burn rate
        annual_burn_usd = quarterly_burn_usd * 4
        annual_burn_eth = annual_burn_usd / eth_price if eth_price > 0 else 0

        # Net productivity = yield - burn
        net_annual_eth = annual_yield_eth - annual_burn_eth
        net_annual_usd = annual_yield_usd - annual_burn_usd

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
            "Quarterly Burn USD": quarterly_burn_usd,
            "Annual Burn USD": annual_burn_usd,
            "Annual Burn ETH": annual_burn_eth,
            "Burn Source": burn_source,
            "Net Annual ETH": net_annual_eth,
            "Net Annual USD": net_annual_usd,
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
    st.subheader("Company Productivity: Yield vs Burn")

    from config import ETF_STAKING_YIELD
    st.caption(f"Network staking: {staking_apy*100:.2f}% APY | ETF staking: {ETF_STAKING_YIELD*100:.1f}% APY (after fees)")

    # Build productivity table
    productivity_data = []
    today = datetime.now()

    for _, row in df.iterrows():
        ticker = row["Ticker"]
        company_config = DAT_COMPANIES.get(ticker, {})

        eth_holdings = row["ETH Holdings"]
        annual_yield_eth = row["Annual Yield ETH"]
        annual_burn_eth = row["Annual Burn ETH"]
        quarterly_burn = row["Quarterly Burn USD"]

        # ETH from premium issuance (from config)
        eth_from_premium = company_config.get("eth_from_premium", 0)

        # Calculate months active to annualize premium
        dat_start_str = company_config.get("dat_start_date", "2024-01-01")
        dat_start = datetime.strptime(dat_start_str, "%Y-%m-%d")
        months_active = max(1, (today - dat_start).days / 30.44)  # Avg days per month
        years_active = months_active / 12

        # Annualize premium capture
        annualized_premium_eth = eth_from_premium / years_active if years_active > 0 else 0

        # Total productivity = Yield - Burn + Annualized Premium
        total_annual_eth = annual_yield_eth - annual_burn_eth + annualized_premium_eth

        # Net productivity rate including premium (as % of holdings)
        net_rate = (total_annual_eth / eth_holdings) if eth_holdings > 0 else 0

        # Yield multiples
        yield_multiple_vs_staking = net_rate / staking_apy if staking_apy > 0 else 0
        yield_multiple_vs_etf = net_rate / ETF_STAKING_YIELD if ETF_STAKING_YIELD > 0 else 0

        # Is the company net accretive or dilutive (including premium)?
        is_accretive = total_annual_eth > 0

        productivity_data.append({
            "Ticker": ticker,
            "ETH Holdings": eth_holdings,
            "Staked %": row["Staked %"],
            "Yield (ETH/yr)": annual_yield_eth,
            "Burn (ETH/yr)": annual_burn_eth,
            "Quarterly Burn": quarterly_burn,
            "Premium (ETH/yr)": annualized_premium_eth,
            "Total (ETH/yr)": total_annual_eth,
            "Net Rate": net_rate,
            "Yield Multiple": yield_multiple_vs_staking,
            "vs ETF": yield_multiple_vs_etf,
            "Months Active": months_active,
            "ETH from Premium": eth_from_premium,
            "Accretive": is_accretive,
        })

    prod_df = pd.DataFrame(productivity_data)

    # Sort by total productivity (best first)
    prod_df = prod_df.sort_values("Total (ETH/yr)", ascending=False)

    # Display as table
    display_prod = prod_df.copy()
    display_prod["ETH Holdings"] = display_prod["ETH Holdings"].apply(lambda x: f"{x:,.0f}")
    display_prod["Staked %"] = display_prod["Staked %"].apply(lambda x: f"{x*100:.0f}%")
    display_prod["Yield (ETH/yr)"] = display_prod["Yield (ETH/yr)"].apply(lambda x: f"{x:,.0f}")
    display_prod["Burn (ETH/yr)"] = display_prod["Burn (ETH/yr)"].apply(lambda x: f"{x:,.0f}")
    display_prod["Premium (ETH/yr)"] = display_prod["Premium (ETH/yr)"].apply(
        lambda x: f"+{x:,.0f}" if x > 0 else "-"
    )
    display_prod["Total (ETH/yr)"] = display_prod["Total (ETH/yr)"].apply(
        lambda x: f"+{x:,.0f}" if x >= 0 else f"{x:,.0f}"
    )
    display_prod["Net Rate"] = display_prod["Net Rate"].apply(
        lambda x: f"+{x*100:.1f}%" if x >= 0 else f"{x*100:.1f}%"
    )
    display_prod["Yield Multiple"] = display_prod["Yield Multiple"].apply(
        lambda x: f"{x:.1f}x" if x >= 0 else f"{x:.1f}x"
    )
    display_prod["vs ETF"] = display_prod["vs ETF"].apply(
        lambda x: f"{x:.1f}x" if x >= 0 else f"{x:.1f}x"
    )
    display_prod["Status"] = display_prod["Accretive"].apply(
        lambda x: "Accretive" if x else "Dilutive"
    )

    st.dataframe(
        display_prod[["Ticker", "ETH Holdings", "Yield (ETH/yr)", "Burn (ETH/yr)",
                      "Premium (ETH/yr)", "Total (ETH/yr)", "Net Rate", "Yield Multiple",
                      "Status"]],
        use_container_width=True,
        hide_index=True,
    )

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_yield = prod_df["Yield (ETH/yr)"].sum()
    total_burn = prod_df["Burn (ETH/yr)"].sum()
    total_premium = prod_df["Premium (ETH/yr)"].sum()
    total_productivity = prod_df["Total (ETH/yr)"].sum()
    accretive_count = prod_df["Accretive"].sum()

    with col1:
        st.metric("Staking Yield", f"{total_yield:,.0f} ETH/yr")

    with col2:
        st.metric("Operating Burn", f"-{total_burn:,.0f} ETH/yr")

    with col3:
        st.metric("Premium Capture", f"+{total_premium:,.0f} ETH/yr",
                  delta="annualized")

    with col4:
        total_label = f"+{total_productivity:,.0f}" if total_productivity >= 0 else f"{total_productivity:,.0f}"
        st.metric("Total Productivity", f"{total_label} ETH/yr",
                  delta=f"{int(accretive_count)}/{len(prod_df)} accretive")

    st.caption("""
    **Total (ETH/yr)** = Yield - Burn + Annualized Premium Capture
    **Net Rate** = Total / Holdings (as annual %). Includes premium capture.
    **Yield Multiple** = Net Rate / Network Staking APY (>1x = outperforming pure staking)
    **Premium (ETH/yr)** = ETH from Premium / Years Active (annualized contribution)
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
