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
    rets: pd.DataFrame | None = None,
    weights: np.ndarray | None = None,
    periods_per_year: int = 252,
) -> dict:
    """
    Calcule les métriques principales du portefeuille.
    """

    pr = portfolio_returns.dropna()

    if pr.empty:
        return {
            "annual_return": np.nan,
            "annual_vol": np.nan,
            "sharpe": np.nan,
            "max_drawdown": np.nan,
        }

    # ---- Annualized return ----
    cumulative = (1.0 + pr).prod()
    n = len(pr)
    annual_return = cumulative ** (periods_per_year / n) - 1.0

    # ---- Annualized volatility ----
    annual_vol = pr.std() * np.sqrt(periods_per_year)

    # ---- Sharpe ratio ----
    sharpe = annual_return / annual_vol if annual_vol > 0 else np.nan

    # ---- Max drawdown ----
    cum_val = compute_cumulated_values(pr, initial_value=1.0)
    mdd = max_drawdown(cum_val)

    # Base metrics
    metrics = {
        "annual_return": float(annual_return),
        "annual_vol": float(annual_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(mdd),
    }

    # ---- Diversification effects (optional) ----
    if (rets is not None) and (weights is not None):

        # Sync dates between asset returns and portfolio returns
        asset_rets = rets.dropna(how="all")
        common_idx = pr.index.intersection(asset_rets.index)
        asset_rets = asset_rets.loc[common_idx]

        if not asset_rets.empty:

            # Annualized vol of each asset
            asset_vols = asset_rets.std() * np.sqrt(periods_per_year)

            # Naive vol = sum(|w_i| * sigma_i)
            naive_vol = float(np.sum(np.abs(weights) * asset_vols.values))

            # Diversification ratio
            if annual_vol > 0:
                diversification_ratio = naive_vol / annual_vol
            else:
                diversification_ratio = np.nan

            metrics["naive_annual_vol"] = naive_vol
            metrics["diversification_ratio"] = float(diversification_ratio)

    return metrics



# ---------------------------------------------
# 7 — CORRELATION MATRIX
# ---------------------------------------------

def compute_correlation_matrix(asset_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Matrice de corrélation entre les actifs.
    """
    return asset_returns.corr()

