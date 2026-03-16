# S02: Global Pair Selector + Page Migration

**Goal:** Wire global pair selector in header, populate it from cache, and migrate all page layouts from DBC to DMC components. Pages read pair from global store instead of having their own selectors.
**Demo:** User selects ETH/ETC in header bar, navigates to Deep Dive and sees the pair pre-selected. Navigates to a Research module and sees the pair already there. All form controls are DMC (dark-themed Select, NumberInput, Button).

## Must-Haves

- Global pair bar in header populated with cached pairs on app load
- dcc.Store("global-pair-store") updated when user changes header selects
- Pair Scanner page rebuilt with DMC components, reads from global store
- Pair Deep Dive page rebuilt with DMC components, reads from global store
- Research Hub modules read pair from global store (module-specific params stay per-module)
- All dcc.Dropdown replaced with dmc.Select (searchable)
- All dbc.Input replaced with dmc.NumberInput
- All dbc.Button replaced with dmc.Button
- All dbc.Card/Alert/Table replaced with dmc.Paper/Alert/Table equivalents
- Remove dbc_dark_overrides.css

## Proof Level

- This slice proves: integration (global state flows correctly across all pages)
- Real runtime required: yes
- Human/UAT required: yes (visual inspection)

## Verification

- `python run_dashboard.py` starts without errors
- Select ETH/ETC in header → navigate to /deep-dive → pair is pre-selected
- Navigate to /research/rolling-coint → pair is pre-selected
- Run rolling coint for ETH/ETC → chart renders correctly
- No JavaScript console errors
- No white/light-themed form elements remaining

## Tasks

- [ ] **T01: Wire global pair selector and populate from cache** `est:30m`
  - Why: Central to the entire UX improvement — select once, use everywhere
  - Files: `layout.py`, `main.py`
  - Do:
    - Add callback to populate global-asset1/asset2 options from cache on app load
    - Store pair selection in global-pair-store
    - Ensure header selects are searchable and pre-populated
  - Done when: Header pair selects show all cached pairs, store updates on selection

- [ ] **T02: Migrate Pair Scanner to DMC** `est:45m`
  - Why: First page migration, establishes the pattern
  - Files: `pair_scanner.py`
  - Do:
    - Replace all DBC components with DMC equivalents
    - Read initial pair from global-pair-store (for pre-selection)
    - Keep all existing callbacks working (scan still runs, results still render)
  - Done when: Scanner page is fully DMC, reads global pair, scans work

- [ ] **T03: Migrate Pair Deep Dive to DMC** `est:45m`
  - Files: `pair_deep_dive.py`
  - Do: Same pattern as scanner migration. Remove "Load pairs" button.
  - Done when: Deep Dive fully DMC, reads global pair, analysis runs

- [ ] **T04: Migrate Research Hub modules to DMC + global pair** `est:60m`
  - Files: `research_hub.py`, `research_ui.py`
  - Do:
    - Replace pair_control_bar with DMC-based controls reading from global store
    - Keep module-specific params (window size, etc.) as per-module DMC NumberInputs
    - Replace takeaway_banner with dmc.Alert
    - Replace all dbc.Table with dmc.Table
    - Replace dbc.Card with dmc.Paper
  - Done when: All 8 research modules use DMC, read global pair, produce correct results

- [ ] **T05: Remove DBC overrides and cleanup** `est:15m`
  - Files: `assets/dbc_dark_overrides.css`, `pyproject.toml`
  - Do: Delete dbc_dark_overrides.css. Verify no DBC components remain. Keep DBC in deps for now (some edge cases may still reference it).
  - Done when: No CSS override file, no white-themed form elements visible

## Files Likely Touched

- `src/statistical_arbitrage/app/layout.py`
- `src/statistical_arbitrage/app/main.py`
- `src/statistical_arbitrage/app/pages/pair_scanner.py`
- `src/statistical_arbitrage/app/pages/pair_deep_dive.py`
- `src/statistical_arbitrage/app/pages/research_hub.py`
- `src/statistical_arbitrage/app/components/research_ui.py`
- `src/statistical_arbitrage/app/assets/dbc_dark_overrides.css` (delete)
