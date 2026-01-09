from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from datetime import datetime, timedelta
from pathlib import Path
import sys
import traceback

import numpy as np
import pandas as pd

# Project imports (repo root must be on PYTHONPATH when running from repo root)
from modules.data.multi_asset_loader import load_multi_asset_prices, DEFAULT_TICKERS
from modules.portfolio.portfolio_logic import (
    compute_returns,
    normalize_weights,
    compute_portfolio_returns_with_rebalancing,
    compute_cumulated_values,
    compute_portfolio_metrics,
    compute_correlation_matrix,
)


def _safe_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    # Report configuration
    tickers = DEFAULT_TICKERS
    interval = "1d"
    rebal_freq = "none"  # "none", "M", "Q", "A"
    weights_mode = "Equal weight"

    # Time window (last 365 days)
    end = datetime.now()
    start = end - timedelta(days=365)

    # Paths
    root = Path(__file__).resolve().parents[1]  # ~/quant-dashboard
    reports_dir = root / "reports"
    report_date = end.strftime("%Y-%m-%d")
    report_path = reports_dir / f"report_{report_date}.txt"

    try:
        # Download prices
        prices = load_multi_asset_prices(
            tickers=tickers,
            start=start,
            end=end,
            interval=interval,
        )

        if prices is None or prices.empty:
            _safe_write_text(
                report_path,
                f"Daily Report {report_date}\n\nERROR: No price data downloaded.\n",
            )
            return 1

        # Clean prices (forward fill small gaps, drop all-NaN columns)
        prices = prices.sort_index()
        prices = prices.ffill().dropna(axis=1, how="all")

        if prices.shape[1] < 2:
            _safe_write_text(
                report_path,
                f"Daily Report {report_date}\n\nERROR: Not enough valid assets after cleaning.\n"
                f"Columns: {list(prices.columns)}\n",
            )
            return 1

        # Equal weights (normalized)
        raw_w = {t: 1.0 for t in prices.columns}
        weights = normalize_weights(raw_w, list(prices.columns))

        # Returns and portfolio series
        rets = compute_returns(prices, log=False)
        rets = rets.dropna(how="all")

        port_rets = compute_portfolio_returns_with_rebalancing(
            rets,
            weights,
            rebal_freq=rebal_freq,
        )

        port_val = compute_cumulated_values(port_rets, initial_value=100.0)

        # Metrics (includes diversification if implemented in your logic)
        periods_per_year = 252
        metrics = compute_portfolio_metrics(
            port_rets,
            rets=rets,
            weights=weights,
            periods_per_year=periods_per_year,
        )

        # Correlation (last available)
        corr = compute_correlation_matrix(rets)

        # Format report text
        lines: list[str] = []
        lines.append(f"Daily Report — {report_date}")
        lines.append("")
        lines.append("Configuration")
        lines.append(f"- Assets: {', '.join(list(prices.columns))}")
        lines.append(f"- Interval: {interval}")
        lines.append(f"- Weights mode: {weights_mode}")
        lines.append(f"- Rebalancing: {rebal_freq}")
        lines.append(f"- Window: last 365 days (approx)")
        lines.append("")

        lines.append("Latest data points")
        last_dt = prices.index.max()
        lines.append(f"- Last timestamp: {last_dt}")
        lines.append(f"- Last prices:")
        last_prices = prices.iloc[-1].to_dict()
        for k, v in last_prices.items():
            try:
                lines.append(f"  - {k}: {float(v):.4f}")
            except Exception:
                lines.append(f"  - {k}: {v}")
        lines.append("")

        lines.append("Portfolio metrics")
        def _fmt_pct(x: float | None) -> str:
            if x is None or (isinstance(x, float) and np.isnan(x)):
                return "N/A"
            return f"{x*100:.2f}%"

        def _fmt_num(x: float | None) -> str:
            if x is None or (isinstance(x, float) and np.isnan(x)):
                return "N/A"
            return f"{x:.4f}"

        lines.append(f"- Annual return: {_fmt_pct(metrics.get('annual_return'))}")
        lines.append(f"- Annual vol: {_fmt_pct(metrics.get('annual_vol'))}")
        lines.append(f"- Sharpe: {_fmt_num(metrics.get('sharpe'))}")
        lines.append(f"- Max drawdown: {_fmt_pct(metrics.get('max_drawdown'))}")
        if "diversification_ratio" in metrics:
            lines.append(f"- Diversification ratio: {_fmt_num(metrics.get('diversification_ratio'))}")
        lines.append("")

        lines.append("Correlation matrix (rounded)")
        corr_round = corr.round(2)
        lines.append(corr_round.to_string())
        lines.append("")

        # Small sanity info
        lines.append("Sanity checks")
        lines.append(f"- Observations (returns): {len(rets)}")
        lines.append(f"- Assets used: {rets.shape[1]}")
        lines.append("")

        _safe_write_text(report_path, "\n".join(lines) + "\n")
        return 0

    except Exception as e:
        err = [
            f"Daily Report — {report_date}",
            "",
            "ERROR: Exception while generating report.",
            f"Type: {type(e).__name__}",
            f"Message: {e}",
            "",
            "Traceback:",
            traceback.format_exc(),
            "",
        ]
        _safe_write_text(report_path, "\n".join(err))
        return 2


if __name__ == "__main__":
    sys.exit(main())