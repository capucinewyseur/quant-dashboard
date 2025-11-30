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
    Fetch market caps from yfinance for the given tickers.
    If not available (FX, futures...), fallback to 1.0.
    """
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
    st.title("Quant B — Multi-Asset Portfolio Module")

    # -----------------------------------------
    # Sidebar : paramètres du portefeuille
    # -----------------------------------------
    st.sidebar.header("Portfolio settings")

    # 1) Choix des actifs
    tickers = st.sidebar.multiselect(
        "Select assets",
        options=DEFAULT_TICKERS,
        default=DEFAULT_TICKERS,
        help="Select at least 2 assets to build a portfolio.",
    )

    if len(tickers) < 2:
        st.warning("Please select at least two assets to build a portfolio.")
        return

    # 2) Période d'analyse
    today = date.today()
    default_start = date(today.year - 1, today.month, today.day)  # 1 an par défaut

    start_date = st.sidebar.date_input("Start date", default_start)
    end_date = st.sidebar.date_input("End date", today)

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        return

    # 3) Data interval (intraday / daily)
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
    # (assuming ~252 trading days, ~6.5h per day)
    periods_map = {
        "15 minutes": 26 * 252,   # 6.5h * 4 = 26 bars/day
        "30 minutes": 13 * 252,
        "1 hour": 6 * 252,        # approx (ignore the .5)
        "4 hours": 2 * 252,       # approx
        "Daily": 252,
    }

    data_interval = interval_map[interval_label]
    periods_per_year = periods_map[interval_label]

    # 4) Mode de poids : equal / price / mkt cap / custom
    weights_mode = st.sidebar.radio(
        "Weights mode",
        ["Equal weight", "Price-weighted", "Market-cap weighted", "Custom"],
        index=0,
    )

    # 5) Rebalancing frequency
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

    # Custom weights sliders (only used if mode == Custom)
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

    # -----------------------------------------
    # Chargement des prix
    # -----------------------------------------
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

    # -----------------------------------------
    # Construction des poids selon le mode choisi
    # -----------------------------------------
    raw_weights: dict[str, float] = {}

    if weights_mode == "Equal weight":
        raw_weights = {t: 1.0 for t in tickers}

    elif weights_mode == "Price-weighted":
        # Last available price per asset (with forward fill)
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

    # Normalize weights (sum = 1)
    weights = normalize_weights(raw_weights, tickers)

    # ---------- DISPLAY: selected assets + weights ----------
    st.write("### Selected assets")
    st.write(", ".join(tickers))

    st.write(f"**Portfolio weights ({weights_mode}):**")
    weights_dict = {t: float(w) for t, w in zip(tickers, weights)}
    weights_df = (
        pd.DataFrame.from_dict(weights_dict, orient="index", columns=["Weight"])
        .rename_axis("Asset")
    )
    st.dataframe(weights_df.style.format({"Weight": "{:.2%}"}))

    # -----------------------------------------
    # Returns, portefeuille, métriques
    # -----------------------------------------
    rets = compute_returns(prices, log=False)

    # Portfolio returns with chosen rebalancing frequency
    port_rets = compute_portfolio_returns_with_rebalancing(
        rets,
        weights,
        rebal_freq=rebal_freq,
    )
    port_val = compute_cumulated_values(port_rets, initial_value=100.0)

    # -----------------------------------------
    # Graphique : actifs vs portefeuille
    # -----------------------------------------
    st.write("### Assets vs Portfolio (normalized to 100)")

    fig = go.Figure()

    # Normalisation des actifs à 100 (par 1er prix valide)
    for col in prices.columns:
        series = prices[col]
        non_na = series.dropna()
        if non_na.empty:
            continue
        first_valid = non_na.iloc[0]
        series_norm = series / first_valid * 100.0

        fig.add_trace(
            go.Scatter(
                x=series_norm.index,
                y=series_norm,
                mode="lines",
                name=col,
            )
        )

    # Ajout de la courbe portefeuille
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

    # -----------------------------------------
    # Metrics du portefeuille (incl. diversification)
    # -----------------------------------------
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

    # -----------------------------------------
    # Matrice de corrélation
    # -----------------------------------------
    st.write("### Correlation matrix")
    corr = compute_correlation_matrix(rets)
    st.dataframe(corr.style.format("{:.2f}"))
