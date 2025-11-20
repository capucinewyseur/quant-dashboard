import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh
from modules.data import load_asset
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

st.sidebar.header("Navigation")
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])

# Sélection du ticker dans la sidebar
ticker = st.sidebar.text_input("Ticker", "AAPL")

if page == "Single Asset":
    # Chargement des données avec le ticker sélectionné
    df = load_asset(ticker)
    
    st.subheader(f"Prix de {ticker}")
    st.line_chart(df["Close"])
    
    # Bloc KPIs
    last_price = df["Close"].iloc[-1]
    daily_ret = df["return"].iloc[-1]
    vol_20d = df["return"].rolling(20).std().iloc[-1] * np.sqrt(252)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Dernier prix", f"{last_price:.2f}")
    col2.metric("Rendement jour", f"{daily_ret:.2%}")
    col3.metric("Vol 20j annualisée", f"{vol_20d:.2%}")
    
    # Afficher aussi le module détaillé avec le ticker sélectionné
    display_single_asset_module(ticker)
else:
    display_portfolio_module()

