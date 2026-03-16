# M002: UI Redesign — Dash Mantine Components

**Vision:** Transform the app from generic Bootstrap dark theme into a polished Mantine-based research platform with sidebar navigation, global pair selector, and cohesive visual design.

## Success Criteria

- App launches with DMC AppShell layout: header with global pair bar, left sidebar with navigation hierarchy, main content area
- User selects a pair once in the header and it flows to Scanner, Deep Dive, and all Research Hub modules via shared store
- Research Hub modules are navigated via sidebar sub-links, not cramped tab rows
- All 8 research modules produce the same analysis results as before (no analysis code changes)
- Plotly charts integrate visually with Mantine dark theme
- No JavaScript console errors during normal usage

## Key Risks / Unknowns

- **DMC + Dash 4 callback wiring** — DMC components have different property names than DBC (e.g., `value` vs `checked`, different event triggers). Callbacks may need adjustment.
- **Global pair store → page-level consumption** — each page currently manages its own pair state. Wiring a shared store to all pages without breaking existing callbacks is the tricky part.

## Proof Strategy

- DMC + Dash 4 wiring → retire in S01 by building the AppShell with working navigation and proving DMC renders correctly
- Global pair store → retire in S02 by wiring the store to Deep Dive and verifying pair selection flows

## Verification Classes

- Contract verification: app starts without errors, all pages render
- Integration verification: global pair selector flows to all pages, all 8 research modules still produce correct results
- Operational verification: none (local dev tool)
- UAT / human verification: visual inspection of layout, navigation, chart integration, overall polish

## Milestone Definition of Done

This milestone is complete only when all are true:

- All pages render correctly with DMC components
- Global pair selector works and flows state to all pages
- Sidebar navigation provides access to all pages and research modules
- All 8 research modules produce correct analysis results
- Plotly charts look good inside Mantine dark theme
- No console errors during normal navigation and analysis runs
- `python run_dashboard.py` starts clean

## Requirement Coverage

- Covers: R004 (consistent UX), R005 (proper axis labels / dark theme), R006 (loading spinners / error states)
- Partially covers: R001 (8 modules — they still work, just new UI)
- Leaves for later: R007-R010 (deferred modules)
- Orphan risks: none

## Slices

- [x] **S01: AppShell + Sidebar Navigation** `risk:high` `depends:[]`
  > After this: app renders with DMC AppShell (header, sidebar, main area), sidebar navigation works for all pages, Mantine dark theme applied — but pages still use DBC internally
- [x] **S02: Global Pair Selector + Page Migration** `risk:medium` `depends:[S01]`
  > After this: global pair bar in header stores pair/timeframe selection, all pages rebuilt with DMC components, pair flows to Scanner, Deep Dive, and Research Hub
- [x] **S03: Research Hub Redesign + Polish** `risk:low` `depends:[S02]`
  > After this: Research Hub modules navigated via sidebar sub-links, no more tab rows, all 8 modules wired to global pair, charts themed consistently, final visual polish

## Boundary Map

### S01 → S02, S03

Produces:
- DMC AppShell shell with `dmc.MantineProvider`, `dmc.AppShellHeader`, `dmc.AppShellNavbar`, `dmc.AppShellMain`
- Sidebar with `dmc.NavLink` for Scanner, Deep Dive, Research Hub (with sub-links)
- URL-based routing still works (`dcc.Location` + callback)
- `dcc.Store("global-pair-store")` created (but not yet populated)
- Plotly dark theme template matching Mantine colors

Consumes:
- nothing (first slice)

### S02 → S03

Produces:
- Global pair selector components in header (Asset 1, Asset 2, Timeframe selects)
- `global-pair-store` populated by header callbacks
- Scanner and Deep Dive pages rebuilt with DMC components consuming global pair
- Pattern for pages reading from global store

Consumes:
- AppShell layout from S01

### S03

Produces:
- Research Hub with sidebar navigation (no tabs)
- All 8 research modules consuming global pair store
- Consistent chart theming
- Final visual polish pass

Consumes:
- AppShell + sidebar from S01
- Global pair store + page migration pattern from S02
