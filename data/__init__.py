"""Data module for thesis dashboard"""
from .fetchers import (
    fetch_eth_price,
    fetch_eth_treasury_companies,
    fetch_stock_data,
    fetch_stock_history,
    fetch_fred_series,
    fetch_fed_balance_sheet,
    fetch_treasury_general_account,
    fetch_reverse_repo,
    fetch_deficit_gdp_ratio,
    fetch_defi_tvl,
    fetch_eth_staking_stats,
    fetch_eth_burn_stats,
    fetch_eth_supply_stats,
    fetch_dxy,
    fetch_all_dat_stocks,
    calculate_net_liquidity,
)

from .calculations import (
    calculate_nav,
    calculate_nav_per_share,
    calculate_nav_discount,
    calculate_eth_per_share,
    calculate_drawdown,
    calculate_dilution_rate,
    calculate_treasury_value_change,
    determine_dat_phase,
    calculate_position_value,
    calculate_portfolio_metrics,
    get_health_status,
    check_precondition_health,
    count_transition_signals,
    format_large_number,
    format_eth_amount,
    format_percentage,
)

from .news_fetcher import (
    fetch_all_dat_news,
    fetch_company_news,
    fetch_lookonchain_mentions,
    get_time_ago,
)

from .edgar_fetcher import (
    fetch_all_dat_filings,
    fetch_company_edgar,
    get_filing_type_description,
    get_filing_type_emoji,
    DAT_COMPANY_CIKS,
)
