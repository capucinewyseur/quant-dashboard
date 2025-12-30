# modules/portfolio/portfolio_logic.py

from __future__ import annotations

import numpy as np
import pandas as pd


# Basic helpers
def compute_returns(prices: pd.DataFrame, log: bool = False) -> pd.DataFrame:
    """
    Compute daily (or period) returns from price data.

    Parameters
    ----------
    prices : pd.DataFrame
        Price data, index = dates, columns = tickers.
    log : bool
        If True, compute log-returns, otherwise simple pct change.

    Returns
    -------
    pd.DataFrame
        Returns aligned with prices.index/prices.columns.
    """
    prices = prices.sort_index()
    if log:
        rets = np.log(prices / prices.shift(1))
    else:
        # pct_change with explicit fill_method=None to avoid FutureWarning
        rets = prices.pct_change(fill_method=None)

    return rets.fillna(0.0)


def normalize_weights(raw_weights: dict[str, float], tickers: list[str]) -> np.ndarray:
    """
    Convert a dict of raw weights into a normalized numpy vector
    aligned with tickers.
    """
    w = np.array([raw_weights.get(t, 0.0) for t in tickers], dtype=float)
    total = np.sum(np.abs(w))

    if total <= 0:
        # Fallback: equal weight
        n = len(tickers)
        return np.ones(n, dtype=float) / n

    return w / total


def compute_portfolio_returns(rets: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """
    Simple static-weight portfolio: each date uses the same weights.
    """
    rets_clean = rets.fillna(0.0)
    w = np.array(weights, dtype=float).reshape(-1, 1)
    port = rets_clean.values @ w  # (n_dates x n_assets) @ (n_assets x 1)
    return pd.Series(
        port.ravel(),
        index=rets_clean.index,
        name="Portfolio Returns",
    )


def compute_cumulated_values(
    returns: pd.Series,
    initial_value: float = 100.0,
) -> pd.Series:
    """
    Compute cumulative portfolio value starting from initial_value.
    """
    r = returns.fillna(0.0)
    cum = (1.0 + r).cumprod() * float(initial_value)
    cum.name = "portfolio_value"
    return cum


def max_drawdown(cum_values: pd.Series) -> float:
    """
    Compute maximum drawdown from a cumulative value series (base 1 or base 100).
    Returns a negative number (e.g. -0.25 for -25%).
    """
    series = cum_values.astype(float)
    running_max = series.cummax()
    drawdowns = (series / running_max) - 1.0
    return float(drawdowns.min())



# Portfolio metrics (incl. diversification)
def compute_portfolio_metrics(
    portfolio_returns: pd.Series,
    rets: pd.DataFrame | None = None,
    weights: np.ndarray | None = None,
    periods_per_year: int = 252,
) -> dict:
    """
    Compute main portfolio metrics.

    Parameters
    ----------
    portfolio_returns : pd.Series
        Portfolio returns.
    rets : pd.DataFrame, optional
        Asset returns (columns = tickers). Used for diversification metrics.
    weights : np.ndarray, optional
        Portfolio weights aligned with rets.columns.
    periods_per_year : int
        E.g. 252 for daily data.

    Returns
    -------
    dict with keys:
        'annual_return', 'annual_vol', 'sharpe', 'max_drawdown',
        and optionally 'naive_annual_vol', 'diversification_ratio'.
    """
    pr = portfolio_returns.dropna()

    if pr.empty:
        return {
            "annual_return": np.nan,
            "annual_vol": np.nan,
            "sharpe": np.nan,
            "max_drawdown": np.nan,
        }

    # Annualized return (geometric)
    cumulative = (1.0 + pr).prod()
    n = len(pr)
    annual_return = cumulative ** (periods_per_year / n) - 1.0

    # Annualized volatility
    annual_vol = pr.std() * np.sqrt(periods_per_year)

    # ---- Sharpe ratio (rf = 0) ----
    sharpe = annual_return / annual_vol if annual_vol > 0 else np.nan

    # ---- Max drawdown ----
    cum_val = compute_cumulated_values(pr, initial_value=1.0)
    mdd = max_drawdown(cum_val)

    metrics: dict[str, float] = {
        "annual_return": float(annual_return),
        "annual_vol": float(annual_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(mdd),
    }

    # ---- Diversification effects (optional) ----
    if (rets is not None) and (weights is not None):
        asset_rets = rets.dropna(how="all")
        common_idx = pr.index.intersection(asset_rets.index)
        asset_rets = asset_rets.loc[common_idx]

        if not asset_rets.empty:
            asset_vols = asset_rets.std() * np.sqrt(periods_per_year)

            # Naive vol = sum(|w_i| * sigma_i)
            naive_vol = float(np.sum(np.abs(weights) * asset_vols.values))

            if annual_vol > 0:
                diversification_ratio = naive_vol / annual_vol
            else:
                diversification_ratio = np.nan

            metrics["naive_annual_vol"] = naive_vol
            metrics["diversification_ratio"] = float(diversification_ratio)

    return metrics


def compute_correlation_matrix(rets: pd.DataFrame) -> pd.DataFrame:
    """
    Simple correlation matrix of asset returns.
    """
    return rets.corr()


# --------------------------------------------------
# Portfolio with rebalancing
# --------------------------------------------------


def compute_portfolio_returns_with_rebalancing(
    rets: pd.DataFrame,
    weights: np.ndarray,
    rebal_freq: str = "none",
) -> pd.Series:
    """
    Compute portfolio returns with periodic rebalancing to target weights.

    Parameters
    ----------
    rets : pd.DataFrame
        Asset returns, index = dates, columns = tickers.
    weights : np.ndarray
        Target portfolio weights (sum = 1), aligned with rets.columns.
    rebal_freq : str
        'none'  -> no rebalancing (static weights)
        'M'     -> rebalance monthly
        'Q'     -> rebalance quarterly
        'A'     -> rebalance yearly

    Returns
    -------
    pd.Series
        Daily portfolio returns with rebalancing.
    """
    if rebal_freq is None or rebal_freq.lower() == "none":
        return compute_portfolio_returns(rets, weights)

    rets_clean = rets.fillna(0.0).sort_index()
    dates = rets_clean.index

    # Define rebalancing dates: first date of each period
    try:
        grouped = rets_clean.groupby(pd.Grouper(freq=rebal_freq))
    except Exception:
        # Invalid frequency -> fallback to static weights
        return compute_portfolio_returns(rets, weights)

    rebal_dates: list[pd.Timestamp] = []
    for _, grp in grouped:
        if len(grp) > 0:
            rebal_dates.append(grp.index[0])
    rebal_dates_set = set(rebal_dates)

    # Simulate portfolio path
    port_rets = []
    portfolio_value = 1.0
    holdings = portfolio_value * np.array(weights, dtype=float)

    for t, dt in enumerate(dates):
        r_t = rets_clean.iloc[t].values  # per-asset returns at date dt

        # Update holdings with asset returns
        holdings = holdings * (1.0 + r_t)
        new_portfolio_value = float(holdings.sum())

        step_ret = new_portfolio_value / portfolio_value - 1.0
        port_rets.append(step_ret)
        portfolio_value = new_portfolio_value

        # Rebalance at this date if needed
        if dt in rebal_dates_set:
            holdings = portfolio_value * np.array(weights, dtype=float)

    port_rets_series = pd.Series(
        port_rets,
        index=dates,
        name="Portfolio Returns",
    )
    return port_rets_series
