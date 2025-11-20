"""
Simple prediction module using Linear Regression
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def predict_future_prices(df, days_ahead=30, price_col="Close"):
    """
    Simple linear regression prediction for future prices.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with historical price data
    days_ahead : int
        Number of days to predict (default: 30)
    price_col : str
        Name of the price column (default: "Close")
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns: 'Date', 'Predicted_Price', 'Lower_Bound', 'Upper_Bound'
    """
    if df.empty or price_col not in df.columns:
        return pd.DataFrame()
    
    # Prepare data
    prices = df[price_col].values
    n = len(prices)
    
    if n < 10:  # Need at least 10 data points
        return pd.DataFrame()
    
    # Create feature: day index
    X = np.arange(n).reshape(-1, 1)
    y = prices
    
    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict historical values to calculate error
    y_pred_hist = model.predict(X)
    mse = mean_squared_error(y, y_pred_hist)
    std_error = np.sqrt(mse)
    
    # Generate future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead, freq='D')
    
    # Predict future prices
    future_X = np.arange(n, n + days_ahead).reshape(-1, 1)
    future_prices = model.predict(future_X)
    
    # Calculate confidence interval (±2 standard deviations)
    lower_bound = future_prices - 2 * std_error
    upper_bound = future_prices + 2 * std_error
    
    # Create result DataFrame
    result = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Price': future_prices,
        'Lower_Bound': lower_bound,
        'Upper_Bound': upper_bound
    })
    result.set_index('Date', inplace=True)
    
    return result

