"""
Risk module for ASTRA.

Provides risk and return calculation functionality.
"""

from risk.metrics import (
    calculate_returns,
    calculate_volatility,
    calculate_drawdown,
    find_major_drawdowns,
    calculate_recovery,
    calculate_risk_metrics,
)

__all__ = [
    "calculate_returns",
    "calculate_volatility",
    "calculate_drawdown",
    "find_major_drawdowns",
    "calculate_recovery",
    "calculate_risk_metrics",
]

