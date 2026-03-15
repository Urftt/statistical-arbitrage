# Project

## What This Is

A crypto statistical arbitrage research platform for Bitvavo (EUR pairs). Dash-based web app with data collection (CCXT), caching (parquet), cointegration analysis (Engle-Granger), and interactive research modules. Currently: pair scanner, deep dive, and research hub pages operational. Research hub being rebuilt.

## Core Value

Empirical research engine that tests every stat-arb assumption with real data instead of accepting conventional defaults.

## Current State

- Data pipeline: CCXT → Bitvavo API → parquet cache with delta updates. 1h data cached for ~20 EUR pairs.
- Analysis: PairAnalysis class (EG cointegration, ADF, z-scores, half-life, spread properties)
- Dashboard: 3 pages — pair scanner (batch coint testing), pair deep dive (single pair analysis), research hub (6 modules, being rebuilt)
- Findings: 10 cointegrated pairs found from 40 tested. Key finding: cointegration is temporally unstable.
- Research hub: 6 modules exist but are buggy and unclear. Being replaced with 8 new modules in M001.

## Architecture / Key Patterns

- **Stack**: Python 3.12, UV, Dash + DBC, Plotly, Polars, statsmodels/scipy, CCXT
- **Config**: pydantic-settings with config/.env for secrets
- **Data**: Polars DataFrames, parquet storage, DataCacheManager singleton
- **Analysis**: PairAnalysis takes pl.Series, converts to numpy internally
- **Visualization**: All plots return Plotly Figure objects
- **App routing**: Manual routing in main.py, each page module has layout() + register_callbacks(app)

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [ ] M001: Research Hub Rebuild — 8 empirical research modules with proper UX and takeaway banners
