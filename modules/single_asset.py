import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

def get_apple_data(period="1d", interval="1m"):
    """
    Récupère les données de l'action Apple depuis Yahoo Finance
    
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

def display_single_asset_module():
    """
    Affiche le module d'analyse d'un actif unique (Apple)
    """
    st.header("Analyse de l'action Apple (AAPL)")
    
    # Afficher le statut de mise à jour
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dernière mise à jour", datetime.now().strftime("%H:%M:%S"))
    
    # Récupération du prix actuel
    current_price = get_current_price()
    with col2:
        st.metric("Prix actuel (USD)", f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price)
    
    # Récupération des données historiques
    with st.spinner("Récupération des données en cours..."):
        data = get_apple_data(period="5d", interval="15m")
    
    if not data.empty:
        # Afficher les statistiques clés
        st.subheader("Statistiques clés")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            latest_close = data['Close'].iloc[-1]
            st.metric("Dernier cours", f"${latest_close:.2f}")
        
        with col2:
            daily_change = data['Close'].iloc[-1] - data['Open'].iloc[-1]
            daily_change_pct = (daily_change / data['Open'].iloc[-1]) * 100
            st.metric("Variation journalière", f"${daily_change:.2f}", f"{daily_change_pct:.2f}%")
        
        with col3:
            high_24h = data['High'].tail(96).max()  # Max sur 24h (96 * 15min)
            st.metric("Max 24h", f"${high_24h:.2f}")
        
        with col4:
            low_24h = data['Low'].tail(96).min()  # Min sur 24h
            st.metric("Min 24h", f"${low_24h:.2f}")
        
        # Graphique de série temporelle
        st.subheader("Graphique de série temporelle")
        
        fig = go.Figure()
        
        # Ligne de prix de clôture
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Prix de clôture',
            line=dict(color='#1f77b4', width=2)
        ))
        
        # Ligne de prix d'ouverture
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Open'],
            mode='lines',
            name='Prix d\'ouverture',
            line=dict(color='#ff7f0e', width=1, dash='dash')
        ))
        
        fig.update_layout(
            title="Évolution du prix de l'action Apple (AAPL)",
            xaxis_title="Date/Heure",
            yaxis_title="Prix (USD)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des dernières données
        st.subheader("Dernières données")
        st.dataframe(
            data.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']].style.format({
                'Open': '${:.2f}',
                'High': '${:.2f}',
                'Low': '${:.2f}',
                'Close': '${:.2f}',
                'Volume': '{:,.0f}'
            }),
            use_container_width=True
        )
        
    else:
        st.warning("Aucune donnée disponible pour le moment.")
    
    # Message sur le rafraîchissement automatique
    st.info("Les données se mettent à jour automatiquement toutes les 5 minutes")
