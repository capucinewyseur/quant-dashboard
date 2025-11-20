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
    return df

