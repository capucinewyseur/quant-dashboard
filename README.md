Quant Dashboard
Project Overview

This project consists of a quantitative finance dashboard developed in Python using Streamlit. It implements a complete quantitative workflow, from market data extraction to strategy backtesting, performance analysis, and automated reporting.

Technical Stack

Language: Python

Framework: Streamlit

Version Control: Git / GitHub

Deployment: AWS (Linux VM)

Scheduling: Cron

Data Sources: Financial market APIs (Alpha Vantage / Yahoo Finance)

Project Structure

The application follows a modular architecture:

Data loading and preprocessing

Technical indicators computation

Trading strategies implementation

Backtesting and performance metrics

Visualization and reporting modules

Quant A — Single Asset Analysis

Quant A focuses on the analysis of a single financial asset (AAPL):

Real-time market data updates (every 5 minutes)

Implementation of Buy & Hold, Momentum, and RSI strategies

Equity curve construction and strategy comparison

Performance metrics: annualized return, volatility, Sharpe ratio, and max drawdown

Simple linear regression price prediction (illustrative purpose only)

Quant B — Multi-Asset Portfolio Analysis

Quant B extends the framework to a multi-asset portfolio:

Portfolio construction (equal-weighted and custom allocations)

Portfolio backtesting and performance evaluation

Risk analysis using correlation matrices

Automated daily performance reports generated via cron jobs

Deployment and Automation

The dashboard is deployed on an AWS cloud infrastructure and remains continuously accessible. Daily reports are automatically generated on the virtual machine without manual intervention.
