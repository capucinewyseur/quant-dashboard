import streamlit as st

st.title("Quant Dashboard - Projet Python, Git, Linux pour Finance")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Module", ["Single Asset", "Portfolio"])

if page == "Single Asset":
    st.subheader("Module Single Asset (Quant A)")
    st.write("Ici viendront les stratégies et backtests sur un actif.")
else:
    st.subheader("Module Portfolio (Quant B)")
    st.write("Ici viendront les simulations de portefeuille multi-actifs.")

