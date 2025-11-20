import streamlit as st
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
    
    # Afficher aussi le module détaillé avec le ticker sélectionné
    display_single_asset_module(ticker)
else:
    display_portfolio_module()

