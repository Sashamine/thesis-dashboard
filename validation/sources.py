"""
Data Validation Sources
Maps each data field to authoritative sources for verification
"""

# Authoritative sources for each data type
DATA_SOURCES = {
    # BTC Holdings
    "btc_holdings": {
        "primary": "bitcointreasuries.net",
        "secondary": ["company 8-K filings", "company investor relations"],
        "mstr_specific": "strategy.com/purchases",
    },

    # ETH Holdings
    "eth_holdings": {
        "primary": "company 8-K/10-Q filings",
        "secondary": ["etherscan.io (if wallet known)", "press releases"],
    },

    # Stock Data (price, market cap, shares outstanding)
    "stock_data": {
        "primary": "Yahoo Finance API",
        "secondary": ["Google Finance", "company 10-Q"],
    },

    # Crypto Prices
    "crypto_prices": {
        "primary": "CoinGecko API",
        "secondary": ["CoinMarketCap", "exchange APIs"],
    },

    # Burn Rate / Operating Costs
    "burn_rate": {
        "primary": "company 10-Q/10-K filings",
        "notes": "Use 'Total Operating Expenses' or 'Cash used in operations'",
    },

    # Staking Data
    "staking_apy": {
        "eth": "beaconcha.in or rated.network",
        "sol": "solanabeach.io or Marinade stats",
        "general": "stakingrewards.com",
    },

    # Preferred Dividends (STRK/STRF)
    "preferred_dividends": {
        "primary": "SEC S-3 filing (offering docs)",
        "secondary": "company investor relations",
    },

    # Mining Production
    "btc_mined": {
        "primary": "company monthly production reports",
        "secondary": "8-K filings",
    },
}

# Validation rules for each field
VALIDATION_RULES = {
    "holdings": {
        "max_age_days": 30,  # Re-verify monthly
        "tolerance_pct": 5,  # Flag if >5% different from source
    },
    "burn_rate": {
        "max_age_days": 90,  # Re-verify quarterly (after 10-Q)
        "tolerance_pct": 10,
    },
    "stock_data": {
        "max_age_days": 1,  # Daily refresh
        "tolerance_pct": 1,
    },
    "crypto_prices": {
        "max_age_days": 0,  # Real-time
        "tolerance_pct": 1,
    },
}

# Company-specific source URLs
COMPANY_SOURCES = {
    "MSTR": {
        "holdings": "https://www.strategy.com/purchases",
        "filings": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001050446",
        "ir": "https://www.strategy.com/investor-relations",
    },
    "MARA": {
        "holdings": "https://ir.mara.com/",
        "production": "https://ir.mara.com/news-events/press-releases",
        "filings": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001507605",
    },
    "RIOT": {
        "filings": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001167419",
        "ir": "https://www.riotplatforms.com/investors",
    },
    # Add more as needed
}
