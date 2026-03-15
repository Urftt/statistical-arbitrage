# Requirements

## Active

### R001 — Empirical Research Modules
- Class: core-capability
- Status: active
- Description: 8 interactive research modules that each test one stat-arb assumption with real cached Bitvavo OHLCV data and produce visual results with auto-generated takeaway banners
- Why it matters: Every trading parameter must be earned through data, not assumed from convention
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: M001/S02, M001/S03, M001/S04
- Validation: unmapped
- Notes: Modules: rolling cointegration stability, out-of-sample validation, optimal timeframe, spread construction, z-score threshold, lookback window, transaction cost sensitivity, cointegration test method

### R002 — Consistent Module UX
- Class: primary-user-loop
- Status: active
- Description: Every research module has the same control bar (pre-populated pair selector, timeframe where relevant, run button), results area with charts, and colored takeaway banner
- Why it matters: The current research hub is confusing — inconsistent layouts and unclear charts make it hard to trust results
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Dark theme (DARKLY), proper axis labels, loading spinners, graceful error/empty states

### R003 — Takeaway Banners
- Class: primary-user-loop
- Status: active
- Description: Each module auto-generates a one-line colored takeaway from the computed results (green/yellow/red severity)
- Why it matters: Turns raw charts into actionable insight without requiring the user to interpret everything manually
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Data-driven text, not hardcoded. E.g. "⚡ This pair loses cointegration 3 times in 90 days — unstable"

### R004 — Analysis Layer Separation
- Class: quality-attribute
- Status: active
- Description: All new analysis functions live in src/statistical_arbitrage/analysis/, testable independently from Dash callbacks
- Why it matters: Current research_hub.py is 1300 lines with analysis logic mixed into callbacks — untestable and hard to maintain
- Source: inferred
- Primary owning slice: M001/S01
- Supporting slices: M001/S02, M001/S03, M001/S04
- Validation: unmapped
- Notes: Extend PairAnalysis or create new analysis classes as appropriate

### R005 — Robustness Under Edge Cases
- Class: failure-visibility
- Status: active
- Description: Charts and modules handle insufficient data, inf/nan values, missing cache, and API errors gracefully with clear user-facing messages
- Why it matters: Current modules show broken/blank graphs when data is missing or insufficient
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Every chart path must handle the empty/error case explicitly

### R006 — Existing Pages Unbroken
- Class: continuity
- Status: active
- Description: Scanner, Deep Dive, and Home pages continue to function after the research hub rebuild
- Why it matters: Don't break working functionality while rebuilding one page
- Source: inferred
- Primary owning slice: M001/S04
- Supporting slices: none
- Validation: unmapped
- Notes: Smoke test all pages after rebuild

## Deferred

### R007 — Verdict Document Generation
- Class: differentiator
- Status: deferred
- Description: Generate structured findings documents (like docs/findings/) from research module results
- Why it matters: Would create a persistent record of empirical learnings
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: User expressed interest but concerned about quality — deferred to V2

### R008 — Half-life Stability Module
- Class: core-capability
- Status: deferred
- Description: Research module for rolling half-life analysis over time
- Why it matters: Useful but derivative of rolling cointegration stability
- Source: inferred
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: V2 candidate

### R009 — Spread Normality Module
- Class: core-capability
- Status: deferred
- Description: Research module for testing whether spread distributions are normal
- Why it matters: Good to know but doesn't change the workflow much in V1
- Source: inferred
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: V2 candidate

### R010 — Regime Detection Module
- Class: core-capability
- Status: deferred
- Description: Detect bull/bear/sideways regimes and their effect on cointegration
- Why it matters: Needs more data history to be meaningful
- Source: inferred
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: V2 candidate, depends on regime detection research

## Out of Scope

### R011 — Backtesting Engine
- Class: core-capability
- Status: out-of-scope
- Description: Full strategy backtesting with P&L simulation
- Why it matters: Prevents scope creep — this is Phase 2 per CLAUDE.md
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Research modules inform backtesting parameters but don't implement it

### R012 — Paper Trading
- Class: core-capability
- Status: out-of-scope
- Description: Real-time paper trading system
- Why it matters: Phase 3+ per CLAUDE.md
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Explicitly out of scope for this milestone

### R013 — Mobile / Tablet Layout
- Class: constraint
- Status: out-of-scope
- Description: Responsive mobile/tablet layouts
- Why it matters: Desktop-only research tool — prevents unnecessary CSS work
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Reasonable desktop widths only

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R001 | core-capability | active | M001/S01 | S02, S03, S04 | unmapped |
| R002 | primary-user-loop | active | M001/S01 | none | unmapped |
| R003 | primary-user-loop | active | M001/S01 | none | unmapped |
| R004 | quality-attribute | active | M001/S01 | S02, S03, S04 | unmapped |
| R005 | failure-visibility | active | M001/S01 | none | unmapped |
| R006 | continuity | active | M001/S04 | none | unmapped |
| R007 | differentiator | deferred | none | none | unmapped |
| R008 | core-capability | deferred | none | none | unmapped |
| R009 | core-capability | deferred | none | none | unmapped |
| R010 | core-capability | deferred | none | none | unmapped |
| R011 | core-capability | out-of-scope | none | none | n/a |
| R012 | core-capability | out-of-scope | none | none | n/a |
| R013 | constraint | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 6
- Mapped to slices: 0
- Validated: 0
- Unmapped active requirements: 6
