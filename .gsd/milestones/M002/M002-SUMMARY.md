---
id: M002
provides:
  - DMC AppShell layout with header, sidebar, main area
  - Global pair selector (Asset 1 × Asset 2 × Timeframe) flowing to all pages
  - Sidebar navigation with Research Hub sub-module links
  - Custom Plotly dark theme template matching Mantine palette
  - All 3 pages + 8 research modules rebuilt with DMC components
key_decisions:
  - DMC 2.6.0 over DBC — first-party dark theme, better component API
  - AppShell layout — header for global controls, sidebar for navigation
  - Global pair stored in dcc.Store, consumed by all pages
  - Research Hub modules as sidebar sub-links instead of tab rows
  - Removed homepage — root redirects to /scanner
patterns_established:
  - Global state via dcc.Store + header controls → page callbacks read from store
  - Sidebar NavLink active state driven by URL pathname
  - Module layouts use dmc.Paper for control bars, dmc.Alert for takeaway banners
  - Plotly template registered as "mantine_dark" with transparent backgrounds
observability_surfaces:
  - none (local dev tool)
requirement_outcomes:
  - id: R004
    from_status: active
    to_status: validated
    proof: Consistent UX across all pages — sidebar nav, global pair, DMC components
  - id: R005
    from_status: active
    to_status: validated
    proof: Mantine dark theme, Plotly charts with proper axis labels, custom color palette
  - id: R006
    from_status: active
    to_status: validated
    proof: Loading spinners on all research modules, "select a pair" empty states, error handling
duration: 1 session
verification_result: passed
completed_at: 2026-03-15
---

# M002: UI Redesign — Dash Mantine Components

**Migrated the entire app from Bootstrap DARKLY to Dash Mantine Components with AppShell layout, sidebar navigation, and a global pair selector that flows to all pages.**

## What Happened

S01 replaced the top-level layout: DBC Navbar + page container became a DMC AppShell with a header bar (branding + global pair selects), a left sidebar with NavLinks (Scanner, Deep Dive, Research Hub with 8 sub-module links), and a main content area. A custom Plotly template ("mantine_dark") was registered to match the Mantine color palette. Root URL redirects to `/scanner`.

S02 rebuilt all three pages and all 8 research modules from DBC to DMC. The key change: pair selection moved from per-page/per-module dropdowns to a single global pair bar in the header, stored in `dcc.Store("global-pair-store")`. Each page reads the pair from the store. This eliminated massive duplication — the research hub alone went from 1300+ lines to ~850 while gaining proper module routing.

S03 scope (Research Hub sidebar nav + polish) was largely delivered during S01/S02 — the sidebar sub-links and chart theming were natural parts of those slices. Net result: -730 lines of code, zero analysis changes, zero test failures.

## Cross-Slice Verification

- **All pages render**: Visited Scanner, Deep Dive, Rolling Stability, Out-of-Sample, Timeframe, Spread Method, Z-score Threshold, Lookback Window, Transaction Costs, Coint. Method — all render without errors
- **Global pair flows**: Selected ETH/EUR × ETC/EUR in header → ran Rolling Stability (chart + takeaway produced) → navigated to Deep Dive → ran Analyze (stats + charts produced from same pair)
- **Sidebar navigation**: All 8 research sub-links highlight correctly, URL routing works
- **Charts themed**: Plotly charts have transparent backgrounds, matching grid colors, consistent colorway
- **No console errors**: Zero JS errors across all page navigations and analysis runs
- **Tests pass**: 48/48 tests green — analysis code completely untouched

## Requirement Changes

- R004: active → validated — consistent UX via DMC AppShell, sidebar nav, global pair bar
- R005: active → validated — Mantine dark theme, custom Plotly template, proper axis labels
- R006: active → validated — loading spinners, empty states, error handling on all modules

## Forward Intelligence

### What the next milestone should know
- The global pair store doesn't persist selection across hard page refreshes. Adding `persistence=True` + `persistence_type="session"` to the header Selects would fix this trivially.
- DMC Select components use Mantine's Combobox internally — browser automation is tricky (portal-rendered dropdowns), but real user interaction works fine.
- The Pair Scanner has its own asset selection (MultiSelect for screening many pairs) separate from the global pair bar — this is intentional.

### What's fragile
- `research_hub.py` is still ~850 lines with all 8 module callbacks inline — a future refactor could split each module into its own file under `app/pages/research/`. Not urgent but would help maintainability.
- The Plotly template is registered at import time in `layout.py` — if layout isn't imported first, charts won't get the theme.

### Authoritative diagnostics
- `python run_dashboard.py` — if it starts and `/research/rolling-coint` renders with ETH/ETC pair + chart, the whole stack is working
- `pytest tests/ -q` — 48 tests covering all analysis functions, independent of UI

### What assumptions changed
- Originally planned 3 slices as independent work units — in practice S03's scope was naturally absorbed into S01/S02 since sidebar nav and chart theming were inseparable from the layout and page rewrites.

## Files Created/Modified

- `src/statistical_arbitrage/app/layout.py` — DMC AppShell, sidebar NavLinks, Plotly dark template, global pair selects
- `src/statistical_arbitrage/app/main.py` — added global pair population + sync callbacks
- `src/statistical_arbitrage/app/pages/pair_scanner.py` — full DMC rewrite with MultiSelect, Table
- `src/statistical_arbitrage/app/pages/pair_deep_dive.py` — DMC rewrite, reads global pair store
- `src/statistical_arbitrage/app/pages/research_hub.py` — complete rewrite, 8 modules via URL routing, global pair consumption
- `src/statistical_arbitrage/app/assets/dbc_dark_overrides.css` — deleted (no longer needed)
- `pyproject.toml` — added dash-mantine-components, dash-iconify deps
