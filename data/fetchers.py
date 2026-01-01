"""
Data fetching functions for various APIs
CoinGecko, Yahoo Finance, FRED, DefiLlama
"""
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import streamlit as st

# Cache timeout in seconds
CACHE_TTL = 300  # 5 minutes


@st.cache_data(ttl=CACHE_TTL)
def fetch_eth_price() -> Dict[str, Any]:
    """Fetch current ETH price from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "ethereum",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "price": data["ethereum"]["usd"],
            "change_24h": data["ethereum"].get("usd_24h_change", 0),
            "market_cap": data["ethereum"].get("usd_market_cap", 0),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "price": None}


@st.cache_data(ttl=CACHE_TTL)
def fetch_eth_treasury_companies() -> List[Dict[str, Any]]:
    """Fetch ETH treasury company data from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/companies/public_treasury/ethereum"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("companies", [])
    except Exception as e:
        return []


@st.cache_data(ttl=CACHE_TTL)
def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price and basic info
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        # Get historical data for drawdown calculation
        hist = stock.history(period="1y")

        ath_1y = hist["High"].max() if not hist.empty else None
        drawdown = None
        if ath_1y and current_price:
            drawdown = (current_price - ath_1y) / ath_1y

        return {
            "ticker": ticker,
            "price": current_price,
            "market_cap": info.get("marketCap"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "pe_ratio": info.get("trailingPE"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "ath_1y": ath_1y,
            "drawdown_from_ath": drawdown,
            "volume": info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "name": info.get("shortName", ticker),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "price": None}


@st.cache_data(ttl=CACHE_TTL)
def fetch_stock_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch historical stock data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # 1 hour cache for FRED data
def fetch_fred_series(series_id: str, api_key: str, limit: int = 100) -> pd.DataFrame:
    """Fetch data from FRED API"""
    if not api_key:
        return pd.DataFrame()

    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        observations = data.get("observations", [])
        df = pd.DataFrame(observations)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df.sort_values("date")
        return df
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL)
def fetch_fed_balance_sheet(api_key: str) -> Dict[str, Any]:
    """Fetch Fed balance sheet (WALCL) from FRED"""
    df = fetch_fred_series("WALCL", api_key, limit=10)
    if df.empty:
        return {"error": "No data", "value": None}

    latest = df.iloc[-1]
    return {
        "value": latest["value"],
        "date": latest["date"].isoformat(),
        "unit": "Millions of Dollars",
    }


@st.cache_data(ttl=CACHE_TTL)
def fetch_treasury_general_account(api_key: str) -> Dict[str, Any]:
    """Fetch Treasury General Account (TGA) from FRED"""
    df = fetch_fred_series("WTREGEN", api_key, limit=10)
    if df.empty:
        return {"error": "No data", "value": None}

    latest = df.iloc[-1]
    return {
        "value": latest["value"],
        "date": latest["date"].isoformat(),
        "unit": "Millions of Dollars",
    }


@st.cache_data(ttl=CACHE_TTL)
def fetch_reverse_repo(api_key: str) -> Dict[str, Any]:
    """Fetch Reverse Repo (RRP) from FRED"""
    df = fetch_fred_series("RRPONTSYD", api_key, limit=10)
    if df.empty:
        return {"error": "No data", "value": None}

    latest = df.iloc[-1]
    return {
        "value": latest["value"],
        "date": latest["date"].isoformat(),
        "unit": "Billions of Dollars",
    }


@st.cache_data(ttl=CACHE_TTL)
def fetch_deficit_gdp_ratio(api_key: str) -> Dict[str, Any]:
    """Fetch US Deficit as % of GDP from FRED"""
    df = fetch_fred_series("FYFSGDA188S", api_key, limit=10)
    if df.empty:
        return {"error": "No data", "value": None}

    latest = df.iloc[-1]
    return {
        "value": latest["value"],
        "date": latest["date"].isoformat(),
        "unit": "Percent of GDP",
    }


@st.cache_data(ttl=CACHE_TTL)
def fetch_defi_tvl() -> Dict[str, Any]:
    """Fetch DeFi TVL data from DefiLlama"""
    try:
        # Get all chains TVL
        url = "https://api.llama.fi/v2/chains"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        chains = response.json()

        # Calculate ETH dominance
        eth_tvl = 0
        total_tvl = 0

        for chain in chains:
            tvl = chain.get("tvl", 0)
            total_tvl += tvl
            if chain.get("name", "").lower() == "ethereum":
                eth_tvl = tvl

        # Get L2s TVL (Arbitrum, Optimism, Base, etc.)
        l2_names = ["arbitrum", "optimism", "base", "polygon", "zksync era", "linea", "scroll", "starknet"]
        l2_tvl = sum(
            chain.get("tvl", 0)
            for chain in chains
            if chain.get("name", "").lower() in l2_names
        )

        eth_ecosystem_tvl = eth_tvl + l2_tvl
        dominance = eth_ecosystem_tvl / total_tvl if total_tvl > 0 else 0

        return {
            "eth_l1_tvl": eth_tvl,
            "l2_tvl": l2_tvl,
            "eth_ecosystem_tvl": eth_ecosystem_tvl,
            "total_tvl": total_tvl,
            "eth_dominance": dominance,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=CACHE_TTL)
def fetch_eth_staking_stats() -> Dict[str, Any]:
    """Fetch ETH staking statistics from Beaconcha.in API"""
    try:
        # Using DefiLlama for staking data as a fallback
        url = "https://api.llama.fi/protocol/lido"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Lido is the largest staking provider, use as proxy
        lido_tvl = data.get("tvl", [])[-1].get("totalLiquidityUSD", 0) if data.get("tvl") else 0

        # Approximate staking yield (this should ideally come from rated.network)
        # Using a placeholder - in production, integrate with rated.network API
        estimated_apy = 0.035  # 3.5% approximate

        return {
            "lido_tvl_usd": lido_tvl,
            "estimated_apy": estimated_apy,
            "timestamp": datetime.now().isoformat(),
            "note": "APY is estimated. Integrate rated.network for accurate data.",
        }
    except Exception as e:
        return {"error": str(e), "estimated_apy": None}


@st.cache_data(ttl=CACHE_TTL)
def fetch_dxy() -> Dict[str, Any]:
    """Fetch DXY (Dollar Index) from Yahoo Finance"""
    try:
        dxy = yf.Ticker("DX-Y.NYB")
        info = dxy.info
        hist = dxy.history(period="5d")

        current = hist["Close"].iloc[-1] if not hist.empty else None

        return {
            "value": current,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "value": None}


def fetch_all_dat_stocks(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch stock data for all DAT companies"""
    results = {}
    for ticker in tickers:
        results[ticker] = fetch_stock_data(ticker)
    return results


def calculate_net_liquidity(fed_bs: float, tga: float, rrp: float) -> float:
    """
    Calculate net liquidity: Fed Balance Sheet - TGA - RRP
    All values should be in the same unit (billions)
    """
    return fed_bs - tga - rrp
