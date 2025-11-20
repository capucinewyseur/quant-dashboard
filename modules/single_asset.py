import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np
from modules.data import load_asset

def get_apple_data(period="1d", interval="1m"):
    """
    Récupère les données de l'action Apple depuis Yahoo Finance (pour données récentes)
    
    Args:
        period: Période de données (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Intervalle entre les données (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        DataFrame avec les données OHLCV
    """
    try:
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period=period, interval=interval)
        return data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return pd.DataFrame()

def get_current_price():
    """
    Récupère le prix actuel de l'action Apple
    """
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        return current_price
    except Exception as e:
        st.error(f"Erreur lors de la récupération du prix: {e}")
        return "N/A"

def display_single_asset_module(ticker="AAPL"):
    """
    Affiche le module d'analyse d'un actif unique
    
    Args:
        ticker: Symbole de l'actif à analyser (défaut: "AAPL")
    """
    st.header(f"Analyse de l'action {ticker}")
    
    # Afficher le statut de mise à jour
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dernière mise à jour", datetime.now().strftime("%H:%M:%S"))
    
    # Récupération du prix actuel
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
    except:
        current_price = "N/A"
    
    with col2:
        st.metric("Prix actuel (USD)", f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price)
    
    # Récupération des données historiques avec rendements
    with st.spinner("Récupération des données en cours..."):
        # Données récentes pour l'affichage en temps réel
        try:
            ticker_obj = yf.Ticker(ticker)
            data_recent = ticker_obj.history(period="5d", interval="15m")
        except:
            data_recent = pd.DataFrame()
        # Données historiques avec rendements pour les KPIs
        data = load_asset(ticker, start="2018-01-01", interval="1d")
    
    if not data.empty and not data_recent.empty:
        # Afficher les statistiques clés
        st.subheader("Statistiques clés")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            latest_close = float(data['Close'].iloc[-1])
            st.metric("Dernier cours", f"${latest_close:.2f}")
        
        with col2:
            latest_close_val = float(data['Close'].iloc[-1])
            latest_open_val = float(data['Open'].iloc[-1])
            daily_change = latest_close_val - latest_open_val
            daily_change_pct = (daily_change / latest_open_val) * 100
            st.metric("Variation journalière", f"${daily_change:.2f}", f"{daily_change_pct:.2f}%")
        
        with col3:
            if not data_recent.empty:
                high_24h = float(data_recent['High'].max())
            else:
                high_24h = float(data['High'].iloc[-1])
            st.metric("Max récent", f"${high_24h:.2f}")
        
        with col4:
            if not data_recent.empty:
                low_24h = float(data_recent['Low'].min())
            else:
                low_24h = float(data['Low'].iloc[-1])
            st.metric("Min récent", f"${low_24h:.2f}")
        
        # KPIs sur les rendements
        st.subheader("KPIs sur les rendements")
        
        # Calcul des KPIs
        returns = data['return'].dropna()
        mean_return = float(returns.mean()) * 100  # En pourcentage
        volatility = float(returns.std()) * np.sqrt(252) * 100  # Volatilité annualisée
        sharpe_ratio = float((mean_return / 100 * 252) / (volatility / 100)) if volatility > 0 else 0.0
        max_drawdown = float(((data['Close'] / data['Close'].cummax()) - 1).min()) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rendement moyen annuel", f"{mean_return * 252:.2f}%")
        
        with col2:
            st.metric("Volatilité annualisée", f"{volatility:.2f}%")
        
        with col3:
            st.metric("Ratio de Sharpe", f"{sharpe_ratio:.2f}")
        
        with col4:
            st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
        
        # Graphique de série temporelle - Prix
        st.subheader("Graphique de série temporelle - Prix")
        
        fig_price = go.Figure()
        
        # Ligne de prix de clôture (données historiques)
        fig_price.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Prix de clôture',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig_price.update_layout(
            title=f"Évolution du prix de l'action {ticker}",
            xaxis_title="Date",
            yaxis_title="Prix (USD)",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Graphique de série temporelle - Rendements
        st.subheader("Graphique de série temporelle - Rendements")
        
        fig_returns = go.Figure()
        
        # Ligne des rendements
        fig_returns.add_trace(go.Scatter(
            x=data.index,
            y=data['return'] * 100,
            mode='lines',
            name='Rendements journaliers',
            line=dict(color='#2ca02c', width=1),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.1)'
        ))
        
        # Ligne zéro
        fig_returns.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig_returns.update_layout(
            title=f"Rendements journaliers de l'action {ticker}",
            xaxis_title="Date",
            yaxis_title="Rendement (%)",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_returns, use_container_width=True)
        
        # Tableau des dernières données avec rendements
        st.subheader("Dernières données")
        display_data = data.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume', 'return']].copy()
        display_data['return'] = display_data['return'] * 100  # Convertir en pourcentage
        st.dataframe(
            display_data.style.format({
                'Open': '${:.2f}',
                'High': '${:.2f}',
                'Low': '${:.2f}',
                'Close': '${:.2f}',
                'Volume': '{:,.0f}',
                'return': '{:.2f}%'
            }),
            use_container_width=True
        )
        
    else:
        st.warning("Aucune donnée disponible pour le moment.")
    
    # Message sur le rafraîchissement automatique
    st.info("Les données se mettent à jour automatiquement toutes les 5 minutes")
