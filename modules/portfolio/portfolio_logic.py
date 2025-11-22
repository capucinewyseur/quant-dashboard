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
def compute_cumulative_value(portfolio_returns: pd.Series, initial_value: float = 100.0) -> pd.Series:
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
def compute_drawdowns(series: pd.Series) -> float:
    """
    Compute the maximum drawdown of a cumulative value series.

    Parameters:
    - series: Series with cumulative values (index = datetime).

    Returns:
    - Maximum drawdown as a float.
    """
    running_max = series.cummax()
    drawdowns = (series - running_max) / running_max
    return float(drawdowns.min())

# metrics

def compute_performance_metrics(portfolio_returns: pd.Series, risk_free_rate: float=0.0, periods_per_year: int=252) -> Dict[str, float]:
    """
    Compute performance metrics for the portfolio returns.

    Parameters:
    - portfolio_returns: Series with portfolio returns (index = datetime).
    - risk_free_rate: Annualized risk-free rate for Sharpe ratio calculation.
    - periods_per_year: Number of trading periods in a year.

    Returns:
    - Dictionary with performance metrics: annualized return, annualized volatility, Sharpe ratio, max drawdown.
    """
    #annualized return
    meanr.ret = portfolio_returns.mean()
    vol = portfolio_returns.std()

    ann_ret = (1 + meanr.ret) ** periods_per_year - 1
    ann_vol = vol * np.sqrt(periods_per_year)

    if ann_vol > 0:
        sharpe = (ann_ret - risk_free_rate) / ann_vol
    else:
        sharpe = np.nan
    
    #max drawdown
    cum = (1 + portfolio_returns).cumprod()
    mdd = compute_drawdowns(cum)

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

