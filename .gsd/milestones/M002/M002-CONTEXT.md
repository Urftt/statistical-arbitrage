# M002: UI Redesign — Dash Mantine Components

**Gathered:** 2026-03-15
**Status:** Ready for planning

## Project Description

Full UI shell redesign of the StatArb Research platform. Migrate from Dash Bootstrap Components (DARKLY theme) to Dash Mantine Components for a modern, cohesive design. Restructure navigation from flat top-bar to sidebar AppShell. Add global pair selector to eliminate redundant per-module pair pickers.

## Why This Milestone

The current UI has structural problems:
1. **Redundant pair selection** — every Research Hub module has its own Asset 1/Asset 2 dropdowns. User selects the same pair 8 times.
2. **Empty void on page load** — every page shows nothing until you manually click Run. No information density, no visual reward.
3. **Generic Bootstrap look** — DBC DARKLY is the default for every Dash tutorial. Nothing distinctive.
4. **Flat navigation** — 3 text links in a top bar. Research Hub crams 8 modules into 2 rows of tabs.
5. **No state flow** — Scanner finds a good pair, but Deep Dive and Research Hub don't know about it.

## User-Visible Outcome

### When this milestone is complete, the user can:

- Open the app and see a polished sidebar with clear navigation hierarchy (Scanner > Deep Dive > Research modules)
- Select a pair once in the global header bar and have it flow to all pages/modules
- Navigate Research Hub modules via sidebar sub-links instead of cramped tab rows
- See a visually distinctive, professional dark-theme design (Mantine, not Bootstrap)

### Entry point / environment

- Entry point: `python run_dashboard.py` → http://localhost:8050
- Environment: local dev / browser
- Live dependencies involved: Bitvavo API (via cache)

## Completion Class

- Contract complete means: app starts, all pages render, no console errors, all 8 research modules still produce correct results
- Integration complete means: global pair selector flows to all pages, navigation works across all routes
- Operational complete means: none (local dev tool)

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- User can select ETH/ETC in the global pair bar, navigate through Scanner → Deep Dive → all 8 Research modules, and see results for that pair on every page without re-selecting
- All existing analysis functionality still works (rolling coint, OOS, spread, etc.)
- No JavaScript console errors during normal usage

## Risks and Unknowns

- **DMC + Dash 4 compatibility** — DMC 2.x claims Dash 4 support but we haven't tested it yet
- **Callback ID conflicts** — migrating from DBC to DMC means changing many component IDs; could break existing callbacks
- **Plotly chart theme integration** — need Plotly figures to look good inside Mantine's dark theme

## Existing Codebase / Prior Art

- `src/statistical_arbitrage/app/main.py` — current Dash app entry point, page routing, DBC-based
- `src/statistical_arbitrage/app/layout.py` — current DBC navbar + page container
- `src/statistical_arbitrage/app/pages/research_hub.py` — 1297 lines, 8 modules with per-module pair selectors
- `src/statistical_arbitrage/app/components/research_ui.py` — shared DBC-based module components
- `src/statistical_arbitrage/app/pages/pair_scanner.py` — scanner page with DBC controls
- `src/statistical_arbitrage/app/pages/pair_deep_dive.py` — deep dive page with DBC controls
- `src/statistical_arbitrage/analysis/research.py` — analysis functions (untouched by this milestone)

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions.

## Scope

### In Scope

- Migrate entire app shell from DBC to DMC (AppShell, sidebar, header)
- Global pair selector in header (Asset 1, Asset 2, Timeframe) stored in dcc.Store
- Sidebar navigation with NavLink hierarchy (pages + research sub-modules)
- Rebuild all page layouts with DMC components (Paper, Card, Select, Button, etc.)
- Consistent Mantine dark theme across all pages
- Plotly figure template that matches Mantine dark theme
- Remove homepage — go directly to Scanner
- Pre-populate all pair selectors at layout time (no "Load pairs" button)

### Out of Scope / Non-Goals

- New analysis modules or research functionality
- Mobile/tablet responsive design
- Backtesting engine or paper trading
- New data fetching capabilities
- Auto-run behavior (keep explicit Run buttons for now)

## Technical Constraints

- Python 3.12, Dash 4.0.0
- DMC 2.x with dash-iconify for icons
- Keep all analysis code in `analysis/` untouched
- Must remain a single-page Dash app with client-side routing
- Desktop-only (no responsive breakpoints needed)

## Integration Points

- `analysis/research.py` — all research analysis functions, called by callbacks
- `analysis/cointegration.py` — PairAnalysis class, used by scanner and deep dive
- `data/cache_manager.py` — DataCacheManager for fetching/caching OHLCV data
