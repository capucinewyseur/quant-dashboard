from typing import Dict
import numpy as np
import pandas as pd

#1 Calculate returns

def compute_returns(prices: pd.DataFrame, log : bool = False) -> pd.DataFrame:
    """
    Compute the daily returns of the assets using the prices.

    Parameters:
    - prices: DataFrame with asset prices (columns = assets, index = datetime).
    - log: Boolean indicating whether to compute log returns or simple returns.

    Returns:
    - DataFrame with daily returns.
    """
    if log:
        rets = np.log(prices / prices.shift(1))
    else:
        rets = prices.pct_change()
    
    return rets.dropna()




# Weight normalization function
def normalize_weights(raw_weights: Dict[str, float], tickers) -> np.ndarray:
    """
    Normalize a dictionary of asset weights so that they sum to 1.

    Parameters:
    - raw_weights: Dictionary with asset tickers as keys and their weights as values.
    - tickers: List of asset tickers to consider.

    Returns:
    - Dictionary with normalized weights.
    """
    w = np.array([raw_weights.get(t, 0.0) for t in tickers], dtype=float)
    w_sum = np.sum(w)

    if w_sum<=0:
        #fallback to equal weights
        w = np.ones(len(tickers)) / len(tickers)
    else:
        w /= w_sum
    return w

# Portfolio returns calculation
def compute_portfolio_returns(asset_returns: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """
    Compute the portfolio returns given asset returns and weights.
    R_port = sum(w_i * R_i)

    Parameters:
    - asset_returns: DataFrame with asset returns (columns = assets, index = datetime).
    - weights: Numpy array with asset weights.

    Returns:
    - Series with portfolio returns.
    """
    R = asset_returns.values  # shape (T, N)
    port_rets = R @ weights   # shape (T,)

    return pd.Series(port_rets, index=asset_returns.index, name="Portfolio Returns")



#cumulative value calculation
def compute_cumulated_values(portfolio_returns: pd.Series, initial_value: float = 100.0) -> pd.Series:
    """
    Compute the cumulative value curve of an investment given the returns.

    Parameters:
    - portfolio_returns: Series with returns (index = datetime).
    - initial_value: Initial investment value.

    Returns:
    - Series with cumulative values.
    """
    cumulative_value = initial_value * (1 + portfolio_returns).cumprod()
    cumulative_value.name = "portfolio_value"
    return cumulative_value

# Drawdown calculation
def max_drawdown(series: pd.Series) -> float:
    """
    Calcule le max drawdown d'une série de valeur cumulée.
    """
    running_max = series.cummax()
    drawdown = (series - running_max) / running_max
    return float(drawdown.min())


# metrics

def compute_portfolio_metrics(
    portfolio_returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> Dict[str, float]:
    """
    Calcule les principales métriques du portefeuille.

    Parameters
    ----------
    portfolio_returns : Series
        Rendements du portefeuille (fréquence = daily par défaut).
    risk_free_rate : float
        Taux sans risque annualisé (ex: 0.02 pour 2%)
    periods_per_year : int
        252 pour daily, 52 pour weekly, 12 pour monthly.

    Returns
    -------
    dict avec :
        - annual_return
        - annual_vol
        - sharpe
        - max_drawdown
    """
    mean_ret = portfolio_returns.mean()
    vol = portfolio_returns.std()

    # rendement annualisé (en partant d'un rendement moyen par période)
    ann_return = (1 + mean_ret) ** periods_per_year - 1
    # volatilité annualisée
    ann_vol = vol * np.sqrt(periods_per_year)

    if ann_vol > 0:
        sharpe = (ann_return - risk_free_rate) / ann_vol
    else:
        sharpe = np.nan

    # courbe cumulée pour calculer le max drawdown
    cum = (1 + portfolio_returns).cumprod()
    mdd = max_drawdown(cum)

    return {
        "annual_return": float(ann_return),
        "annual_vol": float(ann_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(mdd),
    }



# ---------------------------------------------
# 7 — CORRELATION MATRIX
# ---------------------------------------------

def compute_correlation_matrix(asset_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Matrice de corrélation entre les actifs.
    """
    return asset_returns.corr()

