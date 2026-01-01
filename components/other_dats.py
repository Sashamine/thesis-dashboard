"""
Other DAT Universe Component
Displays SOL, HYPE, and BNB treasury companies (for tracking/news only)
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any
from config import SOL_DAT_COMPANIES, HYPE_DAT_COMPANIES, BNB_DAT_COMPANIES, BTC_DAT_COMPANIES
from data import fetch_stock_data


def get_asset_price(asset: str) -> float:
    """Fetch current price for BTC, SOL, HYPE, or BNB"""
    # Using CoinGecko IDs
    asset_ids = {
        "BTC": "bitcoin",
        "SOL": "solana",
        "HYPE": "hyperliquid",
        "BNB": "binancecoin",
    }

    try:
        import requests
        cg_id = asset_ids.get(asset)
        if not cg_id:
            return 0

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get(cg_id, {}).get("usd", 0)
    except Exception:
        pass

    # Fallback prices
    fallback = {"BTC": 95000.0, "SOL": 125.0, "HYPE": 25.0, "BNB": 700.0}
    return fallback.get(asset, 0)


def build_dat_dataframe(companies: Dict[str, Any], asset_price: float) -> pd.DataFrame:
    """Build DataFrame with DAT company metrics"""
    rows = []

    for ticker, company in companies.items():
        holdings = company.get("holdings", 0)
        cost_basis = company.get("cost_basis_avg", 0)
        staking_pct = company.get("staking_pct", 0)
        staking_apy = company.get("staking_apy", 0)

        # Calculate values
        treasury_value = holdings * asset_price
        cost_value = holdings * cost_basis
        unrealized_pnl = treasury_value - cost_value
        pnl_pct = (unrealized_pnl / cost_value * 100) if cost_value > 0 else 0

        # Annual yield from staking
        staked_holdings = holdings * staking_pct
        annual_yield = staked_holdings * staking_apy
        annual_yield_usd = annual_yield * asset_price

        # Fetch stock data for market cap
        stock = fetch_stock_data(ticker)
        stock_price = stock.get("price", 0) or 0
        market_cap = stock.get("market_cap", 0) or 0

        rows.append({
            "Ticker": ticker,
            "Company": company["name"],
            "Tier": company["tier"],
            "Holdings": holdings,
            "Treasury Value": treasury_value,
            "Cost Basis": cost_value,
            "Unrealized P&L": unrealized_pnl,
            "P&L %": pnl_pct,
            "Staked %": staking_pct,
            "Staking APY": staking_apy,
            "Annual Yield": annual_yield,
            "Annual Yield USD": annual_yield_usd,
            "Stock Price": stock_price,
            "Market Cap": market_cap,
            "Leader": company.get("leader", ""),
            "Strategy": company.get("strategy", ""),
            "Notes": company.get("notes", ""),
        })

    return pd.DataFrame(rows)


def format_large_number(num: float) -> str:
    """Format large numbers with B/M suffix"""
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.1f}M"
    elif num >= 1e3:
        return f"${num/1e3:.0f}K"
    else:
        return f"${num:.0f}"


def render_asset_section(asset: str, companies: Dict[str, Any], asset_price: float) -> None:
    """Render a section for a specific asset type"""
    if not companies:
        st.caption(f"No {asset} treasury companies configured")
        return

    st.caption(f"{asset} Price: ${asset_price:,.2f}")

    df = build_dat_dataframe(companies, asset_price)

    # Format for display
    display_df = df.copy()
    display_df["Holdings"] = display_df["Holdings"].apply(lambda x: f"{x:,.0f}")
    display_df["Treasury Value"] = display_df["Treasury Value"].apply(format_large_number)
    display_df["Unrealized P&L"] = display_df["Unrealized P&L"].apply(
        lambda x: f"+{format_large_number(x)}" if x >= 0 else f"-{format_large_number(abs(x))}"
    )
    display_df["P&L %"] = display_df["P&L %"].apply(
        lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%"
    )
    display_df["Staked %"] = display_df["Staked %"].apply(lambda x: f"{x*100:.0f}%")
    display_df["Staking APY"] = display_df["Staking APY"].apply(lambda x: f"{x*100:.1f}%")
    display_df["Annual Yield"] = display_df["Annual Yield"].apply(lambda x: f"{x:,.0f}")
    display_df["Stock Price"] = display_df["Stock Price"].apply(
        lambda x: f"${x:.2f}" if x else "N/A"
    )
    display_df["Market Cap"] = display_df["Market Cap"].apply(
        lambda x: format_large_number(x) if x else "N/A"
    )

    # Display columns
    columns_to_show = [
        "Ticker", "Company", "Holdings", "Treasury Value",
        "Unrealized P&L", "Staked %", "Staking APY", "Stock Price"
    ]

    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        hide_index=True,
    )

    # Summary stats
    total_holdings = df["Holdings"].sum()
    total_value = df["Treasury Value"].sum()
    total_yield = df["Annual Yield"].sum()
    total_yield_usd = df["Annual Yield USD"].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"Total {asset}", f"{total_holdings:,.0f}")
    with col2:
        st.metric("Treasury Value", format_large_number(total_value))
    with col3:
        st.metric(f"Annual Yield", f"{total_yield:,.0f} {asset}")
    with col4:
        st.metric("Yield (USD)", format_large_number(total_yield_usd))

    # Expandable details for each company
    with st.expander("Company Details"):
        for _, row in df.iterrows():
            st.markdown(f"**{row['Ticker']} - {row['Company']}**")
            st.caption(f"Strategy: {row['Strategy']}")
            st.caption(f"Leader: {row['Leader']}")
            st.caption(f"Notes: {row['Notes']}")
            st.markdown("---")


def render_productivity_section(asset: str, companies: Dict[str, Any], asset_price: float) -> None:
    """Render Yield vs Burn productivity analysis for a specific asset"""
    if not companies or asset_price <= 0:
        return

    st.subheader(f"{asset} Company Productivity: Yield vs Burn")

    productivity_data = []

    for ticker, company in companies.items():
        holdings = company.get("holdings", 0)
        staking_pct = company.get("staking_pct", 0)
        staking_apy = company.get("staking_apy", 0)
        quarterly_burn_usd = company.get("quarterly_burn_usd", 0)

        # Annual yield from staking
        staked_holdings = holdings * staking_pct
        annual_yield_tokens = staked_holdings * staking_apy
        annual_yield_usd = annual_yield_tokens * asset_price

        # Annual burn
        annual_burn_usd = quarterly_burn_usd * 4
        annual_burn_tokens = annual_burn_usd / asset_price if asset_price > 0 else 0

        # Net productivity
        net_tokens = annual_yield_tokens - annual_burn_tokens
        net_usd = annual_yield_usd - annual_burn_usd

        # Net rate (as % of holdings)
        net_rate = (net_tokens / holdings) if holdings > 0 else 0

        # Yield multiple vs pure staking
        yield_multiple = net_rate / staking_apy if staking_apy > 0 else 0

        # Is accretive?
        is_accretive = net_tokens > 0

        productivity_data.append({
            "Ticker": ticker,
            "Holdings": holdings,
            "Staked %": staking_pct,
            "Staking APY": staking_apy,
            f"Yield ({asset}/yr)": annual_yield_tokens,
            "Yield (USD/yr)": annual_yield_usd,
            f"Burn ({asset}/yr)": annual_burn_tokens,
            "Burn (USD/yr)": annual_burn_usd,
            f"Net ({asset}/yr)": net_tokens,
            "Net (USD/yr)": net_usd,
            "Net Rate": net_rate,
            "Yield Multiple": yield_multiple,
            "Accretive": is_accretive,
            "Burn Source": company.get("burn_source", ""),
        })

    prod_df = pd.DataFrame(productivity_data)

    # Sort by net productivity
    prod_df = prod_df.sort_values(f"Net ({asset}/yr)", ascending=False)

    # Format for display
    display_prod = prod_df.copy()
    display_prod["Holdings"] = display_prod["Holdings"].apply(lambda x: f"{x:,.0f}")
    display_prod["Staked %"] = display_prod["Staked %"].apply(lambda x: f"{x*100:.0f}%")
    display_prod["Staking APY"] = display_prod["Staking APY"].apply(lambda x: f"{x*100:.1f}%")
    display_prod[f"Yield ({asset}/yr)"] = display_prod[f"Yield ({asset}/yr)"].apply(lambda x: f"{x:,.0f}")
    display_prod[f"Burn ({asset}/yr)"] = display_prod[f"Burn ({asset}/yr)"].apply(lambda x: f"{x:,.0f}")
    display_prod[f"Net ({asset}/yr)"] = display_prod[f"Net ({asset}/yr)"].apply(
        lambda x: f"+{x:,.0f}" if x >= 0 else f"{x:,.0f}"
    )
    display_prod["Net Rate"] = display_prod["Net Rate"].apply(
        lambda x: f"+{x*100:.2f}%" if x >= 0 else f"{x*100:.2f}%"
    )
    display_prod["Yield Multiple"] = display_prod["Yield Multiple"].apply(
        lambda x: f"{x:.2f}x" if x >= 0 else f"{x:.2f}x"
    )
    display_prod["Status"] = display_prod["Accretive"].apply(
        lambda x: "Accretive" if x else "Dilutive"
    )

    # Display table
    columns_to_show = [
        "Ticker", "Holdings", f"Yield ({asset}/yr)", f"Burn ({asset}/yr)",
        f"Net ({asset}/yr)", "Net Rate", "Yield Multiple", "Status"
    ]

    st.dataframe(
        display_prod[columns_to_show],
        use_container_width=True,
        hide_index=True,
    )

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_yield = prod_df[f"Yield ({asset}/yr)"].sum()
    total_burn = prod_df[f"Burn ({asset}/yr)"].sum()
    total_net = prod_df[f"Net ({asset}/yr)"].sum()
    accretive_count = prod_df["Accretive"].sum()

    with col1:
        st.metric("Total Yield", f"{total_yield:,.0f} {asset}/yr")

    with col2:
        st.metric("Total Burn", f"{total_burn:,.0f} {asset}/yr")

    with col3:
        net_label = f"+{total_net:,.0f}" if total_net >= 0 else f"{total_net:,.0f}"
        st.metric("Net Productivity", f"{net_label} {asset}/yr",
                  delta=f"{int(accretive_count)}/{len(prod_df)} accretive")

    with col4:
        total_net_usd = prod_df["Net (USD/yr)"].sum()
        st.metric("Net (USD)", format_large_number(total_net_usd))

    st.caption(f"""
    **Yield Multiple** = Net Rate / Staking APY (>1x = outperforming pure staking)
    **Net Rate** = (Yield - Burn) / Holdings as annual %
    **Accretive** = Company generates more from staking than it burns on operations
    """)


def render_other_dats_page() -> None:
    """Render the Other DATs universe page"""
    st.title("Other DAT Universe")
    st.caption("BTC, SOL, HYPE, and BNB treasury companies (for tracking/news - not part of core ETH thesis)")

    # Fetch prices
    with st.spinner("Loading prices..."):
        btc_price = get_asset_price("BTC")
        sol_price = get_asset_price("SOL")
        hype_price = get_asset_price("HYPE")
        bnb_price = get_asset_price("BNB")

    # Create tabs for each asset
    tab1, tab2, tab3, tab4 = st.tabs(["Bitcoin (BTC)", "Solana (SOL)", "Hyperliquid (HYPE)", "BNB Chain (BNB)"])

    with tab1:
        st.subheader("Bitcoin Treasury Companies")
        st.caption("The OG DAT strategy - started by MicroStrategy in Aug 2020")
        render_asset_section("BTC", BTC_DAT_COMPANIES, btc_price)
        st.markdown("---")
        render_productivity_section("BTC", BTC_DAT_COMPANIES, btc_price)

    with tab2:
        st.subheader("Solana Treasury Companies")
        render_asset_section("SOL", SOL_DAT_COMPANIES, sol_price)
        st.markdown("---")
        render_productivity_section("SOL", SOL_DAT_COMPANIES, sol_price)

    with tab3:
        st.subheader("Hyperliquid Treasury Companies")
        render_asset_section("HYPE", HYPE_DAT_COMPANIES, hype_price)
        st.markdown("---")
        render_productivity_section("HYPE", HYPE_DAT_COMPANIES, hype_price)

    with tab4:
        st.subheader("BNB Treasury Companies")
        render_asset_section("BNB", BNB_DAT_COMPANIES, bnb_price)
        st.markdown("---")
        render_productivity_section("BNB", BNB_DAT_COMPANIES, bnb_price)

    # Overall summary
    st.markdown("---")
    st.subheader("Cross-Chain DAT Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        btc_total = sum(c["holdings"] for c in BTC_DAT_COMPANIES.values())
        btc_value = btc_total * btc_price
        st.metric("BTC Holdings", f"{btc_total:,.0f}", format_large_number(btc_value))
        st.caption(f"{len(BTC_DAT_COMPANIES)} companies")

    with col2:
        sol_total = sum(c["holdings"] for c in SOL_DAT_COMPANIES.values())
        sol_value = sol_total * sol_price
        st.metric("SOL Holdings", f"{sol_total:,.0f}", format_large_number(sol_value))
        st.caption(f"{len(SOL_DAT_COMPANIES)} companies")

    with col3:
        hype_total = sum(c["holdings"] for c in HYPE_DAT_COMPANIES.values())
        hype_value = hype_total * hype_price
        st.metric("HYPE Holdings", f"{hype_total:,.0f}", format_large_number(hype_value))
        st.caption(f"{len(HYPE_DAT_COMPANIES)} companies")

    with col4:
        bnb_total = sum(c["holdings"] for c in BNB_DAT_COMPANIES.values())
        bnb_value = bnb_total * bnb_price
        st.metric("BNB Holdings", f"{bnb_total:,.0f}", format_large_number(bnb_value))
        st.caption(f"{len(BNB_DAT_COMPANIES)} companies")

    # Key observations
    st.markdown("---")
    st.subheader("Key Observations")
    st.markdown("""
    **Bitcoin DATs (The OG):**
    - MicroStrategy dominates with 446K BTC (~$42B) - trades at 2x NAV
    - Miners (MARA, RIOT, CLSK, HUT) are hybrid mining + treasury
    - No native staking yield - pure price appreciation play
    - Most mature DAT ecosystem, started Aug 2020

    **Solana DATs:**
    - Fastest growing category with 5+ companies
    - Forward Industries (FWDI) dominates with ~7M SOL ($1.6B+ raised)
    - Higher staking yields (7-11%) than ETH staking
    - Many backed by top-tier crypto VCs (Galaxy, Pantera, Multicoin)

    **Hyperliquid DATs:**
    - Emerging category with 2 companies
    - PURR (Hyperliquid Strategies) is largest with 12.6M HYPE
    - Created via SPAC/merger structures

    **BNB DATs:**
    - BNC (CEA Industries) dominates with 500K BNB
    - Heavy involvement from YZi Labs (CZ family office)
    - Higher regulatory risk due to Binance association
    """)

    # Data sources
    st.caption("Data sources: CoinGecko, SEC EDGAR, company press releases")
