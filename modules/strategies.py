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

