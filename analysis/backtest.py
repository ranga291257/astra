"""
Module: analysis/backtest.py

Purpose:
    Implement simple backtesting utilities (e.g., moving-average crossover).

Responsibilities:
    - Pure strategy logic
    - No Streamlit, no plotting
"""

from typing import Dict, Optional, Tuple

import pandas as pd


def run_ma_crossover_strategy(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 100,
) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, float]], Optional[str]]:
    """
    Run a simple moving-average crossover strategy.

    Contract:
    - Input:
        - df: DataFrame with Date, Close, Daily_Return.
        - short_window: Short MA length.
        - long_window: Long MA length.
    - Output:
        - (equity_df, stats, error_message)
        - equity_df: DataFrame with Strategy_Equity and BuyHold_Equity if success, else None.
        - stats: Dict with basic metrics (CAGR, etc.). (Placeholder for now.)
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, None, message) if required columns missing.
    - Side effects:
        - None.
    """
    if "Date" not in df.columns or "Close" not in df.columns or "Daily_Return" not in df.columns:
        return None, None, "DataFrame must contain Date, Close, and Daily_Return columns."

    prices = df.set_index("Date")["Close"]
    short_ma = prices.rolling(short_window).mean()
    long_ma = prices.rolling(long_window).mean()

    signal = (short_ma > long_ma).astype(int)
    strategy_returns = signal.shift(1).fillna(0) * df.set_index("Date")["Daily_Return"]
    strategy_equity = (1 + strategy_returns).cumprod()
    buy_hold_equity = prices / prices.iloc[0]

    equity_df = pd.DataFrame(
        {
            "Strategy_Equity": strategy_equity,
            "BuyHold_Equity": buy_hold_equity,
        }
    ).dropna()

    stats: Dict[str, float] = {}  # Placeholder for Phase B

    return equity_df, stats, None

