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
                                 compute_volatility, compute_sharpe_ratio, compute_max_drawdown, compute_cagr, compute_total_return)
from modules.prediction import predict_future_prices_simple
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
        vol_annual = None
        sharpe = None
        max_dd = None
        cagr = None
        total_return = None
        
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
                total_return = compute_total_return(equity_strat)
    
    # Graphique principal : Prix brut + Valeur cumulée de la stratégie (OBLIGATOIRE)
    # Ce graphique doit afficher 2 courbes :
    # 1. Prix brut de l'actif (axe Y gauche)
    # 2. Valeur cumulée de la stratégie (axe Y droit)
    if 'strat_df' in locals() and "Equity_Strategy" in strat_df.columns:
        st.markdown("---")
        st.subheader(f"Main Chart - Raw Asset Price vs Cumulative Strategy Value")
        st.caption(f"Asset: {ticker} | Strategy: {strategy_name}")
        
        # Step 3: Calculate predictions
        predictions = predict_future_prices_simple(df, days_ahead=30, price_col="Close")
        
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
        
        # Step 3: Add predictions if available
        if not predictions.empty:
            # Step 4: Add confidence interval (upper bound)
            fig.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions['Upper_Bound'],
                mode='lines',
                name='Upper Confidence',
                line=dict(color='rgba(255, 127, 14, 0.3)', width=1),
                yaxis='y',
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Step 4: Add confidence interval (lower bound with fill)
            fig.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions['Lower_Bound'],
                mode='lines',
                name='Confidence Interval',
                fill='tonexty',
                fillcolor='rgba(255, 127, 14, 0.1)',
                line=dict(color='rgba(255, 127, 14, 0.3)', width=1),
                yaxis='y',
                hovertemplate='<b>Confidence Interval</b><br>Date: %{x}<br>Lower: $%{y:.2f}<extra></extra>'
            ))
            
            # Prediction line
            fig.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions['Predicted_Price'],
                mode='lines',
                name='Predicted Price (30 days)',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                yaxis='y',
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Predicted: $%{y:.2f}<extra></extra>'
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
        
        # Bonus: Separate prediction chart
        if not predictions.empty:
            st.markdown("---")
            st.subheader("Price Prediction - 30 Days Forecast")
            st.caption(f"Simple Linear Regression Model | Asset: {ticker}")
            
            fig_pred = go.Figure()
            
            # Historical prices (last 60 days for context)
            recent_df = df.tail(60)
            fig_pred.add_trace(go.Scatter(
                x=recent_df.index,
                y=recent_df["Close"],
                mode='lines',
                name=f'Historical Price - {ticker}',
                line=dict(color='#1f77b4', width=2),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ))
            
            # Prediction line
            fig_pred.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions['Predicted_Price'],
                mode='lines',
                name='Predicted Price',
                line=dict(color='#ff7f0e', width=3, dash='dash'),
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Predicted: $%{y:.2f}<extra></extra>'
            ))
            
            # Confidence interval upper
            fig_pred.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions['Upper_Bound'],
                mode='lines',
                name='Upper Bound',
                line=dict(color='rgba(255, 127, 14, 0.3)', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Confidence interval lower (filled)
            fig_pred.add_trace(go.Scatter(
                x=predictions.index,
                y=predictions['Lower_Bound'],
                mode='lines',
                name='Confidence Interval (95%)',
                fill='tonexty',
                fillcolor='rgba(255, 127, 14, 0.15)',
                line=dict(color='rgba(255, 127, 14, 0.3)', width=1),
                hovertemplate='<b>Confidence Interval</b><br>Date: %{x}<br>Lower: $%{y:.2f}<extra></extra>'
            ))
            
            # Vertical line to separate historical from prediction
            last_historical_date = recent_df.index[-1]
            # Convert Timestamp to string for Plotly compatibility
            fig_pred.add_vline(
                x=str(last_historical_date),
                line_dash="dot",
                line_color="gray",
                annotation_text="Today",
                annotation_position="top"
            )
            
            fig_pred.update_layout(
                title=f"{ticker} Price Prediction - Linear Regression Model",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                hovermode='x unified',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_pred, use_container_width=True)
            
            # Display prediction summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Predicted Price (30 days)", f"${predictions['Predicted_Price'].iloc[-1]:.2f}")
            with col2:
                current_price = float(df["Close"].iloc[-1])
                predicted_price = float(predictions['Predicted_Price'].iloc[-1])
                change_pct = ((predicted_price - current_price) / current_price) * 100
                st.metric("Expected Change (30d)", f"{change_pct:.2f}%")
            with col3:
                confidence_range = float(predictions['Upper_Bound'].iloc[-1] - predictions['Lower_Bound'].iloc[-1])
                st.metric("Confidence Range", f"${confidence_range:.2f}")
    
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
            if vol_annual is not None and sharpe is not None and max_dd is not None and cagr is not None and total_return is not None:
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

