# modules/portfolio/portfolio_app.py

from datetime import datetime, date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.data.multi_asset_loader import (
    load_multi_asset_prices,
    DEFAULT_TICKERS,
)
from modules.portfolio.portfolio_logic import (
    compute_returns,
    normalize_weights,
    compute_portfolio_returns,
    compute_cumulated_values,
    compute_portfolio_metrics,
    compute_correlation_matrix,
)


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
    default_start = date(today.year - 3, today.month, today.day)

    start_date = st.sidebar.date_input("Start date", default_start)
    end_date = st.sidebar.date_input("End date", today)

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        return

    # 3) Mode de poids : equal ou custom
    weights_mode = st.sidebar.radio(
        "Weights mode",
        ["Equal weight", "Custom"],
        index=0,
    )

    raw_weights = {}
    if weights_mode == "Custom":
        st.sidebar.subheader("Custom weights")
        for t in tickers:
            raw_weights[t] = st.sidebar.slider(
                f"Weight for {t}",
                min_value=0.0,
                max_value=1.0,
                value=1.0 / len(tickers),
                step=0.01,
            )
    else:
        raw_weights = {t: 1.0 for t in tickers}

    # Normalisation des poids (somme = 1)
    weights = normalize_weights(raw_weights, tickers)

    # ---------- DISPLAY: selected assets + weights (clean) ----------
    st.write("### Selected assets")
    st.write(", ".join(tickers))

    st.write("**Portfolio weights:**")
    weights_dict = {t: float(w) for t, w in zip(tickers, weights)}
    weights_df = (
        pd.DataFrame.from_dict(weights_dict, orient="index", columns=["Weight"])
        .rename_axis("Asset")
    )
    st.dataframe(weights_df.style.format({"Weight": "{:.2%}"}))

    # -----------------------------------------
    # Chargement des prix
    # -----------------------------------------
    with st.spinner("Loading price data..."):
        prices = load_multi_asset_prices(
            tickers=tickers,
            start=datetime.combine(start_date, datetime.min.time()),
            end=datetime.combine(end_date, datetime.min.time()),
            interval="1d",
        )

    if prices.empty:
        st.error("No price data downloaded. Please check tickers or dates.")
        return

    st.write("### Raw prices (first rows)")
    st.dataframe(prices.head())

    # -----------------------------------------
    # Returns, portefeuille, métriques
    # -----------------------------------------
    rets = compute_returns(prices, log=False)
    port_rets = compute_portfolio_returns(rets, weights)
    port_val = compute_cumulated_values(port_rets, initial_value=100.0)

    # -----------------------------------------
    # Graphique : actifs vs portefeuille
    # -----------------------------------------
    st.write("### Assets vs Portfolio (normalized to 100)")

    fig = go.Figure()

    # Normalisation des actifs à 100 au départ
    norm_prices = prices / prices.iloc[0] * 100.0

    for col in norm_prices.columns:
        fig.add_trace(
            go.Scatter(
                x=norm_prices.index,
                y=norm_prices[col],
                mode="lines",
                name=col,
            )
        )

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
    # Metrics du portefeuille
    # -----------------------------------------
    st.write("### Portfolio metrics")

    metrics = compute_portfolio_metrics(port_rets)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annual return", f"{metrics['annual_return']*100:.2f} %")
    col2.metric("Annual vol", f"{metrics['annual_vol']*100:.2f} %")
    col3.metric("Sharpe", f"{metrics['sharpe']:.2f}")
    col4.metric("Max drawdown", f"{metrics['max_drawdown']*100:.2f} %")

    # -----------------------------------------
    # Matrice de corrélation
    # -----------------------------------------
    st.write("### Correlation matrix")
    corr = compute_correlation_matrix(rets)
    st.dataframe(corr.style.format("{:.2f}"))
