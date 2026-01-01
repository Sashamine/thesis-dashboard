"""
News fetcher for DAT company updates
Aggregates news from multiple crypto news sources
"""
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import streamlit as st
from bs4 import BeautifulSoup

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
            try:
                parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                parsed_date = datetime.now()

            news.append({
                "title": title,
                "url": link,
                "source": source,
                "date": parsed_date,
                "date_str": parsed_date.strftime("%b %d, %Y %H:%M"),
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
                try:
                    parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                except:
                    try:
                        parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                    except:
                        parsed_date = datetime.now()

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
                try:
                    parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                except:
                    parsed_date = datetime.now()

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

    # Sort by date (newest first)
    unique_news.sort(key=lambda x: x.get("date", datetime.min), reverse=True)

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
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt

    if diff.days > 7:
        return dt.strftime("%b %d")
    elif diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "just now"
