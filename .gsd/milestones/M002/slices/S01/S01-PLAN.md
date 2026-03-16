# S01: AppShell + Sidebar Navigation

**Goal:** Replace the DBC top-navbar layout with a DMC AppShell (header + sidebar + main). Navigation works for all pages. Mantine dark theme applied globally.
**Demo:** User opens http://localhost:8050, sees a dark-themed Mantine layout with sidebar navigation. Clicking sidebar links navigates to Scanner, Deep Dive, and Research Hub. Pages still render their DBC content inside the new shell.

## Must-Haves

- DMC MantineProvider wrapping entire app with dark color scheme
- AppShell with header (app title + placeholder for future pair bar) and sidebar navbar
- Sidebar NavLinks for Scanner, Deep Dive, Research Hub (with expandable sub-links for 8 modules)
- URL-based routing still works (dcc.Location + callback)
- Active NavLink highlighting based on current URL
- Plotly figure template that matches Mantine dark theme colors
- DBC stylesheets removed, DMC stylesheets in place
- Existing pages render inside the new shell (they still use DBC components internally — that's fine for S01)

## Proof Level

- This slice proves: integration (DMC + Dash 4 work together, navigation routes correctly)
- Real runtime required: yes (browser verification)
- Human/UAT required: yes (visual inspection of layout)

## Verification

- `python run_dashboard.py` starts without errors
- Browser: navigate to /, /scanner, /deep-dive, /research — all render inside AppShell
- Sidebar links highlight correctly for current page
- No JavaScript console errors

## Tasks

- [ ] **T01: Create DMC AppShell layout and routing** `est:45m`
  - Why: This is the core structural change — replaces the entire DBC layout with DMC
  - Files: `src/statistical_arbitrage/app/layout.py`, `src/statistical_arbitrage/app/main.py`, `pyproject.toml`
  - Do: 
    - Rewrite `layout.py` with `dmc.MantineProvider` + `dmc.AppShell` + `dmc.AppShellHeader` + `dmc.AppShellNavbar` + `dmc.AppShellMain`
    - Build sidebar with `dmc.NavLink` hierarchy: Scanner, Deep Dive, Research Hub (expandable with 8 module sub-links)
    - Update `main.py`: remove DBC external_stylesheets, add DMC stylesheets, update routing callback
    - Add `dcc.Store("global-pair-store")` placeholder
    - Create Plotly template that matches Mantine dark theme
    - Keep existing page layout() functions — they render inside AppShellMain
  - Verify: `python run_dashboard.py`, navigate all pages in browser
  - Done when: AppShell renders, sidebar navigation works for all routes, no console errors

- [ ] **T02: Active NavLink highlighting and visual polish** `est:20m`
  - Why: Sidebar needs to show which page/module is active based on URL
  - Files: `src/statistical_arbitrage/app/layout.py`
  - Do:
    - Use `dmc.NavLink(active="exact")` for top-level pages and `active="partial"` for Research Hub parent
    - Add `href` to all NavLinks matching URL routes
    - Style the header (app title, subtle branding)
    - Add custom CSS if needed for AppShell padding, scrolling, sidebar width
  - Verify: Click each sidebar link, verify highlight follows, verify URL matches
  - Done when: Active state correctly shown for all navigation paths including research sub-modules

## Files Likely Touched

- `src/statistical_arbitrage/app/layout.py` — complete rewrite
- `src/statistical_arbitrage/app/main.py` — update imports, stylesheets, routing
- `pyproject.toml` — already has DMC deps added
- `src/statistical_arbitrage/app/assets/` — optional custom CSS
