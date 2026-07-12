"""Small, explicit formulas used throughout the project."""

from __future__ import annotations


def _positive(value: float, name: str) -> float:
    value = float(value)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def share(part: float, whole: float, *, as_percent: bool = True) -> float:
    """Return part / whole, optionally expressed as a percentage."""

    whole = _positive(whole, "whole")
    result = float(part) / whole
    return result * 100 if as_percent else result


def percent_change(current: float, previous: float) -> float:
    """Return the percentage change from previous to current."""

    previous = _positive(previous, "previous")
    return (float(current) / previous - 1) * 100


def cagr(start: float, end: float, periods: float) -> float:
    """Return compound annual growth in percent."""

    start = _positive(start, "start")
    end = _positive(end, "end")
    periods = _positive(periods, "periods")
    return ((end / start) ** (1 / periods) - 1) * 100


def percentage_point_gap(high: float, low: float) -> float:
    """Return a difference between two percentages in percentage points."""

    return float(high) - float(low)


def ratio(numerator: float, denominator: float) -> float:
    """Return a simple numerator-to-denominator ratio."""

    denominator = _positive(denominator, "denominator")
    return float(numerator) / denominator


def growth_contribution(component_change: float, total_change: float) -> float:
    """Return a component's contribution to net growth in percent.

    The result can exceed 100% when another component shrinks.
    """

    if float(total_change) == 0:
        raise ValueError("total_change must not be zero")
    return float(component_change) / float(total_change) * 100

