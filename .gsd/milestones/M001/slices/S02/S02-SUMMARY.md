# S02: Core Statistical Modules

**Delivered:** Out-of-sample validation, spread construction comparison, and cointegration test method (EG vs Johansen) modules — analysis functions, takeaway generators, charts, and summary tables.

## What Was Built
- `analysis/research.py`: Added `out_of_sample_validation()`, `compare_spread_methods()`, `compare_cointegration_methods()` + takeaway generators
- `app/pages/research_hub.py`: 3 new callbacks with chart builders and result tables
- `tests/test_research_modules.py`: 20 unit tests covering OOS validation, spread methods, cointegration method comparison, and all takeaway generators

## Verification
- 20 tests pass covering cointegrated/independent pairs, edge cases, takeaway severity
- Johansen test uses `det_order=0, k_ar_diff=1` — verified against EG on known pairs
- All 3 modules render correctly in browser
