# Quant Dashboard

Quantitative analysis dashboard for finance built with Python and Streamlit.

## Features

- Real-time financial data retrieval from Yahoo Finance
- Single asset analysis with technical indicators (RSI, MACD, SMA)
- Trading strategies (Buy & Hold, RSI Strategy, Momentum Strategy)
- Backtesting engine with performance metrics
- Interactive visualizations with Plotly
- Daily automated reports via cron
- Automatic data refresh every 5 minutes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/capucinewyseur/quant-dashboard.git
cd quant-dashboard
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

### Features

- **Asset Selection**: Choose from popular tickers or enter a custom ticker
- **Periodicity**: Select Daily, Weekly, or Monthly data
- **Strategy Selection**: Choose between Buy & Hold, RSI Strategy, or Momentum Strategy
- **Interactive Charts**: View price data, RSI, strategy positions, and equity curves
- **Performance Metrics**: View Sharpe Ratio, Max Drawdown, Volatility, CAGR, and Total Return

## Daily Reports (Cron Job)

The project includes an automated daily report generator that runs via cron.

### Quick Setup (Automatic Installation)

**Install the cron job automatically** (recommended):
```bash
cd /path/to/quant-dashboard
./cron/install_cron.sh
```

This script will:
- Automatically detect paths (project, Python)
- Create the `reports/` directory if needed
- Configure the cron job to run every day at 8:00 PM (20:00)
- Verify everything works

### Manual Setup

1. **Generate a test report manually**:
```bash
python cron/generate_report.py AAPL
```

This will create a report in `reports/YYYY-MM-DD.txt`

2. **Configure cron job** (Linux/Mac):

Edit your crontab:
```bash
crontab -e
```

Add the following line (adjust paths to your project):
```bash
0 20 * * * cd /path/to/quant-dashboard && /path/to/venv/bin/python cron/generate_report.py >> cron/cron.log 2>&1
```

This will run the report generator every day at 8:00 PM (20:00).

3. **Verify cron job**:
```bash
crontab -l
```

4. **View cron logs**:
```bash
tail -f cron/cron.log
```

**For more details, see**: `cron/README_CRON.md`

### Report Contents

Each daily report includes:
- **Price Data**: Latest open/close prices and daily change
- **Performance Metrics**: 
  - Annualized Volatility
  - Sharpe Ratio
  - Max Drawdown
  - CAGR (Compound Annual Growth Rate)
  - Total Return
- **Data Summary**: Total data points and date range

Reports are saved in `reports/YYYY-MM-DD.txt` format.

### Customizing the Report

You can modify `cron/generate_report.py` to:
- Change the default ticker
- Add additional metrics
- Change the report format (CSV, JSON, etc.)
- Include multiple tickers

## Project Structure

```
quant-dashboard/
├── app.py                 # Main Streamlit application
├── modules/
│   ├── data.py           # Data loading from Yahoo Finance
│   ├── indicators.py     # Technical indicators (RSI, MACD, SMA)
│   ├── strategies.py     # Trading strategies
│   ├── backtesting.py    # Backtesting engine and metrics
│   ├── single_asset.py    # Single asset analysis module
│   └── portfolio.py      # Portfolio analysis module (placeholder)
├── cron/
│   ├── generate_report.py    # Daily report generator
│   └── crontab.example       # Cron configuration example
├── reports/              # Generated daily reports (created automatically)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Dependencies

- streamlit
- pandas
- numpy
- matplotlib
- yfinance
- requests
- plotly
- streamlit-autorefresh

## Development

### Git Workflow

This project uses Git for version control with separate branches for different modules:
- `ptAcapucine`: Single Asset Analysis Module (Quant A)
- Other branches for Portfolio Module (Quant B)

## License

This project is part of an academic assignment for quantitative finance analysis.
