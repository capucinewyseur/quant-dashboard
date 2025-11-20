import pandas as pd
import numpy as np

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

def build_equity_curves(df, asset_return_col="Return", strat_return_col="StrategyReturn",
                        asset_equity_col="Equity_Asset", strat_equity_col="Equity_Strategy",
                        initial_capital=1.0):
    """
    Construit les courbes de valeur cumulée (equity curves) pour l'actif
    et pour la stratégie.

    Parameters
    ----------
    df : pd.DataFrame
        Doit contenir asset_return_col et strat_return_col.
    asset_return_col : str
        Nom de la colonne contenant les retours de l'actif.
    strat_return_col : str
        Nom de la colonne contenant les retours de la stratégie.
    asset_equity_col : str
        Nom de la colonne d'equity curve de l'actif à créer.
    strat_equity_col : str
        Nom de la colonne d'equity curve de la stratégie à créer.
    initial_capital : float
        Capital initial (défaut: 1.0).

    Returns
    -------
    pd.DataFrame
        df + 2 colonnes d'equity curves.
    """
    df = df.copy()
    
    df[asset_equity_col] = initial_capital * (1 + df[asset_return_col]).cumprod()
    df[strat_equity_col] = initial_capital * (1 + df[strat_return_col]).cumprod()
    
    return df

