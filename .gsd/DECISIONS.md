# Decisions Register

| # | When | Scope | Decision | Choice | Rationale | Revisable? |
|---|------|-------|----------|--------|-----------|------------|
| 1 | 2026-03-15 | M001 | Research module count for V1 | 8 modules | Balance between coverage and quality. Deferred: half-life stability, spread normality, regime detection, hedge ratio method. | Yes — can add deferred modules in V2 |
| 2 | 2026-03-15 | M001 | Takeaway format | One-line auto-generated banners (green/yellow/red) | Low complexity, data-driven, no risk of bad prose. Richer summaries deferred. | Yes — can upgrade to multi-line in V2 |
| 3 | 2026-03-15 | M001 | Analysis code location | Separate analysis/ module, not in Dash callbacks | Current research_hub.py is 1300 lines with mixed concerns. Testability requires separation. | No — this is a quality constraint |
| 4 | 2026-03-15 | M001 | Pair selector behavior | Pre-populated from cache on page load | Current "Load pairs" button is unnecessary friction. | No — UX improvement |
| 5 | 2026-03-15 | M001 | Spread construction methods | Price-level, log-price, ratio (3 methods) | Must compare empirically which produces most stationary spread. | Yes — can add more methods later |
| 6 | 2026-03-15 | M001 | Cointegration test methods | Engle-Granger + Johansen | EG is order-sensitive (which asset is dependent). Johansen is symmetric. Both in statsmodels. | Yes — can add Phillips-Ouliaris later |
| 7 | 2026-03-15 | M002 | UI framework | Dash Mantine Components (DMC) replacing Dash Bootstrap Components (DBC) | DBC/DARKLY is generic Bootstrap. DMC provides Mantine's AppShell, proper sidebar nav, beautiful dark theme, better form controls. Different tier from Bootstrap. | No — full migration |
| 8 | 2026-03-15 | M002 | App layout pattern | AppShell with sidebar navigation | Flat top-bar with 3 links wastes space, provides no hierarchy. Sidebar gives room for Research Hub sub-modules and future expansion. | Yes — could add collapsible sidebar later |
| 9 | 2026-03-15 | M002 | Global pair selector | Header-level pair bar with dcc.Store | Currently each module/page has its own pair dropdowns. User selects same pair 8 times. Global selector eliminates redundancy. | No — core UX improvement |
| 10 | 2026-03-15 | M002 | Homepage | Remove — sidebar provides direct navigation | Homepage was 3 info cards linking to pages. Sidebar makes it redundant. Scanner is the natural entry point. | Yes — could add overview dashboard later |
