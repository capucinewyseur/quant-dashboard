# modules/data/multi_asset_loader.py

from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pandas as pd
import yfinance as yf

# Default universe for the portfolio module
DEFAULT_TICKERS = ["AAPL", "BTC-USD", "EURUSD=X", "GC=F", "^DJI"]


def _to_list(tickers: str | Iterable[str] | None) -> list[str]:
    if tickers is None:
        return DEFAULT_TICKERS
    if isinstance(tickers, str):
        return [tickers]
    return list(tickers)


def load_multi_asset_prices(
    tickers: str | Iterable[str] | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Download multi-asset prices from Yahoo Finance.

    For daily data ('1d'), we honor start/end.
    For intraday data (e.g. '15m', '30m', '60m', '240m'), Yahoo only allows
    limited history, and behaves better with 'period' instead of start/end,
    so we ignore start/end and use a fixed period (e.g. 60d).

    Returns
    -------
    pd.DataFrame
        index = Datetime (timezone-naive),
        columns = tickers, values = adjusted close.
    """
    tickers_list = _to_list(tickers)

    # Choose download mode depending on interval
    is_daily = interval == "1d"

    if is_daily:
        data = yf.download(
            tickers=tickers_list,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
            progress=False,
            group_by="column",
        )
    else:
        # Intraday mode: use period instead of (start, end).
        # Yahoo typically supports up to ~60 days for 15m data.
        data = yf.download(
            tickers=tickers_list,
            period="60d",
            interval=interval,
            auto_adjust=True,
            progress=False,
            group_by="column",
        )

    if data is None or data.empty:
        return pd.DataFrame()

    # Handle multi-index columns (when multiple tickers)
    if isinstance(data.columns, pd.MultiIndex):
        # We use 'Adj Close' if present, else 'Close'
        if "Adj Close" in data.columns.levels[0]:
            px = data["Adj Close"].copy()
        else:
            px = data["Close"].copy()
    else:
        # Single ticker case -> make it a 1-column dataframe
        if "Adj Close" in data.columns:
            px = data[["Adj Close"]].copy()
        else:
            px = data[["Close"]].copy()
        px.columns = tickers_list

    # Remove timezone if present
    px.index = px.index.tz_localize(None)

    # Ensure columns order matches tickers_list
    px = px.reindex(columns=tickers_list)

    # Sort by date ascending
    px = px.sort_index()

    return px
