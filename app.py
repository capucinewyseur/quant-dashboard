import streamlit as st
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from modules.data import load_asset
from modules.indicators import add_rsi, add_macd, add_sma
from modules.strategies import buy_and_hold, rsi_strategy, momentum_strategy
from modules.backtesting import (apply_strategy_returns, build_equity_curves, 
                                 compute_returns, apply_strategy_position, compute_cumulative_returns,
                                 backtest_complete,
                                 compute_volatility, compute_sharpe_ratio, compute_max_drawdown, compute_cagr)
from modules.single_asset import display_single_asset_module
from modules.portfolio import display_portfolio_module

# Configuration de la page
st.set_page_config(
    page_title="Quant Dashboard",
    layout="wide"
)

# Rafraîchissement automatique toutes les 5 minutes (300000 millisecondes)
st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

st.title("Quant Dashboard - Python, Git, Linux Project for Finance")
st.caption("Quantitative analysis dashboard for finance")

st.sidebar.header("Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])
st.sidebar.markdown("---")

# Sélection du ticker dans la sidebar
st.sidebar.subheader("Asset Selection")
ticker_options = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "JNJ"]
ticker_selected = st.sidebar.selectbox("Select Ticker", ticker_options, index=0)
ticker_custom = st.sidebar.text_input("Or enter custom ticker", "")
ticker = ticker_custom if ticker_custom else ticker_selected

# Sélection de la périodicité
st.sidebar.markdown("---")
periodicity = st.sidebar.selectbox(
    "Periodicity",
    ["Daily", "Weekly", "Monthly"],
    index=0
)

# Mapping périodicité vers interval
periodicity_map = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo"
}
interval = periodicity_map[periodicity]

# Sélection de la stratégie dans la sidebar
st.sidebar.markdown("---")
strategy_name = st.sidebar.selectbox(
    "Strategy",
    ["Buy & Hold", "RSI strategy", "Momentum strategy"]
)

if page == "Single Asset":
    # Chargement des données avec le ticker et la périodicité sélectionnés
    df = load_asset(ticker, interval=interval)
    
    # Ajout des indicateurs techniques
    rsi_window = st.sidebar.slider("RSI window", 5, 30, 14)
    df = add_rsi(df, window=rsi_window)
    df = add_macd(df)
    df = add_sma(df, window=20)
    
    # Application de la stratégie sélectionnée
    if strategy_name == "Buy & Hold":
        strat_df = buy_and_hold(df)
    elif strategy_name == "RSI strategy":
        rsi_low = st.sidebar.slider("RSI low", 10, 40, 30)
        rsi_high = st.sidebar.slider("RSI high", 60, 90, 70)
        strat_df = rsi_strategy(df, low=rsi_low, high=rsi_high)
    else:
        momentum_period = st.sidebar.slider("Momentum period", 5, 50, 12)
        strat_df = momentum_strategy(df, period=momentum_period)
    
    # Backtesting complet : calculer les retours, appliquer la stratégie, construire les courbes
    if 'strat_df' in locals():
        # Utiliser la fonction complète de backtesting
        strat_df = backtest_complete(strat_df, 
                                     position_col="Position",
                                     price_col="Close",
                                     return_col="return",
                                     initial_capital=1.0)
        
        # Calcul des métriques de performance
        if "StrategyReturn" in strat_df.columns and "Equity_Strategy" in strat_df.columns:
            strat_ret = strat_df["StrategyReturn"].dropna()
            equity_strat = strat_df["Equity_Strategy"].dropna()
            
            if len(strat_ret) > 0 and len(equity_strat) > 0:
                # Déterminer periods_per_year selon la périodicité
                periods_map = {
                    "Daily": 252,
                    "Weekly": 52,
                    "Monthly": 12
                }
                periods_per_year = periods_map.get(periodicity, 252)
                
                vol_annual = compute_volatility(strat_ret, periods_per_year=periods_per_year)
                sharpe = compute_sharpe_ratio(strat_ret, periods_per_year=periods_per_year, risk_free_rate=0.0)
                max_dd = compute_max_drawdown(equity_strat)
                cagr = compute_cagr(equity_strat, periods_per_year=periods_per_year)
    
    # Graphique principal : Prix brut + Valeur cumulée de la stratégie (OBLIGATOIRE)
    # Ce graphique doit afficher 2 courbes :
    # 1. Prix brut de l'actif (axe Y gauche)
    # 2. Valeur cumulée de la stratégie (axe Y droit)
    if 'strat_df' in locals() and "Equity_Strategy" in strat_df.columns:
        st.markdown("---")
        st.subheader(f"📊 Main Chart - Raw Asset Price vs Cumulative Strategy Value")
        st.caption(f"Asset: {ticker} | Strategy: {strategy_name}")
        
        fig = go.Figure()
        
        # Courbe 1 : Prix brut de l'actif (OBLIGATOIRE - axe Y gauche)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            mode='lines',
            name=f'Raw Price - {ticker}',
            line=dict(color='#1f77b4', width=3),
            yaxis='y',
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
        ))
        
        # Courbe 2 : Valeur cumulée de la stratégie (OBLIGATOIRE - axe Y droit)
        fig.add_trace(go.Scatter(
            x=strat_df.index,
            y=strat_df["Equity_Strategy"],
            mode='lines',
            name=f'Cumulative Strategy Value - {strategy_name}',
            line=dict(color='#2ca02c', width=3),
            yaxis='y2',
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Cumulative Value: %{y:.4f}<extra></extra>'
        ))
        
        # Configuration avec deux axes Y
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
    
    st.subheader(f"{ticker} Price")
    st.line_chart(df["Close"])
    
    st.subheader("RSI")
    st.line_chart(df["RSI"])
    
    # Affichage des positions de la stratégie
    if 'strat_df' in locals():
        st.subheader("Strategy Positions")
        st.line_chart(strat_df["Position"])
        
        # Affichage des equity curves
        if "Equity_Asset" in strat_df.columns and "Equity_Strategy" in strat_df.columns:
            st.subheader("Equity Curves - Strategy vs Buy & Hold Comparison")
            st.line_chart(strat_df[["Equity_Asset", "Equity_Strategy"]])
            
            # Affichage des métriques de performance
            if 'vol_annual' in locals() and 'sharpe' in locals() and 'max_dd' in locals() and 'cagr' in locals():
                st.subheader("Strategy Performance Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Annualized Volatility", f"{vol_annual:.2%}")
                
                with col2:
                    sharpe_display = f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A"
                    st.metric("Sharpe Ratio", sharpe_display)
                
                with col3:
                    max_dd_display = f"{max_dd:.2%}" if not np.isnan(max_dd) else "N/A"
                    st.metric("Max Drawdown", max_dd_display)
                
                with col4:
                    cagr_display = f"{cagr:.2%}" if not np.isnan(cagr) else "N/A"
                    st.metric("CAGR", cagr_display)
    
    # Bloc KPIs simples (prix actuel, rendement jour, vol 20j)
    st.markdown("---")
    st.subheader("Daily KPIs")
    last_price = float(df["Close"].iloc[-1])
    daily_ret = float(df["return"].iloc[-1])
    vol_20d = float(df["return"].rolling(20).std().iloc[-1]) * np.sqrt(252)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Last Price", f"${last_price:.2f}")
    col2.metric("Daily Return", f"{daily_ret:.2%}")
    col3.metric("20d Annualized Vol", f"{vol_20d:.2%}")
    
    # Afficher aussi le module détaillé avec le ticker sélectionné
    display_single_asset_module(ticker)
else:
    display_portfolio_module()

