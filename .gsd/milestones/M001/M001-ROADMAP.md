# M001: Research Hub Rebuild

**Vision:** Rebuild the Research Hub with 8 empirical research modules that test every critical stat-arb assumption with real data, replacing the current buggy implementation with proper UX, consistent layouts, and auto-generated takeaway banners.

## Success Criteria

- User can run any of 8 research modules against any cached pair and get clear, labeled charts with auto-generated takeaway banners
- Rolling cointegration stability module reveals whether a pair's cointegration persists or breaks over time
- Out-of-sample validation module shows whether in-sample cointegration predicts out-of-sample behavior
- Transaction cost module answers "is this pair even profitable after Bitvavo fees?"
- No broken charts, no callback errors in browser console during normal usage
- Existing pages (scanner, deep dive, home) still function

## Key Risks / Unknowns

- Johansen test parameter selection — wrong det_order/k_ar_diff produces misleading results
- Rolling cointegration performance — ~8700 iterations for 365d of 1h data may be slow
- Cache coverage — only 1h data currently cached, other timeframes trigger API fetches

## Proof Strategy

- Johansen parameters → retire in S02 by running Johansen vs EG on known pairs and verifying agreement
- Rolling performance → retire in S01 by benchmarking on PEPE/BONK 1h data and adding progress indication if needed
- Cache coverage → retire in S03 by running optimal timeframe module and confirming cache manager handles multi-timeframe fetches

## Verification Classes

- Contract verification: pytest for analysis functions (cointegration methods, spread construction, takeaway generation)
- Integration verification: all 8 modules run in Dash app with real cached data for PEPE/BONK and ETH/ETC
- Operational verification: none (local dev tool)
- UAT / human verification: visual inspection of charts, takeaway banner relevance, overall UX flow

## Milestone Definition of Done

This milestone is complete only when all are true:

- All 8 research modules render, run, and produce correct results
- Every chart has axis labels and handles edge cases (no data, inf, nan) gracefully
- Takeaway banners generate meaningful one-liners from actual computed results
- No callback errors in browser console during normal usage
- Existing pages (scanner, deep dive, home) still work
- Analysis functions have unit tests

## Requirement Coverage

- Covers: R001, R002, R003, R004, R005, R006
- Partially covers: none
- Leaves for later: R007, R008, R009, R010
- Orphan risks: none

## Slices

- [ ] **S01: Foundation + Rolling Cointegration Stability** `risk:high` `depends:[]`
  > After this: user can navigate to /research, select a pair from pre-populated dropdown, run the rolling cointegration module, and see a rolling p-value chart with stability takeaway banner
- [ ] **S02: Core Statistical Modules** `risk:medium` `depends:[S01]`
  > After this: user can also run out-of-sample validation, spread construction comparison, and cointegration test method (EG vs Johansen) modules
- [ ] **S03: Signal Parameter Modules** `risk:medium` `depends:[S01]`
  > After this: user can also run optimal timeframe, z-score threshold, and lookback window modules
- [ ] **S04: Transaction Costs + Polish** `risk:low` `depends:[S02,S03]`
  > After this: all 8 modules complete, transaction cost sensitivity module works, edge cases handled, existing pages verified, analysis functions tested

## Boundary Map

### S01 → S02, S03, S04

Produces:
- Shared module UI components: `_module_layout()`, `_control_bar()`, `_takeaway_banner()` reusable across all modules
- Research hub page shell with tab navigation and auto-populated pair selector
- Analysis function pattern: analysis functions in `analysis/` module, separate from Dash callbacks
- `research_hub.py` new structure with callback registration pattern

Consumes:
- nothing (first slice)

### S02 → S04

Produces:
- Extended PairAnalysis or new analysis classes for Johansen test, log-price spread, ratio spread
- 3 additional working modules with takeaway banners

Consumes:
- Shared UI components and page shell from S01

### S03 → S04

Produces:
- 3 additional working modules (timeframe, z-score threshold, lookback)
- Reusable heatmap/sweep visualization patterns

Consumes:
- Shared UI components and page shell from S01

### S04

Produces:
- Transaction cost sensitivity module
- Unit tests for analysis functions
- Edge case handling across all modules
- Verified existing pages still work

Consumes:
- All modules from S01, S02, S03
