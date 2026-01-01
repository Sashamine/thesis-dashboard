"""
Reusable Chart Components
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
from data import fetch_stock_history


def create_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    y_label: str = "",
    color: str = "#636EFA",
    height: int = 400,
) -> go.Figure:
    """Create a basic line chart"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode="lines",
        line=dict(color=color, width=2),
        name=y_col,
    ))

    fig.update_layout(
        title=title,
        yaxis_title=y_label or y_col,
        xaxis_title=x_col,
        height=height,
        showlegend=False,
    )

    return fig


def create_multi_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str,
    y_label: str = "",
    height: int = 400,
) -> go.Figure:
    """Create a multi-line chart"""
    fig = go.Figure()

    colors = px.colors.qualitative.Plotly

    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=2),
            name=y_col,
        ))

    fig.update_layout(
        title=title,
        yaxis_title=y_label,
        xaxis_title=x_col,
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_bar_chart(
    labels: List[str],
    values: List[float],
    title: str,
    y_label: str = "",
    colors: Optional[List[str]] = None,
    height: int = 400,
) -> go.Figure:
    """Create a bar chart"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        marker_color=colors or "#636EFA",
    ))

    fig.update_layout(
        title=title,
        yaxis_title=y_label,
        height=height,
    )

    return fig


def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: str,
    height: int = 400,
) -> go.Figure:
    """Create a pie chart"""
    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
    ))

    fig.update_layout(
        title=title,
        height=height,
    )

    return fig


def create_gauge_chart(
    value: float,
    title: str,
    min_val: float = 0,
    max_val: float = 100,
    thresholds: Optional[Dict[str, float]] = None,
    height: int = 300,
) -> go.Figure:
    """Create a gauge chart for metrics"""
    # Default thresholds
    if thresholds is None:
        thresholds = {
            "red": 0.33,
            "yellow": 0.66,
            "green": 1.0,
        }

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "bar": {"color": "#636EFA"},
            "steps": [
                {"range": [min_val, max_val * thresholds["red"]], "color": "lightcoral"},
                {"range": [max_val * thresholds["red"], max_val * thresholds["yellow"]], "color": "lightyellow"},
                {"range": [max_val * thresholds["yellow"], max_val], "color": "lightgreen"},
            ],
        },
    ))

    fig.update_layout(height=height)

    return fig


def render_comparison_chart(
    tickers: List[str],
    period: str = "1y",
    normalize: bool = True,
) -> None:
    """Render price comparison chart for multiple tickers"""
    fig = go.Figure()

    colors = px.colors.qualitative.Plotly

    for i, ticker in enumerate(tickers):
        hist = fetch_stock_history(ticker, period)

        if hist.empty:
            continue

        prices = hist["Close"]

        if normalize:
            # Normalize to 100 at start
            prices = (prices / prices.iloc[0]) * 100

        fig.add_trace(go.Scatter(
            x=hist.index,
            y=prices,
            mode="lines",
            name=ticker,
            line=dict(color=colors[i % len(colors)], width=2),
        ))

    title = "Normalized Price Comparison" if normalize else "Price Comparison"
    y_label = "Normalized (100 = Start)" if normalize else "Price ($)"

    fig.update_layout(
        title=title,
        yaxis_title=y_label,
        xaxis_title="Date",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_eth_holdings_chart(holdings_data: Dict[str, float]) -> None:
    """Render ETH holdings comparison chart"""
    # Sort by holdings
    sorted_data = dict(sorted(holdings_data.items(), key=lambda x: x[1], reverse=True))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(sorted_data.keys()),
        y=list(sorted_data.values()),
        marker_color="#00CC96",
    ))

    fig.update_layout(
        title="ETH Holdings by Company",
        yaxis_title="ETH Holdings",
        xaxis_title="Company",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_nav_discount_chart(discount_data: Dict[str, float]) -> None:
    """Render NAV discount comparison chart"""
    # Sort by discount (most discounted first)
    sorted_data = dict(sorted(discount_data.items(), key=lambda x: x[1] or 0))

    # Color by discount/premium
    colors = ["#EF553B" if v and v < 0 else "#00CC96" for v in sorted_data.values()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(sorted_data.keys()),
        y=[v * 100 if v else 0 for v in sorted_data.values()],
        marker_color=colors,
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    fig.update_layout(
        title="NAV Discount/Premium by Company",
        yaxis_title="Discount (-) / Premium (+) %",
        xaxis_title="Company",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_treemap(
    labels: List[str],
    parents: List[str],
    values: List[float],
    title: str,
) -> None:
    """Render a treemap visualization"""
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value+percent parent",
    ))

    fig.update_layout(
        title=title,
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)
