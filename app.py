import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh
from modules.data import load_asset
from modules.indicators import add_rsi, add_macd, add_sma
from modules.strategies import buy_and_hold, rsi_strategy, momentum_strategy
from modules.backtesting import apply_strategy_returns, build_equity_curves, compute_volatility, compute_sharpe_ratio
from modules.single_asset import display_single_asset_module
from modules.portfolio import display_portfolio_module

# Configuration de la page
st.set_page_config(
    page_title="Quant Dashboard",
    layout="wide"
)

# Rafraîchissement automatique toutes les 5 minutes (300000 millisecondes)
st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

st.title("Quant Dashboard - Projet Python, Git, Linux pour Finance")
st.caption("Dashboard d'analyse quantitative pour la finance")

st.sidebar.header("Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])

# Sélection du ticker dans la sidebar
ticker = st.sidebar.text_input("Ticker", "AAPL")

# Sélection de la stratégie dans la sidebar
strategy_name = st.sidebar.selectbox(
    "Stratégie",
    ["Buy & Hold", "RSI strategy", "Momentum strategy"]
)

if page == "Single Asset":
    # Chargement des données avec le ticker sélectionné
    df = load_asset(ticker)
    
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
    
    # Backtesting : calculer les retours de la stratégie
    if 'strat_df' in locals():
        # S'assurer que la colonne return existe
        if 'return' not in strat_df.columns:
            strat_df["return"] = strat_df["Close"].pct_change()
        
        # Nettoyer les NaN de return seulement (Position sera créée par les stratégies)
        if 'return' in strat_df.columns:
            strat_df = strat_df.dropna(subset=['return'])
        
        # Vérifier que Position existe (créée par les stratégies)
        if 'Position' in strat_df.columns:
            # Nettoyer aussi les NaN de Position si nécessaire
            strat_df = strat_df.dropna(subset=['Position'])
            
            if len(strat_df) > 0 and 'return' in strat_df.columns:
                strat_df = apply_strategy_returns(strat_df, return_col="return", position_col="Position")
                strat_df = build_equity_curves(strat_df, asset_return_col="return", strat_return_col="StrategyReturn")
                
                # Calcul des métriques de performance
                if "StrategyReturn" in strat_df.columns:
                    strat_ret = strat_df["StrategyReturn"].dropna()
                    if len(strat_ret) > 0:
                        vol_annual = compute_volatility(strat_ret, periods_per_year=252)
                        sharpe = compute_sharpe_ratio(strat_ret, periods_per_year=252, risk_free_rate=0.0)
    
    st.subheader(f"Prix de {ticker}")
    st.line_chart(df["Close"])
    
    st.subheader("RSI")
    st.line_chart(df["RSI"])
    
    # Affichage des positions de la stratégie
    if 'strat_df' in locals():
        st.subheader("Positions de la stratégie")
        st.line_chart(strat_df["Position"])
        
        # Affichage des equity curves
        if "Equity_Asset" in strat_df.columns and "Equity_Strategy" in strat_df.columns:
            st.subheader("Equity Curves - Comparaison stratégie vs Buy & Hold")
            st.line_chart(strat_df[["Equity_Asset", "Equity_Strategy"]])
            
            # Affichage des métriques de performance
            if 'vol_annual' in locals() and 'sharpe' in locals():
                st.subheader("Métriques de performance de la stratégie")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Volatilité annualisée", f"{vol_annual:.2%}")
                with col2:
                    sharpe_display = f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A"
                    st.metric("Ratio de Sharpe", sharpe_display)
    
    # Bloc KPIs
    st.markdown("---")
    last_price = float(df["Close"].iloc[-1])
    daily_ret = float(df["return"].iloc[-1])
    vol_20d = float(df["return"].rolling(20).std().iloc[-1]) * np.sqrt(252)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Dernier prix", f"{last_price:.2f}")
    col2.metric("Rendement jour", f"{daily_ret:.2%}")
    col3.metric("Vol 20j annualisée", f"{vol_20d:.2%}")
    
    # Afficher aussi le module détaillé avec le ticker sélectionné
    display_single_asset_module(ticker)
else:
    display_portfolio_module()

