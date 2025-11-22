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
    period: str = "5y",
) -> pd.DataFrame:
    """
    Charge les données d'un seul actif (utilisé par le module Single Asset / Quant A).

    Parameters
    ----------
    ticker : str
        Ticker Yahoo Finance (ex: "AAPL", "MSFT", "EURUSD=X").
    interval : str
        "1d", "1wk", "1mo", etc.
    period : str
        Fenêtre d'historique (ex: "5y", "2y", "1y").

    Returns
    -------
    DataFrame contenant au minimum :
        - 'Close' : prix de clôture
        - 'return' : rendement simple (Close_t / Close_{t-1} - 1)
        + toutes les autres colonnes téléchargées (Open, High, Low, Volume...)
    """
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

    # On remet une colonne 'Close' propre dans le DataFrame
    df = df.copy()
    df["Close"] = close

    # Calcul d'un rendement simple de base → utilisé par les KPIs de app.py
    df["return"] = df["Close"].pct_change()

    return df


__all__ = ["load_asset", "load_multi_asset_prices", "DEFAULT_TICKERS"]
