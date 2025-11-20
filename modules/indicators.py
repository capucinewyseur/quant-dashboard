import pandas as pd

def add_rsi(df, window=14):
    """
    Ajoute l'indicateur RSI (Relative Strength Index) au DataFrame
    
    Args:
        df: DataFrame avec colonnes 'Close'
        window: Période pour le calcul du RSI (défaut: 14)
    
    Returns:
        DataFrame avec colonne 'RSI' ajoutée
    """
    delta = df["Close"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    rs = up.rolling(window).mean() / down.rolling(window).mean()
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def add_macd(df, fast=12, slow=26, signal=9):
    """
    Ajoute l'indicateur MACD (Moving Average Convergence Divergence) au DataFrame
    
    Args:
        df: DataFrame avec colonnes 'Close'
        fast: Période pour la moyenne mobile rapide (défaut: 12)
        slow: Période pour la moyenne mobile lente (défaut: 26)
        signal: Période pour la ligne de signal (défaut: 9)
    
    Returns:
        DataFrame avec colonnes 'MACD' et 'MACD_signal' ajoutées
    """
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    return df

def add_sma(df, window=20):
    """
    Ajoute une moyenne mobile simple (SMA) au DataFrame
    
    Args:
        df: DataFrame avec colonnes 'Close'
        window: Période pour la moyenne mobile (défaut: 20)
    
    Returns:
        DataFrame avec colonne 'SMA_{window}' ajoutée
    """
    df[f"SMA_{window}"] = df["Close"].rolling(window).mean()
    return df

