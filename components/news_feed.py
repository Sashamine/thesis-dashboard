"""
News Feed Component
Displays DAT-related news and announcements
"""
import streamlit as st
from typing import List, Dict, Any, Optional
from data.news_fetcher import (
    fetch_all_dat_news,
    fetch_company_news,
    fetch_lookonchain_mentions,
    get_time_ago,
)
from data.edgar_fetcher import (
    fetch_all_dat_filings,
    fetch_company_edgar,
    get_filing_type_description,
    get_filing_type_emoji,
)


def render_news_item(item: Dict[str, Any], show_source: bool = True) -> None:
    """Render a single news item"""
    title = item.get("title", "")
    url = item.get("url", "")
    source = item.get("source", "")
    date = item.get("date")
    description = item.get("description", "")

    time_str = get_time_ago(date) if date else item.get("date_str", "")

    # Source badge color
    source_colors = {
        "CoinDesk": "blue",
        "Cointelegraph": "green",
        "The Block": "orange",
        "Twitter/X": "gray",
    }

    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"**[{title}]({url})**")
        if description:
            st.caption(description)

    with col2:
        if show_source:
            st.caption(f"{source}")
        st.caption(f"{time_str}")


def render_news_feed(
    max_items: int = 15,
    show_sources: bool = True,
    compact: bool = False,
) -> None:
    """Render the full news feed"""
    st.subheader("Latest DAT News")

    # Refresh button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Refresh", key="refresh_news"):
            st.cache_data.clear()
            st.rerun()

    # Fetch news
    with st.spinner("Loading news..."):
        news = fetch_all_dat_news()

    if not news:
        st.info("No recent news found. Check back later or verify your internet connection.")
        return

    # Display news items
    for i, item in enumerate(news[:max_items]):
        if compact:
            title = item.get("title", "")
            url = item.get("url", "")
            source = item.get("source", "")
            time_str = get_time_ago(item.get("date")) if item.get("date") else ""

            st.markdown(f"• [{title[:80]}{'...' if len(title) > 80 else ''}]({url}) *({source}, {time_str})*")
        else:
            render_news_item(item, show_sources)
            if i < len(news[:max_items]) - 1:
                st.markdown("---")

    # Lookonchain plug
    st.markdown("---")
    st.markdown("**Real-time Whale Tracking**")
    st.markdown("Follow [@lookonchain](https://twitter.com/lookonchain) on X for instant alerts on DAT acquisitions")


def render_company_news(ticker: str, max_items: int = 5) -> None:
    """Render news feed for a specific company"""
    st.subheader(f"{ticker} News")

    with st.spinner(f"Loading {ticker} news..."):
        news = fetch_company_news(ticker)

    if not news:
        st.info(f"No recent news found for {ticker}")
        return

    for i, item in enumerate(news[:max_items]):
        render_news_item(item)
        if i < len(news[:max_items]) - 1:
            st.divider()


def render_news_sidebar() -> None:
    """Render compact news feed for sidebar"""
    st.markdown("**Latest News**")

    news = fetch_all_dat_news()

    if not news:
        st.caption("No news available")
        return

    for item in news[:5]:
        title = item.get("title", "")
        url = item.get("url", "")
        time_str = get_time_ago(item.get("date")) if item.get("date") else ""

        # Truncate title
        short_title = title[:50] + "..." if len(title) > 50 else title
        st.caption(f"[{short_title}]({url})")
        st.caption(f"*{time_str}*")


def render_sec_filing(filing: Dict[str, Any]) -> None:
    """Render a single SEC filing"""
    emoji = get_filing_type_emoji(filing.get("form_type", ""))
    form_type = filing.get("form_type", "")
    ticker = filing.get("ticker", "")
    company = filing.get("company", "")
    url = filing.get("url", "")
    date_str = filing.get("date_str", "")
    description = get_filing_type_description(form_type)

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"{emoji} **[{ticker}: {form_type}]({url})** - {description}")
        if company:
            st.caption(company)

    with col2:
        st.caption(date_str)


def render_sec_filings_feed(max_items_per_company: int = 5) -> None:
    """Render SEC filings feed organized by company"""
    st.subheader("SEC EDGAR Filings")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Refresh", key="refresh_edgar"):
            st.cache_data.clear()
            st.rerun()

    # Company order and names
    companies = [
        ("BMNR", "Bitmine Immersion Technologies"),
        ("SBET", "SharpLink Gaming"),
        ("ETHM", "The Ether Machine"),
        ("BTBT", "Bit Digital"),
        ("BTCS", "BTCS Inc."),
        ("ETHZ", "ETHZilla Corporation"),
        ("GAME", "GameSquare Holdings"),
        ("FGNX", "Fundamental Global"),
    ]

    with st.spinner("Loading SEC filings..."):
        filings = fetch_all_dat_filings(count_per_company=max_items_per_company)

    if not filings:
        st.info("No SEC filings found.")
        return

    # Group filings by ticker
    filings_by_company = {}
    for filing in filings:
        ticker = filing.get("ticker", "")
        if ticker not in filings_by_company:
            filings_by_company[ticker] = []
        filings_by_company[ticker].append(filing)

    # Display by company
    for ticker, company_name in companies:
        company_filings = filings_by_company.get(ticker, [])
        filing_count = len(company_filings)

        with st.expander(f"**{ticker}** - {company_name} ({filing_count} filings)", expanded=False):
            if not company_filings:
                st.caption("No recent filings found")
            else:
                for i, filing in enumerate(company_filings):
                    emoji = get_filing_type_emoji(filing.get("form_type", ""))
                    form_type = filing.get("form_type", "")
                    url = filing.get("url", "")
                    date_str = filing.get("date_str", "")
                    description = get_filing_type_description(form_type)

                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"{emoji} **[{form_type}]({url})** - {description}")
                    with col2:
                        st.caption(date_str)

                    if i < len(company_filings) - 1:
                        st.markdown("---")


def render_company_sec_filings(ticker: str, max_items: int = 10) -> None:
    """Render SEC filings for a specific company"""
    st.subheader(f"{ticker} SEC Filings")

    with st.spinner(f"Loading {ticker} SEC filings..."):
        filings = fetch_company_edgar(ticker, max_items)

    if not filings:
        st.info(f"No SEC filings found for {ticker}. CIK may not be configured.")
        return

    for i, filing in enumerate(filings):
        render_sec_filing(filing)
        if i < len(filings) - 1:
            st.divider()


def render_news_page() -> None:
    """Render the full news page"""
    st.title("News & Announcements")
    st.markdown("*Latest updates on ETH treasury companies*")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["All News", "SEC Filings", "By Company", "Key Sources"])

    with tab1:
        render_news_feed(max_items=20)

    with tab2:
        render_sec_filings_feed(max_items_per_company=5)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.selectbox(
                "Select Company",
                options=["BMNR", "SBET", "ETHM", "BTBT", "BTCS", "ETHZ", "GAME", "FGNX"],
            )

        st.markdown("---")
        st.subheader("News")
        render_company_news(ticker, max_items=10)

        st.markdown("---")
        render_company_sec_filings(ticker, max_items=10)

    with tab4:
        st.subheader("Key Sources to Monitor")

        st.markdown("""
        **Real-time (minutes)**
        - [@lookonchain](https://twitter.com/lookonchain) - Whale wallet tracking
        - [@ArkhamIntel](https://twitter.com/ArkhamIntel) - On-chain intelligence

        **Same-day**
        - [The Block Treasuries](https://theblock.co/treasuries/ethereum-treasuries)
        - [ethereumtreasuries.net](https://ethereumtreasuries.net)
        - [strategicethreserve.xyz](https://strategicethreserve.xyz)

        **Company IR / Twitter**
        - [@Bitmine_BMNR](https://twitter.com/Bitmine_BMNR) - Weekly updates
        - [@SharpLinkGaming](https://twitter.com/SharpLinkGaming)

        **SEC EDGAR (Quarterly)**
        - [SEC EDGAR Search](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
        - [SBET Filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001784851)
        - [BTBT Filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001799290)
        - [BTCS Filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001436229)
        """)

        st.markdown("---")
        st.subheader("RSS Feeds")
        st.code("""
# Add to your RSS reader:
https://www.coindesk.com/arc/outboundfeeds/rss/
https://cointelegraph.com/rss
https://news.google.com/rss/search?q=Ethereum+treasury+company
        """)
