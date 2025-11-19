"""
Module: risk/metrics.py

Purpose:
    Implements core risk and return calculations:
    - Daily returns
    - Rolling volatility
    - Drawdown series
    - Major drawdown detection
    - Recovery calculations
    - Aggregate risk metrics (CAGR, Sharpe, etc.)
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import ffn
import quantstats as qs


RISK_FREE_RATE: float = 0.025
TRADING_DAYS_PER_YEAR: int = 252


def calculate_returns(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Calculate daily returns.

    Contract:
    - Input:
        - df: DataFrame with at least Date and Close columns.
    - Output:
        - (result_df, error_message)
        - result_df: DataFrame with new Daily_Return column if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if Close column is missing.
    - Side effects:
        - None (returns modified copy).
    """
    if "Close" not in df.columns:
        return None, "DataFrame must contain 'Close' column."

    result = df.copy()
    result["Daily_Return"] = result["Close"].pct_change()
    return result, None


def calculate_volatility(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Calculate annualized rolling volatility for different windows.

    Contract:
    - Input:
        - df: DataFrame with Daily_Return column.
    - Output:
        - (result_df, error_message)
        - result_df: DataFrame with Volatility_30d, Volatility_60d, Volatility_252d (%) if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if Daily_Return is missing.
    - Side effects:
        - None (returns modified copy).
    """
    if "Daily_Return" not in df.columns:
        return None, "DataFrame must contain 'Daily_Return' column."

    result = df.copy()
    for window in (30, 60, TRADING_DAYS_PER_YEAR):
        rolling_std = result["Daily_Return"].rolling(window=window).std()
        annualized_vol = rolling_std * np.sqrt(TRADING_DAYS_PER_YEAR) * 100.0
        result[f"Volatility_{window}d"] = annualized_vol

    return result, None


def calculate_drawdown(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Calculate drawdown series using ffn.

    Contract:
    - Input:
        - df: DataFrame with Date and Close.
    - Output:
        - (result_df, error_message)
        - result_df: DataFrame with Drawdown (%), Running_Max, Max_Drawdown (%) if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if required columns are missing.
    - Side effects:
        - None.
    """
    if "Date" not in df.columns or "Close" not in df.columns:
        return None, "DataFrame must contain Date and Close columns."

    result = df.copy()
    prices = pd.Series(result["Close"].values, index=result["Date"])
    dd_series = ffn.to_drawdown_series(prices)

    result["Drawdown"] = dd_series.values * 100.0
    result["Running_Max"] = result["Close"].expanding().max()
    result["Max_Drawdown"] = result["Drawdown"].expanding().min()
    return result, None


def _calculate_drawdown_metrics(
    df: pd.DataFrame, drawdown_start_idx: int, end_idx: int, threshold: float
) -> Optional[Dict]:
    """
    Calculate metrics for a single drawdown period.

    Contract:
    - Input:
        - df: DataFrame with Date, Close columns.
        - drawdown_start_idx: Index where drawdown started.
        - end_idx: Index where drawdown ended (new peak reached).
        - threshold: Minimum drawdown threshold (%).
    - Output:
        - Dictionary with drawdown metrics if threshold met, else None.
    - Errors:
        - Returns None if drawdown doesn't meet threshold.
    - Side effects:
        - None.
    """
    window = df.loc[drawdown_start_idx:end_idx]
    trough_idx = window["Close"].idxmin()
    trough_price = df.loc[trough_idx, "Close"]
    dd_pct = (trough_price - df.loc[drawdown_start_idx, "Close"]) / df.loc[drawdown_start_idx, "Close"] * 100.0

    if abs(dd_pct) < threshold:
        return None

    return {
        "Peak_Date": df.loc[drawdown_start_idx, "Date"],
        "Trough_Date": df.loc[trough_idx, "Date"],
        "Peak_Price": df.loc[drawdown_start_idx, "Close"],
        "Trough_Price": trough_price,
        "Drawdown_Pct": dd_pct,
        "Duration_Days": int((df.loc[trough_idx, "Date"] - df.loc[drawdown_start_idx, "Date"]).days),
    }


def find_major_drawdowns(df: pd.DataFrame, threshold: float = 20.0) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Find major drawdown periods where loss exceeds threshold.

    Contract:
    - Input:
        - df: DataFrame with Date, Close.
        - threshold: Drawdown threshold (%) as positive number.
    - Output:
        - (drawdowns_df, error_message)
        - drawdowns_df: DataFrame with Peak_Date, Trough_Date, Peak_Price, Trough_Price,
          Drawdown_Pct (negative), Duration_Days if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if inputs invalid.
    - Side effects:
        - None.
    """
    if "Date" not in df.columns or "Close" not in df.columns:
        return None, "DataFrame must contain Date and Close columns."

    if threshold <= 0:
        return None, "threshold must be positive."

    if df.empty:
        return pd.DataFrame(), None

    records = []
    current_peak_idx = 0
    current_peak_price = df.loc[0, "Close"]
    in_drawdown = False
    drawdown_start_idx: Optional[int] = None

    for i in range(1, len(df)):
        price = df.loc[i, "Close"]

        if price > current_peak_price:
            if in_drawdown and drawdown_start_idx is not None:
                metrics = _calculate_drawdown_metrics(df, drawdown_start_idx, i, threshold)
                if metrics:
                    records.append(metrics)

            in_drawdown = False
            current_peak_idx = i
            current_peak_price = price

        elif not in_drawdown and price < current_peak_price * 0.95:
            in_drawdown = True
            drawdown_start_idx = current_peak_idx

    return pd.DataFrame(records), None


def calculate_recovery(df: pd.DataFrame, drawdowns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute recovery time (days/months) for each major drawdown.

    Contract:
    - Input:
        - df: Price DataFrame with Date, Close.
        - drawdowns_df: DataFrame from find_major_drawdowns.
    - Output:
        - DataFrame with Recovery_Days, Recovery_Months, Trough_Date, Recovery_Date, etc.
    - Errors:
        - Raises ValueError if required columns missing.
    - Side effects:
        - None.
    """
    if drawdowns_df.empty:
        return drawdowns_df

    records = []
    for _, row in drawdowns_df.iterrows():
        trough_date = row["Trough_Date"]
        peak_price = row["Peak_Price"]

        future = df[df["Date"] > trough_date]
        recovery = future[future["Close"] >= peak_price]

        if recovery.empty:
            continue

        recovery_date = recovery.iloc[0]["Date"]
        recovery_days = int((recovery_date - trough_date).days)
        recovery_months = round(recovery_days / 30.44, 1)

        records.append(
            {
                "Drawdown_Pct": row["Drawdown_Pct"],
                "Drawdown_Duration_Days": row["Duration_Days"],
                "Recovery_Days": recovery_days,
                "Recovery_Months": recovery_months,
                "Trough_Date": trough_date,
                "Recovery_Date": recovery_date,
            }
        )

    return pd.DataFrame(records)


def calculate_risk_metrics(df: pd.DataFrame, ticker: str) -> Tuple[Optional[Dict[str, float]], Optional[str]]:
    """
    Calculate aggregate risk metrics for a price series.

    Contract:
    - Input:
        - df: DataFrame with Date, Close, Daily_Return.
        - ticker: Ticker symbol (for reference/logging).
    - Output:
        - (metrics_dict, error_message)
        - metrics_dict: Dict of metrics (CAGR, volatility, Sharpe, Sortino, max_drawdown, years, etc.) if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if required columns are missing.
    - Side effects:
        - None.
    """
    if "Date" not in df.columns or "Close" not in df.columns or "Daily_Return" not in df.columns:
        return None, "DataFrame must contain Date, Close, and Daily_Return columns."

    prices = pd.Series(df["Close"].values, index=df["Date"])
    returns = pd.Series(df["Daily_Return"].values, index=df["Date"])

    stats = ffn.calc_stats(prices)
    total_return = stats.total_return

    cagr = qs.stats.cagr(returns)
    vol = qs.stats.volatility(returns, periods=TRADING_DAYS_PER_YEAR)
    sharpe = qs.stats.sharpe(returns, rf=RISK_FREE_RATE, periods=TRADING_DAYS_PER_YEAR)
    sortino = qs.stats.sortino(returns, rf=RISK_FREE_RATE, periods=TRADING_DAYS_PER_YEAR)
    max_dd = qs.stats.max_drawdown(returns)

    years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
    excess_return = cagr - RISK_FREE_RATE

    metrics = {
        "total_return": float(total_return),
        "cagr": float(cagr),
        "volatility": float(vol),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_drawdown": float(max_dd),
        "years": float(years),
        "excess_return": float(excess_return),
        "risk_free_rate": float(RISK_FREE_RATE),
    }
    return metrics, None

