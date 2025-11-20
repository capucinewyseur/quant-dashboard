import yfinance as yf
import pandas as pd

def load_asset(ticker, start="2018-01-01", end=None, interval="1d"):
    """
    Charge les données d'un actif depuis Yahoo Finance et calcule les rendements
    
    Args:
        ticker: Symbole de l'actif (ex: "AAPL")
        start: Date de début (format "YYYY-MM-DD")
        end: Date de fin (format "YYYY-MM-DD" ou None pour aujourd'hui)
        interval: Intervalle des données ("1d", "1h", "1m", etc.)
    
    Returns:
        DataFrame avec les colonnes: Open, High, Low, Close, Volume, return
    """
    df = yf.download(ticker, start=start, end=end, interval=interval)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    
    # Rendements journaliers
    df["return"] = df["Close"].pct_change()
    
    return df

