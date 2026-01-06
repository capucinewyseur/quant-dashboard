import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

from modules.data import load_asset
from modules.indicators import add_rsi, add_macd, add_sma
from modules.strategies import buy_and_hold, rsi_strategy, momentum_strategy
from modules.backtesting import (apply_strategy_returns, build_equity_curves,
                                 compute_returns, apply_strategy_position, compute_cumulative_returns,
                                 backtest_complete,
                                 compute_volatility, compute_sharpe_ratio, compute_max_drawdown, compute_cagr, compute_total_return)
from modules.prediction import predict_future_prices_simple
from modules.single_asset import display_single_asset_module
from modules.portfolio import display_portfolio_module


#put the docstring in a function so it doesn't appear in the streamlit app
def comment():
    """
    Quant Dashboard (Streamlit App Entry Point)

    This file is the main Streamlit application that provides two modules:
    - Single Asset: technical indicators, strategy signals, backtesting, and performance metrics
    - Portfolio: multi-asset portfolio module (handled in modules.portfolio)

    The app is structured as follows:
    1) Global Streamlit configuration (page layout + auto-refresh)
    2) Sidebar navigation between modules (Single Asset vs Portfolio)
    3) Single Asset workflow:
   - Select ticker and data periodicity
   - Load data and compute indicators (RSI, MACD, SMA)
   - Generate strategy positions (Buy & Hold / RSI / Momentum)
   - Run a backtest (equity curves + strategy returns)
   - Display charts and risk/performance metrics
    4) Portfolio workflow:
   - Delegated to display_portfolio_module()

    Notes
    -----
    - backtest_complete() is expected to add/compute columns such as:
  'StrategyReturn', 'Equity_Strategy', and sometimes 'Equity_Asset'.
    - Some functions may return DataFrames with MultiIndex columns; these are flattened
  to ensure compatibility with Streamlit plotting functions.
    """


# Configuration de la page
st.set_page_config(
    page_title="Quant Dashboard",
    layout="wide"
)

# Auto-refresh every 5 minutes (300000 milliseconds)
st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

st.title("Quant Dashboard - Python, Git, Linux Project for Finance")
st.caption("Quantitative analysis dashboard for finance")

# Main navigation
st.sidebar.header("Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])
st.sidebar.markdown("---")

#Single asset Mode
if page == "Single Asset":
    # --------- Sidebar : paramètres single asset ----------
    st.sidebar.subheader("Asset Selection")
    ticker_options = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
                      "META", "NVDA", "JPM", "V", "JNJ"]
    ticker_selected = st.sidebar.selectbox("Select Ticker", ticker_options, index=0)
    ticker_custom = st.sidebar.text_input("Or enter custom ticker", "")
    ticker = ticker_custom if ticker_custom else ticker_selected

    st.sidebar.markdown("---")
    periodicity = st.sidebar.selectbox(
        "Periodicity",
        ["Daily", "Weekly", "Monthly"],
        index=0
    )

    periodicity_map = {
        "Daily": "1d",
        "Weekly": "1wk",
        "Monthly": "1mo"
    }
    interval = periodicity_map[periodicity]

    st.sidebar.markdown("---")
    strategy_name = st.sidebar.selectbox(
        "Strategy",
        ["Buy & Hold", "RSI strategy", "Momentum strategy"]
    )

    # loading data on single asset mode
    df = load_asset(ticker, interval=interval)

    # Add technical indicators
    rsi_window = st.sidebar.slider("RSI window", 5, 30, 14)
    df = add_rsi(df, window=rsi_window)
    df = add_macd(df)
    df = add_sma(df, window=20)

    # Apply selected strategy
    if strategy_name == "Buy & Hold":
        strat_df = buy_and_hold(df)
    elif strategy_name == "RSI strategy":
        rsi_low = st.sidebar.slider("RSI low", 10, 40, 30)
        rsi_high = st.sidebar.slider("RSI high", 60, 90, 70)
        strat_df = rsi_strategy(df, low=rsi_low, high=rsi_high)
    else:
        momentum_period = st.sidebar.slider("Momentum period", 5, 50, 12)
        strat_df = momentum_strategy(df, period=momentum_period)

# Backtesting complet
if 'strat_df' in locals():
    strat_df = backtest_complete(
        strat_df,
        position_col="Position",
        price_col="Close",
        return_col="return",
        initial_capital=1.0
    )

    # flatten MultiIndex columns if needed because Streamlit expects flat columns
    if isinstance(strat_df.columns, pd.MultiIndex):
        strat_df.columns = [
            c[0] if isinstance(c, tuple) else c
            for c in strat_df.columns
        ]

    vol_annual = None
    sharpe = None
    max_dd = None
    cagr = None
    total_return = None

    if "StrategyReturn" in strat_df.columns and "Equity_Strategy" in strat_df.columns:
        strat_ret = strat_df["StrategyReturn"].dropna()
        equity_strat = strat_df["Equity_Strategy"].dropna()

        if len(strat_ret) > 0 and len(equity_strat) > 0:
            periods_map = {
                "Daily": 252,
                "Weekly": 52,
                "Monthly": 12
            }
            periods_per_year = periods_map.get(periodicity, 252)

            vol_annual = compute_volatility(strat_ret, periods_per_year=periods_per_year)
            sharpe = compute_sharpe_ratio(
                strat_ret,
                periods_per_year=periods_per_year,
                risk_free_rate=0.0
            )
            max_dd = compute_max_drawdown(equity_strat)
            cagr = compute_cagr(equity_strat, periods_per_year=periods_per_year)
            total_return = compute_total_return(equity_strat)

    # main graph : price vs strategy
    if 'strat_df' in locals() and "Equity_Strategy" in strat_df.columns:
        st.markdown("---")
        st.subheader("Main Chart - Raw Asset Price vs Cumulative Strategy Value")
        st.caption(f"Asset: {ticker} | Strategy: {strategy_name}")

        # Calculate price predictions
        predictions = predict_future_prices_simple(df, days_ahead=30, price_col="Close")

        fig = go.Figure()

        # raw price
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            mode='lines',
            name=f'Raw Price - {ticker}',
            line=dict(color='#1f77b4', width=3),
            yaxis='y',
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
        ))

        # cummulative value of strat
        fig.add_trace(go.Scatter(
            x=strat_df.index,
            y=strat_df["Equity_Strategy"],
            mode='lines',
            name=f'Cumulative Strategy Value - {strategy_name}',
            line=dict(color='#2ca02c', width=3),
            yaxis='y2',
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Cumulative Value: %{y:.4f}<extra></extra>'
        ))

        # Chart configuration with dual Y-axes
        fig.update_layout(
            title=f"Raw Price vs Strategy Performance ({strategy_name})",
            xaxis_title="Date",
            yaxis=dict(
                title=dict(text="Price (USD)", font=dict(color='#1f77b4')),
                tickfont=dict(color='#1f77b4')
            ),
            yaxis2=dict(
                title=dict(text="Cumulative Value (Equity)", font=dict(color='#2ca02c')),
                tickfont=dict(color='#2ca02c'),
                anchor='x',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=500,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    # secondary graphs
    st.subheader(f"{ticker} Price")
    st.line_chart(df["Close"])

    st.subheader("RSI")
    st.line_chart(df["RSI"])

    # Display strategy positions
    if 'strat_df' in locals():
        st.subheader("Strategy Positions")
        st.line_chart(strat_df["Position"])

        # equity curves
        if all(col in strat_df.columns for col in ["Equity_Asset", "Equity_Strategy"]):
            st.subheader("Equity Curves - Strategy vs Buy & Hold Comparison")
            st.line_chart(strat_df[["Equity_Asset", "Equity_Strategy"]])
        else:
            st.info("Equity curves are not available for this configuration.")

            if all(v is not None for v in [vol_annual, sharpe, max_dd, cagr, total_return]):
                st.markdown("---")
                st.subheader("Strategy Performance Metrics")
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("Sharpe Ratio", f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")
                with col2:
                    max_dd_display = f"{max_dd:.2%}" if not np.isnan(max_dd) else "N/A"
                    st.metric("Max Drawdown", max_dd_display)
                with col3:
                    st.metric("Annualized Volatility", f"{vol_annual:.2%}")
                with col4:
                    cagr_display = f"{cagr:.2%}" if not np.isnan(cagr) else "N/A"
                    st.metric("CAGR", cagr_display)
                with col5:
                    total_return_display = f"{total_return:.2%}" if not np.isnan(total_return) else "N/A"
                    st.metric("Total Return", total_return_display)

    # KPIs daily
    st.markdown("---")
    st.subheader("Daily KPIs")
    last_price = float(df["Close"].iloc[-1])
    daily_ret = float(df["return"].iloc[-1])
    vol_20d = float(df["return"].rolling(20).std().iloc[-1]) * np.sqrt(252)

    col1, col2, col3 = st.columns(3)
    col1.metric("Last Price", f"${last_price:.2f}")
    col2.metric("Daily Return", f"{daily_ret:.2%}")
    col3.metric("20d Annualized Vol", f"{vol_20d:.2%}")

    # Display detailed single asset module
    display_single_asset_module(ticker)
else:
    display_portfolio_module()

#PORTFOLIO MODE
