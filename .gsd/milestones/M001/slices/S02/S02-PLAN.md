# S02: Core Statistical Modules

**Goal:** Add three research modules that test fundamental statistical methodology: out-of-sample validation, spread construction methods, and cointegration test comparison (EG vs Johansen).
**Demo:** User can run out-of-sample validation to see if in-sample cointegration predicts out-of-sample, compare price/log/ratio spread construction, and check EG vs Johansen agreement — all with charts and takeaway banners.

## Must-Haves

- Out-of-sample validation module: split data into formation/trading periods, test if cointegration holds
- Spread construction module: compare price-level, log-price, and ratio spreads by stationarity
- Cointegration test method module: EG vs Johansen side-by-side with agreement check
- All three produce charts and takeaway banners
- Analysis functions in analysis/research.py, not in callbacks

## Proof Level

- This slice proves: integration
- Real runtime required: yes
- Human/UAT required: yes

## Verification

- `pytest tests/test_research_modules.py -v` — unit tests for all three analysis functions
- All three modules run in dashboard for PEPE/BONK and ETH/ETC
- No callback errors in browser console

## Tasks

- [x] **T01: Analysis functions for S02 modules** `est:1h`
  - Why: All three modules need analysis functions before UI wiring
  - Files: `src/statistical_arbitrage/analysis/research.py`, `tests/test_research_modules.py`
  - Do: Add `out_of_sample_validation()` (split data, test coint on both halves, return comparison), `compare_spread_methods()` (price/log/ratio with ADF stats for each), `compare_cointegration_methods()` (EG + Johansen side-by-side). Add takeaway generators for each. Write tests with synthetic data.
  - Verify: `pytest tests/test_research_modules.py -v`
  - Done when: All tests pass

- [x] **T02: Wire three modules into dashboard** `est:1h`
  - Why: Connect analysis functions to Dash UI with charts and takeaway banners
  - Files: `src/statistical_arbitrage/app/pages/research_hub.py`
  - Do: Add layouts and callbacks for oos-validation, spread-construction, coint-method tabs. Each gets the shared control bar, a chart, and takeaway banner. Mark them as built in MODULES list.
  - Verify: Run dashboard, test all three modules with real data
  - Done when: All three produce charts and takeaway banners for PEPE/BONK

## Files Likely Touched

- `src/statistical_arbitrage/analysis/research.py`
- `src/statistical_arbitrage/app/pages/research_hub.py`
- `tests/test_research_modules.py` (new)
