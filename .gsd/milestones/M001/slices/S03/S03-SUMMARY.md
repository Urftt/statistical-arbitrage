# S03: Signal Parameter Modules

**Delivered:** Optimal timeframe comparison, z-score threshold sweep, and lookback window optimization modules — analysis functions, takeaway generators, heatmap/line charts, and summary tables.

## What Was Built
- `analysis/research.py`: Added `compare_timeframes()`, `sweep_zscore_thresholds()`, `sweep_lookback_windows()` + takeaway generators
- `app/pages/research_hub.py`: 3 new callbacks with chart builders (including heatmap for threshold sweep) and result tables
- `tests/test_research_s03.py`: 15 unit tests covering timeframe comparison, z-score threshold sweep, lookback window sweep, and all takeaway generators

## Verification
- 15 tests pass covering multi-timeframe data, NaN handling, empty data, strong signals, takeaway severity
- Timeframe module uses `get_merged_fn` callback pattern for clean data access
- All 3 modules render correctly in browser
