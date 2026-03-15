# M001: Research Hub Rebuild

**Gathered:** 2026-03-15
**Status:** Ready for planning

## Project Description

Rebuild the Research Hub from scratch with 8 empirical research modules that test every critical stat-arb assumption with real Bitvavo OHLCV data. Replace the existing 6 buggy modules with properly designed, consistent UX and auto-generated takeaway banners.

## Why This Milestone

The current research hub has bugs (graphs not rendering), unclear visualizations, and is missing the most critical research questions (rolling stability, out-of-sample validation, transaction costs). The strategy parameters must be earned through empirical data, not assumed. This milestone produces the tooling to do that.

## User-Visible Outcome

### When this milestone is complete, the user can:

- Navigate to /research and run any of 8 research modules against any cached pair
- See clear, labeled charts with auto-generated takeaway banners summarizing key findings
- Test rolling cointegration stability, out-of-sample validation, timeframe comparison, spread construction methods, z-score thresholds, lookback windows, transaction cost sensitivity, and EG vs Johansen cointegration tests

### Entry point / environment

- Entry point: `python run_dashboard.py` → http://localhost:8050/research
- Environment: local dev, browser
- Live dependencies involved: Bitvavo API via CCXT (only for initial cache population — cached data used thereafter)

## Completion Class

- Contract complete means: analysis functions have unit tests, modules produce correct output for known pairs
- Integration complete means: all 8 modules work end-to-end in the Dash app with real cached data
- Operational complete means: none (local dev tool)

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- All 8 modules run successfully for PEPE/BONK and ETH/ETC, producing charts and takeaway banners
- No callback errors in browser console during normal usage of any module
- Existing pages (scanner, deep dive, home) still function after the rebuild

## Risks and Unknowns

- Johansen test parameter selection (det_order, k_ar_diff) — wrong settings produce misleading results
- Rolling cointegration over 365d × 1h data (~8700 iterations) — may be slow, needs benchmarking
- Only 1h data currently cached — other timeframes trigger API fetches via cache manager

## Existing Codebase / Prior Art

- `src/statistical_arbitrage/app/pages/research_hub.py` — current 1300-line research hub, being replaced entirely
- `src/statistical_arbitrage/analysis/cointegration.py` — PairAnalysis class, will be extended
- `src/statistical_arbitrage/data/cache_manager.py` — DataCacheManager, used as-is
- `src/statistical_arbitrage/app/main.py` — Dash app entry point, routing
- `config/settings.py` — StrategySettings has transaction_fee (0.0025)
- `docs/findings/01_pair_discovery_cointegration.md` — existing findings

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions — it is an append-only register; read it during planning, append to it during execution.

## Relevant Requirements

- R001 — 8 empirical research modules (core deliverable)
- R002 — Consistent module UX
- R003 — Takeaway banners
- R004 — Analysis layer separation
- R005 — Robustness under edge cases
- R006 — Existing pages unbroken

## Scope

### In Scope

- 8 research modules rebuilt from scratch
- New analysis functions in analysis/ module
- Shared module UI components
- Unit tests for analysis functions
- Auto-populated pair selector

### Out of Scope / Non-Goals

- Backtesting engine (Phase 2)
- Paper trading (Phase 3+)
- Verdict document generation (V2)
- Deferred modules: half-life stability, spread normality, regime detection, hedge ratio method
- Mobile/tablet layouts
- Changes to scanner or deep dive pages

## Technical Constraints

- Dash + DBC + Plotly for all UI
- Polars for dataframes, numpy for statsmodels/scipy interop
- DARKLY Bootstrap theme
- Existing DataCacheManager for data access
- No new dependencies unless truly required

## Integration Points

- DataCacheManager — all data reads
- PairAnalysis — extended for new methods
- Dash app routing — /research route
- config/settings.py — transaction fee

## Open Questions

- Johansen det_order — will test with default during implementation
- Rolling cointegration performance — benchmark in S01
