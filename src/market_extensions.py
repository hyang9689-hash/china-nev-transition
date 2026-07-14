"""Derived metrics for NEV powertrain composition and automobile exports."""

from __future__ import annotations

import pandas as pd


class MarketExtensionError(ValueError):
    """Raised when source tables cannot support a coherent derived metric."""


def _require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise MarketExtensionError(f"{label} is missing columns: {', '.join(missing)}")


def derive_powertrain_mix(
    powertrain: pd.DataFrame,
    annual: pd.DataFrame,
    *,
    tolerance_m: float = 0.002,
) -> pd.DataFrame:
    """Reconcile rounded component volumes and calculate their NEV shares."""

    _require_columns(
        powertrain,
        {
            "year",
            "nev_sales_m",
            "bev_sales_m",
            "phev_sales_m",
            "fcev_sales_m",
            "source_id",
        },
        "powertrain table",
    )
    _require_columns(annual, {"year", "nev_sales_m"}, "annual market table")

    result = powertrain.copy().sort_values("year").reset_index(drop=True)
    result["component_total_m"] = result[
        ["bev_sales_m", "phev_sales_m", "fcev_sales_m"]
    ].sum(axis=1)
    result["component_reconciliation_gap_m"] = (
        result["component_total_m"] - result["nev_sales_m"]
    )

    bad_components = result.loc[
        result["component_reconciliation_gap_m"].abs() > tolerance_m,
        ["year", "component_reconciliation_gap_m"],
    ]
    if not bad_components.empty:
        details = ", ".join(
            f"{int(row.year)} ({row.component_reconciliation_gap_m:+.4f}m)"
            for row in bad_components.itertuples()
        )
        raise MarketExtensionError(
            f"powertrain components do not reconcile within {tolerance_m:.4f}m: {details}"
        )

    annual_reference = annual[["year", "nev_sales_m"]].rename(
        columns={"nev_sales_m": "annual_nev_sales_m"}
    )
    result = result.merge(annual_reference, on="year", how="left", validate="one_to_one")
    if result["annual_nev_sales_m"].isna().any():
        missing_years = result.loc[result["annual_nev_sales_m"].isna(), "year"].tolist()
        raise MarketExtensionError(f"annual NEV reference missing for years: {missing_years}")

    result["annual_reconciliation_gap_m"] = (
        result["nev_sales_m"] - result["annual_nev_sales_m"]
    )
    bad_annual = result.loc[
        result["annual_reconciliation_gap_m"].abs() > tolerance_m,
        ["year", "annual_reconciliation_gap_m"],
    ]
    if not bad_annual.empty:
        details = ", ".join(
            f"{int(row.year)} ({row.annual_reconciliation_gap_m:+.4f}m)"
            for row in bad_annual.itertuples()
        )
        raise MarketExtensionError(
            f"powertrain NEV totals disagree with the annual table: {details}"
        )

    for component in ("bev", "phev", "fcev"):
        result[f"{component}_share_of_nev_pct"] = (
            result[f"{component}_sales_m"] / result["nev_sales_m"] * 100
        )
    return result


def derive_export_metrics(
    exports: pd.DataFrame,
    annual: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate export intensity and explicitly labelled non-export residuals."""

    _require_columns(
        exports,
        {"year", "total_auto_exports_m", "nev_exports_m", "source_id"},
        "exports table",
    )
    _require_columns(
        annual,
        {"year", "total_auto_sales_m", "nev_sales_m"},
        "annual market table",
    )

    annual_reference = annual[["year", "total_auto_sales_m", "nev_sales_m"]]
    result = (
        exports.copy()
        .sort_values("year")
        .merge(annual_reference, on="year", how="left", validate="one_to_one")
        .reset_index(drop=True)
    )
    if result[["total_auto_sales_m", "nev_sales_m"]].isna().any(axis=None):
        missing_years = result.loc[result["total_auto_sales_m"].isna(), "year"].tolist()
        raise MarketExtensionError(f"annual sales reference missing for years: {missing_years}")

    checks = {
        "NEV exports exceed total automobile exports": (
            result["nev_exports_m"] > result["total_auto_exports_m"]
        ),
        "total automobile exports exceed industry deliveries": (
            result["total_auto_exports_m"] > result["total_auto_sales_m"]
        ),
        "NEV exports exceed NEV industry deliveries": (
            result["nev_exports_m"] > result["nev_sales_m"]
        ),
    }
    for message, mask in checks.items():
        if mask.any():
            years = result.loc[mask, "year"].astype(int).tolist()
            raise MarketExtensionError(f"{message} in years: {years}")

    result["total_exports_share_of_sales_pct"] = (
        result["total_auto_exports_m"] / result["total_auto_sales_m"] * 100
    )
    result["nev_share_of_exports_pct"] = (
        result["nev_exports_m"] / result["total_auto_exports_m"] * 100
    )
    result["nev_exports_share_of_nev_sales_pct"] = (
        result["nev_exports_m"] / result["nev_sales_m"] * 100
    )
    result["non_export_total_sales_proxy_m"] = (
        result["total_auto_sales_m"] - result["total_auto_exports_m"]
    )
    result["non_export_nev_sales_proxy_m"] = (
        result["nev_sales_m"] - result["nev_exports_m"]
    )
    result["non_export_nev_share_proxy_pct"] = (
        result["non_export_nev_sales_proxy_m"]
        / result["non_export_total_sales_proxy_m"]
        * 100
    )
    return result
