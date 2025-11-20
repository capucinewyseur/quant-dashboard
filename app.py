import streamlit as st
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from modules.data import load_asset
from modules.indicators import add_rsi, add_macd, add_sma
from modules.strategies import buy_and_hold, rsi_strategy, momentum_strategy
from modules.backtesting import apply_strategy_returns, build_equity_curves, compute_volatility, compute_sharpe_ratio, compute_max_drawdown, compute_cagr
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
ticker = st.sidebar.text_input("Ticker", "AAPL")

# Sélection de la stratégie dans la sidebar
strategy_name = st.sidebar.selectbox(
    "Strategy",
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
        
        # Nettoyer les NaN - utiliser dropna() sans subset pour éviter les erreurs
        # On nettoie toutes les colonnes NaN, puis on vérifie que return et Position existent
        strat_df = strat_df.dropna()
        
        # Vérifier que les colonnes nécessaires existent après nettoyage
        if len(strat_df) > 0 and 'return' in strat_df.columns and 'Position' in strat_df.columns:
            strat_df = apply_strategy_returns(strat_df, return_col="return", position_col="Position")
            strat_df = build_equity_curves(strat_df, asset_return_col="return", strat_return_col="StrategyReturn")
            
            # Calcul des métriques de performance
            if "StrategyReturn" in strat_df.columns and "Equity_Strategy" in strat_df.columns:
                strat_ret = strat_df["StrategyReturn"].dropna()
                equity_strat = strat_df["Equity_Strategy"].dropna()
                
                if len(strat_ret) > 0 and len(equity_strat) > 0:
                    vol_annual = compute_volatility(strat_ret, periods_per_year=252)
                    sharpe = compute_sharpe_ratio(strat_ret, periods_per_year=252, risk_free_rate=0.0)
                    max_dd = compute_max_drawdown(equity_strat)
                    cagr = compute_cagr(equity_strat, periods_per_year=252)
    
    # Graphique principal : Prix brut + Valeur cumulée de la stratégie
    if 'strat_df' in locals() and "Equity_Strategy" in strat_df.columns:
        st.subheader(f"Main Chart - {ticker} Price vs Strategy Performance ({strategy_name})")
        
        fig = go.Figure()
        
        # Courbe 1 : Prix brut de l'actif (axe Y gauche)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            mode='lines',
            name=f'{ticker} Price',
            line=dict(color='#1f77b4', width=2),
            yaxis='y'
        ))
        
        # Courbe 2 : Valeur cumulée de la stratégie (axe Y droit)
        fig.add_trace(go.Scatter(
            x=strat_df.index,
            y=strat_df["Equity_Strategy"],
            mode='lines',
            name=f'Equity {strategy_name}',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2'
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
                title=dict(text="Valeur cumulée (Equity)", font=dict(color='#2ca02c')),
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
            if 'vol_annual' in locals() and 'sharpe' in locals() and 'max_dd' in locals() and 'cagr' in locals():
                st.subheader("Métriques de performance de la stratégie")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Volatilité annualisée", f"{vol_annual:.2%}")
                
                with col2:
                    sharpe_display = f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A"
                    st.metric("Ratio de Sharpe", sharpe_display)
                
                with col3:
                    max_dd_display = f"{max_dd:.2%}" if not np.isnan(max_dd) else "N/A"
                    st.metric("Max Drawdown", max_dd_display)
                
                with col4:
                    cagr_display = f"{cagr:.2%}" if not np.isnan(cagr) else "N/A"
                    st.metric("CAGR", cagr_display)
    
    # Bloc KPIs simples (prix actuel, rendement jour, vol 20j)
    st.markdown("---")
    st.subheader("KPIs du jour")
    last_price = float(df["Close"].iloc[-1])
    daily_ret = float(df["return"].iloc[-1])
    vol_20d = float(df["return"].rolling(20).std().iloc[-1]) * np.sqrt(252)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Dernier prix", f"${last_price:.2f}")
    col2.metric("Rendement jour", f"{daily_ret:.2%}")
    col3.metric("Vol 20j annualisée", f"{vol_20d:.2%}")
    
    # Afficher aussi le module détaillé avec le ticker sélectionné
    display_single_asset_module(ticker)
else:
    display_portfolio_module()

