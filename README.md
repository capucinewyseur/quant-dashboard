# Quant Dashboard

A quantitative analysis dashboard for finance built with Python and Streamlit. This project provides real-time financial data analysis, trading strategy backtesting, and automated daily reports.

## Project Purpose

This dashboard is designed for quantitative finance analysis, allowing users to:
- Analyze single assets with technical indicators (RSI, MACD, SMA)
- Test trading strategies (Buy & Hold, RSI Strategy, Momentum Strategy)
- View performance metrics (Sharpe Ratio, Max Drawdown, Volatility, CAGR, Total Return)
- Generate automated daily reports via cron jobs

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**:
```bash
git clone https://github.com/capucinewyseur/quant-dashboard.git
cd quant-dashboard
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
```

3. **Activate the virtual environment**:
```bash
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit dashboard:
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501` in your web browser.

### Features

- **Asset Selection**: Choose from popular tickers (AAPL, MSFT, GOOGL, etc.) or enter a custom ticker
- **Periodicity**: Select Daily, Weekly, or Monthly data intervals
- **Strategy Selection**: Choose between Buy & Hold, RSI Strategy, or Momentum Strategy
- **Interactive Charts**: View price data, RSI, strategy positions, and equity curves
- **Performance Metrics**: View Sharpe Ratio, Max Drawdown, Annualized Volatility, CAGR, and Total Return
- **Auto-refresh**: Data updates automatically every 5 minutes

## Project Structure

```
quant-dashboard/
├── app.py                      # Main Streamlit application
├── modules/
│   ├── data.py                # Data loading from Yahoo Finance
│   ├── indicators.py          # Technical indicators (RSI, MACD, SMA)
│   ├── strategies.py          # Trading strategies
│   ├── backtesting.py         # Backtesting engine and metrics
│   ├── single_asset.py        # Single asset analysis module
│   └── portfolio.py           # Portfolio analysis module
├── cron/
│   ├── generate_report.py     # Daily report generator
│   ├── install_cron.sh        # Automatic cron job installer
│   ├── crontab.example        # Cron configuration example
│   └── README_CRON.md        # Cron documentation
├── reports/                   # Generated daily reports (auto-created)
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Usage Examples

### Basic Usage

1. Launch the application: `streamlit run app.py`
2. Select a ticker from the sidebar (e.g., "AAPL")
3. Choose a periodicity (Daily, Weekly, or Monthly)
4. Select a trading strategy
5. Adjust strategy parameters using the sliders
6. View the results in the dashboard

### Running Daily Reports Manually

Generate a report for a specific ticker:
```bash
python3 cron/generate_report.py AAPL
```

Reports are saved in `reports/YYYY-MM-DD.txt` format.

## Cron Job Configuration

### Automatic Installation (Recommended)

Install the cron job automatically:
```bash
./cron/install_cron.sh
```

This will configure the system to generate a daily report at 8:00 PM (20:00) every day.

### Manual Installation

1. Edit your crontab:
```bash
crontab -e
```

2. Add this line (adjust paths to your project):
```bash
0 20 * * * cd /path/to/quant-dashboard && /path/to/venv/bin/python3 cron/generate_report.py >> cron/cron.log 2>&1
```

3. Verify the installation:
```bash
crontab -l
```

4. View cron logs:
```bash
tail -f cron/cron.log
```

### Report Contents

Each daily report includes:
- Latest open/close prices and daily change
- Annualized Volatility
- Sharpe Ratio
- Max Drawdown
- CAGR (Compound Annual Growth Rate)
- Total Return
- Data summary (total data points and date range)

## Dependencies

- streamlit
- pandas
- numpy
- matplotlib
- yfinance
- requests
- plotly
- streamlit-autorefresh

## Known Issues and Limitations

- **Data Source**: Relies on Yahoo Finance API (yfinance). If the API is down, data loading will fail.
- **Rate Limiting**: Yahoo Finance may rate-limit requests if too many are made in a short time.
- **Historical Data**: Limited by Yahoo Finance's available historical data (typically 5-10 years for daily data).
- **Ticker Validation**: Invalid tickers will result in empty data. Always verify ticker symbols.
- **Network Dependency**: Requires an active internet connection to fetch data.
- **Platform**: Cron jobs are configured for Linux/Mac. Windows users need to use Task Scheduler instead.

## Troubleshooting

### Application won't start
- Ensure the virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python3 --version` (should be 3.8+)

### No data displayed
- Check your internet connection
- Verify the ticker symbol is correct
- Try a different ticker (e.g., AAPL, MSFT)

### Cron job not running
- Verify cron is installed: `which cron` or `systemctl status cron`
- Check cron logs: `tail -f cron/cron.log`
- Verify the cron job is installed: `crontab -l`
- Test the script manually: `python3 cron/generate_report.py AAPL`

## License

This project is part of an academic assignment for quantitative finance analysis.

## Contact

For issues or questions, please open an issue on the GitHub repository.
