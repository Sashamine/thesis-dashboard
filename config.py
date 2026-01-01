"""
Configuration for Thesis Tracking Dashboard
Contains API keys, thresholds, DAT definitions, and thesis taxonomy
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (set these in .env file, environment variables, or Streamlit secrets)
def get_api_key(key_name: str, default: str = "") -> str:
    """Get API key from environment or Streamlit secrets"""
    # First try environment variable
    value = os.getenv(key_name, "")
    if value:
        return value

    # Then try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass

    return default

FRED_API_KEY = get_api_key("FRED_API_KEY")
ALPHA_VANTAGE_KEY = get_api_key("ALPHA_VANTAGE_KEY")  # Free: 25 calls/day
FMP_API_KEY = get_api_key("FMP_API_KEY")  # Free: 250 calls/day

# Edwin's Personal Positions
PERSONAL_POSITIONS = {
    "BMNR": {"shares": 10000, "cost_basis": None},
    "SBET": {"shares": 10000, "cost_basis": None},
    "ETH": {"amount": None, "cost_basis": None},  # Update with actual holdings
}

# Personal Timeline
PERSONAL_MILESTONES = {
    "wedding": "2026-06-01",  # Update with actual date
    "family_planning": "2027-06-01",  # Q2-Q3 2027
}

# Staking ETF benchmark
# ETHE (2.5% fee): Net yield ~0% or negative (fees exceed staking rewards)
# ETH Mini Trust (0.15% fee): Net yield ~3.2% (best case for retail)
# Using Mini Trust as benchmark - if DATs can't beat this, not worth the complexity
ETF_STAKING_YIELD = 0.032  # 3.2% - Grayscale ETH Mini Trust net yield after 0.15% fee

# DAT Company Definitions
# Burn rates from latest 10-Q/10-K filings (quarterly opex in USD)
# Premium issuance methodology:
#   ETH from Premium = Capital Raised × (Avg Premium / (1 + Avg Premium)) / ETH Price
#   Assumes: ATM 20%, PIPE 25%, Converts 10%, small caps 5-10%
#   Testable: If ETH/share grows faster than staking yield, premium capture is working
# dat_start_date: When company pivoted to DAT strategy (for annualizing premium capture)
DAT_COMPANIES = {
    # Tier 1: Major Players (>100k ETH)
    "BMNR": {
        "name": "Bitmine Immersion",
        "ticker": "BMNR",
        "tier": 1,
        "dat_start_date": "2025-07-01",  # Pivoted to DAT strategy July 2025
        "eth_holdings": 4_066_000,  # Dec 21, 2025 per press release
        "staking_pct": 0.85,  # 85% staked via MAVAN validators
        "staking_method": "MAVAN validators",
        "quarterly_burn_usd": 2_500_000,  # ~$2.5M/quarter opex from 10-Q
        "burn_source": "Q3 2025 10-Q",
        # Premium issuance: $10B ATM + $615M PIPE per Kerrisdale analysis
        # ATM: $10B × (0.20/1.20) / $3,500 = 476K ETH
        # PIPE: $615M × (0.25/1.25) / $3,500 = 35K ETH
        "capital_raised_atm": 10_000_000_000,
        "capital_raised_pipe": 615_000_000,
        "avg_issuance_premium": 0.20,  # Normalized: high early, discount now
        "eth_from_premium": 510_000,  # 476K + 35K from premium capture
        "leader": "Tom Lee (Fundstrat)",
        "strategy": "5% of ETH supply goal, staking, MAVAN validators Q1 2026",
        "shares_outstanding": None,
        "notes": "Largest ETH treasury. NAV ~$30/share. Trades at 0.8x book. $24.5B ATM capacity.",
    },
    "SBET": {
        "name": "SharpLink Gaming",
        "ticker": "SBET",
        "tier": 1,
        "dat_start_date": "2025-05-01",  # First major ETH acquisition May 2025
        "eth_holdings": 860_000,  # Oct 2025: 859,853 ETH per press release
        "staking_pct": 0.95,  # 95% staked via Linea/Lido
        "staking_method": "Linea/Lido",
        "quarterly_burn_usd": 2_850_000,  # ~$2.85M/quarter (TTM opex ~$11.4M)
        "burn_source": "Q3 2025 10-Q - verify, user reports may be higher",
        # Premium issuance: ~$2.6B total (ATM/RD + PIPE) per Q2 2025 report
        # ATM/RD: $2B × (0.15/1.15) / $3,500 = 74K ETH
        # PIPE: $600M × (0.20/1.20) / $3,500 = 29K ETH
        "capital_raised_atm": 2_000_000_000,
        "capital_raised_pipe": 600_000_000,
        "avg_issuance_premium": 0.15,  # More disciplined issuance
        "eth_from_premium": 103_000,  # 74K + 29K from premium capture
        "leader": "Joe Lubin (Ethereum co-founder)",
        "strategy": "Staking, Linea partnership, tokenized equity via Superstate",
        "shares_outstanding": None,
        "notes": "#2 ETH treasury. $1.5B buyback program. Trades at ~0.83x mNAV.",
    },
    "ETHM": {
        "name": "The Ether Machine",
        "ticker": "ETHM",
        "tier": 1,
        "dat_start_date": "2025-10-01",  # SPAC merger announced Oct 2025
        "eth_holdings": 495_362,  # Per CoinGecko/company data
        "staking_pct": 1.0,  # 100% staked - "fully staked treasury"
        "staking_method": "Native staking",
        "quarterly_burn_usd": 800_000,  # ~$800K/quarter (lean ops)
        "burn_source": "S-4 Filing 2025",
        # SPAC merger with Dynamix - no ATM premium issuance
        "capital_raised_atm": 0,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0,
        "eth_from_premium": 0,  # N/A - SPAC merger structure
        "leader": "Andrew Keys",
        "strategy": "DeFi/staking 'machine' to grow ETH",
        "shares_outstanding": None,
        "notes": "SPAC merger with Dynamix (ETHM). Trades at 24% premium. 3rd largest ETH treasury.",
    },
    "BTBT": {
        "name": "Bit Digital",
        "ticker": "BTBT",
        "tier": 1,
        "dat_start_date": "2025-01-01",  # Pivoted from BTC mining to ETH staking Jan 2025
        "eth_holdings": 154_000,  # Oct 2025: 153,547 ETH per monthly report
        "staking_pct": 0.86,  # 86.3% staked per Oct report
        "staking_method": "Native staking",
        "quarterly_burn_usd": 8_500_000,  # ~$8.5M/quarter (mining + staking ops)
        "burn_source": "Q3 2025 10-Q",
        # $150M converts at 8.2% + $172M public offering
        # Converts: $150M × (0.08/1.08) / $3,500 = 3.2K ETH
        # Offering: $172M × (0.15/1.15) / $3,500 = 6.4K ETH
        "capital_raised_atm": 172_000_000,
        "capital_raised_converts": 150_000_000,
        "avg_issuance_premium": 0.10,  # Blended converts + offering
        "eth_from_premium": 9_500,  # 3.2K + 6.4K from premium capture
        "leader": "Sam Tabar",
        "strategy": "86% staked, fully exited BTC. Avg cost $3,045/ETH.",
        "shares_outstanding": None,
        "notes": "Staking yield ~2.93% annualized. mNAV $3.84/share (Sep 2025).",
    },
    # Tier 2: Mid-Size (10k-100k ETH)
    "ETHZ": {
        "name": "ETHZilla",
        "ticker": "ETHZ",
        "tier": 2,
        "dat_start_date": "2024-07-01",  # Early DAT, now pivoting away
        "eth_holdings": 69_802,  # Dec 2025 - sold 24,291 ETH ($74.5M) to pay down debt
        "staking_pct": 0.80,  # Estimated 80% staked
        "staking_method": "Native staking",
        "quarterly_burn_usd": 1_200_000,  # ~$1.2M/quarter
        "burn_source": "Q3 2025 10-Q",
        # SELLING ETH, not issuing at premium - pivoting away from DAT
        "capital_raised_atm": 0,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0,
        "eth_from_premium": 0,  # Actually sold $114.5M ETH (Oct+Dec)
        "leader": "Peter Thiel backed",
        "strategy": "Pivoting to RWA tokenization, sold ETH for debt paydown & buybacks",
        "shares_outstanding": None,
        "notes": "Sold $40M ETH (Oct) + $74.5M ETH (Dec). Stock down 96% from Aug highs. Discontinued mNAV dashboard.",
    },
    "BTCS": {
        "name": "BTCS Inc.",
        "ticker": "BTCS",
        "tier": 2,
        "dat_start_date": "2024-01-01",  # One of earliest DATs
        "eth_holdings": 70_000,
        "staking_pct": 0.75,  # 75% staked via Builder+
        "staking_method": "Builder+ validators",
        "quarterly_burn_usd": 1_800_000,  # ~$1.8M/quarter
        "burn_source": "Q3 2025 10-Q",
        # Smaller company, estimate ~$60M raised at 10% avg premium
        "capital_raised_atm": 60_000_000,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0.10,
        "eth_from_premium": 1_600,  # $60M × (0.10/1.10) / $3,500
        "leader": "",
        "strategy": "ETH 'Bividend,' DeFi/TradFi flywheel, Builder+",
        "shares_outstanding": None,
        "notes": "",
    },
    "GAME": {
        "name": "GameSquare",
        "ticker": "GAME",
        "tier": 2,
        "dat_start_date": "2024-10-01",  # Started ETH strategy Oct 2024
        "eth_holdings": 10_000,
        "staking_pct": 0.50,  # Estimated 50% - newer to ETH
        "staking_method": "Lido/stETH",
        "quarterly_burn_usd": 12_000_000,  # ~$12M/quarter (esports/gaming ops)
        "burn_source": "Q3 2025 10-Q",
        # Small ETH position, estimate ~$30M raised at 5% avg premium
        "capital_raised_atm": 30_000_000,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0.05,
        "eth_from_premium": 400,  # $30M × (0.05/1.05) / $3,500
        "leader": "",
        "strategy": "$250M authorization for more",
        "shares_outstanding": None,
        "notes": "High burn rate relative to ETH holdings.",
    },
    "FGNX": {
        "name": "Fundamental Global",
        "ticker": "FGNX",
        "tier": 2,
        "dat_start_date": "2024-09-01",  # Started ETH strategy Sep 2024
        "eth_holdings": 6_000,
        "staking_pct": 0.60,  # Estimated 60%
        "staking_method": "Lido/stETH",
        "quarterly_burn_usd": 2_000_000,  # ~$2M/quarter (insurance ops)
        "burn_source": "Q3 2025 10-Q",
        # Smallest position, estimate ~$20M raised at 5% avg premium
        "capital_raised_atm": 20_000_000,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0.05,
        "eth_from_premium": 270,  # $20M × (0.05/1.05) / $3,500
        "leader": "",
        "strategy": "Insurance/reinsurance pivot",
        "shares_outstanding": None,
        "notes": "",
    },
}

# Solana DAT Companies (for tracking/news only)
# Burn rates from 10-Q/10-K filings (quarterly opex in USD)
# Premium methodology: Capital Raised × (Avg Premium / (1 + Avg Premium)) / SOL Price
SOL_DAT_COMPANIES = {
    "FWDI": {
        "name": "Forward Industries",
        "ticker": "FWDI",
        "tier": 1,
        "dat_start_date": "2025-04-01",  # Pivot announced ~Q2 2025
        "holdings": 6_921_342,  # Dec 2025
        "asset": "SOL",
        "cost_basis_avg": 232.08,  # per SOL
        "staking_pct": 0.99,  # Nearly all staked
        "staking_apy": 0.07,  # 6.82-7.01% gross APY
        "quarterly_burn_usd": 3_400_000,  # ~$13.6M annual opex / 4
        "burn_source": "FY 2025 10-K",
        # Premium issuance: $1.65B PIPE at premium
        "capital_raised_atm": 0,
        "capital_raised_pipe": 1_650_000_000,
        "avg_issuance_premium": 0.25,  # PIPE typically at 20-30% premium
        "sol_from_premium": 2_640_000,  # $1.65B × (0.25/1.25) / $125
        "leader": "Galaxy, Jump Crypto, Multicoin backed",
        "strategy": "World's largest SOL treasury, validator infrastructure",
        "notes": "Raised $1.65B PIPE. Debt free. Changed ticker from FORD to FWDI.",
    },
    "HSDT": {
        "name": "Solana Company (fka Helius Medical)",
        "ticker": "HSDT",
        "tier": 1,
        "dat_start_date": "2025-05-01",
        "holdings": 2_200_000,  # Oct 2025 estimate
        "asset": "SOL",
        "cost_basis_avg": 227.00,
        "staking_pct": 0.95,
        "staking_apy": 0.065,
        "quarterly_burn_usd": 12_000_000,  # $36M Q3 opex (includes bonuses)
        "burn_source": "Q3 2025 10-Q - inflated by PIPE costs",
        "capital_raised_atm": 0,
        "capital_raised_pipe": 500_000_000,
        "avg_issuance_premium": 0.20,
        "sol_from_premium": 667_000,  # $500M × (0.20/1.20) / $125
        "leader": "Pantera Capital, Summer Capital",
        "strategy": "SOL treasury via Anchorage Digital custody",
        "notes": "Raised $500M. Partnered with Solana Foundation for discounted SOL.",
    },
    "DFDV": {
        "name": "DeFi Development Corp",
        "ticker": "DFDV",
        "tier": 1,
        "dat_start_date": "2025-04-01",
        "holdings": 2_195_926,  # Oct 2025
        "asset": "SOL",
        "cost_basis_avg": 110.00,
        "staking_pct": 0.90,
        "staking_apy": 0.114,  # 11.4% organic yield reported
        "quarterly_burn_usd": 1_500_000,  # ~$6M annual (lean ops)
        "burn_source": "Q3 2025 10-Q estimate",
        # Has $5B ELOC for future raises
        "capital_raised_atm": 200_000_000,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0.15,
        "sol_from_premium": 209_000,  # $200M × (0.15/1.15) / $125
        "leader": "Formerly Janover Inc.",
        "strategy": "First US public company with SOL-focused treasury. Target 1 SPS by Dec 2028.",
        "notes": "$5B ELOC. $4.6M quarterly revenue. Validator operations.",
    },
    "UPXI": {
        "name": "Upexi",
        "ticker": "UPXI",
        "tier": 1,
        "dat_start_date": "2025-04-01",
        "holdings": 2_106_989,  # Oct 2025
        "asset": "SOL",
        "cost_basis_avg": 157.66,
        "staking_pct": 0.95,
        "staking_apy": 0.08,  # ~8% yield
        "quarterly_burn_usd": 2_500_000,  # Consumer brands ops + treasury
        "burn_source": "Q1 2026 10-Q",
        "capital_raised_atm": 100_000_000,
        "capital_raised_pipe": 200_000_000,
        "avg_issuance_premium": 0.15,
        "sol_from_premium": 313_000,  # $300M × (0.15/1.15) / $125
        "leader": "Arthur Hayes (advisory)",
        "strategy": "SOL treasury + consumer brands (Cure Mushrooms, Lucky Tail)",
        "notes": "42% locked SOL at mid-teens discount. $50M buyback approved Nov 2025.",
    },
    "HODL": {
        "name": "Sol Strategies",
        "ticker": "HODL",  # CSE: HODL, NASDAQ: STKE
        "tier": 2,
        "dat_start_date": "2024-06-01",  # Earlier than US companies
        "holdings": 526_637,  # Nov 2025
        "asset": "SOL",
        "cost_basis_avg": 130.00,
        "staking_pct": 0.85,
        "staking_apy": 0.065,
        "quarterly_burn_usd": 1_200_000,  # Canadian small cap ops
        "burn_source": "FY 2025 annual report",
        "capital_raised_atm": 50_000_000,
        "capital_raised_pipe": 0,
        "avg_issuance_premium": 0.10,
        "sol_from_premium": 36_000,  # $50M × (0.10/1.10) / $125
        "leader": "Canadian company",
        "strategy": "Validator operations, staking provider for VanEck Solana ETF",
        "notes": "3.7M SOL delegated. Selected as VanEck staking provider Nov 2025.",
    },
}

# Hyperliquid DAT Companies (for tracking/news only)
# Premium methodology: Capital Raised × (Avg Premium / (1 + Avg Premium)) / HYPE Price
HYPE_DAT_COMPANIES = {
    "PURR": {
        "name": "Hyperliquid Strategies",
        "ticker": "PURR",
        "tier": 1,
        "dat_start_date": "2025-12-01",  # Merger closed Dec 2025
        "holdings": 12_600_000,  # Dec 2025 merger close
        "asset": "HYPE",
        "cost_basis_avg": 46.27,  # $583M / 12.6M
        "staking_pct": 0.80,
        "staking_apy": 0.05,
        "quarterly_burn_usd": 2_000_000,  # New company, lean ops + Sonnet legacy
        "burn_source": "Estimate - just launched Dec 2025",
        # SPAC merger - no traditional ATM premium, but got HYPE via deal structure
        "capital_raised_atm": 0,
        "capital_raised_pipe": 583_000_000,  # $583M in HYPE contribution
        "avg_issuance_premium": 0.10,  # SPAC deals typically have modest premium
        "hype_from_premium": 2_120_000,  # Estimate based on deal structure
        "leader": "David Schamis (CEO), Bob Diamond (Board)",
        "strategy": "HYPE treasury via Sonnet merger. Staking + yield optimization.",
        "notes": "Merged with Sonnet Dec 2025. $888M combined assets. $30M buyback.",
    },
    "HYPD": {
        "name": "Hyperion DeFi (fka Eyenovia)",
        "ticker": "HYPD",
        "tier": 2,
        "dat_start_date": "2025-07-01",  # Rebranded Jul 2025
        "holdings": 1_712_195,  # Sep 2025
        "asset": "HYPE",
        "cost_basis_avg": 38.25,
        "staking_pct": 0.90,
        "staking_apy": 0.05,
        "quarterly_burn_usd": 1_500_000,  # Small biotech pivot
        "burn_source": "Q2 2025 10-Q estimate",
        "capital_raised_atm": 0,
        "capital_raised_pipe": 50_000_000,
        "avg_issuance_premium": 0.15,
        "hype_from_premium": 260_000,  # $50M × (0.15/1.15) / $25
        "leader": "First US public HYPE treasury",
        "strategy": "Validator node via Kinetiq. Aims to be largest HYPE holder.",
        "notes": "Raised $50M PIPE. Rebranded from Eyenovia Jul 2025.",
    },
}

# BNB DAT Companies (for tracking/news only)
# Premium methodology: Capital Raised × (Avg Premium / (1 + Avg Premium)) / BNB Price
BNB_DAT_COMPANIES = {
    "BNC": {
        "name": "BNB Network Company (CEA Industries)",
        "ticker": "BNC",
        "tier": 1,
        "dat_start_date": "2025-06-01",
        "holdings": 500_000,  # Dec 2025
        "asset": "BNB",
        "cost_basis_avg": 870.00,  # ~$435M for 500K per filing
        "staking_pct": 0.50,
        "staking_apy": 0.03,
        "quarterly_burn_usd": 3_000_000,  # Treasury ops + legacy CEA
        "burn_source": "FY Q2 2026 10-Q estimate",
        "capital_raised_atm": 0,
        "capital_raised_pipe": 500_000_000,
        "avg_issuance_premium": 0.20,
        "bnb_from_premium": 119_000,  # $500M × (0.20/1.20) / $700
        "leader": "YZi Labs (CZ family office) backed",
        "strategy": "Target 1% of BNB supply. Largest corporate BNB holder.",
        "notes": "$500M PIPE closed. YZi Labs owns 7% seeking board control. Rights plan adopted Dec 2025.",
    },
    "WINT": {
        "name": "Windtree Therapeutics",
        "ticker": "WINT",
        "tier": 2,
        "dat_start_date": "2025-08-01",
        "holdings": 100_000,  # Estimated from $520M commitment
        "asset": "BNB",
        "cost_basis_avg": 650.00,
        "staking_pct": 0.40,
        "staking_apy": 0.03,
        "quarterly_burn_usd": 4_000_000,  # Biopharma legacy ops
        "burn_source": "10-Q estimate - biopharma overhead",
        "capital_raised_atm": 0,
        "capital_raised_pipe": 520_000_000,  # $500M ELOC + $20M
        "avg_issuance_premium": 0.15,
        "bnb_from_premium": 97_000,  # $520M × (0.15/1.15) / $700
        "leader": "First US biopharma with BNB treasury",
        "strategy": "$520M commitment for BNB via Kraken custody",
        "notes": "$500M ELOC + $20M from Build & Build Corp. 99% for BNB acquisition.",
    },
    "NA": {
        "name": "Nano Labs",
        "ticker": "NA",
        "tier": 2,
        "dat_start_date": "2025-06-01",
        "holdings": 128_000,  # Jul 2025
        "asset": "BNB",
        "cost_basis_avg": 600.00,
        "staking_pct": 0.30,
        "staking_apy": 0.03,
        "quarterly_burn_usd": 5_000_000,  # HK chip design + Web3 ops
        "burn_source": "20-F estimate",
        "capital_raised_atm": 0,
        "capital_raised_converts": 500_000_000,
        "avg_issuance_premium": 0.05,  # Converts at lower premium
        "bnb_from_premium": 34_000,  # $500M × (0.05/1.05) / $700
        "leader": "Hong Kong Web3 infrastructure",
        "strategy": "BNB treasury via convertible notes",
        "notes": "Issued $500M convertible notes (interest-free, 360 days) Jun 2025.",
    },
}

# Bitcoin DAT Companies (the OG treasury strategy)
# Yield sources: Mining production (miners) or Premium issuance (treasury cos)
# BTC has no native staking - miners produce BTC, treasury cos capture premium
# Using btc_acquired_2025 for actual annual acquisition rate (more accurate than premium calc)
BTC_DAT_COMPANIES = {
    "MSTR": {
        "name": "Strategy (fka MicroStrategy)",
        "ticker": "MSTR",
        "tier": 1,
        "dat_start_date": "2024-01-01",  # Use 2024 as base - when 21/21 plan started
        "holdings": 672_497,  # Dec 29, 2025 - per strategy.com/purchases
        "asset": "BTC",
        "cost_basis_avg": 74_997,  # $50.44B / 672K BTC
        "is_miner": False,
        "btc_mined_annual": 0,  # Pure treasury, no mining
        # Actual 2025 acquisition - more accurate than premium calc
        "btc_acquired_2025": 257_000,  # Added ~257K BTC in 2025 (from ~415K to 672K)
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 15_000_000,  # Software biz + treasury ops
        "burn_source": "Q3 2025 10-Q",
        # Premium issuance tracking (for reference)
        "capital_raised_2025": 22_000_000_000,  # ~$22B raised in 2025 via ATM/converts
        "avg_issuance_premium": 0.50,  # Trades at ~2x NAV
        "btc_from_premium": 73_000,  # Estimate: $22B × (0.50/1.50) / $100K
        "leader": "Michael Saylor (Executive Chairman)",
        "strategy": "21/21 Plan: $21B equity + $21B debt for BTC. Rebranded to Strategy Feb 2025.",
        "notes": "672K BTC @ $75K avg. Trades at ~2x NAV. Largest corporate BTC holder.",
    },
    "MARA": {
        "name": "Marathon Digital",
        "ticker": "MARA",
        "tier": 1,
        "dat_start_date": "2024-01-01",
        "holdings": 44_893,  # Dec 2025 per bitcointreasuries.net
        "asset": "BTC",
        "cost_basis_avg": 43_000,
        "is_miner": True,
        "btc_mined_annual": 18_000,  # ~50 EH/s, ~1,500 BTC/month production
        "btc_acquired_2025": 22_000,  # Net additions in 2025 (mined + bought - sold)
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 85_000_000,  # Mining ops (power, hosting, depreciation)
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 4_000,  # From converts/ATM premium
        "leader": "Fred Thiel (CEO)",
        "strategy": "HODL miner - keeps all mined BTC. 50 EH/s hashrate.",
        "notes": "Largest US public miner. 'HODL' strategy. Zero-coupon converts.",
    },
    "RIOT": {
        "name": "Riot Platforms",
        "ticker": "RIOT",
        "tier": 1,
        "dat_start_date": "2024-01-01",
        "holdings": 17_722,  # Dec 2025
        "asset": "BTC",
        "cost_basis_avg": 39_000,
        "is_miner": True,
        "btc_mined_annual": 6_000,  # ~30 EH/s, but sells some for ops
        "btc_acquired_2025": 3_000,  # Net - sells some BTC
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 120_000_000,  # Mining + Corsicana facility ramp
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 1_500,
        "leader": "Jason Les (CEO)",
        "strategy": "1 GW Corsicana facility. Mining + data center pivot.",
        "notes": "Sells some BTC for ops. Activist pressure from Starboard Value.",
    },
    "CLSK": {
        "name": "CleanSpark",
        "ticker": "CLSK",
        "tier": 1,
        "dat_start_date": "2024-01-01",
        "holdings": 10_556,  # Dec 2025
        "asset": "BTC",
        "cost_basis_avg": 45_000,
        "is_miner": True,
        "btc_mined_annual": 9_000,  # ~37 EH/s
        "btc_acquired_2025": 5_500,  # Net additions
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 65_000_000,  # Mining ops
        "burn_source": "Q4 2025 10-Q",
        "btc_from_premium": 600,
        "leader": "Zach Bradford (CEO)",
        "strategy": "Efficient US miner. 37 EH/s.",
        "notes": "Acquired GRIID. Aggressive expansion in Georgia/Mississippi.",
    },
    "HUT": {
        "name": "Hut 8",
        "ticker": "HUT",
        "tier": 1,
        "dat_start_date": "2024-01-01",
        "holdings": 10_208,  # Dec 2025
        "asset": "BTC",
        "cost_basis_avg": 24_000,  # Lowest cost basis among majors
        "is_miner": True,
        "btc_mined_annual": 2_800,  # 7.5 EH/s
        "btc_acquired_2025": 1_500,  # Net - HODL strategy
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 45_000_000,  # Mining + HPC/AI pivot
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 400,
        "leader": "Asher Genoot (CEO)",
        "strategy": "HODL + AI/HPC diversification. 7.5 EH/s.",
        "notes": "Merged with USBTC. Canadian origin. Expanding to AI data centers.",
    },
    "ASST": {
        "name": "Strive Asset Management",
        "ticker": "ASST",
        "tier": 1,
        "dat_start_date": "2024-05-01",  # Semler started May 2024
        "holdings": 10_900,  # Post-merger with Semler
        "asset": "BTC",
        "cost_basis_avg": 100_000,
        "is_miner": False,
        "btc_mined_annual": 0,  # Pure treasury
        # Semler acquisition was DILUTIVE - paid 2x NAV ($600M equity for ~$300M BTC)
        # Post-merger PIPE: $675M for 5,816 BTC at $116K (~market price, neutral)
        # Net effect: ~3,000 BTC from Semler at 2x cost = -3,000 BTC equivalent dilution
        # PIPE ~neutral. Total: roughly 0 net accretion after accounting for dilution
        "btc_acquired_2025": 0,  # Dilutive acquisition offsets raw BTC added
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 12_000_000,  # Asset mgmt + medical device ops
        "burn_source": "Q3 2025 10-Q estimate",
        "btc_from_premium": 0,  # Paid premium, didn't capture it
        "leader": "Vivek Ramaswamy (Co-Founder)",
        "strategy": "First publicly traded asset mgmt BTC treasury. 'Preferred equity only' model.",
        "notes": "Acquired Semler at 2x NAV (dilutive). PIPE at ~market. Net: ~0 accretion.",
    },
    "BITF": {
        "name": "Bitfarms",
        "ticker": "BITF",
        "tier": 2,
        "dat_start_date": "2024-01-01",
        "holdings": 1_188,  # Dec 2025 (reduced - sells monthly)
        "asset": "BTC",
        "cost_basis_avg": 55_000,
        "is_miner": True,
        "btc_mined_annual": 3_500,  # 12 EH/s production
        "btc_acquired_2025": -500,  # Net negative - sells more than mines
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 50_000_000,  # Mining ops
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 100,
        "leader": "Ben Gagnon (CEO)",
        "strategy": "Monthly BTC sales for operations. 12 EH/s.",
        "notes": "Sells BTC monthly (not HODL). Argentina/Paraguay operations.",
    },
    "WULF": {
        "name": "TeraWulf",
        "ticker": "WULF",
        "tier": 2,
        "dat_start_date": "2024-01-01",
        "holdings": 699,  # Dec 2025 (sells most production)
        "asset": "BTC",
        "cost_basis_avg": 60_000,
        "is_miner": True,
        "btc_mined_annual": 3_000,  # ~10 EH/s production
        "btc_acquired_2025": -200,  # Net negative - sells most production
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 35_000_000,  # Mining ops
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 75,
        "leader": "Paul Prager (CEO)",
        "strategy": "Zero-carbon miner. Lake Mariner facility (NY).",
        "notes": "Nuclear-powered mining. Pivoting to AI/HPC. Sells most BTC mined.",
    },
    "KULR": {
        "name": "KULR Technology",
        "ticker": "KULR",
        "tier": 2,
        "dat_start_date": "2024-12-01",  # Very recent
        "holdings": 510,  # Jan 2026
        "asset": "BTC",
        "cost_basis_avg": 97_000,
        "is_miner": False,
        "btc_mined_annual": 0,  # Pure treasury
        "btc_acquired_2025": 510,  # All acquired in Dec 2024/Jan 2025
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 4_000_000,  # Battery tech + treasury ops
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 25,
        "leader": "Michael Mo (CEO)",
        "strategy": "Battery/thermal tech company with BTC treasury.",
        "notes": "Started Dec 2024. NASA supplier. Small cap, high volatility.",
    },
    "CIFR": {
        "name": "Cipher Mining",
        "ticker": "CIFR",
        "tier": 2,
        "dat_start_date": "2024-01-01",
        "holdings": 1_034,  # Dec 2025
        "asset": "BTC",
        "cost_basis_avg": 50_000,
        "is_miner": True,
        "btc_mined_annual": 2_500,  # 8.7 EH/s
        "btc_acquired_2025": 500,  # Net - sells some for ops
        "staking_pct": 0,
        "staking_apy": 0,
        "quarterly_burn_usd": 40_000_000,  # Mining ops
        "burn_source": "Q3 2025 10-Q",
        "btc_from_premium": 100,
        "leader": "Tyler Page (CEO)",
        "strategy": "Texas-based miner. HPC pivot.",
        "notes": "8.7 EH/s. Sells some BTC for ops. Data center JV with partners.",
    },
}

# Phase Definitions
PHASES = {
    "accumulation": {
        "name": "Phase 6a: Accumulation",
        "description": "Current phase - NAV discount/premium drives valuation",
        "metrics": ["eth_holdings", "eth_per_share", "nav_discount", "dilution_rate"],
    },
    "transition": {
        "name": "Phase 6b: Transition",
        "description": "Hybrid NAV → Earnings valuation",
        "signals": ["dividend_announced", "ops_costs_declining", "analyst_narrative_shift", "nav_discount_narrowing"],
    },
    "terminal": {
        "name": "Phase 6c: Terminal",
        "description": "P/E on yield (40-50x like Franco-Nevada)",
        "target_pe": (40, 50),
        "target_yield": (0.06, 0.11),
    },
}

# Thesis Definitions
THESES = {
    # Layer 1: Macro Worldview
    1: {
        "layer": 1,
        "layer_name": "Macro Worldview",
        "title": "Fiscal Dominance & Dollar Endgame",
        "core_claim": "Sovereign debt dynamics have shifted from monetary to fiscal dominance. The US cannot sustain its debt trajectory without default, inflation, or financial repression.",
        "confirms": [
            "Continued deficit spending regardless of rate environment",
            "Fed forced to accommodate Treasury issuance",
            "Real rates staying negative despite nominal hikes",
            "Dollar losing reserve status gradually",
        ],
        "refutes": [
            "Sustained fiscal consolidation",
            "Productivity boom that grows out of debt",
            "Dollar strengthening while debt grows indefinitely",
        ],
        "status": "worldview",
        "conviction": "high",
    },
    2: {
        "layer": 1,
        "layer_name": "Macro Worldview",
        "title": "Liquidity Mechanics > Narratives",
        "core_claim": "Global liquidity plumbing drives asset prices more than fundamentals or narratives in the short-to-medium term.",
        "confirms": [
            "Risk assets correlating tightly with net liquidity measures",
            "Narrative-driven rallies failing when liquidity drains",
            "'Bad news is good news' dynamics",
        ],
        "refutes": [
            "Major assets decoupling from liquidity",
            "Fundamentals mattering more than liquidity for sustained periods",
        ],
        "status": "active",
        "conviction": "high",
    },
    3: {
        "layer": 1,
        "layer_name": "Macro Worldview",
        "title": "Speculation Precedes Adoption",
        "core_claim": "Markets price narratives before fundamentals materialize, then crash before real adoption matures.",
        "confirms": [
            "ETH/crypto usage growing during bear markets",
            "Speculative bubbles forming on potential, not revenue",
            "Post-crash organic growth exceeding bubble-era growth",
        ],
        "refutes": [
            "Adoption and price correlating tightly",
            "Speculation never returning after adoption matures",
        ],
        "status": "active",
        "conviction": "high",
    },
    # Layer 2: Asset-Level Theses
    4: {
        "layer": 2,
        "layer_name": "Asset-Level",
        "title": "ETH as Productive Capital → Store of Value",
        "core_claim": "ETH becomes a store of value through demonstrated monetization efficiency, not instead of it. DAT companies generating consistent yield are the proof mechanism.",
        "confirms": [
            "DAT yield consistency over multiple cycles",
            "ETH outperforming as collateral",
            "Institutions holding ETH for yield, not just speculation",
            "ETH volatility declining relative to other crypto",
        ],
        "refutes": [
            "DAT yield strategies failing or compressing to zero",
            "ETH remaining purely speculative",
            "Alternative assets capturing 'productive store of value' narrative",
        ],
        "status": "core",
        "conviction": "high",
    },
    5: {
        "layer": 2,
        "layer_name": "Asset-Level",
        "title": "BTC vs ETH Role Separation",
        "core_claim": "Bitcoin becomes neutral reserve collateral. Ethereum becomes the financial operating system. Complementary, not competitive.",
        "confirms": [
            "BTC adopted as reserve asset (sovereign, corporate, ETF)",
            "ETH adopted as infrastructure (DeFi, tokenization, settlement)",
            "Minimal overlap in use cases over time",
        ],
        "refutes": [
            "BTC developing smart contract capabilities",
            "ETH absorbing monetary premium",
            "Neither winning (stablecoins or CBDCs dominating)",
        ],
        "status": "active",
        "conviction": "medium-high",
    },
    6: {
        "layer": 2,
        "layer_name": "Asset-Level",
        "title": "DAT as Asset Class (Phased Evolution)",
        "core_claim": "DAT companies evolve through distinct phases: Accumulation → Transition → Terminal (ETH royalty companies at 40-50x P/E).",
        "confirms": [
            "Dividend initiation by major DATs",
            "Operational costs declining as % of treasury",
            "Analyst language shifting to P/E focus",
            "NAV discounts narrowing",
        ],
        "refutes": [
            "DATs failing to generate consistent yield",
            "Permanent NAV discounts",
            "DAT model abandoned by market",
        ],
        "status": "core",
        "conviction": "high",
    },
    # Layer 3: Structural/Infrastructure Theses
    7: {
        "layer": 3,
        "layer_name": "Structural/Infrastructure",
        "title": "Tokenization ≠ Liquidity",
        "core_claim": "Tokenizing assets does not automatically create liquidity. Liquidity must be engineered through derivatives, arbitrage, leverage, and incentive design.",
        "confirms": [
            "Tokenized assets sitting illiquid despite being on-chain",
            "Derivatives volume exceeding spot volume for liquid assets",
            "Projects that engineer liquidity outperforming",
        ],
        "refutes": [
            "Tokenization alone driving deep liquidity",
            "Spot markets becoming more important than derivatives",
        ],
        "status": "active",
        "conviction": "high",
    },
    8: {
        "layer": 3,
        "layer_name": "Structural/Infrastructure",
        "title": "Data as Financial Primitive",
        "core_claim": "Settlement-grade data becomes infrastructure. Real-time, verifiable balance sheet data enables new financial products.",
        "confirms": [
            "Products built on real-time data outperforming traditional",
            "Oracles becoming critical infrastructure",
            "Companies willing to pay for real-time data",
        ],
        "refutes": [
            "Quarterly filings remaining sufficient",
            "Data commoditizing (no moat)",
        ],
        "status": "active",
        "conviction": "high",
    },
    9: {
        "layer": 3,
        "layer_name": "Structural/Infrastructure",
        "title": "Volatility & Derivatives as Value Engines",
        "core_claim": "Volatility itself is a monetizable resource. Derivatives often generate more value than spot markets.",
        "confirms": [
            "Derivatives volume multiples of spot volume in mature markets",
            "Volatility products driving exchange revenue",
            "DAT premiums correlating with implied volatility",
        ],
        "refutes": [
            "Spot markets dominating derivatives long-term",
            "Volatility compressing permanently",
        ],
        "status": "active",
        "conviction": "high",
    },
    10: {
        "layer": 3,
        "layer_name": "Structural/Infrastructure",
        "title": "Regulatory Convergence (Hybrid Rails)",
        "core_claim": "Regulation reshapes topology. Hybrid systems (permissioned + public) emerge and coexist.",
        "confirms": [
            "Institutional adoption via regulated wrappers (ETFs, custodians)",
            "Canton/permissioned systems growing alongside public chains",
            "CLARITY Act or similar providing safe harbors",
        ],
        "refutes": [
            "Full on-chain migration (no hybrid needed)",
            "Regulation killing on-chain activity entirely",
        ],
        "status": "active",
        "conviction": "medium-high",
    },
    # Layer 4: Business Theses (Reserve Labs)
    11: {
        "layer": 4,
        "layer_name": "Business (Reserve Labs)",
        "title": "Institutional Demand for DAT Derivatives Exists",
        "core_claim": "Billions in capital are trading DAT premiums through complex multi-leg positions. This demand can be captured.",
        "confirms": [
            "13F filings showing fund positions in DATs",
            "Options/convertible activity on MSTR, MARA, etc.",
            "Direct conversations confirming demand",
        ],
        "refutes": [
            "Institutional interest fading",
            "Existing instruments being sufficient",
        ],
        "status": "active",
        "conviction": "high",
    },
    12: {
        "layer": 4,
        "layer_name": "Business (Reserve Labs)",
        "title": "Data Licensing as Partnership Wedge",
        "core_claim": "DAT companies will partner for data licensing and revenue sharing rather than requiring traditional LOIs or equity deals.",
        "confirms": [
            "Companies engaging on rev-share proposals",
            "Data partnerships closing",
            "Companies seeing data as asset to monetize",
        ],
        "refutes": [
            "Companies unwilling to share data",
            "Demanding equity or traditional structures",
        ],
        "status": "testing",
        "conviction": "medium",
    },
    13: {
        "layer": 4,
        "layer_name": "Business (Reserve Labs)",
        "title": "AI/Agentic Economy Needs On-Chain Rails",
        "core_claim": "AI agents will transact autonomously and need deterministic, programmable finance. Ethereum becomes machine-native finance.",
        "confirms": [
            "AI agents using crypto for payments/settlement",
            "Agent-to-agent transactions growing",
            "Composability becoming more valuable than UX",
        ],
        "refutes": [
            "AI agents using traditional rails",
            "Centralized platforms handling settlement internally",
        ],
        "status": "long-term",
        "conviction": "medium",
    },
}

# Invalidation Thresholds
INVALIDATION_THRESHOLDS = {
    "eth_tvl_dominance": {
        "metric": "ETH L1+L2 TVL Share",
        "threshold": 0.40,
        "direction": "below",
        "duration": "2+ years",
        "meaning": "ETH loses settlement dominance - core thesis broken",
    },
    "eth_staking_yield": {
        "metric": "ETH Staking APY",
        "threshold": 0.01,
        "direction": "below",
        "duration": "2+ years",
        "meaning": "Productive capital thesis broken",
    },
    "bmnr_eth_per_share": {
        "metric": "BMNR ETH/Share",
        "threshold": "declining",
        "duration": "3+ consecutive quarters",
        "meaning": "Accumulation failing",
    },
    "dat_category_abandoned": {
        "metric": "Major DATs liquidating treasuries",
        "threshold": "qualitative",
        "meaning": "No institutional recognition",
    },
    "regulatory_kill": {
        "metric": "US bans corporate crypto holdings",
        "threshold": "qualitative",
        "meaning": "Can't operate",
    },
}

# Alert Thresholds (customize these)
ALERT_THRESHOLDS = {
    "nav_discount_warning": 0.30,  # Warn if NAV discount > 30%
    "drawdown_warning": 0.40,  # Warn if drawdown > 40%
    "dilution_warning": 0.30,  # Warn if annual dilution > 30%
    "eth_yield_warning": 0.02,  # Warn if staking yield < 2%
}

# Health Status Definitions
HEALTH_STATUS = {
    "healthy": {"emoji": "✅", "color": "green", "label": "Healthy"},
    "warning": {"emoji": "⚠️", "color": "orange", "label": "Warning"},
    "critical": {"emoji": "❌", "color": "red", "label": "Critical"},
    "unknown": {"emoji": "❓", "color": "gray", "label": "Unknown"},
}
