import pandas as pd

def buy_and_hold(df):
    """
    Stratégie Buy & Hold (stratégie référence)
    
    Principe: Toujours investi 100% dans l'actif, sans jamais sortir.
    Sert de benchmark pour comparer les stratégies actives.
    
    Args:
        df: DataFrame avec colonnes 'Close' et autres données de prix
    
    Returns:
        DataFrame avec colonne 'Position' ajoutée (toujours à 1.0)
    """
    df = df.copy()
    df["Position"] = 1.0   # toujours investi
    return df

def rsi_strategy(df, low=30, high=70):
    """
    Stratégie basée sur le RSI (Relative Strength Index)
    
    Principe:
    - RSI < low ⇒ marché survendu ⇒ on prend une position long (Position = 1.0)
    - RSI > high ⇒ marché suracheté ⇒ on sort / passe en cash (Position = 0.0)
    - Entre les deux ⇒ on garde la dernière position
    
    Args:
        df: DataFrame avec colonnes 'RSI' (doit être calculé avant)
        low: Seuil bas du RSI pour entrer en position (défaut: 30)
        high: Seuil haut du RSI pour sortir de position (défaut: 70)
    
    Returns:
        DataFrame avec colonne 'Position' ajoutée (0.0 ou 1.0)
    """
    df = df.copy()
    df["Position"] = 0.0
    df.loc[df["RSI"] < low, "Position"] = 1.0
    df.loc[df["RSI"] > high, "Position"] = 0.0
    # Forward fill pour garder la dernière position entre les seuils
    df["Position"] = df["Position"].replace(0.0, method='ffill').fillna(0.0)
    return df

def momentum_strategy(df, period=12):
    """
    Stratégie basée sur le Momentum (version simple)
    
    Principe:
    - Momentum > 0 ⇒ tendance haussière ⇒ on achète (Position = 1.0)
    - Momentum < 0 ⇒ tendance baissière ⇒ on sort / cash (Position = 0.0)
    
    Le momentum le plus simple = Close(t) - Close(t-n)
    
    Args:
        df: DataFrame avec colonnes 'Close'
        period: Nombre de périodes pour calculer le momentum (défaut: 12)
    
    Returns:
        DataFrame avec colonnes 'Momentum' et 'Position' ajoutées
    """
    df = df.copy()
    
    # Momentum simple : différence de prix sur n périodes
    df["Momentum"] = df["Close"] - df["Close"].shift(period)
    
    df["Position"] = 0.0
    df.loc[df["Momentum"] > 0, "Position"] = 1.0
    df.loc[df["Momentum"] < 0, "Position"] = 0.0
    
    return df

