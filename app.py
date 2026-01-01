"""
Thesis Tracking Dashboard
Main Streamlit Application

A personal investment thesis tracking dashboard for monitoring
the health of interconnected investment theses over a 10-15 year horizon.

Run with: streamlit run app.py

Version: 1.0.1
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DAT_COMPANIES, PERSONAL_MILESTONES, FRED_API_KEY
from components.home import render_home_page
from components.dat_table import render_dat_table, render_add_dat_form
from components.dat_detail import render_dat_detail_page, render_dat_selector
from components.thesis_tracker import render_thesis_tracker, render_thesis_dependencies
from components.charts import render_comparison_chart, render_eth_holdings_chart, render_nav_discount_chart
from components.news_feed import render_news_page, render_news_feed
from data import fetch_eth_price, fetch_stock_data, calculate_nav_discount, calculate_nav_per_share
from utils import days_until, format_date

# Page configuration
st.set_page_config(
    page_title="Thesis Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .css-1d391kg {
        padding: 1rem;
    }
    div[data-testid="stExpander"] details summary p {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar() -> str:
    """Render sidebar and return selected page"""
    with st.sidebar:
        st.title("📊 Thesis Tracker")
        st.caption("Investment Thesis Dashboard")

        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            options=[
                "Home",
                "News",
                "DAT Universe",
                "Company Details",
                "Thesis Tracker",
                "Charts & Analysis",
                "Settings",
            ],
            index=0,
        )

        st.markdown("---")

        # Quick stats
        st.subheader("Quick Stats")

        eth_data = fetch_eth_price()
        eth_price = eth_data.get("price", 0)

        if eth_price:
            st.metric("ETH", f"${eth_price:,.2f}")

        # Personal milestones
        st.markdown("---")
        st.subheader("Milestones")

        wedding_days = days_until(PERSONAL_MILESTONES["wedding"])
        family_days = days_until(PERSONAL_MILESTONES["family_planning"])

        st.caption(f"Wedding: {wedding_days} days")
        st.caption(f"Family: {family_days} days")

        st.markdown("---")

        # API status
        st.subheader("Data Sources")
        st.caption("✅ CoinGecko")
        st.caption("✅ Yahoo Finance")
        st.caption("✅ DefiLlama")
        st.caption(f"{'✅' if FRED_API_KEY else '⚠️'} FRED (macro data)")

        if not FRED_API_KEY:
            st.caption("Add FRED_API_KEY to .env")

    return page


def render_charts_page() -> None:
    """Render charts and analysis page"""
    st.title("Charts & Analysis")

    tab1, tab2, tab3 = st.tabs(["Price Comparison", "ETH Holdings", "NAV Analysis"])

    with tab1:
        st.subheader("DAT Price Comparison")

        tickers = list(DAT_COMPANIES.keys())
        selected = st.multiselect(
            "Select companies to compare",
            options=tickers,
            default=["BMNR", "SBET"],
        )

        if selected:
            col1, col2 = st.columns([3, 1])
            with col1:
                period = st.selectbox(
                    "Period",
                    options=["1mo", "3mo", "6mo", "1y", "2y"],
                    index=3,
                )
            with col2:
                normalize = st.checkbox("Normalize", value=True)

            render_comparison_chart(selected, period, normalize)

    with tab2:
        st.subheader("ETH Holdings Distribution")

        holdings = {ticker: data["eth_holdings"] for ticker, data in DAT_COMPANIES.items()}
        render_eth_holdings_chart(holdings)

        # Tier breakdown
        st.subheader("Holdings by Tier")

        tier1_eth = sum(c["eth_holdings"] for c in DAT_COMPANIES.values() if c["tier"] == 1)
        tier2_eth = sum(c["eth_holdings"] for c in DAT_COMPANIES.values() if c["tier"] == 2)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tier 1 Total", f"{tier1_eth:,.0f} ETH")
        with col2:
            st.metric("Tier 2 Total", f"{tier2_eth:,.0f} ETH")

    with tab3:
        st.subheader("NAV Discount/Premium Analysis")

        eth_data = fetch_eth_price()
        eth_price = eth_data.get("price", 0) or 0

        if eth_price:
            discounts = {}
            for ticker, company in DAT_COMPANIES.items():
                stock = fetch_stock_data(ticker)
                stock_price = stock.get("price", 0) or 0
                shares = stock.get("shares_outstanding", 0) or 0

                if shares > 0:
                    nav_per_share = calculate_nav_per_share(
                        company["eth_holdings"], eth_price, shares
                    )
                    discount = calculate_nav_discount(stock_price, nav_per_share)
                    discounts[ticker] = discount

            if discounts:
                render_nav_discount_chart(discounts)

                # Summary
                valid_discounts = [v for v in discounts.values() if v is not None]
                if valid_discounts:
                    avg_discount = sum(valid_discounts) / len(valid_discounts)
                    st.metric(
                        "Average NAV Discount/Premium",
                        f"{avg_discount * 100:.2f}%"
                    )


def render_settings_page() -> None:
    """Render settings page"""
    st.title("Settings")

    tab1, tab2, tab3 = st.tabs(["API Keys", "Alert Thresholds", "Personal Positions"])

    with tab1:
        st.subheader("API Configuration")

        st.markdown("""
        Configure API keys in a `.env` file in the project root:

        ```
        FRED_API_KEY=your_key_here
        ```

        Get a free FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html
        """)

        st.info("CoinGecko, Yahoo Finance, and DefiLlama don't require API keys.")

    with tab2:
        st.subheader("Alert Thresholds")

        st.markdown("Configure when to show warnings:")

        col1, col2 = st.columns(2)

        with col1:
            nav_warning = st.slider(
                "NAV Discount Warning (%)",
                min_value=10,
                max_value=50,
                value=30,
                help="Show warning when NAV discount exceeds this"
            )

            drawdown_warning = st.slider(
                "Drawdown Warning (%)",
                min_value=20,
                max_value=60,
                value=40,
                help="Show warning when drawdown exceeds this"
            )

        with col2:
            dilution_warning = st.slider(
                "Annual Dilution Warning (%)",
                min_value=10,
                max_value=50,
                value=30,
                help="Show warning when annual dilution exceeds this"
            )

            yield_warning = st.slider(
                "ETH Yield Warning (%)",
                min_value=1.0,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Show warning when staking yield falls below this"
            )

        if st.button("Save Thresholds"):
            st.success("Thresholds saved! (Note: In production, this would persist to config)")

    with tab3:
        st.subheader("Personal Positions")

        st.markdown("Update your holdings:")

        col1, col2 = st.columns(2)

        with col1:
            bmnr_shares = st.number_input(
                "BMNR Shares",
                min_value=0,
                value=10000,
                step=100,
            )

            sbet_shares = st.number_input(
                "SBET Shares",
                min_value=0,
                value=10000,
                step=100,
            )

        with col2:
            bmnr_cost = st.number_input(
                "BMNR Cost Basis ($)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Your average cost per share"
            )

            sbet_cost = st.number_input(
                "SBET Cost Basis ($)",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

        if st.button("Save Positions"):
            st.success("Positions saved! (Note: In production, this would persist to config)")


def main():
    """Main application entry point"""
    page = render_sidebar()

    if page == "Home":
        render_home_page()

    elif page == "News":
        render_news_page()

    elif page == "DAT Universe":
        render_dat_table()
        st.markdown("---")
        render_add_dat_form()

    elif page == "Company Details":
        ticker = render_dat_selector()
        if ticker:
            render_dat_detail_page(ticker)

    elif page == "Thesis Tracker":
        render_thesis_tracker()
        st.markdown("---")
        render_thesis_dependencies()

    elif page == "Charts & Analysis":
        render_charts_page()

    elif page == "Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
