"""
Pair Scanner page — scan Bitvavo pairs for cointegration relationships.

This is the systematic discovery tool: select coins, run cointegration tests,
rank by statistical significance.
"""

import traceback

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import polars as pl
from dash import Input, Output, State, callback, dcc, html, no_update

from statistical_arbitrage.analysis.cointegration import PairAnalysis
from statistical_arbitrage.data.cache_manager import get_cache_manager


def layout():
    """Pair Scanner page layout."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🔍 Pair Scanner", className="mt-3 mb-1"),
                html.P(
                    "Systematically scan pairs for cointegration. No assumptions — let the data tell us.",
                    className="text-muted mb-3",
                ),
            ])
        ]),

        # Controls row
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    # Coin selector
                    dbc.Col([
                        dbc.Label("Select coins to scan", className="fw-bold"),
                        dcc.Dropdown(
                            id="scanner-coins",
                            multi=True,
                            placeholder="Loading available pairs...",
                            className="mb-2",
                        ),
                        dbc.Button(
                            "Load available pairs",
                            id="scanner-load-pairs",
                            color="secondary",
                            size="sm",
                            className="me-2",
                        ),
                        dbc.Button(
                            "Select top 20 by volume",
                            id="scanner-select-top",
                            color="outline-secondary",
                            size="sm",
                        ),
                    ], md=5),

                    # Parameters
                    dbc.Col([
                        dbc.Label("Timeframe", className="fw-bold"),
                        dcc.Dropdown(
                            id="scanner-timeframe",
                            options=[
                                {"label": "15 minutes", "value": "15m"},
                                {"label": "1 hour", "value": "1h"},
                                {"label": "4 hours", "value": "4h"},
                                {"label": "1 day", "value": "1d"},
                            ],
                            value="1h",
                            clearable=False,
                        ),
                    ], md=2),

                    dbc.Col([
                        dbc.Label("History (days)", className="fw-bold"),
                        dbc.Input(
                            id="scanner-days",
                            type="number",
                            value=90,
                            min=7,
                            max=365,
                        ),
                    ], md=2),

                    # Run button
                    dbc.Col([
                        dbc.Label("\u00a0", className="fw-bold"),  # Spacer
                        html.Div([
                            dbc.Button(
                                [html.I(className="fa-solid fa-play me-2"), "Run Scan"],
                                id="scanner-run",
                                color="primary",
                                className="w-100",
                            ),
                        ]),
                    ], md=3),
                ]),
            ]),
        ], className="mb-3"),

        # Progress / status
        html.Div(id="scanner-status", className="mb-3"),

        # Results
        dcc.Loading(
            html.Div(id="scanner-results"),
            type="dot",
            color="#375a7f",
        ),
    ], fluid=True, className="px-4")


def register_callbacks(app):
    """Register all callbacks for the Pair Scanner page."""

    @app.callback(
        Output("scanner-coins", "options"),
        Input("scanner-load-pairs", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_available_pairs(_):
        """Fetch available EUR pairs from Bitvavo."""
        try:
            cache = get_cache_manager()
            pairs_df = cache.get_available_pairs()
            options = [
                {"label": row["symbol"], "value": row["symbol"]}
                for row in pairs_df.to_dicts()
            ]
            return options
        except Exception as e:
            return [{"label": f"Error: {e}", "value": ""}]

    @app.callback(
        Output("scanner-coins", "value"),
        Input("scanner-select-top", "n_clicks"),
        State("scanner-coins", "options"),
        prevent_initial_call=True,
    )
    def select_top_coins(_, options):
        """Select top coins by common crypto market cap."""
        if not options:
            return no_update

        # Common high-volume EUR pairs on Bitvavo
        top_symbols = [
            "BTC/EUR", "ETH/EUR", "XRP/EUR", "SOL/EUR", "ADA/EUR",
            "DOGE/EUR", "DOT/EUR", "LINK/EUR", "AVAX/EUR", "MATIC/EUR",
            "UNI/EUR", "ATOM/EUR", "LTC/EUR", "ETC/EUR", "ALGO/EUR",
            "XLM/EUR", "FIL/EUR", "NEAR/EUR", "APT/EUR", "ARB/EUR",
        ]
        available = {o["value"] for o in options if o["value"]}
        return [s for s in top_symbols if s in available]

    @app.callback(
        Output("scanner-results", "children"),
        Output("scanner-status", "children"),
        Input("scanner-run", "n_clicks"),
        State("scanner-coins", "value"),
        State("scanner-timeframe", "value"),
        State("scanner-days", "value"),
        prevent_initial_call=True,
    )
    def run_scan(_, coins, timeframe, days):
        """Run cointegration scan on selected pairs."""
        if not coins or len(coins) < 2:
            return no_update, dbc.Alert(
                "Select at least 2 coins to scan.", color="warning"
            )

        cache = get_cache_manager()

        # Step 1: Download data for all selected coins
        status_parts = []
        data = {}
        for i, symbol in enumerate(coins):
            try:
                df = cache.get_candles(symbol, timeframe, days_back=days)
                if not df.is_empty():
                    data[symbol] = df
            except Exception as e:
                status_parts.append(f"⚠️ {symbol}: {e}")

        if len(data) < 2:
            return no_update, dbc.Alert(
                "Need at least 2 coins with data. Check API connection.", color="danger"
            )

        # Step 2: Test all pairs for cointegration
        results = []
        pair_count = 0
        symbols = sorted(data.keys())

        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i + 1:]:
                pair_count += 1
                try:
                    # Align timestamps
                    df1 = data[sym1].select(["timestamp", "close"]).rename({"close": "close1"})
                    df2 = data[sym2].select(["timestamp", "close"]).rename({"close": "close2"})
                    merged = df1.join(df2, on="timestamp", how="inner")

                    if len(merged) < 30:
                        continue

                    # Run cointegration analysis
                    analysis = PairAnalysis(merged["close1"], merged["close2"])
                    coint_result = analysis.test_cointegration()
                    half_life = analysis.calculate_half_life()
                    correlation = analysis.get_correlation()
                    spread_props = analysis.analyze_spread_properties()

                    results.append({
                        "Pair": f"{sym1} / {sym2}",
                        "Asset 1": sym1,
                        "Asset 2": sym2,
                        "Cointegrated": "✅" if coint_result["is_cointegrated"] else "❌",
                        "p-value": round(coint_result["p_value"], 4),
                        "Test Stat": round(coint_result["cointegration_score"], 2),
                        "Hedge Ratio": round(coint_result["hedge_ratio"], 4),
                        "Half-life": round(half_life, 1) if half_life < 10000 else "∞",
                        "Correlation": round(correlation, 3),
                        "Spread Skew": round(spread_props["skewness"], 2),
                        "Spread Kurt": round(spread_props["kurtosis"], 2),
                        "Datapoints": len(merged),
                    })
                except Exception as e:
                    results.append({
                        "Pair": f"{sym1} / {sym2}",
                        "Asset 1": sym1,
                        "Asset 2": sym2,
                        "Cointegrated": "⚠️",
                        "p-value": None,
                        "Test Stat": None,
                        "Hedge Ratio": None,
                        "Half-life": None,
                        "Correlation": None,
                        "Spread Skew": None,
                        "Spread Kurt": None,
                        "Datapoints": 0,
                    })

        if not results:
            return no_update, dbc.Alert("No valid pairs found.", color="warning")

        # Sort by p-value (most cointegrated first)
        results_df = pl.DataFrame(results)
        
        # Build results display
        cointegrated = [r for r in results if r["Cointegrated"] == "✅"]
        not_cointegrated = [r for r in results if r["Cointegrated"] == "❌"]

        status = dbc.Alert([
            html.Strong(f"Scanned {pair_count} pairs. "),
            f"Found {len(cointegrated)} cointegrated, {len(not_cointegrated)} not cointegrated.",
        ], color="success" if cointegrated else "info")

        # Build results table
        table = _build_results_table(results)

        # Build p-value distribution chart
        p_values = [r["p-value"] for r in results if r["p-value"] is not None]
        p_chart = _build_pvalue_chart(p_values)

        return html.Div([
            table,
            dcc.Graph(figure=p_chart, className="mt-3"),
        ]), status


def _build_results_table(results: list[dict]):
    """Build a formatted results table."""
    # Sort: cointegrated first, then by p-value
    sorted_results = sorted(
        results,
        key=lambda r: (0 if r["Cointegrated"] == "✅" else 1, r["p-value"] or 999),
    )

    header = html.Thead(html.Tr([
        html.Th("Pair"),
        html.Th("Coint?"),
        html.Th("p-value"),
        html.Th("Test Stat"),
        html.Th("Hedge Ratio"),
        html.Th("Half-life"),
        html.Th("Correlation"),
        html.Th("Skewness"),
        html.Th("Kurtosis"),
        html.Th("Points"),
    ]))

    rows = []
    for r in sorted_results:
        # Color-code the row
        style = {}
        if r["Cointegrated"] == "✅":
            style = {"backgroundColor": "rgba(0, 200, 83, 0.1)"}

        rows.append(html.Tr([
            html.Td(r["Pair"], className="fw-bold"),
            html.Td(r["Cointegrated"]),
            html.Td(
                f"{r['p-value']:.4f}" if r["p-value"] is not None else "—",
                className="fw-bold" if r["p-value"] is not None and r["p-value"] < 0.05 else "",
            ),
            html.Td(f"{r['Test Stat']:.2f}" if r["Test Stat"] is not None else "—"),
            html.Td(f"{r['Hedge Ratio']:.4f}" if r["Hedge Ratio"] is not None else "—"),
            html.Td(str(r["Half-life"]) if r["Half-life"] is not None else "—"),
            html.Td(f"{r['Correlation']:.3f}" if r["Correlation"] is not None else "—"),
            html.Td(f"{r['Spread Skew']:.2f}" if r["Spread Skew"] is not None else "—"),
            html.Td(f"{r['Spread Kurt']:.2f}" if r["Spread Kurt"] is not None else "—"),
            html.Td(str(r["Datapoints"])),
        ], style=style))

    return dbc.Table(
        [header, html.Tbody(rows)],
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
        className="mt-3",
    )


def _build_pvalue_chart(p_values: list[float]):
    """Build a histogram of p-values."""
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=p_values,
        nbinsx=20,
        marker_color="rgba(55, 90, 127, 0.7)",
        marker_line=dict(color="rgba(55, 90, 127, 1)", width=1),
    ))

    # Add significance threshold line
    fig.add_vline(x=0.05, line_dash="dash", line_color="red",
                  annotation_text="p = 0.05", annotation_position="top right")

    fig.update_layout(
        title="Distribution of Cointegration p-values",
        xaxis_title="p-value",
        yaxis_title="Count",
        template="plotly_dark",
        height=300,
        margin=dict(t=40, b=40, l=40, r=20),
    )

    return fig
