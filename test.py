from modules.data.multi_asset_loader import load_multi_asset_prices, DEFAULT_TICKERS
from modules.portfolio.portfolio_logic import compute_returns, normalize_weights, compute_portfolio_returns, compute_cumulated_values, compute_portfolio_metrics

prices = load_multi_asset_prices(DEFAULT_TICKERS)
rets = compute_returns(prices)

weights = normalize_weights({t: 1 for t in prices.columns}, prices.columns)
port_rets = compute_portfolio_returns(rets, weights)
port_val = compute_cumulated_values(port_rets)
metrics = compute_portfolio_metrics(port_rets)

print(prices.head())
print(rets.head())
print(port_val.head())
print(metrics)
