# Quant Dashboard

## Project Presentation

This project consists in the development of a **quantitative finance dashboard** in Python, built with **Streamlit**, enabling financial data analysis, trading strategy backtesting, and automated report generation.

The objective is to implement a **modular architecture** reproducing a complete quantitative workflow: data extraction, processing, indicators, strategies, performance evaluation, and visual reporting.

---

## Environment and Tools

- **Language**: Python  
- **Interface**: Streamlit  
- **Version Control**: Git / GitHub  
- **Deployment**: AWS (Linux virtual machine)  
- **Scheduling**: Cron  
- **Data Sources**: Financial APIs (Alpha Vantage / Yahoo Finance)

A Python virtual environment was used to isolate project dependencies.

## Quant A — Single Asset Analysis

The **Quant A** module is dedicated to the analysis of a single financial asset (Apple – AAPL).

### Main features
- Automatic market data retrieval (updated every 5 minutes)
- Price and return visualization
- Quantitative strategy implementation:
  - Buy & Hold  
  - Momentum  
  - RSI  
- Performance metrics computation:
  - Annualized return  
  - Volatility  
  - Sharpe ratio  
  - Maximum drawdown  
- Technical indicators display (RSI, moving averages)
- Simple linear regression price prediction (illustrative purpose only)

---

## Quant B — Multi-Asset Portfolio Analysis

The **Quant B** module extends the analysis to a portfolio composed of multiple assets.

### Main features
- Real-time monitoring of multiple asset prices
- Portfolio construction:
  - Equal-weighted portfolio  
  - Custom-weight portfolios  
- Portfolio value simulation over time
- Full portfolio backtesting
- Automatic computation of performance metrics:
  - Annualized return  
  - Volatility  
  - Sharpe ratio  
  - Maximum drawdown  
- Diversification analysis using a correlation matrix
- Automated daily report generation (scheduled on the AWS virtual machine)

---

## Deployment and Automation

The application is deployed on an **AWS cloud infrastructure**, allowing remote access to the Streamlit dashboard.  
Cron jobs are configured to automatically generate daily text-based reports without manual intervention.

---

## Collaborative Development

The project was developed collaboratively using Git:

- **main** branch: stable version  
- Development branches:
  - `emile` (Quant A)
  - `ptAcapucine` (Quant B)

All merges were performed after feature validation.
