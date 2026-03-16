# Project

## What This Is

A crypto statistical arbitrage research platform for Bitvavo (EUR pairs). Dash-based web app with data collection (CCXT), caching (parquet), cointegration analysis (Engle-Granger + Johansen), and interactive research modules. DMC-based UI with AppShell, sidebar navigation, and global pair selector.

## Core Value

Empirical research engine that tests every stat-arb assumption with real data instead of accepting conventional defaults.

## Current State

- Data pipeline: CCXT → Bitvavo API → parquet cache with delta updates. 1h data cached for ~20 EUR pairs.
- Analysis: PairAnalysis class (EG cointegration, ADF, z-scores, half-life, spread properties) + research analysis module (8 empirical functions)
- Dashboard: DMC AppShell with sidebar navigation. 3 page areas — pair scanner (batch coint testing), pair deep dive (single pair analysis), research hub (8 modules with takeaway banners)
- Research Hub: 8 modules — rolling cointegration stability, out-of-sample validation, optimal timeframe, spread construction, z-score threshold, lookback window, transaction cost sensitivity, cointegration test method
- Findings: 10 cointegrated pairs found from 40 tested. Key finding: cointegration is temporally unstable.
- Tests: 48 unit tests for research analysis functions and takeaway generators

## Architecture / Key Patterns

- **Stack**: Python 3.12, UV, Dash + DMC (Mantine), Plotly, Polars, statsmodels/scipy, CCXT
- **Config**: pydantic-settings with config/.env for secrets
- **Data**: Polars DataFrames, parquet storage, DataCacheManager singleton
- **Analysis**: PairAnalysis takes pl.Series, converts to numpy internally. Research functions in analysis/research.py (pure Python, no Dash).
- **Visualization**: All plots return Plotly Figure objects. Custom Mantine dark Plotly template.
- **App layout**: DMC AppShell with sidebar navigation, global pair selector in header, dcc.Store for pair state
- **App routing**: URL-based routing in main.py, each page module has layout() + register_callbacks(app)

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [x] M001: Research Hub Rebuild — 8 empirical research modules with proper UX and takeaway banners ✅
- [x] M002: UI Redesign — Dash Mantine Components ✅
