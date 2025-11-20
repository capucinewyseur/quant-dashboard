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

