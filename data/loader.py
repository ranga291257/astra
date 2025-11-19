"""
Module: data/loader.py

Purpose:
    Downloads and cleans stock data from external sources (e.g., Yahoo Finance).

Responsibilities:
    - Download historical price data
    - Basic cleaning and normalization
    - Return (data, error_message) tuples

No dependencies on other ASTRA modules.
"""

from typing import Optional, Tuple

import pandas as pd
import yfinance as yf


def download_data(ticker: str, start_date: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Download historical data for a given ticker.

    Contract:
    - Input:
        - ticker: Symbol to download.
        - start_date: Optional start date (YYYY-MM-DD).
    - Output:
        - (df, error_message)
        - df: DataFrame with raw OHLCV data if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) on download failure or empty data.
    - Side effects:
        - Network call to Yahoo Finance via yfinance.
    """
    try:
        if start_date:
            data = yf.download(ticker, start=start_date, interval="1d", progress=False, auto_adjust=True)
        else:
            data = yf.download(ticker, period="max", interval="1d", progress=False, auto_adjust=True)
    except Exception as e:
        return None, f"Failed to download data for {ticker}: {e}"

    if data is None or data.empty:
        return None, f"No data returned for ticker: {ticker}"

    return data, None


def clean_data(raw_data: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Clean and preprocess raw price data.

    Contract:
    - Input:
        - raw_data: DataFrame from download_data.
    - Output:
        - (df, error_message)
        - df: Cleaned DataFrame with Date, Open, High, Low, Close, Volume.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, message) if required fields are missing.
    - Side effects:
        - None.
    """
    if raw_data is None or raw_data.empty:
        return None, "Input raw_data is empty."

    df = raw_data.copy()

    if isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index().rename(columns={"index": "Date"})

    if "Date" not in df.columns:
        return None, "Missing Date column after reset_index."

    df["Date"] = pd.to_datetime(df["Date"])

    # Prefer Adj Close if available
    if "Adj Close" in df.columns:
        df["Close"] = df["Adj Close"]

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    df = df.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)

    return df, None

