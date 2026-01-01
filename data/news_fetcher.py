"""
News fetcher for DAT company updates
Aggregates news from multiple crypto news sources
"""
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.utils import parsedate_to_datetime
import streamlit as st
from bs4 import BeautifulSoup


def parse_rss_date(date_str: str) -> datetime:
    """Parse RSS date string robustly"""
    if not date_str:
        return datetime.now()

    # Try email.utils parser first (handles RFC 2822 format used by RSS)
    try:
        dt = parsedate_to_datetime(date_str)
        # Convert to naive datetime
        return dt.replace(tzinfo=None)
    except:
        pass

    # Try common formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo:
                dt = dt.replace(tzinfo=None)
            return dt
        except:
            continue

    return datetime.now()

# Keywords to filter for DAT-related news
DAT_KEYWORDS = [
    # Company tickers and names
    "BMNR", "Bitmine", "BitMine Immersion",
    "SBET", "SharpLink",
    "ETHM", "Ether Machine",
    "BTBT", "Bit Digital",
    "BTCS",
    "ETHZ", "ETHZilla",
    "GAME", "GameSquare",
    "FGNX", "Fundamental Global",
    # General terms
    "ETH treasury", "Ethereum treasury",
    "corporate Ethereum", "corporate ETH",
    "ETH accumulation", "Ethereum accumulation",
    "digital asset treasury",
]

# Leaders to track
DAT_LEADERS = [
    "Tom Lee", "Joe Lubin", "Andrew Keys", "Sam Tabar",
    "Peter Thiel",
]


@st.cache_data(ttl=900)  # 15 minute cache
def fetch_google_news(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """Fetch news from Google News RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:num_results]

        news = []
        for item in items:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
            source = item.find('source').text if item.find('source') else ""

            # Parse date
            parsed_date = parse_rss_date(pub_date)

            news.append({
                "title": title,
                "url": link,
                "source": source,
                "date": parsed_date,
                "date_str": parsed_date.strftime("%b %d, %Y"),
            })

        return news
    except Exception as e:
        return []


@st.cache_data(ttl=900)
def fetch_coindesk_news() -> List[Dict[str, Any]]:
    """Fetch latest news from CoinDesk RSS"""
    try:
        url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:30]

        news = []
        for item in items:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
            description = item.find('description').text if item.find('description') else ""

            # Check if relevant to DAT
            content = (title + " " + description).lower()
            is_relevant = any(kw.lower() in content for kw in DAT_KEYWORDS)

            if is_relevant:
                parsed_date = parse_rss_date(pub_date)

                news.append({
                    "title": title,
                    "url": link,
                    "source": "CoinDesk",
                    "date": parsed_date,
                    "date_str": parsed_date.strftime("%b %d, %Y"),
                    "description": description[:200] + "..." if len(description) > 200 else description,
                })

        return news
    except Exception as e:
        return []


@st.cache_data(ttl=900)
def fetch_theblock_treasury_news() -> List[Dict[str, Any]]:
    """Fetch treasury-related news from The Block"""
    try:
        # The Block doesn't have a public RSS, so we search via Google
        return fetch_google_news("site:theblock.co ethereum treasury OR BMNR OR SBET", 10)
    except Exception as e:
        return []


@st.cache_data(ttl=900)
def fetch_cointelegraph_news() -> List[Dict[str, Any]]:
    """Fetch news from Cointelegraph RSS"""
    try:
        url = "https://cointelegraph.com/rss"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:30]

        news = []
        for item in items:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""

            # Check if relevant
            if any(kw.lower() in title.lower() for kw in DAT_KEYWORDS):
                parsed_date = parse_rss_date(pub_date)

                news.append({
                    "title": title,
                    "url": link,
                    "source": "Cointelegraph",
                    "date": parsed_date,
                    "date_str": parsed_date.strftime("%b %d, %Y"),
                })

        return news
    except Exception as e:
        return []


def make_naive(dt):
    """Convert datetime to naive (remove timezone info)"""
    if dt is None:
        return datetime.min
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


@st.cache_data(ttl=600)  # 10 minute cache
def fetch_all_dat_news() -> List[Dict[str, Any]]:
    """Aggregate news from all sources"""
    all_news = []

    # Fetch from each source
    sources = [
        ("BMNR Bitmine Ethereum", fetch_google_news, ["BMNR Bitmine Ethereum treasury"]),
        ("SBET SharpLink Ethereum", fetch_google_news, ["SBET SharpLink Ethereum"]),
        ("Ethereum treasury company", fetch_google_news, ["Ethereum treasury company"]),
        ("CoinDesk", fetch_coindesk_news, []),
        ("Cointelegraph", fetch_cointelegraph_news, []),
    ]

    for name, fetcher, args in sources:
        try:
            if args:
                news = fetcher(args[0])
            else:
                news = fetcher()
            all_news.extend(news)
        except Exception as e:
            continue

    # Deduplicate by URL
    seen_urls = set()
    unique_news = []
    for item in all_news:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_news.append(item)

    # Sort by date (newest first) - convert to naive datetime for comparison
    unique_news.sort(key=lambda x: make_naive(x.get("date", datetime.min)), reverse=True)

    return unique_news[:30]  # Return top 30


@st.cache_data(ttl=600)
def fetch_company_news(ticker: str) -> List[Dict[str, Any]]:
    """Fetch news for a specific company"""
    company_queries = {
        "BMNR": "BMNR OR Bitmine Immersion Ethereum",
        "SBET": "SBET OR SharpLink Gaming Ethereum",
        "ETHM": "Ether Machine ETHM Ethereum",
        "BTBT": "BTBT Bit Digital Ethereum",
        "BTCS": "BTCS Ethereum treasury",
        "ETHZ": "ETHZilla ETHZ Ethereum",
        "GAME": "GameSquare Ethereum treasury",
        "FGNX": "Fundamental Global Ethereum",
    }

    query = company_queries.get(ticker, f"{ticker} Ethereum")
    return fetch_google_news(query, 10)


@st.cache_data(ttl=300)  # 5 minute cache for Twitter/Lookonchain
def fetch_lookonchain_mentions() -> List[Dict[str, Any]]:
    """
    Placeholder for Lookonchain feed.
    In production, you would use Twitter API or Nitter RSS.
    """
    # Note: Twitter API requires authentication
    # This returns a placeholder with instructions
    return [{
        "title": "Follow @lookonchain on X for real-time whale alerts",
        "url": "https://twitter.com/lookonchain",
        "source": "Twitter/X",
        "date": datetime.now(),
        "date_str": "Live",
        "description": "Lookonchain tracks whale wallets and often catches DAT acquisitions before official announcements.",
    }]


def get_time_ago(dt: datetime) -> str:
    """Convert datetime to relative time string"""
    if dt is None:
        return ""

    # Make both naive for comparison
    dt_naive = make_naive(dt)
    now = datetime.now()

    try:
        diff = now - dt_naive

        if diff.days > 7:
            return dt_naive.strftime("%b %d")
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    except:
        return dt_naive.strftime("%b %d") if dt_naive else ""
