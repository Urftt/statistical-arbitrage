# S01: Foundation + Rolling Cointegration Stability

**Goal:** Replace research hub with new architecture (shared UI components, separated analysis layer, auto-populated pair selector) and deliver the first working module — rolling cointegration stability.
**Demo:** User navigates to /research, sees pre-populated pair dropdowns, selects PEPE/BONK, runs the rolling cointegration module, and sees a rolling p-value chart with a colored takeaway banner like "⚡ This pair loses cointegration 3 times in 90 days — unstable"

## Must-Haves

- Shared module UI components reusable by S02/S03/S04
- Auto-populated pair selector (no "Load pairs" button)
- Rolling cointegration stability module with chart + takeaway banner
- Analysis function for rolling cointegration in analysis/ module (not in Dash callbacks)
- Existing pages (scanner, deep dive, home) still work after the rewrite

## Proof Level

- This slice proves: integration
- Real runtime required: yes (Dash app with cached data)
- Human/UAT required: yes (visual inspection of charts and takeaway banners)

## Verification

- `pytest tests/test_rolling_cointegration.py -v` — analysis function unit tests
- Launch dashboard, navigate to /research, run rolling cointegration for PEPE/BONK — chart renders, takeaway banner shows
- Navigate to /scanner, /deep-dive, / — all still render without errors
- Browser console shows no callback errors

## Observability / Diagnostics

- Runtime signals: Dash callback errors surfaced in browser console
- Inspection surfaces: browser dev tools console, Dash debug mode
- Failure visibility: error alerts shown in module results area on analysis failure
- Redaction constraints: none

## Integration Closure

- Upstream surfaces consumed: `DataCacheManager.get_candles()`, `DataCacheManager.get_available_pairs()`, `PairAnalysis.test_cointegration()`
- New wiring introduced in this slice: new research_hub.py replaces old one, registered in main.py
- What remains before the milestone is truly usable end-to-end: 7 more modules (S02, S03, S04), unit tests for all analysis functions

## Tasks

- [x] **T01: Analysis layer — rolling cointegration function** `est:45m`
  - Why: Core analysis logic must be testable independent of Dash. This establishes the pattern for all future modules.
  - Files: `src/statistical_arbitrage/analysis/research.py`, `tests/test_rolling_cointegration.py`
  - Do: Create `analysis/research.py` with `rolling_cointegration()` function. Takes two price series + window size + step size, returns a Polars DataFrame with columns: timestamp, p_value, is_cointegrated, hedge_ratio, test_statistic. Also add `generate_rolling_coint_takeaway()` that takes the results DF and returns a dict with `text` and `severity` (green/yellow/red). Write pytest tests with synthetic data (known cointegrated + known non-cointegrated series).
  - Verify: `pytest tests/test_rolling_cointegration.py -v`
  - Done when: Tests pass for both cointegrated and non-cointegrated synthetic data, takeaway function produces correct severity levels

- [x] **T02: Shared UI components + research hub shell** `est:45m`
  - Why: Every module needs the same control bar, results area, and takeaway banner. Build these once, reuse everywhere.
  - Files: `src/statistical_arbitrage/app/pages/research_hub.py`, `src/statistical_arbitrage/app/components/research_ui.py`
  - Do: Create `components/research_ui.py` with: `module_layout(module_id, title, description, controls, results_id)` — standard module wrapper; `pair_control_bar(prefix, extra_controls=None)` — pair selector + timeframe + run button; `takeaway_banner(text, severity)` — colored alert banner (green/yellow/red). Rewrite `research_hub.py` from scratch: tab navigation for 8 modules (only rolling coint functional, others show "Coming soon" placeholder), auto-populate pair dropdowns on page load via single callback. Keep research_hub.py under 200 lines — it's just layout and callback wiring, all analysis logic lives in analysis/.
  - Verify: `python run_dashboard.py` — /research loads, tabs render, pair dropdowns populated, "Coming soon" shown for unbuilt modules
  - Done when: Page loads without errors, all 8 tabs visible, pair dropdowns auto-populated from cache

- [x] **T03: Wire rolling cointegration module end-to-end** `est:30m`
  - Why: Connect the analysis function (T01) to the UI shell (T02) to produce the first working module.
  - Files: `src/statistical_arbitrage/app/pages/research_hub.py`, `src/statistical_arbitrage/app/components/research_ui.py`
  - Do: Add callback for rolling cointegration module: fetch data from cache, call `rolling_cointegration()`, render rolling p-value line chart (with 0.05 significance threshold line), render takeaway banner. Handle edge cases: insufficient data, no cached data, analysis errors. Add window size control (default 90, range 30-365). Chart: x-axis = date, y-axis = p-value, color regions above/below 0.05 threshold.
  - Verify: Run dashboard, select PEPE/BONK, run module — chart shows rolling p-value with clear threshold line, takeaway banner renders with correct severity
  - Done when: Module produces correct chart for PEPE/BONK and ETH/ETC, edge cases show error alerts, takeaway banner matches data

## Files Likely Touched

- `src/statistical_arbitrage/analysis/research.py` (new)
- `src/statistical_arbitrage/app/components/__init__.py` (new)
- `src/statistical_arbitrage/app/components/research_ui.py` (new)
- `src/statistical_arbitrage/app/pages/research_hub.py` (rewrite)
- `tests/test_rolling_cointegration.py` (new)
