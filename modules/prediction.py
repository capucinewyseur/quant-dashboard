"""
Simple prediction module using Linear Regression
"""

import pandas as pd
import numpy as np

def predict_future_prices_simple(df, days_ahead=30, price_col="Close"):
    """
    Simple linear regression prediction for future prices.
    Uses basic linear regression: y = a*x + b
    
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
        DataFrame with columns: 'Predicted_Price', 'Lower_Bound', 'Upper_Bound'
        Index is future dates
    """
    if df.empty or price_col not in df.columns:
        return pd.DataFrame()
    
    # Get prices
    prices = df[price_col].values
    n = len(prices)
    
    if n < 10:  # Need at least 10 data points
        return pd.DataFrame()
    
    # Simple linear regression: y = a*x + b
    # x = day number (0, 1, 2, ...)
    # y = price
    
    x = np.arange(n)
    y = prices
    
    # Calculate coefficients manually (simple linear regression)
    # a = slope, b = intercept
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    
    if denominator == 0:
        return pd.DataFrame()
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # Predict historical values to calculate error
    y_pred_hist = slope * x + intercept
    residuals = y - y_pred_hist
    std_error = np.std(residuals)
    
    # Generate future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead, freq='D')
    
    # Predict future prices
    future_x = np.arange(n, n + days_ahead)
    future_prices = slope * future_x + intercept
    
    # Calculate confidence interval (±2 standard deviations)
    lower_bound = future_prices - 2 * std_error
    upper_bound = future_prices + 2 * std_error
    
    # Create result DataFrame
    result = pd.DataFrame({
        'Predicted_Price': future_prices,
        'Lower_Bound': lower_bound,
        'Upper_Bound': upper_bound
    }, index=future_dates)
    
    return result

