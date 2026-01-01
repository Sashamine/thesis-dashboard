"""Components module"""
from .home import render_home_page
from .dat_table import render_dat_table, render_add_dat_form
from .dat_detail import render_dat_detail_page, render_dat_selector
from .thesis_tracker import render_thesis_tracker, render_thesis_dependencies
from .charts import (
    create_line_chart,
    create_multi_line_chart,
    create_bar_chart,
    create_pie_chart,
    create_gauge_chart,
    render_comparison_chart,
    render_eth_holdings_chart,
    render_nav_discount_chart,
    render_treemap,
)
from .news_feed import (
    render_news_feed,
    render_news_page,
    render_company_news,
    render_news_sidebar,
)
