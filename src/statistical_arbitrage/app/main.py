"""
Main Dash application entry point.

Run with:
    python -m statistical_arbitrage.app.main
    # or
    uv run python -m statistical_arbitrage.app.main
"""

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback

from statistical_arbitrage.app.layout import create_layout
from statistical_arbitrage.app.pages import pair_scanner, pair_deep_dive, research_hub

# Initialize Dash app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="StatArb Research",
    use_pages=False,  # We handle routing ourselves
)

# Set layout
app.layout = create_layout()


# ─── Page routing ────────────────────────────────────────────────────────────
@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname: str):
    """Route to the correct page based on URL path."""
    if pathname == "/scanner":
        return pair_scanner.layout()
    elif pathname == "/deep-dive":
        return pair_deep_dive.layout()
    elif pathname == "/research":
        return research_hub.layout()
    else:
        # Home / overview page
        return _home_page()


def _home_page():
    """Landing page with overview and quick links."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("📊 Statistical Arbitrage Research", className="mt-4 mb-3"),
                html.P(
                    "A research platform for learning and analyzing statistical arbitrage "
                    "opportunities in cryptocurrency markets.",
                    className="lead text-muted",
                ),
                html.Hr(),
            ])
        ]),

        # Quick stats row
        dbc.Row([
            dbc.Col(_info_card(
                "🔍", "Pair Scanner",
                "Scan all Bitvavo EUR pairs for cointegration. "
                "Find which pairs actually have a statistically significant relationship.",
                "/scanner",
            ), md=4),
            dbc.Col(_info_card(
                "🔬", "Pair Deep Dive",
                "Full analysis of a single pair: cointegration test, spread, z-scores, "
                "half-life, distribution analysis, and trading signals.",
                "/deep-dive",
            ), md=4),
            dbc.Col(_info_card(
                "🧪", "Research Hub",
                "Systematic research on the assumptions: optimal timeframes, thresholds, "
                "lookback windows, and more — all data-driven.",
                "/research",
            ), md=4),
        ], className="mb-4"),

        # Research agenda
        dbc.Row([
            dbc.Col([
                html.H3("🔬 Research Agenda", className="mt-4 mb-3"),
                html.P(
                    "No assumptions — everything is researched empirically. "
                    "Here's what we're investigating:",
                    className="text-muted",
                ),
                _research_checklist(),
            ])
        ]),
    ], fluid=True, className="px-4")


def _info_card(icon: str, title: str, description: str, href: str):
    """Create a navigation card."""
    return dbc.Card([
        dbc.CardBody([
            html.H2(icon, className="mb-2"),
            html.H4(title),
            html.P(description, className="text-muted small"),
            dbc.Button("Open →", href=href, color="primary", outline=True, size="sm"),
        ])
    ], className="h-100")


def _research_checklist():
    """Research agenda as a checklist."""
    items = [
        ("Pair Selection", [
            "Which coins are actually cointegrated?",
            "Does cointegration persist over time?",
            "Does market cap similarity matter?",
            "Sector/category effects on cointegration",
        ]),
        ("Timeframe & Lookback", [
            "Optimal candle timeframe (1m → 1d)",
            "Optimal lookback window for cointegration test",
            "Rolling window size for z-score calculation",
        ]),
        ("Signal Thresholds", [
            "Entry z-score threshold (±1.5? ±2.0? ±2.5?)",
            "Exit z-score threshold",
            "Asymmetric thresholds (long vs short)",
        ]),
        ("Mean Reversion Properties", [
            "Half-life distribution across pairs",
            "Half-life stability over time",
            "Spread distribution shape (normality, fat tails)",
        ]),
        ("Risk & Regime", [
            "Regime detection (when cointegration breaks)",
            "Correlation between pair spreads",
            "Transaction cost sensitivity",
        ]),
        ("Hedge Ratio", [
            "Static vs rolling hedge ratio",
            "OLS vs TLS vs Kalman filter estimation",
        ]),
    ]

    rows = []
    for category, questions in items:
        rows.append(html.H5(category, className="mt-3 mb-2"))
        for q in questions:
            rows.append(
                dbc.Row([
                    dbc.Col(html.Span("○", className="text-muted me-2"), width="auto"),
                    dbc.Col(html.Span(q, className="small")),
                ], className="mb-1")
            )

    return html.Div(rows)


# Register page callbacks
pair_scanner.register_callbacks(app)
pair_deep_dive.register_callbacks(app)
research_hub.register_callbacks(app)


def run():
    """Run the Dash development server."""
    app.run(debug=True, port=8050)


if __name__ == "__main__":
    run()
