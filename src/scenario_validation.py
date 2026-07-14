"""Held-out validation for the descriptive log-odds sales-share trend."""

from __future__ import annotations

import numpy as np
import pandas as pd


def backtest_logit_trend(
    annual: pd.DataFrame,
    *,
    train_end_year: int = 2022,
    test_start_year: int = 2023,
) -> pd.DataFrame:
    """Fit through ``train_end_year`` and return held-out annual errors."""

    required = {"year", "total_auto_sales_m", "nev_sales_m"}
    missing = sorted(required.difference(annual.columns))
    if missing:
        raise ValueError(f"annual data missing columns: {', '.join(missing)}")
    frame = annual.copy().sort_values("year")
    frame["observed_nev_share_pct"] = (
        frame["nev_sales_m"] / frame["total_auto_sales_m"] * 100
    )
    train = frame.loc[frame["year"] <= train_end_year].copy()
    test = frame.loc[frame["year"] >= test_start_year].copy()
    if len(train) < 3 or test.empty:
        raise ValueError("backtest requires at least three training rows and one test row")
    probability = train["observed_nev_share_pct"].to_numpy() / 100
    if ((probability <= 0) | (probability >= 1)).any():
        raise ValueError("training shares must lie strictly between zero and one")

    origin_year = int(train["year"].min())
    x_train = train["year"].to_numpy() - origin_year
    log_odds = np.log(probability / (1 - probability))
    annual_logit_gain, intercept = np.polyfit(x_train, log_odds, 1)
    x_test = test["year"].to_numpy() - origin_year
    predicted_probability = 1 / (
        1 + np.exp(-(intercept + annual_logit_gain * x_test))
    )
    result = test[["year", "observed_nev_share_pct"]].copy()
    result["predicted_nev_share_pct"] = predicted_probability * 100
    result["absolute_error_pp"] = (
        result["predicted_nev_share_pct"] - result["observed_nev_share_pct"]
    ).abs()
    result["train_end_year"] = train_end_year
    result["annual_logit_gain_fitted"] = annual_logit_gain
    return result.reset_index(drop=True)
