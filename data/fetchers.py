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
import time

# Cache timeout in seconds
CACHE_TTL = 300  # 5 minutes
STOCK_CACHE_TTL = 900  # 15 minutes for stock data (reduce Yahoo API calls)

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


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


def _fetch_from_yahoo(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data from Yahoo Finance"""
    for attempt in range(MAX_RETRIES):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Check if we got valid data (Yahoo returns empty dict on rate limit)
            if not info or len(info) < 5:
                raise Exception("Empty response - possible rate limit")

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not current_price:
                raise Exception("No price data")

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
                "source": "yahoo",
            }
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            continue
    return None


def _fetch_from_alpha_vantage(ticker: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data from Alpha Vantage (free: 25 calls/day)"""
    if not api_key:
        return None

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check for rate limit or error
        if "Note" in data or "Error Message" in data:
            return None

        quote = data.get("Global Quote", {})
        if not quote:
            return None

        price = float(quote.get("05. price", 0))
        if not price:
            return None

        return {
            "ticker": ticker,
            "price": price,
            "market_cap": None,  # Not available in free tier
            "shares_outstanding": None,
            "pe_ratio": None,
            "52w_high": float(quote.get("03. high", 0)) or None,
            "52w_low": float(quote.get("04. low", 0)) or None,
            "ath_1y": None,
            "drawdown_from_ath": None,
            "volume": int(quote.get("06. volume", 0)) or None,
            "avg_volume": None,
            "name": ticker,
            "timestamp": datetime.now().isoformat(),
            "source": "alpha_vantage",
        }
    except Exception:
        return None


def _fetch_from_fmp(ticker: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data from Financial Modeling Prep (free: 250 calls/day)"""
    if not api_key:
        return None

    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}"
        params = {"apikey": api_key}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data or isinstance(data, dict) and "Error" in str(data):
            return None

        quote = data[0] if isinstance(data, list) and len(data) > 0 else None
        if not quote:
            return None

        price = quote.get("price", 0)
        if not price:
            return None

        return {
            "ticker": ticker,
            "price": price,
            "market_cap": quote.get("marketCap"),
            "shares_outstanding": quote.get("sharesOutstanding"),
            "pe_ratio": quote.get("pe"),
            "52w_high": quote.get("yearHigh"),
            "52w_low": quote.get("yearLow"),
            "ath_1y": quote.get("yearHigh"),
            "drawdown_from_ath": (price - quote.get("yearHigh", price)) / quote.get("yearHigh", price) if quote.get("yearHigh") else None,
            "volume": quote.get("volume"),
            "avg_volume": quote.get("avgVolume"),
            "name": quote.get("name", ticker),
            "timestamp": datetime.now().isoformat(),
            "source": "fmp",
        }
    except Exception:
        return None


@st.cache_data(ttl=STOCK_CACHE_TTL)
def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch stock data with automatic fallback between sources"""
    from config import ALPHA_VANTAGE_KEY, FMP_API_KEY

    # Try sources in order: Yahoo -> FMP -> Alpha Vantage
    sources = [
        ("yahoo", lambda: _fetch_from_yahoo(ticker)),
        ("fmp", lambda: _fetch_from_fmp(ticker, FMP_API_KEY)),
        ("alpha_vantage", lambda: _fetch_from_alpha_vantage(ticker, ALPHA_VANTAGE_KEY)),
    ]

    errors = []
    for source_name, fetch_func in sources:
        try:
            result = fetch_func()
            if result and result.get("price"):
                return result
            errors.append(f"{source_name}: no data")
        except Exception as e:
            errors.append(f"{source_name}: {str(e)}")

    # All sources failed
    return {
        "ticker": ticker,
        "error": f"All sources failed: {'; '.join(errors)}",
        "price": None,
        "rate_limited": True,
    }


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
        # Try beaconcha.in API first for accurate staking APR
        try:
            url = "https://beaconcha.in/api/v1/ethstore/latest"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    apr = data.get("data", {}).get("apr", 0.035)
                    return {
                        "estimated_apy": apr,
                        "source": "beaconcha.in",
                        "timestamp": datetime.now().isoformat(),
                    }
        except:
            pass

        # Fallback: Using DefiLlama for Lido data
        url = "https://api.llama.fi/protocol/lido"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Lido is the largest staking provider, use as proxy
        lido_tvl = data.get("tvl", [])[-1].get("totalLiquidityUSD", 0) if data.get("tvl") else 0

        # Current ETH staking yield is approximately 3-4%
        estimated_apy = 0.035  # 3.5% approximate

        return {
            "lido_tvl_usd": lido_tvl,
            "estimated_apy": estimated_apy,
            "source": "estimated",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "estimated_apy": 0.035}


@st.cache_data(ttl=CACHE_TTL)
def fetch_eth_burn_stats() -> Dict[str, Any]:
    """Fetch ETH burn statistics from ultrasound.money API"""
    try:
        # ultrasound.money API endpoint
        url = "https://ultrasound.money/api/v2/fees/eth-burn-total"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            total_burn_wei = data.get("ethBurnSum", 0)
            total_burn_eth = total_burn_wei / 1e18 if total_burn_wei else 0

            return {
                "total_burned_eth": total_burn_eth,
                "source": "ultrasound.money",
                "timestamp": datetime.now().isoformat(),
            }

        # Fallback: fetch from alternative source
        # Using approximate values based on known data
        return {
            "total_burned_eth": 4_500_000,  # ~4.5M ETH burned since EIP-1559
            "daily_burn_rate": 2_000,  # ~2000 ETH/day average
            "annual_burn_rate": 730_000,  # ~730K ETH/year
            "source": "estimated",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_burned_eth": 4_500_000,
            "daily_burn_rate": 2_000,
            "source": "fallback",
        }


@st.cache_data(ttl=CACHE_TTL)
def fetch_eth_supply_stats() -> Dict[str, Any]:
    """Fetch ETH supply and issuance statistics"""
    try:
        # Try ultrasound.money for supply data
        url = "https://ultrasound.money/api/v2/fees/supply-parts"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "total_supply": data.get("supply", 120_000_000),
                "staked_eth": data.get("staked", 34_000_000),
                "staking_ratio": data.get("staked", 34_000_000) / data.get("supply", 120_000_000),
                "source": "ultrasound.money",
                "timestamp": datetime.now().isoformat(),
            }

        # Fallback values based on known data
        return {
            "total_supply": 120_690_000,  # ~120.69M ETH
            "staked_eth": 34_000_000,  # ~34M ETH staked
            "staking_ratio": 0.282,  # ~28.2% staked
            "daily_issuance": 1_500,  # ~1.5K ETH/day post-merge
            "annual_issuance": 547_500,  # ~547.5K ETH/year
            "source": "estimated",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_supply": 120_690_000,
            "staked_eth": 34_000_000,
            "staking_ratio": 0.282,
            "source": "fallback",
        }


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
