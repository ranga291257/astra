"""
Module: ASTRA.py

Purpose:
    Main entry point for the ASTRA application.

    This module is responsible ONLY for:
    - Wiring Streamlit UI to the underlying data/risk/analysis modules
    - Handling user input
    - Coordinating which views/tabs are shown

    It MUST NOT contain business logic such as:
    - Data download/cleaning
    - Risk metrics calculations
    - Indicator computation
    - Backtests or simulations
"""

from typing import Optional, Tuple

import streamlit as st
import pandas as pd

from data.loader import download_data, clean_data
from risk.metrics import (
    calculate_returns,
    calculate_volatility,
    calculate_drawdown,
    find_major_drawdowns,
    calculate_recovery,
    calculate_risk_metrics,
)
from analysis.indicators import calculate_factors
from analysis.backtest import run_ma_crossover_strategy
from analysis.monte_carlo import run_monte_carlo_simulation
from ui.components import (
    render_key_metrics,
    render_risk_dashboard,
    render_drawdowns_table,
    render_recovery_table,
    render_data_summary,
    render_strategy_view,
    render_monte_carlo_view,
)


def _load_and_prepare_data(ticker: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load and preprocess data for a given ticker.

    Contract:
    - Input:
        - ticker: Stock or index ticker symbol.
    - Output:
        - (df, error_message)
        - df: Cleaned DataFrame with all required columns if success, else None.
        - error_message: None on success, or error description on failure.
    - Errors:
        - Returns (None, message) if download or cleaning fails.
    - Side effects:
        - None.
    """
    raw_data, err = download_data(ticker=ticker)
    if err:
        return None, err

    cleaned, err = clean_data(raw_data=raw_data)
    if err:
        return None, err

    return cleaned, None


def main() -> None:
    """
    Main Streamlit application entry point.

    Contract:
    - Input: None (uses Streamlit widgets for input).
    - Output: None (renders UI via Streamlit).
    - Errors: UI shows error messages for data/analysis failures.
    - Side effects: Renders UI in Streamlit.
    """
    st.set_page_config(
        page_title="ASTRA - Advanced Stock Risk Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("ASTRA - Advanced Stock Risk Analysis")

    with st.sidebar:
        ticker: str = st.text_input(
            "Enter Stock Ticker",
            value="^GSPC",
            help="Examples: ^GSPC, AAPL, MSFT, TSLA",
        )
        run_button: bool = st.button("🚀 Run Analysis", use_container_width=True)

    if not run_button:
        st.info("Enter a ticker and click **Run Analysis** to start.")
        return

    df, err = _load_and_prepare_data(ticker=ticker)
    if err or df is None:
        st.error(f"❌ Error: {err or 'Unknown error loading data.'}")
        return

    # Core risk pipeline
    df, err = calculate_returns(df)
    if err or df is None:
        st.error(f"❌ Error calculating returns: {err}")
        return

    df, err = calculate_volatility(df)
    if err or df is None:
        st.error(f"❌ Error calculating volatility: {err}")
        return

    df, err = calculate_drawdown(df)
    if err or df is None:
        st.error(f"❌ Error calculating drawdown: {err}")
        return

    drawdowns_df, err = find_major_drawdowns(df=df, threshold=20.0)
    if err:
        st.error(f"❌ Error finding drawdowns: {err}")
        return
    if drawdowns_df is None:
        drawdowns_df = pd.DataFrame()

    recovery_df = calculate_recovery(df=df, drawdowns_df=drawdowns_df)

    risk_metrics, err = calculate_risk_metrics(df=df, ticker=ticker)
    if err or risk_metrics is None:
        st.error(f"❌ Error calculating risk metrics: {err}")
        return

    # Phase A indicators
    df, err = calculate_factors(df=df)
    if err or df is None:
        st.error(f"❌ Error calculating indicators: {err}")
        return

    tabs = st.tabs(
        [
            "📊 Risk Dashboard",
            "📈 Metrics",
            "📉 Drawdowns",
            "⏱️ Recovery",
            "📂 Data",
            "🧪 Strategy (Phase B)",
            "🎲 Monte Carlo (Phase B)",
        ]
    )

    with tabs[0]:
        render_risk_dashboard(df=df, ticker=ticker, recovery_df=recovery_df)

    with tabs[1]:
        render_key_metrics(risk_metrics=risk_metrics)

    with tabs[2]:
        render_drawdowns_table(drawdowns_df=drawdowns_df)

    with tabs[3]:
        render_recovery_table(recovery_df=recovery_df)

    with tabs[4]:
        render_data_summary(df=df, ticker=ticker)

    with tabs[5]:
        render_strategy_view(df=df, ticker=ticker, run_strategy=run_ma_crossover_strategy)

    with tabs[6]:
        render_monte_carlo_view(df=df, ticker=ticker, run_simulation=run_monte_carlo_simulation)


if __name__ == "__main__":
    main()
