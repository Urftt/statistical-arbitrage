"""
Main app layout — navigation bar + page container.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_layout():
    """Create the main app layout with navbar and page container."""
    return html.Div([
        # URL routing
        dcc.Location(id="url", refresh=False),

        # Navigation bar
        _navbar(),

        # Page content
        html.Div(id="page-content", className="pb-4"),

        # Global stores for shared state
        dcc.Store(id="cached-pairs-store", storage_type="session"),
    ])


def _navbar():
    """Create the top navigation bar."""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.Span("📊 ", style={"fontSize": "1.3rem"}),
                "StatArb Research",
            ], href="/", className="fw-bold"),

            dbc.Nav([
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fa-solid fa-magnifying-glass me-1"),
                    "Pair Scanner",
                ], href="/scanner")),
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fa-solid fa-microscope me-1"),
                    "Deep Dive",
                ], href="/deep-dive")),
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fa-solid fa-flask me-1"),
                    "Research Hub",
                ], href="/research")),
            ], navbar=True),
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-0",
    )
