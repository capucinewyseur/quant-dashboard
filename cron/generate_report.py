#!/usr/bin/env python3
"""
Daily Report Generator for Quant Dashboard

This script generates a daily report with key metrics:
- Volatility
- Open/Close prices
- Sharpe ratio
- Max Drawdown

The report is saved in reports/YYYY-MM-DD.txt
"""

import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.data import load_asset
from modules.indicators import add_rsi, add_macd, add_sma
from modules.strategies import buy_and_hold
from modules.backtesting import (
    backtest_complete,
    compute_volatility,
    compute_sharpe_ratio,
    compute_max_drawdown,
    compute_cagr,
    compute_total_return
)

def generate_daily_report(ticker="AAPL", output_dir="reports"):
    """
    Generate a daily report for the specified ticker.
    
    Args:
        ticker: Stock ticker symbol (default: "AAPL")
        output_dir: Directory to save reports (default: "reports")
    """
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get today's date for filename
    today = datetime.now().strftime("%Y-%m-%d")
    report_filename = os.path.join(output_dir, f"{today}.txt")
    
    try:
        # Load asset data
        print(f"Loading data for {ticker}...")
        df = load_asset(ticker, start="2018-01-01", interval="1d")
        
        if df.empty:
            error_msg = f"ERROR: No data available for {ticker}\n"
            with open(report_filename, 'w') as f:
                f.write(error_msg)
            print(error_msg)
            return
        
        # Add technical indicators
        df = add_rsi(df, window=14)
        df = add_macd(df)
        df = add_sma(df, window=20)
        
        # Apply Buy & Hold strategy (benchmark)
        strat_df = buy_and_hold(df)
        
        # Run backtesting
        strat_df = backtest_complete(
            strat_df,
            position_col="Position",
            price_col="Close",
            return_col="return",
            initial_capital=1.0
        )
        
        # Calculate metrics
        if "StrategyReturn" in strat_df.columns and "Equity_Strategy" in strat_df.columns:
            strat_ret = strat_df["StrategyReturn"].dropna()
            equity_strat = strat_df["Equity_Strategy"].dropna()
            
            if len(strat_ret) > 0 and len(equity_strat) > 0:
                # Volatility (annualized)
                vol_annual = compute_volatility(strat_ret, periods_per_year=252)
                
                # Sharpe ratio
                sharpe = compute_sharpe_ratio(strat_ret, periods_per_year=252, risk_free_rate=0.0)
                
                # Max Drawdown
                max_dd = compute_max_drawdown(equity_strat)
                
                # CAGR
                cagr = compute_cagr(equity_strat, periods_per_year=252)
                
                # Total Return
                total_return = compute_total_return(equity_strat)
                
                # Get latest prices
                latest_open = float(df["Open"].iloc[-1])
                latest_close = float(df["Close"].iloc[-1])
                latest_date = df.index[-1].strftime("%Y-%m-%d")
                
                # Generate report content
                report_content = f"""
================================================================================
QUANT DASHBOARD - DAILY REPORT
================================================================================
Date: {today}
Ticker: {ticker}
Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

================================================================================
PRICE DATA
================================================================================
Latest Date: {latest_date}
Open Price: ${latest_open:.2f}
Close Price: ${latest_close:.2f}
Daily Change: ${latest_close - latest_open:.2f} ({(latest_close/latest_open - 1)*100:.2f}%)

================================================================================
PERFORMANCE METRICS
================================================================================
Annualized Volatility: {vol_annual:.2%}
Sharpe Ratio: {sharpe:.2f} (N/A if NaN)
Max Drawdown: {max_dd:.2%}
CAGR: {cagr:.2%}
Total Return: {total_return:.2%}

================================================================================
DATA SUMMARY
================================================================================
Total Data Points: {len(df)}
Date Range: {df.index[0].strftime("%Y-%m-%d")} to {df.index[-1].strftime("%Y-%m-%d")}
Period: {(df.index[-1] - df.index[0]).days} days

================================================================================
END OF REPORT
================================================================================
"""
                
                # Write report to file
                with open(report_filename, 'w') as f:
                    f.write(report_content)
                
                print(f"Report generated successfully: {report_filename}")
                print(report_content)
                
            else:
                error_msg = f"ERROR: Insufficient data for calculations\n"
                with open(report_filename, 'w') as f:
                    f.write(error_msg)
                print(error_msg)
        else:
            error_msg = f"ERROR: Backtesting failed - missing columns\n"
            with open(report_filename, 'w') as f:
                f.write(error_msg)
            print(error_msg)
            
    except Exception as e:
        error_msg = f"ERROR: Failed to generate report: {str(e)}\n"
        with open(report_filename, 'w') as f:
            f.write(error_msg)
        print(error_msg)
        raise

if __name__ == "__main__":
    # Default ticker is AAPL, but can be overridden via command line
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    generate_daily_report(ticker=ticker)
