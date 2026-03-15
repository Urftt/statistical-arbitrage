"""
Pair Deep Dive page — full analysis of a single pair.

Select two coins and get the complete picture: cointegration test, spread analysis,
z-score over time, half-life, distribution, rolling metrics, and signal visualization.
"""

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
from dash import Input, Output, State, callback, dcc, html, no_update

from statistical_arbitrage.analysis.cointegration import PairAnalysis
from statistical_arbitrage.data.cache_manager import get_cache_manager


def layout():
    """Pair Deep Dive page layout."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🔬 Pair Deep Dive", className="mt-3 mb-1"),
                html.P(
                    "Complete analysis of a single pair — cointegration, spread, z-scores, "
                    "distribution, half-life, and signals.",
                    className="text-muted mb-3",
                ),
            ])
        ]),

        # Controls
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Asset 1"),
                        dcc.Dropdown(id="dd-asset1", placeholder="Select first coin..."),
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Asset 2"),
                        dcc.Dropdown(id="dd-asset2", placeholder="Select second coin..."),
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Timeframe"),
                        dcc.Dropdown(
                            id="dd-timeframe",
                            options=[
                                {"label": "15 min", "value": "15m"},
                                {"label": "1 hour", "value": "1h"},
                                {"label": "4 hours", "value": "4h"},
                                {"label": "1 day", "value": "1d"},
                            ],
                            value="1h",
                            clearable=False,
                        ),
                    ], md=2),
                    dbc.Col([
                        dbc.Label("Days"),
                        dbc.Input(id="dd-days", type="number", value=90, min=7, max=365),
                    ], md=1),
                    dbc.Col([
                        dbc.Label("Z-score window"),
                        dbc.Input(id="dd-zscore-window", type="number", value=60, min=5, max=500),
                    ], md=1),
                    dbc.Col([
                        dbc.Label("\u00a0"),
                        dbc.Button(
                            [html.I(className="fa-solid fa-microscope me-2"), "Analyze"],
                            id="dd-analyze",
                            color="primary",
                            className="w-100",
                        ),
                    ], md=2),
                ]),
                # Load pairs button
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Load available pairs",
                            id="dd-load-pairs",
                            color="link",
                            size="sm",
                            className="mt-2 p-0",
                        ),
                    ]),
                ]),
            ]),
        ], className="mb-3"),

        # Results
        dcc.Loading(
            html.Div(id="dd-results"),
            type="dot",
            color="#375a7f",
        ),
    ], fluid=True, className="px-4")


def register_callbacks(app):
    """Register Deep Dive callbacks."""

    @app.callback(
        Output("dd-asset1", "options"),
        Output("dd-asset2", "options"),
        Input("dd-load-pairs", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_pairs(_):
        cache = get_cache_manager()
        pairs_df = cache.get_available_pairs()
        options = [{"label": r["symbol"], "value": r["symbol"]} for r in pairs_df.to_dicts()]
        return options, options

    @app.callback(
        Output("dd-results", "children"),
        Input("dd-analyze", "n_clicks"),
        State("dd-asset1", "value"),
        State("dd-asset2", "value"),
        State("dd-timeframe", "value"),
        State("dd-days", "value"),
        State("dd-zscore-window", "value"),
        prevent_initial_call=True,
    )
    def run_analysis(_, asset1, asset2, timeframe, days, zscore_window):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")

        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        cache = get_cache_manager()

        try:
            df1 = cache.get_candles(asset1, timeframe, days_back=days)
            df2 = cache.get_candles(asset2, timeframe, days_back=days)
        except Exception as e:
            return dbc.Alert(f"Data fetch error: {e}", color="danger")

        if df1.is_empty() or df2.is_empty():
            return dbc.Alert("No data available for one or both assets.", color="danger")

        # Align on timestamp
        merged = (
            df1.select(["timestamp", "datetime", "close"]).rename({"close": "close1"})
            .join(
                df2.select(["timestamp", "close"]).rename({"close": "close2"}),
                on="timestamp",
                how="inner",
            )
            .sort("timestamp")
        )

        if len(merged) < 30:
            return dbc.Alert(f"Only {len(merged)} overlapping datapoints — need at least 30.", color="danger")

        # Run analysis
        analysis = PairAnalysis(merged["close1"], merged["close2"])
        coint = analysis.test_cointegration()
        half_life = analysis.calculate_half_life()
        correlation = analysis.get_correlation()
        spread_props = analysis.analyze_spread_properties()
        zscore = analysis.calculate_zscore(window=zscore_window)

        datetimes = merged["datetime"].to_list()
        spread = analysis.spread

        # Build all the charts and cards
        return html.Div([
            # Summary cards
            _summary_cards(asset1, asset2, coint, half_life, correlation, spread_props, len(merged)),
            html.Hr(),

            # Price comparison
            dcc.Graph(figure=_price_chart(datetimes, merged["close1"].to_numpy(), merged["close2"].to_numpy(), asset1, asset2)),

            # Spread and Z-score
            dcc.Graph(figure=_spread_zscore_chart(datetimes, spread, zscore, asset1, asset2, zscore_window)),

            # Scatter + regression
            dbc.Row([
                dbc.Col(dcc.Graph(figure=_scatter_chart(merged["close2"].to_numpy(), merged["close1"].to_numpy(), coint, asset1, asset2)), md=6),
                dbc.Col(dcc.Graph(figure=_distribution_chart(spread, zscore, asset1, asset2)), md=6),
            ]),
        ])


# ─── Chart builders ──────────────────────────────────────────────────────────

def _summary_cards(asset1, asset2, coint, half_life, correlation, spread_props, n_points):
    """Summary stats as cards."""
    cards = [
        _stat_card("Cointegrated?", "✅ Yes" if coint["is_cointegrated"] else "❌ No",
                   f"p = {coint['p_value']:.4f}", "success" if coint["is_cointegrated"] else "danger"),
        _stat_card("p-value", f"{coint['p_value']:.4f}",
                   f"Stat: {coint['cointegration_score']:.2f}", "info"),
        _stat_card("Half-life", f"{half_life:.1f}" if half_life < 10000 else "∞",
                   "periods", "info"),
        _stat_card("Correlation", f"{correlation:.3f}", "Pearson", "info"),
        _stat_card("Hedge Ratio", f"{coint['hedge_ratio']:.4f}",
                   f"{asset1} = β × {asset2}", "info"),
        _stat_card("Skewness", f"{spread_props['skewness']:.2f}",
                   "spread distribution", "warning" if abs(spread_props['skewness']) > 1 else "info"),
        _stat_card("Kurtosis", f"{spread_props['kurtosis']:.2f}",
                   "excess (normal=0)", "warning" if spread_props['kurtosis'] > 3 else "info"),
        _stat_card("Datapoints", str(n_points), "overlapping candles", "secondary"),
    ]
    return dbc.Row([dbc.Col(c, className="mb-2") for c in cards])


def _stat_card(title, value, subtitle, color):
    return dbc.Card([
        dbc.CardBody([
            html.P(title, className="text-muted small mb-0"),
            html.H4(value, className="mb-0"),
            html.Small(subtitle, className="text-muted"),
        ], className="p-2"),
    ], color=color, outline=True)


def _price_chart(datetimes, prices1, prices2, name1, name2):
    """Normalized price comparison."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=datetimes, y=prices1, name=name1, line=dict(width=1.5),
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=datetimes, y=prices2, name=name2, line=dict(width=1.5),
    ), secondary_y=True)

    fig.update_layout(
        title="Price Comparison",
        template="plotly_dark",
        height=350,
        margin=dict(t=40, b=30, l=50, r=50),
        legend=dict(orientation="h", y=1.1),
    )
    fig.update_yaxes(title_text=name1, secondary_y=False)
    fig.update_yaxes(title_text=name2, secondary_y=True)

    return fig


def _spread_zscore_chart(datetimes, spread, zscore, name1, name2, window):
    """Spread and z-score with signal thresholds."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.4, 0.6],
        vertical_spacing=0.05,
    )

    # Spread
    fig.add_trace(go.Scatter(
        x=datetimes, y=spread, name="Spread", line=dict(width=1, color="#636EFA"),
    ), row=1, col=1)

    # Z-score
    fig.add_trace(go.Scatter(
        x=datetimes, y=zscore, name="Z-score", line=dict(width=1.5, color="#EF553B"),
    ), row=2, col=1)

    # Threshold lines
    for thresh, color, dash_style in [
        (2.0, "rgba(0,200,83,0.5)", "dash"),
        (-2.0, "rgba(0,200,83,0.5)", "dash"),
        (0.5, "rgba(255,165,0,0.4)", "dot"),
        (-0.5, "rgba(255,165,0,0.4)", "dot"),
        (0, "rgba(255,255,255,0.2)", "solid"),
    ]:
        fig.add_hline(
            y=thresh, row=2, col=1,
            line=dict(color=color, dash=dash_style, width=1),
        )

    # Shade extreme zones
    fig.add_hrect(y0=2.0, y1=4.0, row=2, col=1,
                  fillcolor="rgba(0,200,83,0.05)", line_width=0)
    fig.add_hrect(y0=-4.0, y1=-2.0, row=2, col=1,
                  fillcolor="rgba(0,200,83,0.05)", line_width=0)

    fig.update_layout(
        title=f"Spread & Z-score (window={window})",
        template="plotly_dark",
        height=500,
        margin=dict(t=40, b=30, l=50, r=20),
        legend=dict(orientation="h", y=1.08),
    )
    fig.update_yaxes(title_text="Spread", row=1, col=1)
    fig.update_yaxes(title_text="Z-score", row=2, col=1)

    return fig


def _scatter_chart(x, y, coint, name1, name2):
    """Scatter plot with regression line."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers",
        marker=dict(size=3, color="rgba(99,110,250,0.4)"),
        name="Data",
    ))

    # Regression line
    hedge = coint["hedge_ratio"]
    intercept = coint["intercept"]
    x_line = np.array([x.min(), x.max()])
    y_line = hedge * x_line + intercept

    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        line=dict(color="red", width=2, dash="dash"),
        name=f"β={hedge:.4f}",
    ))

    fig.update_layout(
        title=f"Scatter: {name1} vs {name2}",
        xaxis_title=name2,
        yaxis_title=name1,
        template="plotly_dark",
        height=350,
        margin=dict(t=40, b=40, l=50, r=20),
    )

    return fig


def _distribution_chart(spread, zscore, name1, name2):
    """Spread and z-score distribution histograms."""
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Spread Distribution", "Z-score Distribution"])

    fig.add_trace(go.Histogram(
        x=spread, nbinsx=50,
        marker_color="rgba(99,110,250,0.6)",
        name="Spread",
    ), row=1, col=1)

    zscore_clean = zscore[~np.isnan(zscore)]
    fig.add_trace(go.Histogram(
        x=zscore_clean, nbinsx=50,
        marker_color="rgba(239,85,59,0.6)",
        name="Z-score",
    ), row=1, col=2)

    # Add normal distribution overlay for z-score
    from scipy import stats
    x_range = np.linspace(-4, 4, 100)
    normal_pdf = stats.norm.pdf(x_range)
    # Scale to match histogram
    bin_width = 8 / 50  # range / nbins
    scale = len(zscore_clean) * bin_width
    fig.add_trace(go.Scatter(
        x=x_range, y=normal_pdf * scale,
        mode="lines", line=dict(color="white", width=1, dash="dash"),
        name="Normal",
    ), row=1, col=2)

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(t=40, b=30, l=40, r=20),
        showlegend=False,
    )

    return fig
