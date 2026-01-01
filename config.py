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
# Premium issuance: ETH acquired by issuing shares above NAV
DAT_COMPANIES = {
    # Tier 1: Major Players (>100k ETH)
    "BMNR": {
        "name": "Bitmine Immersion",
        "ticker": "BMNR",
        "tier": 1,
        "eth_holdings": 4_110_000,  # Dec 2025 estimate
        "staking_pct": 0.85,  # 85% staked via MAVAN validators
        "staking_method": "MAVAN validators",
        "quarterly_burn_usd": 2_500_000,  # ~$2.5M/quarter opex from 10-Q
        "burn_source": "Q3 2025 10-Q",
        # Premium issuance tracking (from S-3/424B filings)
        "shares_issued_ytd": 25_000_000,  # Shares issued YTD
        "avg_issuance_premium": 0.15,  # Avg 15% premium to NAV at issuance
        "eth_from_premium": 150_000,  # ETH acquired from premium (calculated)
        "leader": "Tom Lee (Fundstrat)",
        "strategy": "5% of ETH supply goal, staking, MAVAN validators Q1 2026",
        "shares_outstanding": None,  # Will be fetched
        "notes": "Core DAT position, largest ETH treasury company",
    },
    "SBET": {
        "name": "SharpLink Gaming",
        "ticker": "SBET",
        "tier": 1,
        "eth_holdings": 838_000,
        "staking_pct": 0.95,  # 95% staked via Linea/Lido
        "staking_method": "Linea/Lido",
        "quarterly_burn_usd": 2_850_000,  # ~$2.85M/quarter (TTM opex ~$11.4M)
        "burn_source": "Q3 2025 10-Q - verify, user reports may be higher",
        "shares_issued_ytd": 15_000_000,
        "avg_issuance_premium": 0.20,  # 20% premium
        "eth_from_premium": 35_000,
        "leader": "Joe Lubin (Ethereum co-founder)",
        "strategy": "Staking, Linea partnership, tokenized equity via Superstate",
        "shares_outstanding": None,
        "notes": "Core DAT position, #2 ETH treasury. Q3 2025: $104M operating income from ETH gains.",
    },
    "ETHM": {
        "name": "The Ether Machine",
        "ticker": "ETHM",
        "tier": 1,
        "eth_holdings": 496_000,
        "staking_pct": 1.0,  # 100% staked - "fully staked treasury"
        "staking_method": "Native staking",
        "quarterly_burn_usd": 800_000,  # ~$800K/quarter (lean ops)
        "burn_source": "S-4 Filing 2025",
        "shares_issued_ytd": 0,  # New company, SPAC merger
        "avg_issuance_premium": 0,
        "eth_from_premium": 0,
        "leader": "Andrew Keys",
        "strategy": "DeFi/staking 'machine' to grow ETH",
        "shares_outstanding": None,
        "notes": "First 1,000+ ETH yield from fully staked treasury",
    },
    "BTBT": {
        "name": "Bit Digital",
        "ticker": "BTBT",
        "tier": 1,
        "eth_holdings": 154_000,
        "staking_pct": 0.90,  # 90% staked per company statement
        "staking_method": "Native staking",
        "quarterly_burn_usd": 8_500_000,  # ~$8.5M/quarter (mining + staking ops)
        "burn_source": "Q3 2025 10-Q",
        "shares_issued_ytd": 10_000_000,
        "avg_issuance_premium": 0.10,
        "eth_from_premium": 5_000,
        "leader": "Sam Tabar",
        "strategy": "90% staked, fully exited BTC",
        "shares_outstanding": None,
        "notes": "",
    },
    # Tier 2: Mid-Size (10k-100k ETH)
    "ETHZ": {
        "name": "ETHZilla",
        "ticker": "ETHZ",
        "tier": 2,
        "eth_holdings": 69_802,  # Dec 2025 - sold 24,291 ETH ($74.5M) to pay down debt
        "staking_pct": 0.80,  # Estimated 80% staked
        "staking_method": "Native staking",
        "quarterly_burn_usd": 1_200_000,  # ~$1.2M/quarter
        "burn_source": "Q3 2025 10-Q",
        "shares_issued_ytd": 5_000_000,
        "avg_issuance_premium": 0.12,
        "eth_from_premium": 3_500,
        "leader": "Peter Thiel backed",
        "strategy": "Pivoting to RWA tokenization, sold ETH for debt paydown & buybacks",
        "shares_outstanding": None,
        "notes": "Sold $40M ETH (Oct) + $74.5M ETH (Dec). Stock down 96% from Aug highs. Discontinued mNAV dashboard.",
    },
    "BTCS": {
        "name": "BTCS Inc.",
        "ticker": "BTCS",
        "tier": 2,
        "eth_holdings": 70_000,
        "staking_pct": 0.75,  # 75% staked via Builder+
        "staking_method": "Builder+ validators",
        "quarterly_burn_usd": 1_800_000,  # ~$1.8M/quarter
        "burn_source": "Q3 2025 10-Q",
        "shares_issued_ytd": 8_000_000,
        "avg_issuance_premium": 0.08,
        "eth_from_premium": 2_000,
        "leader": "",
        "strategy": "ETH 'Bividend,' DeFi/TradFi flywheel, Builder+",
        "shares_outstanding": None,
        "notes": "",
    },
    "GAME": {
        "name": "GameSquare",
        "ticker": "GAME",
        "tier": 2,
        "eth_holdings": 10_000,
        "staking_pct": 0.50,  # Estimated 50% - newer to ETH
        "staking_method": "Lido/stETH",
        "quarterly_burn_usd": 12_000_000,  # ~$12M/quarter (esports/gaming ops)
        "burn_source": "Q3 2025 10-Q",
        "shares_issued_ytd": 20_000_000,
        "avg_issuance_premium": 0.05,
        "eth_from_premium": 500,
        "leader": "",
        "strategy": "$250M authorization for more",
        "shares_outstanding": None,
        "notes": "",
    },
    "FGNX": {
        "name": "Fundamental Global",
        "ticker": "FGNX",
        "tier": 2,
        "eth_holdings": 6_000,
        "staking_pct": 0.60,  # Estimated 60%
        "staking_method": "Lido/stETH",
        "quarterly_burn_usd": 2_000_000,  # ~$2M/quarter (insurance ops)
        "burn_source": "Q3 2025 10-Q",
        "shares_issued_ytd": 3_000_000,
        "avg_issuance_premium": 0.06,
        "eth_from_premium": 300,
        "leader": "",
        "strategy": "Insurance/reinsurance pivot",
        "shares_outstanding": None,
        "notes": "",
    },
}

# Solana DAT Companies (for tracking/news only)
# Burn rates from 10-Q/10-K filings (quarterly opex in USD)
SOL_DAT_COMPANIES = {
    "FWDI": {
        "name": "Forward Industries",
        "ticker": "FWDI",
        "tier": 1,
        "holdings": 6_921_342,  # Dec 2025
        "asset": "SOL",
        "cost_basis_avg": 232.08,  # per SOL
        "staking_pct": 0.99,  # Nearly all staked
        "staking_apy": 0.07,  # 6.82-7.01% gross APY
        "quarterly_burn_usd": 3_400_000,  # ~$13.6M annual opex / 4
        "burn_source": "FY 2025 10-K",
        "leader": "Galaxy, Jump Crypto, Multicoin backed",
        "strategy": "World's largest SOL treasury, validator infrastructure",
        "notes": "Raised $1.65B PIPE. Debt free. Changed ticker from FORD to FWDI.",
    },
    "HSDT": {
        "name": "Solana Company (fka Helius Medical)",
        "ticker": "HSDT",
        "tier": 1,
        "holdings": 2_200_000,  # Oct 2025 estimate
        "asset": "SOL",
        "cost_basis_avg": 227.00,
        "staking_pct": 0.95,
        "staking_apy": 0.065,
        "quarterly_burn_usd": 12_000_000,  # $36M Q3 opex (includes bonuses)
        "burn_source": "Q3 2025 10-Q - inflated by PIPE costs",
        "leader": "Pantera Capital, Summer Capital",
        "strategy": "SOL treasury via Anchorage Digital custody",
        "notes": "Raised $500M. Partnered with Solana Foundation for discounted SOL.",
    },
    "DFDV": {
        "name": "DeFi Development Corp",
        "ticker": "DFDV",
        "tier": 1,
        "holdings": 2_195_926,  # Oct 2025
        "asset": "SOL",
        "cost_basis_avg": 110.00,
        "staking_pct": 0.90,
        "staking_apy": 0.114,  # 11.4% organic yield reported
        "quarterly_burn_usd": 1_500_000,  # ~$6M annual (lean ops)
        "burn_source": "Q3 2025 10-Q estimate",
        "leader": "Formerly Janover Inc.",
        "strategy": "First US public company with SOL-focused treasury. Target 1 SPS by Dec 2028.",
        "notes": "$5B ELOC. $4.6M quarterly revenue. Validator operations.",
    },
    "UPXI": {
        "name": "Upexi",
        "ticker": "UPXI",
        "tier": 1,
        "holdings": 2_106_989,  # Oct 2025
        "asset": "SOL",
        "cost_basis_avg": 157.66,
        "staking_pct": 0.95,
        "staking_apy": 0.08,  # ~8% yield
        "quarterly_burn_usd": 2_500_000,  # Consumer brands ops + treasury
        "burn_source": "Q1 2026 10-Q",
        "leader": "Arthur Hayes (advisory)",
        "strategy": "SOL treasury + consumer brands (Cure Mushrooms, Lucky Tail)",
        "notes": "42% locked SOL at mid-teens discount. $50M buyback approved Nov 2025.",
    },
    "HODL": {
        "name": "Sol Strategies",
        "ticker": "HODL",  # CSE: HODL, NASDAQ: STKE
        "tier": 2,
        "holdings": 526_637,  # Nov 2025
        "asset": "SOL",
        "cost_basis_avg": 130.00,
        "staking_pct": 0.85,
        "staking_apy": 0.065,
        "quarterly_burn_usd": 1_200_000,  # Canadian small cap ops
        "burn_source": "FY 2025 annual report",
        "leader": "Canadian company",
        "strategy": "Validator operations, staking provider for VanEck Solana ETF",
        "notes": "3.7M SOL delegated. Selected as VanEck staking provider Nov 2025.",
    },
}

# Hyperliquid DAT Companies (for tracking/news only)
HYPE_DAT_COMPANIES = {
    "PURR": {
        "name": "Hyperliquid Strategies",
        "ticker": "PURR",
        "tier": 1,
        "holdings": 12_600_000,  # Dec 2025 merger close
        "asset": "HYPE",
        "cost_basis_avg": 46.27,  # $583M / 12.6M
        "staking_pct": 0.80,
        "staking_apy": 0.05,
        "quarterly_burn_usd": 2_000_000,  # New company, lean ops + Sonnet legacy
        "burn_source": "Estimate - just launched Dec 2025",
        "leader": "David Schamis (CEO), Bob Diamond (Board)",
        "strategy": "HYPE treasury via Sonnet merger. Staking + yield optimization.",
        "notes": "Merged with Sonnet Dec 2025. $888M combined assets. $30M buyback.",
    },
    "HYPD": {
        "name": "Hyperion DeFi (fka Eyenovia)",
        "ticker": "HYPD",
        "tier": 2,
        "holdings": 1_712_195,  # Sep 2025
        "asset": "HYPE",
        "cost_basis_avg": 38.25,
        "staking_pct": 0.90,
        "staking_apy": 0.05,
        "quarterly_burn_usd": 1_500_000,  # Small biotech pivot
        "burn_source": "Q2 2025 10-Q estimate",
        "leader": "First US public HYPE treasury",
        "strategy": "Validator node via Kinetiq. Aims to be largest HYPE holder.",
        "notes": "Raised $50M PIPE. Rebranded from Eyenovia Jul 2025.",
    },
}

# BNB DAT Companies (for tracking/news only)
BNB_DAT_COMPANIES = {
    "BNC": {
        "name": "BNB Network Company (CEA Industries)",
        "ticker": "BNC",
        "tier": 1,
        "holdings": 500_000,  # Dec 2025
        "asset": "BNB",
        "cost_basis_avg": 870.00,  # ~$435M for 500K per filing
        "staking_pct": 0.50,
        "staking_apy": 0.03,
        "quarterly_burn_usd": 3_000_000,  # Treasury ops + legacy CEA
        "burn_source": "FY Q2 2026 10-Q estimate",
        "leader": "YZi Labs (CZ family office) backed",
        "strategy": "Target 1% of BNB supply. Largest corporate BNB holder.",
        "notes": "$500M PIPE closed. YZi Labs owns 7% seeking board control. Rights plan adopted Dec 2025.",
    },
    "WINT": {
        "name": "Windtree Therapeutics",
        "ticker": "WINT",
        "tier": 2,
        "holdings": 100_000,  # Estimated from $520M commitment
        "asset": "BNB",
        "cost_basis_avg": 650.00,
        "staking_pct": 0.40,
        "staking_apy": 0.03,
        "quarterly_burn_usd": 4_000_000,  # Biopharma legacy ops
        "burn_source": "10-Q estimate - biopharma overhead",
        "leader": "First US biopharma with BNB treasury",
        "strategy": "$520M commitment for BNB via Kraken custody",
        "notes": "$500M ELOC + $20M from Build & Build Corp. 99% for BNB acquisition.",
    },
    "NA": {
        "name": "Nano Labs",
        "ticker": "NA",
        "tier": 2,
        "holdings": 128_000,  # Jul 2025
        "asset": "BNB",
        "cost_basis_avg": 600.00,
        "staking_pct": 0.30,
        "staking_apy": 0.03,
        "quarterly_burn_usd": 5_000_000,  # HK chip design + Web3 ops
        "burn_source": "20-F estimate",
        "leader": "Hong Kong Web3 infrastructure",
        "strategy": "BNB treasury via convertible notes",
        "notes": "Issued $500M convertible notes (interest-free, 360 days) Jun 2025.",
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
