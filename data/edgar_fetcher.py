"""
SEC EDGAR data fetcher for DAT companies
Fetches recent SEC filings (10-K, 10-Q, 8-K, etc.)
"""
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st

# SEC requires a User-Agent header with contact info
HEADERS = {
    "User-Agent": "ThesisDashboard contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}

# CIK numbers for DAT companies (10-digit padded)
# These need to be looked up from SEC EDGAR
DAT_COMPANY_CIKS = {
    "BMNR": None,  # Bitmine Immersion - needs lookup
    "SBET": "0001784851",  # SharpLink Gaming
    "ETHM": None,  # The Ether Machine - needs lookup
    "BTBT": "0001799290",  # Bit Digital
    "BTCS": "0001436229",  # BTCS Inc.
    "ETHZ": None,  # ETHZilla - needs lookup
    "GAME": "0001845419",  # GameSquare Holdings
    "FGNX": "0001527352",  # Fundamental Global
}

# Filing types we care about
RELEVANT_FILING_TYPES = [
    "10-K",      # Annual report
    "10-Q",      # Quarterly report
    "8-K",       # Current report (material events)
    "4",         # Insider trading
    "SC 13D",    # Beneficial ownership >5%
    "SC 13G",    # Beneficial ownership (passive)
    "S-1",       # Registration statement
    "S-3",       # Shelf registration
    "424B",      # Prospectus
    "DEF 14A",   # Proxy statement
]


def lookup_cik_by_ticker(ticker: str) -> Optional[str]:
    """Look up CIK number by ticker symbol"""
    try:
        url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": ticker,
            "type": "",
            "dateb": "",
            "owner": "include",
            "count": "1",
            "output": "atom",
        }
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            # Parse the atom feed to extract CIK
            content = response.text
            if "cik=" in content.lower():
                import re
                match = re.search(r'cik=(\d+)', content.lower())
                if match:
                    return match.group(1).zfill(10)
        return None
    except Exception as e:
        return None


@st.cache_data(ttl=3600)  # 1 hour cache
def fetch_company_filings(cik: str, count: int = 10) -> List[Dict[str, Any]]:
    """Fetch recent SEC filings for a company by CIK"""
    if not cik:
        return []

    try:
        # SEC EDGAR API endpoint
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        data = response.json()

        filings = []
        recent = data.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_documents = recent.get("primaryDocument", [])
        descriptions = recent.get("primaryDocDescription", [])

        company_name = data.get("name", "")

        for i in range(min(count * 3, len(forms))):  # Get more to filter
            form_type = forms[i] if i < len(forms) else ""

            # Filter to relevant filing types
            if not any(form_type.startswith(ft) for ft in RELEVANT_FILING_TYPES):
                continue

            filing_date = filing_dates[i] if i < len(filing_dates) else ""
            accession = accession_numbers[i] if i < len(accession_numbers) else ""
            primary_doc = primary_documents[i] if i < len(primary_documents) else ""
            description = descriptions[i] if i < len(descriptions) else ""

            # Build filing URL
            accession_clean = accession.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_clean}/{primary_doc}"

            # Parse date
            try:
                parsed_date = datetime.strptime(filing_date, "%Y-%m-%d")
            except:
                parsed_date = datetime.now()

            filings.append({
                "company": company_name,
                "form_type": form_type,
                "filing_date": filing_date,
                "date": parsed_date,
                "date_str": parsed_date.strftime("%b %d, %Y"),
                "description": description or form_type,
                "url": filing_url,
                "accession": accession,
            })

            if len(filings) >= count:
                break

        return filings
    except Exception as e:
        return []


@st.cache_data(ttl=3600)
def fetch_all_dat_filings(count_per_company: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent SEC filings for all DAT companies"""
    all_filings = []

    for ticker, cik in DAT_COMPANY_CIKS.items():
        if not cik:
            # Try to look up CIK
            cik = lookup_cik_by_ticker(ticker)
            if cik:
                DAT_COMPANY_CIKS[ticker] = cik

        if cik:
            filings = fetch_company_filings(cik, count_per_company)
            for filing in filings:
                filing["ticker"] = ticker
            all_filings.extend(filings)

    # Sort by date (newest first)
    all_filings.sort(key=lambda x: x.get("date", datetime.min), reverse=True)

    return all_filings


@st.cache_data(ttl=3600)
def fetch_company_edgar(ticker: str, count: int = 10) -> List[Dict[str, Any]]:
    """Fetch SEC filings for a specific company by ticker"""
    cik = DAT_COMPANY_CIKS.get(ticker)

    if not cik:
        cik = lookup_cik_by_ticker(ticker)
        if cik:
            DAT_COMPANY_CIKS[ticker] = cik

    if not cik:
        return []

    filings = fetch_company_filings(cik, count)
    for filing in filings:
        filing["ticker"] = ticker

    return filings


def get_filing_type_description(form_type: str) -> str:
    """Get human-readable description of filing type"""
    descriptions = {
        "10-K": "Annual Report",
        "10-Q": "Quarterly Report",
        "8-K": "Current Report (Material Event)",
        "4": "Insider Trading Report",
        "SC 13D": "Beneficial Ownership (>5%)",
        "SC 13G": "Beneficial Ownership (Passive)",
        "S-1": "IPO Registration",
        "S-3": "Shelf Registration",
        "424B": "Prospectus",
        "DEF 14A": "Proxy Statement",
    }

    for key, desc in descriptions.items():
        if form_type.startswith(key):
            return desc

    return form_type


def get_filing_type_emoji(form_type: str) -> str:
    """Get emoji for filing type"""
    if form_type.startswith("10-K"):
        return "📊"
    elif form_type.startswith("10-Q"):
        return "📈"
    elif form_type.startswith("8-K"):
        return "⚡"
    elif form_type == "4":
        return "👤"
    elif form_type.startswith("SC 13"):
        return "🏦"
    elif form_type.startswith("S-"):
        return "📝"
    elif form_type.startswith("424"):
        return "📄"
    elif form_type.startswith("DEF"):
        return "🗳️"
    return "📋"
