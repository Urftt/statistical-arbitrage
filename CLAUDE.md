# CLAUDE.md — Statistical Arbitrage Research Platform

## Project Overview
Personal crypto statistical arbitrage research pipeline. Pairs trading strategies on Bitvavo exchange (EUR pairs). Currently in Phase 1→2 transition: data collection and cointegration analysis done, strategy and backtesting modules next.

## Tech Stack
- **Python 3.12** with **UV** package manager
- **Polars** (not Pandas) for all dataframes
- **Plotly** for visualization
- **statsmodels/scipy** for statistical tests
- **ccxt** for exchange API (Bitvavo)
- **pydantic-settings** for config
- **Jupyter** for research notebooks

## Quick Commands
```bash
uv sync --all-extras      # Install all deps
source .venv/bin/activate  # Activate venv
python run_dashboard.py    # Launch Dash app (http://localhost:8050)
pytest                     # Run tests
ruff check src/            # Lint
ruff format src/           # Format
mypy src/                  # Type check
jupyter lab                # Launch notebooks
```

## Project Structure
```
src/statistical_arbitrage/
├── data/bitvavo_client.py        # CCXT-based data collection from Bitvavo
├── data/cache_manager.py         # Query-once, cache-forever data layer (parquet cache)
├── analysis/cointegration.py     # Engle-Granger cointegration, ADF, z-scores, half-life
├── visualization/
│   ├── spread_plots.py           # Price comparison, spread/z-score, scatter+regression
│   └── educational_plots.py      # Concept explainers (cointegration vs correlation, ADF)
├── app/
│   ├── main.py                   # Dash app entry point, routing
│   ├── layout.py                 # Navbar + page container
│   └── pages/
│       ├── pair_scanner.py       # Batch cointegration scanning
│       ├── pair_deep_dive.py     # Single pair full analysis
│       └── research_hub.py       # 6 research modules (timeframe, lookback, threshold, etc.)
├── strategy/                     # TODO: Trading strategy implementations
└── backtesting/                  # TODO: Backtesting engine
config/settings.py                # Pydantic settings (Bitvavo creds, data paths, strategy params)
run_dashboard.py                  # Launch script for Dash app
notebooks/                        # 00-04: data collection → cointegration → pair discovery → timeframes
docs/findings/                    # Research findings (pair discovery results)
data/{raw,processed,results}/     # Data dirs (not committed, .gitignored)
data/cache/                       # Cached OHLCV timeseries (auto-populated, .gitignored)
```

## Architecture Patterns
- **Config**: `config/settings.py` uses pydantic-settings with `config/.env` for secrets. Access via `from config.settings import settings`.
- **Data format**: Parquet preferred. All data uses Polars DataFrames.
- **Exchange API**: Uses CCXT (not the native python-bitvavo-api). Public data doesn't need API keys.
- **Visualization**: All plots return Plotly `Figure` objects.
- **Analysis**: `PairAnalysis` class takes two `pl.Series`, converts to numpy internally for statsmodels/scipy.

## Coding Conventions
- Use **Polars** for dataframe ops, never Pandas
- Type hints on all function signatures
- Docstrings with Args/Returns sections
- Use `ruff` for linting and formatting
- Notebooks use `nbstripout` — outputs stripped on commit

## Key Domain Concepts
- **Cointegration**: Two assets whose spread is stationary (mean-reverting) — tested via Engle-Granger
- **Hedge ratio**: OLS regression slope between asset prices
- **Z-score**: Standardized spread = (spread - rolling_mean) / rolling_std
- **Half-life**: Mean reversion speed via Ornstein-Uhlenbeck process
- **Entry/exit thresholds**: Z-score levels for opening/closing positions (default: ±2.0 entry, ±0.5 exit)

## Current State
- ✅ Phase 1: Data collection, cointegration analysis, pair discovery (40 pairs tested, 10 cointegrated found)
- 🔲 Phase 2: Strategy implementation + backtesting framework
- 🔲 Phase 3: Parameter optimization + walk-forward analysis
- 🔲 Phase 4: Paper trading system
