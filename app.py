import streamlit as st
from streamlit_autorefresh import st_autorefresh
from modules.single_asset import display_single_asset_module
from modules.portfolio import display_portfolio_module

# Configuration de la page
st.set_page_config(
    page_title="Quant Dashboard",
    page_icon="📊",
    layout="wide"
)

# Rafraîchissement automatique toutes les 5 minutes (300000 millisecondes)
st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")

st.title("📊 Quant Dashboard - Projet Python, Git, Linux pour Finance")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])

if page == "Single Asset":
    display_single_asset_module()
else:
    display_portfolio_module()

