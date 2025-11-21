from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import yfinance as yf

DEFAULT_TICKERS = ['AAPL', 'EURUSD=X', 'BTC-USD', '^DJI', 'GC=F'] ##apple, eur/usd, bitcoin, dow jones, gold

def load_multi_asset_prices(
        tickers : List[str],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        interval: str = '1d',
) -> pd.DataFrame:
    """
    Load historical price data for multiple assets using Yahoo Finance.

    Parameters:
    - tickers: List of asset tickers to load.
    - start: Start date for the data (default is 1 year ago).
    - end: End date for the data (default is today).
    - interval: Data interval (e.g., '1d', '1h').

    Returns:
    - DataFrame with the prices, (column = tickers/asset, index = datetime).
    """

    if end is None:
        end = datetime.today()
    if start is None:
        start = end - timedelta(days=365 * 3)

    if not tickers:
        raise ValueError("Tickers list cannot be empty.")

    data=yf.download(tickers, start=start, end=end, interval=interval, auto_adjust=True, progress=False)

    # If yfinance sends MultiIndex (ex: Adj Close / Close / Volume)
    if isinstance(data.columns, pd.MultiIndex):
        if 'Adj Close' in data.columns.get_level_values(0):
            data = data['Adj Close'].copy()
        else:
            #fallback to Close prices
            try:
                data = data.xs("Close", axis=1, level=0)
            except Exception:
                pass
    #delete rows with all NaN values
    data.dropna(how='all')

    #only keep requested tickers
    cleaned_cols = [col for col in data.columns if col in tickers]
    data = data.loc[:, cleaned_cols]

    return data