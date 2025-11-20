import pandas as pd
import numpy as np

def compute_returns(df, price_col="Close", return_col="return"):
    """
    Compute returns from a price DataFrame.
    
    This is the main function to calculate asset returns for backtesting.
    
    Parameters
    ----------
    df : pd.DataFrame
        Must contain a price column (Close by default)
    price_col : str
        Column used to compute returns (default: "Close")
    return_col : str
        Name of the return column to create (default: "return")
    
    Returns
    -------
    pd.DataFrame
        Original df + a new return column
    """
    df = df.copy()
    df[return_col] = df[price_col].pct_change()
    return df

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

def apply_strategy_position(df, return_col="return", position_col="Position", out_col="StrategyReturn"):
    """
    Apply strategy position to asset returns to get strategy returns.
    
    This function multiplies asset returns by the position (1 = long, 0 = cash, -1 = short)
    to calculate strategy returns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Must contain return_col and position_col columns
    return_col : str
        Name of the column containing asset returns (default: "return")
    position_col : str
        Name of the column containing strategy position (default: "Position")
    out_col : str
        Name of the new strategy returns column (default: "StrategyReturn")
    
    Returns
    -------
    pd.DataFrame
        df + out_col column with strategy returns
    """
    df = df.copy()
    df[out_col] = df[return_col] * df[position_col]
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

def compute_cumulative_returns(df, asset_return_col="return", strat_return_col="StrategyReturn",
                              asset_equity_col="Equity_Asset", strat_equity_col="Equity_Strategy",
                              initial_capital=1.0):
    """
    Compute cumulative returns (equity curves) for asset and strategy.
    
    This function builds cumulative value curves starting from initial_capital.
    The equity curve shows how $1 invested would have grown over time.
    
    Parameters
    ----------
    df : pd.DataFrame
        Must contain asset_return_col and strat_return_col
    asset_return_col : str
        Name of the column containing asset returns (default: "return")
    strat_return_col : str
        Name of the column containing strategy returns (default: "StrategyReturn")
    asset_equity_col : str
        Name of the asset equity curve column to create (default: "Equity_Asset")
    strat_equity_col : str
        Name of the strategy equity curve column to create (default: "Equity_Strategy")
    initial_capital : float
        Initial capital (default: 1.0)
    
    Returns
    -------
    pd.DataFrame
        df + 2 equity curve columns (cumulative values)
    """
    df = df.copy()
    
    # Cumulative product: (1 + r1) * (1 + r2) * ... * (1 + rn)
    df[asset_equity_col] = initial_capital * (1 + df[asset_return_col]).cumprod()
    df[strat_equity_col] = initial_capital * (1 + df[strat_return_col]).cumprod()
    
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

def compute_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Volatilité annualisée d'une série de retours.

    Parameters
    ----------
    returns : pd.Series
        Série de retours (par ex. StrategyReturn).
    periods_per_year : int
        252 pour daily, 52 pour weekly, 12 pour monthly.

    Returns
    -------
    float
        Volatilité annualisée.
    """
    return float(returns.std(ddof=0) * np.sqrt(periods_per_year))

def compute_sharpe_ratio(returns: pd.Series,
                         periods_per_year: int = 252,
                         risk_free_rate: float = 0.0) -> float:
    """
    Sharpe ratio annualisé.

    Parameters
    ----------
    returns : pd.Series
        Série de retours de la stratégie.
    periods_per_year : int
        252 pour daily, 52 pour weekly, 12 pour monthly.
    risk_free_rate : float
        Taux sans risque annuel (e.g. 0.02 pour 2%).

    Returns
    -------
    float
        Sharpe ratio annualisé.
    """
    if returns.std(ddof=0) == 0:
        return np.nan
    
    rf_per_period = risk_free_rate / periods_per_year
    excess_returns = returns - rf_per_period
    
    mean_excess = excess_returns.mean()
    std_excess = excess_returns.std(ddof=0)
    
    sharpe = (mean_excess / std_excess) * np.sqrt(periods_per_year)
    return float(sharpe)

def compute_drawdown(equity_curve: pd.Series) -> pd.Series:
    """
    Calcule la série de drawdown à partir d'une equity curve.

    Parameters
    ----------
    equity_curve : pd.Series
        Série de valeurs cumulées (equity curve).

    Returns
    -------
    pd.Series
        Série de drawdown (valeurs entre 0 et négatives).
    """
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1.0
    return drawdown

def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calcule le max drawdown (valeur la plus basse de la série de drawdown).

    Parameters
    ----------
    equity_curve : pd.Series
        Série de valeurs cumulées (equity curve).

    Returns
    -------
    float
        Max drawdown (négatif).
    """
    drawdown = compute_drawdown(equity_curve)
    return float(drawdown.min())

def compute_cagr(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """
    Calcule le CAGR (taux de croissance annuel composé) à partir d'une equity curve.

    Parameters
    ----------
    equity_curve : pd.Series
        Série de valeurs cumulées (equity curve).
    periods_per_year : int
        252 pour daily, 52 pour weekly, 12 pour monthly.

    Returns
    -------
    float
        CAGR annuel.
    """
    if equity_curve.empty:
        return np.nan
    
    initial_value = equity_curve.iloc[0]
    final_value = equity_curve.iloc[-1]
    
    n_periods = len(equity_curve)
    n_years = n_periods / periods_per_year
    
    if n_years <= 0 or initial_value <= 0:
        return np.nan
    
    cagr = (final_value / initial_value) ** (1 / n_years) - 1
    return float(cagr)

def backtest_complete(df, position_col="Position", price_col="Close", 
                     return_col="return", initial_capital=1.0):
    """
    Complete backtesting pipeline: compute returns, apply strategy, build equity curves.
    
    This is the main orchestration function that runs the complete backtesting process:
    1. Compute asset returns
    2. Apply strategy positions to get strategy returns
    3. Build cumulative equity curves
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with price data and Position column from strategy
    position_col : str
        Name of the position column (default: "Position")
    price_col : str
        Name of the price column (default: "Close")
    return_col : str
        Name of the return column to create (default: "return")
    initial_capital : float
        Initial capital for equity curves (default: 1.0)
    
    Returns
    -------
    pd.DataFrame
        DataFrame with returns, strategy returns, and equity curves
    """
    df = df.copy()
    
    # Step 1: Compute asset returns
    if return_col not in df.columns:
        df = compute_returns(df, price_col=price_col, return_col=return_col)
    
    # Drop NaN values (first row will be NaN for returns)
    df = df.dropna()
    
    # Step 2: Apply strategy position to get strategy returns
    if position_col in df.columns and return_col in df.columns:
        df = apply_strategy_position(df, return_col=return_col, 
                                    position_col=position_col, 
                                    out_col="StrategyReturn")
        
        # Step 3: Build cumulative equity curves
        df = compute_cumulative_returns(df, 
                                        asset_return_col=return_col,
                                        strat_return_col="StrategyReturn",
                                        asset_equity_col="Equity_Asset",
                                        strat_equity_col="Equity_Strategy",
                                        initial_capital=initial_capital)
    
    return df

