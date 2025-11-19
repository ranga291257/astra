"""
Module: ui/components.py

Purpose:
    Streamlit UI helper functions for ASTRA.

Responsibilities:
    - Rendering metrics, tables, and charts
    - No business logic / calculations
"""

from typing import Callable, Dict

import pandas as pd
import streamlit as st


def render_key_metrics(risk_metrics: Dict[str, float]) -> None:
    """
    Render top-level risk metrics in Streamlit.

    Contract:
    - Input:
        - risk_metrics: Dictionary from risk.metrics.calculate_risk_metrics.
    - Output:
        - None (renders UI).
    - Errors:
        - Handles missing keys gracefully.
    - Side effects:
        - UI rendering via Streamlit.
    """
    cols = st.columns(5)
    cols[0].metric("CAGR", f"{risk_metrics.get('cagr', 0.0) * 100:.2f}%")
    cols[1].metric("Volatility", f"{risk_metrics.get('volatility', 0.0) * 100:.2f}%")
    cols[2].metric("Sharpe", f"{risk_metrics.get('sharpe', 0.0):.3f}")
    cols[3].metric("Sortino", f"{risk_metrics.get('sortino', 0.0):.3f}")
    cols[4].metric("Max Drawdown", f"{abs(risk_metrics.get('max_drawdown', 0.0)) * 100:.2f}%")


def render_risk_dashboard(df: pd.DataFrame, ticker: str, recovery_df: pd.DataFrame) -> None:
    """
    Render the main risk dashboard view.

    Contract:
    - Input:
        - df: DataFrame with price, vol, drawdowns, indicators.
        - ticker: Ticker symbol.
        - recovery_df: DataFrame from calculate_recovery.
    - Output:
        - None (renders UI).
    - Errors:
        - Any plotting errors are surfaced via Streamlit.
    - Side effects:
        - UI rendering via Streamlit.
    """
    st.subheader(f"Risk Dashboard - {ticker}")
    st.line_chart(df.set_index("Date")["Close"], height=300)
    if "Volatility_252d" in df.columns:
        st.line_chart(df.set_index("Date")["Volatility_252d"], height=200)


def render_drawdowns_table(drawdowns_df: pd.DataFrame) -> None:
    """Render major drawdown events table."""
    if drawdowns_df.empty:
        st.info("No major drawdowns found for the configured threshold.")
        return
    st.dataframe(drawdowns_df)


def render_recovery_table(recovery_df: pd.DataFrame) -> None:
    """Render drawdown recovery analysis table."""
    if recovery_df.empty:
        st.info("No recovery events computed.")
        return
    st.dataframe(recovery_df)


def render_data_summary(df: pd.DataFrame, ticker: str) -> None:
    """Render data range and basic info."""
    if df.empty:
        st.warning("No data to summarize.")
        return

    st.write(f"**Ticker:** {ticker}")
    st.write(f"**Date Range:** {df['Date'].min().date()} → {df['Date'].max().date()}")
    st.write(f"**Rows:** {len(df):,}")


def render_strategy_view(
    df: pd.DataFrame,
    ticker: str,
    run_strategy: Callable[..., tuple[pd.DataFrame, Dict[str, float]]],
) -> None:
    """Render simple MA strategy UI wrapper."""
    st.subheader(f"Strategy Backtest - {ticker} (Phase B)")
    st.info("Placeholder view. Implement controls and charts in Phase B.")


def render_monte_carlo_view(
    df: pd.DataFrame,
    ticker: str,
    run_simulation: Callable[..., tuple[pd.DataFrame, float]],
) -> None:
    """Render Monte Carlo simulation UI wrapper."""
    st.subheader(f"Monte Carlo Simulation - {ticker} (Phase B)")
    st.info("Placeholder view. Implement sliders and charts in Phase B.")

