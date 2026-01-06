# Explanation of the Prediction Model

## Method Used: Simple Linear Regression

### Mathematical Formula
```
y = a*x + b
```

Where:
- `y` = predicted price
- `x` = day number (0, 1, 2, 3, ...)
- `a` = slope (rate of change per day)
- `b` = intercept (starting price)

### How It Works

1. **Input**: Historical prices (e.g., last 2000 days of AAPL)
2. **Calculation**:
   - Fits a straight line through all historical prices
   - Calculates the slope (trend) and intercept
   - Extrapolates this line 30 days into the future
3. **Output**: Predicted prices following the linear trend

### Example Calculation

If historical prices show:
- Day 0: $100
- Day 1: $102
- Day 2: $104
- Day 3: $106

The model calculates: slope = +$2/day, intercept = $100
Prediction for Day 4: $100 + (4 × $2) = $108

### Why It's Not Very Accurate

**1. Stock prices don't follow linear trends**
- Real stock prices are volatile and non-linear
- They have cycles, trends, reversals, and random movements
- A straight line cannot capture this complexity

**2. Model limitations**
- Ignores volatility patterns
- Ignores market cycles
- Ignores external factors (news, earnings, etc.)
- Assumes constant rate of change (slope)

**3. Simple model for demonstration**
- This is a **bonus feature** for demonstration
- Real trading would use more sophisticated models:
  - ARIMA (time series)
  - LSTM (neural networks)
  - Random Forest
  - Ensemble methods

### Confidence Interval

The confidence band shows:
- **Upper Bound**: Predicted price + 2 standard deviations
- **Lower Bound**: Predicted price - 2 standard deviations
- **Meaning**: 95% probability that actual price falls within this range

The band widens over time because uncertainty increases the further we predict.

### Conclusion

This simple linear regression is:
- ✅ Easy to understand and implement
- ✅ Fast to compute
- ✅ Good for demonstration purposes
- ❌ Not accurate for real trading
- ❌ Too simplistic for financial markets

**Note**: This model is included as a bonus feature to demonstrate predictive capabilities. For actual trading decisions, more sophisticated models would be required.

