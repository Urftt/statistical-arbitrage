# Decisions Register

| # | When | Scope | Decision | Choice | Rationale | Revisable? |
|---|------|-------|----------|--------|-----------|------------|
| 1 | 2026-03-15 | M001 | Research module count for V1 | 8 modules | Balance between coverage and quality. Deferred: half-life stability, spread normality, regime detection, hedge ratio method. | Yes — can add deferred modules in V2 |
| 2 | 2026-03-15 | M001 | Takeaway format | One-line auto-generated banners (green/yellow/red) | Low complexity, data-driven, no risk of bad prose. Richer summaries deferred. | Yes — can upgrade to multi-line in V2 |
| 3 | 2026-03-15 | M001 | Analysis code location | Separate analysis/ module, not in Dash callbacks | Current research_hub.py is 1300 lines with mixed concerns. Testability requires separation. | No — this is a quality constraint |
| 4 | 2026-03-15 | M001 | Pair selector behavior | Pre-populated from cache on page load | Current "Load pairs" button is unnecessary friction. | No — UX improvement |
| 5 | 2026-03-15 | M001 | Spread construction methods | Price-level, log-price, ratio (3 methods) | Must compare empirically which produces most stationary spread. | Yes — can add more methods later |
| 6 | 2026-03-15 | M001 | Cointegration test methods | Engle-Granger + Johansen | EG is order-sensitive (which asset is dependent). Johansen is symmetric. Both in statsmodels. | Yes — can add Phillips-Ouliaris later |
