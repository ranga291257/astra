"""
Analysis module for ASTRA.

Provides technical indicators, backtesting, and simulation functionality.
"""

from analysis.indicators import calculate_factors
from analysis.backtest import run_ma_crossover_strategy
from analysis.monte_carlo import run_monte_carlo_simulation

__all__ = ["calculate_factors", "run_ma_crossover_strategy", "run_monte_carlo_simulation"]

