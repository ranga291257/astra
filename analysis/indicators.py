"""
Module: analysis/indicators.py

Purpose:
    Compute technical indicators such as moving averages and momentum.

Responsibilities:
    - Factor/indicator computation ONLY
    - No plotting, no UI, no data download
"""

from typing import List, Optional, Tuple

import pandas as pd


def calculate_factors(df: pd.DataFrame, ma_windows: Optional[List[int]] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Add basic technical indicators to the DataFrame.

    Contract:
    - Input:
        - df: DataFrame with Date, Close, Daily_Return.
        - ma_windows: Optional list of MA window lengths. Defaults to [20, 100].
    - Output:
        - (result_df, error_message)
        - result_df: DataFrame with new columns (MA_<window>, Mom_20d) if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if Close missing.
    - Side effects:
        - None (returns modified copy).
    """
    if "Close" not in df.columns:
        return None, "DataFrame must contain 'Close' column."

    result = df.copy()
    if ma_windows is None:
        ma_windows = [20, 100]

    for w in ma_windows:
        result[f"MA_{w}"] = result["Close"].rolling(window=w).mean()

    result["Mom_20d"] = result["Close"].pct_change(20) * 100.0
    return result, None

