"""Transparent bounded scenarios for NEV sales share.

These functions are scenario tools, not causal or probabilistic forecasts.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

import pandas as pd


def logit(probability: float) -> float:
    """Transform a probability in (0, 1) to log-odds."""

    probability = float(probability)
    if not 0 < probability < 1:
        raise ValueError("probability must lie strictly between zero and one")
    return math.log(probability / (1 - probability))


def inverse_logit(log_odds: float) -> float:
    """Transform log-odds to a probability in (0, 1)."""

    return 1 / (1 + math.exp(-float(log_odds)))


def project_logit_share(
    anchor_share: float, years_ahead: int, annual_logit_gain: float
) -> float:
    """Project a bounded share from an anchor using a log-odds increment."""

    if years_ahead < 0:
        raise ValueError("years_ahead must be non-negative")
    anchor_probability = float(anchor_share) / 100
    projected = inverse_logit(
        logit(anchor_probability) + years_ahead * float(annual_logit_gain)
    )
    return projected * 100


def scenario_table(
    anchor_year: int,
    anchor_share: float,
    end_year: int,
    annual_logit_gains: Mapping[str, float],
) -> pd.DataFrame:
    """Build a tidy scenario table anchored to an observed share."""

    if end_year < anchor_year:
        raise ValueError("end_year must be at or after anchor_year")

    rows: list[dict[str, float | int | str]] = []
    for name, gain in annual_logit_gains.items():
        for year in range(anchor_year, end_year + 1):
            rows.append(
                {
                    "scenario": name,
                    "year": year,
                    "nev_share_pct": project_logit_share(
                        anchor_share, year - anchor_year, gain
                    ),
                    "annual_logit_gain": gain,
                }
            )
    return pd.DataFrame(rows)

