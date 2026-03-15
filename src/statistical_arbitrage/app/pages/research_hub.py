"""
Research Hub — systematic empirical testing of statistical arbitrage assumptions.

Each tab is a self-contained research module that answers one specific question
with real data. Analysis logic lives in analysis/research.py — this file is
purely layout and callback wiring.
"""

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html, no_update

from statistical_arbitrage.app.components.research_ui import (
    coming_soon_module,
    module_layout,
    pair_control_bar,
    takeaway_banner,
)
from statistical_arbitrage.analysis.research import (
    rolling_cointegration,
    rolling_cointegration_takeaway,
    out_of_sample_validation,
    oos_validation_takeaway,
    compare_spread_methods,
    spread_methods_takeaway,
    compare_cointegration_methods,
    coint_methods_takeaway,
    compare_timeframes,
    timeframe_takeaway,
    sweep_zscore_thresholds,
    zscore_threshold_takeaway,
    sweep_lookback_windows,
    lookback_window_takeaway,
    transaction_cost_analysis,
    tx_cost_takeaway,
)
from statistical_arbitrage.data.cache_manager import get_cache_manager


# ─── Module definitions ──────────────────────────────────────────────────────

MODULES = [
    {"id": "rolling-coint", "label": "🔄 Rolling Stability", "built": True},
    {"id": "oos-validation", "label": "✂️ Out-of-Sample", "built": True},
    {"id": "timeframe", "label": "⏱️ Timeframe", "built": True},
    {"id": "spread-construction", "label": "📉 Spread Method", "built": True},
    {"id": "zscore-threshold", "label": "📊 Z-score Threshold", "built": True},
    {"id": "lookback-window", "label": "🪟 Lookback Window", "built": True},
    {"id": "tx-cost", "label": "💰 Transaction Costs", "built": True},
    {"id": "coint-method", "label": "🧪 Coint. Method", "built": True},
]


# ─── Page layout ─────────────────────────────────────────────────────────────


def layout():
    """Research Hub page layout."""
    # Pre-fetch pair options at layout time
    try:
        cache = get_cache_manager()
        pairs_df = cache.get_available_pairs()
        symbols = sorted(pairs_df["symbol"].to_list())
        pair_options = [{"label": s, "value": s} for s in symbols]
    except Exception:
        pair_options = []

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🧪 Research Hub", className="mt-3 mb-1"),
                html.P(
                    "No assumptions. Test everything empirically.",
                    className="text-muted mb-3",
                ),
            ])
        ]),

        # Module tabs
        dbc.Tabs(
            [dbc.Tab(label=m["label"], tab_id=m["id"]) for m in MODULES],
            id="research-tabs",
            active_tab="rolling-coint",
            className="mb-3",
        ),

        # Tab content
        html.Div(id="research-tab-content"),

        # Hidden store for pair options
        dcc.Store(id="research-pair-options", data=pair_options, storage_type="memory"),
    ], fluid=True, className="px-4")


# ─── Callbacks ───────────────────────────────────────────────────────────────


def register_callbacks(app):
    """Register all Research Hub callbacks."""

    # ── Tab routing ──────────────────────────────────────────────────────
    @app.callback(
        Output("research-tab-content", "children"),
        Input("research-tabs", "active_tab"),
        Input("research-pair-options", "data"),
    )
    def render_tab(tab_id, pair_options):
        opts = pair_options or []

        if tab_id == "rolling-coint":
            return _rolling_coint_layout(opts)
        elif tab_id == "oos-validation":
            return _oos_validation_layout(opts)
        elif tab_id == "spread-construction":
            return _spread_construction_layout(opts)
        elif tab_id == "coint-method":
            return _coint_method_layout(opts)
        elif tab_id == "timeframe":
            return _timeframe_layout(opts)
        elif tab_id == "zscore-threshold":
            return _zscore_threshold_layout(opts)
        elif tab_id == "lookback-window":
            return _lookback_window_layout(opts)
        elif tab_id == "tx-cost":
            return _tx_cost_layout(opts)

        # Find module info for coming soon
        for m in MODULES:
            if m["id"] == tab_id and not m["built"]:
                return coming_soon_module(
                    m["label"],
                    _module_descriptions().get(m["id"], "Research module under development."),
                )

        return html.P("Select a module.")

    # ── Rolling Cointegration module ─────────────────────────────────────
    @app.callback(
        Output("rolling-coint-results", "children"),
        Input("rolling-coint-run", "n_clicks"),
        State("rolling-coint-asset1", "value"),
        State("rolling-coint-asset2", "value"),
        State("rolling-coint-timeframe", "value"),
        State("rolling-coint-window", "value"),
        prevent_initial_call=True,
    )
    def run_rolling_coint(_, asset1, asset2, timeframe, window):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        window = int(window or 90)

        try:
            cache = get_cache_manager()
            days = 365 if timeframe in ("1h", "15m") else 730
            df1 = cache.get_candles(asset1, timeframe, days_back=days)
            df2 = cache.get_candles(asset2, timeframe, days_back=days)

            if df1.is_empty() or df2.is_empty():
                return dbc.Alert(
                    f"No cached data for {asset1} or {asset2} at {timeframe}. "
                    "Data will be fetched on first access — try again in a moment.",
                    color="warning",
                )

            # Merge on timestamp
            merged = (
                df1.select(["timestamp", "datetime", "close"]).rename({"close": "c1"})
                .join(
                    df2.select(["timestamp", "close"]).rename({"close": "c2"}),
                    on="timestamp",
                    how="inner",
                )
                .sort("timestamp")
            )

            if len(merged) < window + 10:
                return dbc.Alert(
                    f"Not enough overlapping data: {len(merged)} points, need at least {window + 10}. "
                    f"Try a smaller window or different timeframe.",
                    color="warning",
                )

            # Run analysis — use step > 1 for large datasets to keep it responsive
            n = len(merged)
            step = max(1, n // 500)  # ~500 data points in output

            results = rolling_cointegration(
                prices1=merged["c1"].to_numpy(),
                prices2=merged["c2"].to_numpy(),
                timestamps=merged["datetime"].to_list(),
                window=window,
                step=step,
            )

            if results.is_empty():
                return dbc.Alert("Analysis produced no results.", color="danger")

            # Generate takeaway
            tk = rolling_cointegration_takeaway(results)

            # Build chart
            fig = _build_rolling_coint_chart(results, asset1, asset2, timeframe, window)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _rolling_coint_stats_table(results),
            ])

        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Out-of-Sample Validation module ──────────────────────────────────
    @app.callback(
        Output("oos-validation-results", "children"),
        Input("oos-validation-run", "n_clicks"),
        State("oos-validation-asset1", "value"),
        State("oos-validation-asset2", "value"),
        State("oos-validation-timeframe", "value"),
        prevent_initial_call=True,
    )
    def run_oos_validation(_, asset1, asset2, timeframe):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        try:
            merged = _fetch_and_merge(asset1, asset2, timeframe)
            if isinstance(merged, dbc.Alert):
                return merged

            results = out_of_sample_validation(
                merged["c1"].to_numpy(),
                merged["c2"].to_numpy(),
            )

            if not results:
                return dbc.Alert("Not enough data for out-of-sample validation (need >60 points).", color="warning")

            tk = oos_validation_takeaway(results)
            fig = _build_oos_chart(results, asset1, asset2, timeframe)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _oos_stats_table(results),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Spread Construction module ───────────────────────────────────────
    @app.callback(
        Output("spread-construction-results", "children"),
        Input("spread-construction-run", "n_clicks"),
        State("spread-construction-asset1", "value"),
        State("spread-construction-asset2", "value"),
        State("spread-construction-timeframe", "value"),
        prevent_initial_call=True,
    )
    def run_spread_construction(_, asset1, asset2, timeframe):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        try:
            merged = _fetch_and_merge(asset1, asset2, timeframe)
            if isinstance(merged, dbc.Alert):
                return merged

            results = compare_spread_methods(
                merged["c1"].to_numpy(),
                merged["c2"].to_numpy(),
            )

            if not results:
                return dbc.Alert("Could not compute any spread methods.", color="danger")

            tk = spread_methods_takeaway(results)
            fig = _build_spread_methods_chart(results, asset1, asset2, timeframe, merged)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _spread_methods_table(results),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Cointegration Method module ──────────────────────────────────────
    @app.callback(
        Output("coint-method-results", "children"),
        Input("coint-method-run", "n_clicks"),
        State("coint-method-asset1", "value"),
        State("coint-method-asset2", "value"),
        State("coint-method-timeframe", "value"),
        prevent_initial_call=True,
    )
    def run_coint_method(_, asset1, asset2, timeframe):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        try:
            merged = _fetch_and_merge(asset1, asset2, timeframe)
            if isinstance(merged, dbc.Alert):
                return merged

            results = compare_cointegration_methods(
                merged["c1"].to_numpy(),
                merged["c2"].to_numpy(),
            )

            if not results:
                return dbc.Alert("Could not run cointegration tests.", color="danger")

            tk = coint_methods_takeaway(results)
            fig = _build_coint_methods_chart(results, asset1, asset2, timeframe)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _coint_methods_table(results),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Timeframe module ─────────────────────────────────────────────────
    @app.callback(
        Output("timeframe-results", "children"),
        Input("timeframe-run", "n_clicks"),
        State("timeframe-asset1", "value"),
        State("timeframe-asset2", "value"),
        prevent_initial_call=True,
    )
    def run_timeframe(_, asset1, asset2):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        try:
            def get_merged(a1, a2, tf):
                m = _fetch_and_merge(a1, a2, tf, min_points=30)
                return None if isinstance(m, dbc.Alert) else m

            results = compare_timeframes(get_merged, asset1, asset2)
            valid = [r for r in results if r.p_value is not None]
            if not valid:
                return dbc.Alert("No timeframes had sufficient data.", color="warning")

            tk = timeframe_takeaway(results)
            fig = _build_timeframe_chart(results, asset1, asset2)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _timeframe_table(results),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Z-score Threshold module ─────────────────────────────────────────
    @app.callback(
        Output("zscore-threshold-results", "children"),
        Input("zscore-threshold-run", "n_clicks"),
        State("zscore-threshold-asset1", "value"),
        State("zscore-threshold-asset2", "value"),
        State("zscore-threshold-timeframe", "value"),
        State("zscore-threshold-window", "value"),
        prevent_initial_call=True,
    )
    def run_zscore_threshold(_, asset1, asset2, timeframe, window):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        window = int(window or 60)

        try:
            merged = _fetch_and_merge(asset1, asset2, timeframe)
            if isinstance(merged, dbc.Alert):
                return merged

            p1 = merged["c1"].to_numpy()
            p2 = merged["c2"].to_numpy()
            hr = float(np.polyfit(p2, p1, 1)[0])
            spread = p1 - hr * p2

            import polars as pl
            spread_series = pl.Series(spread)
            rolling_mean = spread_series.rolling_mean(window_size=window)
            rolling_std = spread_series.rolling_std(window_size=window)
            zscore = ((spread_series - rolling_mean) / rolling_std).to_numpy()

            results = sweep_zscore_thresholds(zscore)
            if not results:
                return dbc.Alert("Could not compute z-score thresholds.", color="danger")

            tk = zscore_threshold_takeaway(results)
            fig = _build_threshold_chart(results, asset1, asset2, timeframe, window)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Lookback Window module ───────────────────────────────────────────
    @app.callback(
        Output("lookback-window-results", "children"),
        Input("lookback-window-run", "n_clicks"),
        State("lookback-window-asset1", "value"),
        State("lookback-window-asset2", "value"),
        State("lookback-window-timeframe", "value"),
        prevent_initial_call=True,
    )
    def run_lookback_window(_, asset1, asset2, timeframe):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        try:
            merged = _fetch_and_merge(asset1, asset2, timeframe)
            if isinstance(merged, dbc.Alert):
                return merged

            p1 = merged["c1"].to_numpy()
            p2 = merged["c2"].to_numpy()
            hr = float(np.polyfit(p2, p1, 1)[0])
            spread = p1 - hr * p2

            results = sweep_lookback_windows(spread)
            if not results:
                return dbc.Alert("Not enough data for lookback analysis.", color="warning")

            tk = lookback_window_takeaway(results)
            fig = _build_lookback_chart(results, asset1, asset2, timeframe)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _lookback_table(results),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")

    # ── Transaction Cost module ──────────────────────────────────────────
    @app.callback(
        Output("tx-cost-results", "children"),
        Input("tx-cost-run", "n_clicks"),
        State("tx-cost-asset1", "value"),
        State("tx-cost-asset2", "value"),
        State("tx-cost-timeframe", "value"),
        State("tx-cost-window", "value"),
        prevent_initial_call=True,
    )
    def run_tx_cost(_, asset1, asset2, timeframe, window):
        if not asset1 or not asset2:
            return dbc.Alert("Select both assets.", color="warning")
        if asset1 == asset2:
            return dbc.Alert("Select two different assets.", color="warning")

        window = int(window or 60)

        try:
            merged = _fetch_and_merge(asset1, asset2, timeframe)
            if isinstance(merged, dbc.Alert):
                return merged

            import polars as pl
            p1 = merged["c1"].to_numpy()
            p2 = merged["c2"].to_numpy()
            hr = float(np.polyfit(p2, p1, 1)[0])
            spread = p1 - hr * p2

            spread_series = pl.Series(spread)
            rolling_mean = spread_series.rolling_mean(window_size=window)
            rolling_std = spread_series.rolling_std(window_size=window)
            zscore = ((spread_series - rolling_mean) / rolling_std).to_numpy()

            results = transaction_cost_analysis(p1, p2, zscore)
            if not results:
                return dbc.Alert("Could not analyze transaction costs.", color="danger")

            tk = tx_cost_takeaway(results)
            fig = _build_tx_cost_chart(results, asset1, asset2, timeframe)

            return html.Div([
                takeaway_banner(tk.text, tk.severity),
                dcc.Graph(figure=fig, config={"displayModeBar": True}),
                _tx_cost_table(results),
            ])
        except Exception as e:
            return dbc.Alert(f"Analysis failed: {e}", color="danger")


def _fetch_and_merge(asset1: str, asset2: str, timeframe: str, min_points: int = 60):
    """Fetch and merge two assets. Returns merged DataFrame or Alert on error."""
    cache = get_cache_manager()
    days = 365 if timeframe in ("1h", "15m") else 730
    df1 = cache.get_candles(asset1, timeframe, days_back=days)
    df2 = cache.get_candles(asset2, timeframe, days_back=days)

    if df1.is_empty() or df2.is_empty():
        return dbc.Alert(
            f"No cached data for {asset1} or {asset2} at {timeframe}.",
            color="warning",
        )

    merged = (
        df1.select(["timestamp", "datetime", "close"]).rename({"close": "c1"})
        .join(
            df2.select(["timestamp", "close"]).rename({"close": "c2"}),
            on="timestamp",
            how="inner",
        )
        .sort("timestamp")
    )

    if len(merged) < min_points:
        return dbc.Alert(
            f"Not enough overlapping data: {len(merged)} points, need at least {min_points}.",
            color="warning",
        )

    return merged


# ─── Module layouts ──────────────────────────────────────────────────────────


def _rolling_coint_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Rolling Cointegration Stability module."""
    controls = pair_control_bar(
        prefix="rolling-coint",
        pair_options=pair_options,
        show_timeframe=True,
        show_window=True,
        window_default=90,
        window_min=30,
        window_max=365,
    )
    return module_layout(
        module_id="rolling-coint",
        title="🔄 Rolling Cointegration Stability",
        description="Does this pair stay cointegrated over time, or does the relationship break down?",
        controls=controls,
    )


def _oos_validation_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Out-of-Sample Validation module."""
    controls = pair_control_bar(
        prefix="oos-validation",
        pair_options=pair_options,
        show_timeframe=True,
    )
    return module_layout(
        module_id="oos-validation",
        title="✂️ Out-of-Sample Validation",
        description="Does in-sample cointegration predict out-of-sample behavior? Splits data at multiple points to test generalization.",
        controls=controls,
    )


def _spread_construction_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Spread Construction module."""
    controls = pair_control_bar(
        prefix="spread-construction",
        pair_options=pair_options,
        show_timeframe=True,
    )
    return module_layout(
        module_id="spread-construction",
        title="📉 Spread Construction Method",
        description="Price-level, log-price, or ratio — which spread construction produces the most stationary result?",
        controls=controls,
    )


def _coint_method_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Cointegration Test Method module."""
    controls = pair_control_bar(
        prefix="coint-method",
        pair_options=pair_options,
        show_timeframe=True,
    )
    return module_layout(
        module_id="coint-method",
        title="🧪 Cointegration Test Method Comparison",
        description="Engle-Granger vs Johansen — do they agree? Tests both directions for EG to check sensitivity.",
        controls=controls,
    )


def _timeframe_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Optimal Timeframe module."""
    controls = pair_control_bar(
        prefix="timeframe",
        pair_options=pair_options,
    )
    return module_layout(
        module_id="timeframe",
        title="⏱️ Optimal Timeframe",
        description="Which candle interval produces the most robust cointegration? Tests 15m, 1h, 4h, and 1d.",
        controls=controls,
    )


def _zscore_threshold_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Z-score Threshold module."""
    controls = pair_control_bar(
        prefix="zscore-threshold",
        pair_options=pair_options,
        show_timeframe=True,
        show_window=True,
        window_default=60,
        window_min=10,
        window_max=300,
    )
    return module_layout(
        module_id="zscore-threshold",
        title="📊 Z-score Threshold Optimization",
        description="What entry/exit z-score levels maximize signal quality? Sweeps entry ±1.0 to ±3.0 and exit 0 to ±1.0.",
        controls=controls,
    )


def _lookback_window_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Lookback Window module."""
    controls = pair_control_bar(
        prefix="lookback-window",
        pair_options=pair_options,
        show_timeframe=True,
    )
    return module_layout(
        module_id="lookback-window",
        title="🪟 Lookback Window Optimization",
        description="What rolling window produces the best z-score signals? Tests 10 to 200 periods.",
        controls=controls,
    )


def _tx_cost_layout(pair_options: list[dict]) -> html.Div:
    """Layout for the Transaction Cost module."""
    controls = pair_control_bar(
        prefix="tx-cost",
        pair_options=pair_options,
        show_timeframe=True,
        show_window=True,
        window_default=60,
        window_min=10,
        window_max=300,
    )
    return module_layout(
        module_id="tx-cost",
        title="💰 Transaction Cost Sensitivity",
        description="Is the spread wide enough to profit after Bitvavo fees (0.15% maker / 0.25% taker)?",
        controls=controls,
    )


# ─── Chart builders ──────────────────────────────────────────────────────────


def _build_rolling_coint_chart(
    results, asset1: str, asset2: str, timeframe: str, window: int,
) -> go.Figure:
    """Build the rolling cointegration p-value chart."""
    valid = results.filter(results["p_value"].is_not_null())

    timestamps = valid["timestamp"].to_list()
    p_values = valid["p_value"].to_list()

    fig = go.Figure()

    # Shade regions: green below 0.05, red above
    fig.add_hrect(
        y0=0, y1=0.05,
        fillcolor="rgba(0, 200, 83, 0.08)",
        line_width=0,
    )
    fig.add_hrect(
        y0=0.05, y1=1.0,
        fillcolor="rgba(255, 82, 82, 0.05)",
        line_width=0,
    )

    # P-value line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=p_values,
        mode="lines",
        name="p-value",
        line=dict(color="#375a7f", width=1.5),
        hovertemplate="Date: %{x}<br>p-value: %{y:.4f}<extra></extra>",
    ))

    # Significance threshold
    fig.add_hline(
        y=0.05,
        line_dash="dash",
        line_color="rgba(255, 193, 7, 0.8)",
        annotation_text="α = 0.05",
        annotation_position="top right",
        annotation_font_color="rgba(255, 193, 7, 0.8)",
    )

    fig.update_layout(
        title=f"Rolling Cointegration: {asset1} / {asset2} ({timeframe}, window={window})",
        xaxis_title="Date",
        yaxis_title="p-value (Engle-Granger)",
        yaxis=dict(range=[0, max(0.2, min(1.0, max(p_values) * 1.1))]),
        template="plotly_dark",
        height=420,
        margin=dict(t=50, b=40, l=60, r=20),
        showlegend=False,
    )

    return fig


def _rolling_coint_stats_table(results) -> dbc.Card:
    """Summary statistics table for rolling cointegration results."""
    import polars as pl

    valid = results.filter(pl.col("p_value").is_not_null())
    if valid.is_empty():
        return html.Div()

    total = valid.height
    coint_count = valid.filter(pl.col("is_cointegrated") == True).height
    pct = coint_count / total * 100

    p_values = valid["p_value"]
    hedge_ratios = valid.filter(pl.col("hedge_ratio").is_not_null())["hedge_ratio"]

    # Count breakdowns
    is_coint = valid["is_cointegrated"].to_list()
    breakdowns = sum(1 for a, b in zip(is_coint[:-1], is_coint[1:]) if a and not b)

    rows = [
        ("Windows tested", str(total)),
        ("Cointegrated", f"{coint_count} / {total} ({pct:.0f}%)"),
        ("Breakdowns", str(breakdowns)),
        ("Median p-value", f"{p_values.median():.4f}"),
        ("Min p-value", f"{p_values.min():.4f}"),
        ("Max p-value", f"{p_values.max():.4f}"),
        ("Median hedge ratio", f"{hedge_ratios.median():.4f}" if not hedge_ratios.is_empty() else "—"),
        ("Hedge ratio std", f"{hedge_ratios.std():.4f}" if not hedge_ratios.is_empty() else "—"),
    ]

    return dbc.Card(
        dbc.CardBody([
            html.H6("Summary Statistics", className="mb-2"),
            dbc.Table([
                html.Tbody([
                    html.Tr([html.Td(label, className="text-muted"), html.Td(value, className="fw-bold")])
                    for label, value in rows
                ]),
            ], bordered=False, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


# ─── Out-of-Sample charts ────────────────────────────────────────────────────


def _build_oos_chart(results, asset1: str, asset2: str, timeframe: str) -> go.Figure:
    """Build out-of-sample validation chart."""
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["p-values by Split", "ADF Statistics by Split"],
    )

    splits = [f"{r.split_ratio:.0%}" for r in results]
    formation_p = [r.formation_p_value for r in results]
    trading_p = [r.trading_p_value for r in results]
    formation_adf = [r.formation_adf_stat for r in results]
    trading_adf = [r.trading_adf_stat for r in results]

    fig.add_trace(go.Bar(x=splits, y=formation_p, name="Formation (in-sample)",
                         marker_color="steelblue"), row=1, col=1)
    fig.add_trace(go.Bar(x=splits, y=trading_p, name="Trading (out-of-sample)",
                         marker_color="coral"), row=1, col=1)
    fig.add_hline(y=0.05, line_dash="dash", line_color="rgba(255,193,7,0.8)",
                  annotation_text="α=0.05", row=1, col=1)

    fig.add_trace(go.Bar(x=splits, y=formation_adf, name="Formation ADF",
                         marker_color="steelblue", showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(x=splits, y=trading_adf, name="Trading ADF",
                         marker_color="coral", showlegend=False), row=1, col=2)

    fig.update_xaxes(title_text="Formation / Trading Split", row=1, col=1)
    fig.update_xaxes(title_text="Formation / Trading Split", row=1, col=2)
    fig.update_yaxes(title_text="p-value", row=1, col=1)
    fig.update_yaxes(title_text="ADF Statistic", row=1, col=2)

    fig.update_layout(
        title=f"Out-of-Sample Validation: {asset1} / {asset2} ({timeframe})",
        template="plotly_dark",
        height=400,
        barmode="group",
        margin=dict(t=50, b=40, l=60, r=20),
    )
    return fig


def _oos_stats_table(results) -> dbc.Card:
    """Summary table for OOS validation results."""
    rows = []
    for r in results:
        f_icon = "✅" if r.formation_cointegrated else "❌"
        t_icon = "✅" if r.trading_cointegrated else "❌"
        rows.append(html.Tr([
            html.Td(f"{r.split_ratio:.0%} / {1-r.split_ratio:.0%}"),
            html.Td(f"{r.formation_n}"),
            html.Td(f"{r.trading_n}"),
            html.Td(f"{f_icon} p={r.formation_p_value:.4f}"),
            html.Td(f"{t_icon} p={r.trading_p_value:.4f}"),
            html.Td(f"{r.formation_hedge_ratio:.4f}"),
            html.Td(f"{r.trading_hedge_ratio:.4f}"),
        ]))

    return dbc.Card(
        dbc.CardBody([
            html.H6("Split Results", className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Split"), html.Th("Form. N"), html.Th("Trade N"),
                    html.Th("Formation"), html.Th("Trading (OOS)"),
                    html.Th("Form. HR"), html.Th("Trade HR"),
                ])),
                html.Tbody(rows),
            ], bordered=True, hover=True, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


# ─── Spread Construction charts ──────────────────────────────────────────────


def _build_spread_methods_chart(results, asset1, asset2, timeframe, merged) -> go.Figure:
    """Build spread methods comparison chart."""
    from plotly.subplots import make_subplots
    import numpy as np

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Spreads Over Time", "Spread Distributions", "ADF Statistics", "Spread Properties"],
    )

    colors = ["#375a7f", "#00c853", "#ff6d00"]
    timestamps = merged["datetime"].to_list()

    for i, r in enumerate(results):
        color = colors[i % len(colors)]
        # Time series (normalize for comparison)
        spread_norm = (r.spread - np.mean(r.spread)) / np.std(r.spread) if np.std(r.spread) > 0 else r.spread
        fig.add_trace(go.Scatter(
            x=timestamps, y=spread_norm, name=r.method,
            mode="lines", line=dict(color=color, width=1),
        ), row=1, col=1)

        # Distribution
        fig.add_trace(go.Histogram(
            x=r.spread, name=r.method, nbinsx=50,
            marker_color=color, opacity=0.5, showlegend=False,
        ), row=1, col=2)

    # ADF bar chart
    methods = [r.method for r in results]
    adf_stats = [r.adf_statistic for r in results]
    adf_colors = ["green" if r.is_stationary else "red" for r in results]
    fig.add_trace(go.Bar(
        x=methods, y=adf_stats, marker_color=adf_colors,
        name="ADF Statistic", showlegend=False,
    ), row=2, col=1)

    # Properties comparison
    props = ["Skewness", "Kurtosis"]
    for i, r in enumerate(results):
        fig.add_trace(go.Bar(
            x=props, y=[r.spread_skewness, r.spread_kurtosis],
            name=r.method, marker_color=colors[i % len(colors)], showlegend=False,
        ), row=2, col=2)

    fig.update_yaxes(title_text="Normalized Spread", row=1, col=1)
    fig.update_yaxes(title_text="ADF Statistic", row=2, col=1)

    fig.update_layout(
        title=f"Spread Construction: {asset1} / {asset2} ({timeframe})",
        template="plotly_dark",
        height=600,
        margin=dict(t=50, b=40, l=60, r=20),
        barmode="group",
    )
    return fig


def _spread_methods_table(results) -> dbc.Card:
    """Summary table for spread methods."""
    rows = [
        html.Tr([
            html.Td(r.method),
            html.Td("✅" if r.is_stationary else "❌"),
            html.Td(f"{r.adf_statistic:.4f}"),
            html.Td(f"{r.adf_p_value:.6f}"),
            html.Td(f"{r.spread_std:.6f}"),
            html.Td(f"{r.spread_skewness:.3f}"),
            html.Td(f"{r.spread_kurtosis:.3f}"),
        ])
        for r in results
    ]

    return dbc.Card(
        dbc.CardBody([
            html.H6("Method Comparison", className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Method"), html.Th("Stationary?"), html.Th("ADF Stat"),
                    html.Th("ADF p-value"), html.Th("Std Dev"), html.Th("Skew"), html.Th("Kurtosis"),
                ])),
                html.Tbody(rows),
            ], bordered=True, hover=True, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


# ─── Cointegration Method charts ─────────────────────────────────────────────


def _build_coint_methods_chart(results, asset1, asset2, timeframe) -> go.Figure:
    """Build cointegration method comparison chart."""
    methods = [r.method for r in results]
    colors = ["green" if r.is_cointegrated else "red" for r in results]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=methods,
        y=[abs(r.statistic) for r in results],
        marker_color=colors,
        text=["✅ Coint." if r.is_cointegrated else "❌ Not coint." for r in results],
        textposition="outside",
        hovertext=[r.detail for r in results],
        hoverinfo="text",
    ))

    # Add critical value markers for Johansen
    for i, r in enumerate(results):
        if r.critical_value is not None:
            fig.add_shape(
                type="line",
                x0=i - 0.4, x1=i + 0.4,
                y0=r.critical_value, y1=r.critical_value,
                line=dict(color="yellow", width=2, dash="dash"),
            )

    fig.update_layout(
        title=f"Cointegration Tests: {asset1} / {asset2} ({timeframe})",
        xaxis_title="Test Method",
        yaxis_title="|Test Statistic|",
        template="plotly_dark",
        height=400,
        margin=dict(t=50, b=100, l=60, r=20),
        showlegend=False,
    )
    fig.update_xaxes(tickangle=-20)

    return fig


def _coint_methods_table(results) -> dbc.Card:
    """Summary table for cointegration methods."""
    rows = [
        html.Tr([
            html.Td(r.method),
            html.Td("✅" if r.is_cointegrated else "❌"),
            html.Td(r.detail),
        ])
        for r in results
    ]

    return dbc.Card(
        dbc.CardBody([
            html.H6("Test Results", className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Method"), html.Th("Cointegrated?"), html.Th("Detail"),
                ])),
                html.Tbody(rows),
            ], bordered=True, hover=True, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


# ─── Timeframe charts ────────────────────────────────────────────────────────


def _build_timeframe_chart(results, asset1, asset2) -> go.Figure:
    """Build timeframe comparison chart."""
    from plotly.subplots import make_subplots

    valid = [r for r in results if r.p_value is not None]
    tfs = [r.timeframe for r in valid]
    pvals = [r.p_value for r in valid]
    colors = ["green" if r.is_cointegrated else "red" for r in valid]
    hls = [r.half_life if r.half_life else 0 for r in valid]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=["p-value by Timeframe", "Half-life (periods)", "Data Points"],
    )

    fig.add_trace(go.Bar(x=tfs, y=pvals, marker_color=colors, showlegend=False), row=1, col=1)
    fig.add_hline(y=0.05, line_dash="dash", line_color="rgba(255,193,7,0.8)",
                  annotation_text="α=0.05", row=1, col=1)

    fig.add_trace(go.Bar(x=tfs, y=hls, marker_color="steelblue", showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(
        x=tfs, y=[r.n_datapoints for r in valid],
        marker_color="orange", showlegend=False,
    ), row=1, col=3)

    fig.update_yaxes(title_text="p-value", row=1, col=1)
    fig.update_yaxes(title_text="Periods", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=3)

    fig.update_layout(
        title=f"Timeframe Comparison: {asset1} / {asset2}",
        template="plotly_dark", height=380,
        margin=dict(t=50, b=40, l=60, r=20),
    )
    return fig


def _timeframe_table(results) -> dbc.Card:
    """Summary table for timeframe comparison."""
    rows = []
    for r in results:
        rows.append(html.Tr([
            html.Td(r.timeframe),
            html.Td(str(r.n_datapoints)),
            html.Td("✅" if r.is_cointegrated else "❌"),
            html.Td(f"{r.p_value:.4f}" if r.p_value is not None else "—"),
            html.Td(f"{r.half_life:.1f}" if r.half_life else "—"),
            html.Td(f"{r.hedge_ratio:.4f}" if r.hedge_ratio else "—"),
            html.Td(f"{r.adf_statistic:.4f}" if r.adf_statistic else "—"),
        ]))

    return dbc.Card(
        dbc.CardBody([
            html.H6("Timeframe Results", className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("TF"), html.Th("Points"), html.Th("Coint?"),
                    html.Th("p-value"), html.Th("Half-life"), html.Th("Hedge Ratio"), html.Th("ADF"),
                ])),
                html.Tbody(rows),
            ], bordered=True, hover=True, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


# ─── Z-score Threshold charts ────────────────────────────────────────────────


def _build_threshold_chart(results, asset1, asset2, timeframe, window) -> go.Figure:
    """Build threshold heatmap."""
    from plotly.subplots import make_subplots

    entries = sorted(set(r.entry for r in results))
    exits = sorted(set(r.exit for r in results))

    trade_matrix = []
    duration_matrix = []
    for exit_t in exits:
        t_row, d_row = [], []
        for entry in entries:
            match = [r for r in results if r.entry == entry and r.exit == exit_t]
            t_row.append(match[0].total_trades if match else 0)
            d_row.append(match[0].avg_duration if match and match[0].avg_duration else 0)
        trade_matrix.append(t_row)
        duration_matrix.append(d_row)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Trade Count", "Avg Duration (periods)"],
    )

    fig.add_trace(go.Heatmap(
        x=[str(e) for e in entries], y=[str(e) for e in exits],
        z=trade_matrix, colorscale="Viridis", name="Trades",
    ), row=1, col=1)

    fig.add_trace(go.Heatmap(
        x=[str(e) for e in entries], y=[str(e) for e in exits],
        z=duration_matrix, colorscale="Plasma", name="Duration",
    ), row=1, col=2)

    fig.update_xaxes(title_text="Entry Threshold (±σ)", row=1, col=1)
    fig.update_xaxes(title_text="Entry Threshold (±σ)", row=1, col=2)
    fig.update_yaxes(title_text="Exit Threshold (±σ)", row=1, col=1)

    fig.update_layout(
        title=f"Z-score Thresholds: {asset1} / {asset2} ({timeframe}, window={window})",
        template="plotly_dark", height=400,
        margin=dict(t=50, b=40, l=60, r=20),
    )
    return fig


# ─── Lookback Window charts ──────────────────────────────────────────────────


def _build_lookback_chart(results, asset1, asset2, timeframe) -> go.Figure:
    """Build lookback window comparison chart."""
    from plotly.subplots import make_subplots

    ws = [r.window for r in results]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["±2σ Crossings", "Autocorrelation", "Skewness", "Kurtosis"],
    )

    fig.add_trace(go.Scatter(x=ws, y=[r.crossings_2 for r in results],
                             mode="lines+markers", name="Crossings"), row=1, col=1)
    fig.add_trace(go.Scatter(x=ws, y=[r.autocorrelation for r in results],
                             mode="lines+markers", name="Autocorr"), row=1, col=2)
    fig.add_trace(go.Scatter(x=ws, y=[r.skewness for r in results],
                             mode="lines+markers", name="Skew"), row=2, col=1)
    fig.add_trace(go.Scatter(x=ws, y=[r.kurtosis for r in results],
                             mode="lines+markers", name="Kurt"), row=2, col=2)

    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=2)

    fig.update_xaxes(title_text="Window Size", row=2, col=1)
    fig.update_xaxes(title_text="Window Size", row=2, col=2)

    fig.update_layout(
        title=f"Lookback Window: {asset1} / {asset2} ({timeframe})",
        template="plotly_dark", height=500, showlegend=False,
        margin=dict(t=50, b=40, l=60, r=20),
    )
    return fig


def _lookback_table(results) -> dbc.Card:
    """Summary table for lookback window results."""
    rows = [
        html.Tr([
            html.Td(str(r.window)),
            html.Td(str(r.crossings_2)),
            html.Td(f"{r.autocorrelation:.3f}"),
            html.Td(f"{r.skewness:.3f}"),
            html.Td(f"{r.kurtosis:.3f}"),
            html.Td(f"{r.zscore_std:.3f}"),
        ])
        for r in results
    ]

    return dbc.Card(
        dbc.CardBody([
            html.H6("Window Comparison", className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Window"), html.Th("±2σ Cross."),
                    html.Th("Autocorr"), html.Th("Skew"), html.Th("Kurt"), html.Th("Z Std"),
                ])),
                html.Tbody(rows),
            ], bordered=True, hover=True, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


# ─── Transaction Cost charts ─────────────────────────────────────────────────


def _build_tx_cost_chart(results, asset1, asset2, timeframe) -> go.Figure:
    """Build transaction cost analysis chart."""
    from plotly.subplots import make_subplots

    fees = [r.fee_pct for r in results]
    profitable_pct = [r.net_profitable_pct for r in results]
    total_fee_pct = [r.round_trip_pct for r in results]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Profitable Trades vs Fee Level", "Fee Breakeven Analysis"],
    )

    # Bar chart: profitable trade percentage at each fee level
    colors = ["green" if p >= 70 else "orange" if p >= 40 else "red" for p in profitable_pct]
    fig.add_trace(go.Bar(
        x=[f"{f:.2f}%" for f in fees],
        y=profitable_pct,
        marker_color=colors,
        name="Profitable %",
        hovertemplate="Fee: %{x}<br>Profitable: %{y:.1f}%<extra></extra>",
    ), row=1, col=1)

    # Bitvavo fee markers
    fig.add_vline(x=5, line_dash="dash", line_color="yellow",
                  annotation_text="Bitvavo Maker (0.15%)", row=1, col=1)

    # Line chart: avg spread vs total fees
    avg_spread = results[0].avg_spread_pct if results else 0
    fig.add_trace(go.Scatter(
        x=[f"{f:.2f}%" for f in fees],
        y=total_fee_pct,
        mode="lines+markers",
        name="Total Fees (4 legs)",
        line=dict(color="red", width=2),
    ), row=1, col=2)
    fig.add_hline(
        y=avg_spread, line_dash="dash", line_color="green",
        annotation_text=f"Avg spread move ({avg_spread:.2f}%)",
        row=1, col=2,
    )

    fig.update_xaxes(title_text="One-way Fee", row=1, col=1)
    fig.update_xaxes(title_text="One-way Fee", row=1, col=2)
    fig.update_yaxes(title_text="Profitable Trades (%)", row=1, col=1)
    fig.update_yaxes(title_text="Cost / Spread (%)", row=1, col=2)

    fig.update_layout(
        title=f"Transaction Cost Sensitivity: {asset1} / {asset2} ({timeframe})",
        template="plotly_dark", height=400,
        margin=dict(t=50, b=40, l=60, r=20),
        showlegend=True,
    )
    return fig


def _tx_cost_table(results) -> dbc.Card:
    """Summary table for transaction cost results."""
    rows = [
        html.Tr([
            html.Td(f"{r.fee_pct:.2f}%"),
            html.Td(f"{r.round_trip_pct:.2f}%"),
            html.Td(str(r.total_trades)),
            html.Td(str(r.profitable_trades)),
            html.Td(f"{r.net_profitable_pct:.1f}%"),
            html.Td(f"{r.avg_spread_pct:.3f}%"),
        ])
        for r in results
    ]

    return dbc.Card(
        dbc.CardBody([
            html.H6("Fee Level Comparison", className="mb-2"),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Fee (1-way)"), html.Th("Total (4-leg)"),
                    html.Th("Trades"), html.Th("Profitable"),
                    html.Th("Win Rate"), html.Th("Avg Spread"),
                ])),
                html.Tbody(rows),
            ], bordered=True, hover=True, size="sm", className="mb-0"),
        ]),
        className="mt-3",
    )


def _module_descriptions() -> dict[str, str]:
    """One-line descriptions for each module."""
    return {
        "rolling-coint": "Does this pair stay cointegrated over time?",
        "oos-validation": "Does in-sample cointegration predict out-of-sample behavior?",
        "timeframe": "Which candle interval produces the most robust cointegration?",
        "spread-construction": "Price-level, log-price, or ratio — which spread is most stationary?",
        "zscore-threshold": "What entry/exit z-score levels maximize signal quality?",
        "lookback-window": "What rolling window produces the best z-score signals?",
        "tx-cost": "Is the spread wide enough to profit after Bitvavo fees?",
        "coint-method": "Engle-Granger vs Johansen — do they agree?",
    }
