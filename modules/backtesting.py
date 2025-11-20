import pandas as pd

def compute_daily_returns(df, price_col="Close"):
    """
    Compute daily returns from a price DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a price column (Close by default)
    price_col : str
        Column used to compute returns

    Returns
    -------
    pd.DataFrame
        Original df + a new 'Return' column
    """
    df = df.copy()
    df["Return"] = df[price_col].pct_change()
    df.dropna(inplace=True)  # first line becomes NaN → drop
    return df

def apply_strategy_returns(df, return_col="Return", position_col="Position", out_col="StrategyReturn"):
    """
    Applique la position (1, 0, -1, etc.) aux retours de l'actif
    pour obtenir les retours de la stratégie.

    Parameters
    ----------
    df : pd.DataFrame
        Doit contenir les colonnes return_col et position_col.
    return_col : str
        Nom de la colonne contenant les retours de l'actif.
    position_col : str
        Nom de la colonne contenant la position de la stratégie.
    out_col : str
        Nom de la nouvelle colonne de retours de la stratégie.

    Returns
    -------
    pd.DataFrame
        df + colonne out_col.
    """
    df = df.copy()
    df[out_col] = df[return_col] * df[position_col]
    return df

