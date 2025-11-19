"""
Tests for data/loader.py
"""

from typing import Tuple

import pandas as pd

from data.loader import download_data, clean_data


def test_download_data_success_smoke() -> None:
    """
    Smoke test: download_data should return either data or a clear error.
    """
    df, err = download_data(ticker="^GSPC")
    assert (df is not None) ^ (err is not None)


def test_clean_data_roundtrip() -> None:
    """
    Smoke test: cleaning valid downloaded data should not raise and should return DataFrame.
    """
    df_raw, err = download_data(ticker="^GSPC")
    if err:
        return  # Skip if network/download fails in test env

    df_clean, err_clean = clean_data(raw_data=df_raw)
    assert err_clean is None
    assert isinstance(df_clean, pd.DataFrame)
    assert not df_clean.empty

