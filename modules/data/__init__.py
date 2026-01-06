# modules/data/__init__.py

from typing import List, Optional
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

# Import pour le module Quant B (multi-actifs)
from .multi_asset_loader import load_multi_asset_prices, DEFAULT_TICKERS


def load_asset(
    ticker: str,
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    period: str = "5y",
) -> pd.DataFrame:
    """
    Charge les données d'un seul actif (utilisé par le module Single Asset / Quant A).

    Peut être appelé soit avec:
    - load_asset(ticker, interval="1d", period="5y")
    - load_asset(ticker, start="2018-01-01", end="2024-01-01", interval="1d")

    Parameters
    ----------
    ticker : str
        Ticker Yahoo Finance (ex: "AAPL", "MSFT", "EURUSD=X").
    interval : str
        "1d", "1wk", "1mo", etc.
    start : str ou None
        Date de début (ex: "2018-01-01"). Si fourni, on ignore `period`.
    end : str ou None
        Date de fin. Si None, yfinance prendra "aujourd'hui".
    period : str
        Fenêtre d'historique si `start` n'est pas fourni (ex: "5y", "2y").

    Returns
    -------
    DataFrame contenant au minimum :
        - 'Close' : prix de clôture
        - 'return' : rendement simple (Close_t / Close_{t-1} - 1)
    """
    # Si une date de début est fournie → on utilise start/end
    if start is not None or end is not None:
        df = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
    else:
        # Sinon on utilise `period` (comportement par défaut)
        df = yf.download(
            ticker,
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False,
        )

    if df.empty:
        return df

    # S'assurer qu'on a une colonne 'Close'
    if isinstance(df.columns, pd.MultiIndex):
        if "Adj Close" in df.columns.get_level_values(0):
            close = df["Adj Close"].copy()
        else:
            close = df.xs("Close", axis=1, level=0).copy()
    else:
        if "Adj Close" in df.columns:
            close = df["Adj Close"].copy()
        else:
            close = df["Close"].copy()

    df = df.copy()
    df["Close"] = close

    # Rendement simple
    df["return"] = df["Close"].pct_change()

    return df



__all__ = ["load_asset", "load_multi_asset_prices", "DEFAULT_TICKERS"]
