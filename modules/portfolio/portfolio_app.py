# modules/portfolio/portfolio_app.py

from datetime import datetime, date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from modules.data.multi_asset_loader import (
    load_multi_asset_prices,
    DEFAULT_TICKERS,
)
from modules.portfolio.portfolio_logic import (
    compute_returns,
    normalize_weights,
    compute_portfolio_returns_with_rebalancing,
    compute_cumulated_values,
    compute_portfolio_metrics,
    compute_correlation_matrix,
)


def _get_market_caps(tickers: list[str]) -> dict[str, float]:
    """
    Retrieve market capitalizations for a list of assets.

    Market capitalizations are fetched using yfinance. If a market cap
    is not available (e.g. FX rates, commodities, indices), a fallback
    value of 1.0 is used so that the asset can still be included in
    market-cap-weighted portfolios.

    Parameters
    ----------
    tickers : list[str]
        List of asset tickers.

    Returns
    -------
    dict[str, float]
        Dictionary mapping each ticker to its market capitalization
        (or 1.0 if unavailable).
    """
    # Fetch market capitalizations from yfinance for the given tickers
    # If market cap is not available (FX, futures, indices), fallback to 1.0
    caps: dict[str, float] = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            cap = info.get("marketCap", None)
            if cap is None or cap <= 0:
                cap = 1.0
        except Exception:
            cap = 1.0
        caps[t] = float(cap)
    return caps


def run():
    """
    Run the multi-asset portfolio Streamlit module.

    This function handles:
    - User input through the sidebar (assets, dates, weights, rebalancing)
    - Price data loading at different frequencies
    - Portfolio construction with optional rebalancing
    - Visualization of asset and portfolio performance
    - Computation and display of portfolio-level metrics, including
      diversification effects and correlation structure
    """
    st.title("Quant B — Multi-Asset Portfolio Module")

    # Sidebar: portfolio parameters
    st.sidebar.header("Portfolio settings")

    # Asset selection
    tickers = st.sidebar.multiselect(
        "Select assets",
        options=DEFAULT_TICKERS,
        default=DEFAULT_TICKERS,
        help="Select at least 2 assets to build a portfolio.",
    )

    if len(tickers) < 2:
        st.warning("Please select at least two assets to build a portfolio.")
        return

    # Analysis period
    today = date.today()
    default_start = date(today.year - 1, today.month, today.day)  # default: 1 year

    start_date = st.sidebar.date_input("Start date", default_start)
    end_date = st.sidebar.date_input("End date", today)

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        return

    # Data interval (intraday / daily)
    interval_label = st.sidebar.selectbox(
        "Data interval",
        ["15 minutes", "30 minutes", "1 hour", "4 hours", "Daily"],
        index=4,
        help="Sampling frequency of downloaded data.",
    )

    interval_map = {
        "15 minutes": "15m",
        "30 minutes": "30m",
        "1 hour": "60m",
        "4 hours": "240m",
        "Daily": "1d",
    }

    # Approximate number of periods per year for annualization
    # Assumes ~252 trading days and ~6.5 trading hours per day
    periods_map = {
        "15 minutes": 26 * 252,
        "30 minutes": 13 * 252,
        "1 hour": 6 * 252,
        "4 hours": 2 * 252,
        "Daily": 252,
    }

    data_interval = interval_map[interval_label]
    periods_per_year = periods_map[interval_label]

    # Weighting scheme: equal / price / market cap / custom
    weights_mode = st.sidebar.radio(
        "Weights mode",
        ["Equal weight", "Price-weighted", "Market-cap weighted", "Custom"],
        index=0,
    )

    # Rebalancing frequency
    rebal_label = st.sidebar.selectbox(
        "Rebalancing frequency",
        ["No rebalancing (buy & hold)", "Monthly", "Quarterly", "Yearly"],
        index=0,
        help="How often the portfolio is rebalanced back to the chosen weights.",
    )
    freq_map = {
        "No rebalancing (buy & hold)": "none",
        "Monthly": "M",
        "Quarterly": "Q",
        "Yearly": "A",
    }
    rebal_freq = freq_map[rebal_label]

    # Custom weight sliders (used only if Custom mode is selected)
    custom_raw_weights: dict[str, float] = {}
    if weights_mode == "Custom":
        st.sidebar.subheader("Custom weights")
        for t in tickers:
            custom_raw_weights[t] = st.sidebar.slider(
                f"Weight for {t}",
                min_value=0.0,
                max_value=1.0,
                value=1.0 / len(tickers),
                step=0.01,
            )

    # Price data loading
    with st.spinner("Loading price data..."):
        prices = load_multi_asset_prices(
            tickers=tickers,
            start=datetime.combine(start_date, datetime.min.time()),
            end=datetime.combine(end_date, datetime.min.time()),
            interval=data_interval,
        )

    if prices.empty:
        st.error("No price data downloaded. Please check tickers, dates or interval.")
        return

    st.write("### Raw prices (recent rows)")
    st.dataframe(prices.sort_index(ascending=False).head())

    # Weight construction based on selected mode
    raw_weights: dict[str, float] = {}

    if weights_mode == "Equal weight":
        raw_weights = {t: 1.0 for t in tickers}

    elif weights_mode == "Price-weighted":
        # Use last available price per asset (with forward fill)
        last_prices = prices.ffill().iloc[-1]
        for t in tickers:
            val = last_prices.get(t, np.nan)
            if pd.isna(val):
                val = 1.0  # fallback if no data
            raw_weights[t] = float(val)

    elif weights_mode == "Market-cap weighted":
        caps = _get_market_caps(tickers)
        raw_weights = caps

    elif weights_mode == "Custom":
        raw_weights = custom_raw_weights

    # Normalize weights so that they sum to 1
    weights = normalize_weights(raw_weights, tickers)

    # Display selected assets and portfolio weights
    st.write("### Selected assets")
    st.write(", ".join(tickers))

    st.write(f"**Portfolio weights ({weights_mode}):**")
    weights_dict = {t: float(w) for t, w in zip(tickers, weights)}
    weights_df = (
        pd.DataFrame.from_dict(weights_dict, orient="index", columns=["Weight"])
        .rename_axis("Asset")
    )
    st.dataframe(weights_df.style.format({"Weight": "{:.2%}"}))

    # Returns, portfolio construction, metrics
    rets = compute_returns(prices, log=False)

    # Compute portfolio returns with the selected rebalancing frequency
    port_rets = compute_portfolio_returns_with_rebalancing(
        rets,
        weights,
        rebal_freq=rebal_freq,
    )
    port_val = compute_cumulated_values(port_rets, initial_value=100.0)

    # Plot: assets vs portfolio
    st.write("### Assets vs Portfolio (normalized to 100)")

    fig = go.Figure()

    # Normalize asset prices to 100 using the first valid price
    prices_plot = prices.ffill()
    for col in prices_plot.columns:
        series = prices_plot[col]
        if series.isna().all():
            continue
        first_valid = series.dropna().iloc[0]
        series_norm = series / first_valid * 100.0

        fig.add_trace(
            go.Scatter(
                x=series_norm.index,
                y=series_norm,
                mode="lines",
                name=col,
            )
        )

    # Add portfolio value curve
    fig.add_trace(
        go.Scatter(
            x=port_val.index,
            y=port_val.values,
            mode="lines",
            name="Portfolio",
            line=dict(width=3),
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Normalized value (100 = start)",
        legend_title="Assets / Portfolio",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Portfolio metrics (including diversification)
    st.write("### Portfolio metrics")

    metrics = compute_portfolio_metrics(
        port_rets,
        rets=rets,
        weights=weights,
        periods_per_year=periods_per_year,
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Annual return", f"{metrics['annual_return']*100:.2f} %")
    col2.metric("Annual vol", f"{metrics['annual_vol']*100:.2f} %")
    col3.metric("Sharpe", f"{metrics['sharpe']:.2f}")
    col4.metric("Max drawdown", f"{metrics['max_drawdown']*100:.2f} %")

    div_ratio = metrics.get("diversification_ratio")
    if div_ratio is not None and not np.isnan(div_ratio):
        col5.metric("Diversification ratio", f"{div_ratio:.2f}")
    else:
        col5.metric("Diversification ratio", "N/A")

    # Correlation matrix
    st.write("### Correlation matrix")
    corr = compute_correlation_matrix(rets)
    st.dataframe(corr.style.format("{:.2f}"))
