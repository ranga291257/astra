"""
UI module for ASTRA.

Provides Streamlit UI components and rendering functions.
"""

from ui.components import (
    render_key_metrics,
    render_risk_dashboard,
    render_drawdowns_table,
    render_recovery_table,
    render_data_summary,
    render_strategy_view,
    render_monte_carlo_view,
)

__all__ = [
    "render_key_metrics",
    "render_risk_dashboard",
    "render_drawdowns_table",
    "render_recovery_table",
    "render_data_summary",
    "render_strategy_view",
    "render_monte_carlo_view",
]

