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

# DAT Company Definitions
DAT_COMPANIES = {
    # Tier 1: Major Players (>100k ETH)
    "BMNR": {
        "name": "Bitmine Immersion",
        "ticker": "BMNR",
        "tier": 1,
        "eth_holdings": 4_110_000,  # Dec 2025 estimate
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
        "leader": "Joe Lubin (Ethereum co-founder)",
        "strategy": "Staking, Linea partnership, tokenized equity via Superstate",
        "shares_outstanding": None,
        "notes": "Core DAT position, #2 ETH treasury company",
    },
    "ETHM": {
        "name": "The Ether Machine",
        "ticker": "ETHM",
        "tier": 1,
        "eth_holdings": 496_000,
        "leader": "Andrew Keys",
        "strategy": "DeFi/staking 'machine' to grow ETH",
        "shares_outstanding": None,
        "notes": "",
    },
    "BTBT": {
        "name": "Bit Digital",
        "ticker": "BTBT",
        "tier": 1,
        "eth_holdings": 154_000,
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
        "eth_holdings": 94_000,
        "leader": "Peter Thiel backed",
        "strategy": "Share buybacks",
        "shares_outstanding": None,
        "notes": "",
    },
    "BTCS": {
        "name": "BTCS Inc.",
        "ticker": "BTCS",
        "tier": 2,
        "eth_holdings": 70_000,
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
        "leader": "",
        "strategy": "Insurance/reinsurance pivot",
        "shares_outstanding": None,
        "notes": "",
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
