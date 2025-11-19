"""
Module: analysis/monte_carlo.py

Purpose:
    Monte Carlo simulation for forward price paths and basic risk estimates.

Responsibilities:
    - Pure numeric simulation
    - No Streamlit, no plotting
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd


def run_monte_carlo_simulation(
    df: pd.DataFrame,
    horizon_days: int = 126,
    n_sims: int = 500,
) -> Tuple[Optional[pd.DataFrame], Optional[float], Optional[str]]:
    """
    Run a basic Monte Carlo price path simulation using historical returns.

    Contract:
    - Input:
        - df: DataFrame with Daily_Return and Close.
        - horizon_days: Number of future trading days to simulate.
        - n_sims: Number of simulation paths.
    - Output:
        - (sim_paths_df, var_5_loss_pct, error_message)
        - sim_paths_df: DataFrame of shape [horizon_days, n_sims] if success, else None.
        - var_5_loss_pct: 5% worst-case loss in % relative to last price if success, else None.
        - error_message: None on success, error description on failure.
    - Errors:
        - Returns (None, None, message) if required columns missing or invalid params.
    - Side effects:
        - None.
    """
    if "Daily_Return" not in df.columns or "Close" not in df.columns:
        return None, None, "DataFrame must contain Daily_Return and Close columns."

    if horizon_days <= 0 or n_sims <= 0:
        return None, None, "horizon_days and n_sims must be positive integers."

    mu = df["Daily_Return"].mean()
    sigma = df["Daily_Return"].std()
    last_price = float(df["Close"].iloc[-1])

    shocks = np.random.normal(mu, sigma, size=(horizon_days, n_sims))
    log_returns = shocks  # Using shocks as daily log-returns approximation
    price_paths = last_price * np.exp(np.cumsum(log_returns, axis=0))

    sim_paths_df = pd.DataFrame(price_paths)
    final_prices = sim_paths_df.iloc[-1]
    var_5_price = np.percentile(final_prices, 5)
    var_5_loss_pct = (last_price - var_5_price) / last_price * 100.0

    return sim_paths_df, float(var_5_loss_pct), None

