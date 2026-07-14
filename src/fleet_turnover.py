"""Transparent stock-flow scenarios for China's registered automobile fleet."""

from __future__ import annotations

import pandas as pd

from src.scenarios import project_logit_share


class FleetTurnoverError(ValueError):
    """Raised when model inputs or accounting identities are invalid."""


def _require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise FleetTurnoverError(f"{label} is missing columns: {', '.join(missing)}")


def _validate_assumptions(assumptions: pd.DataFrame) -> None:
    if assumptions["scenario"].duplicated().any():
        raise FleetTurnoverError("scenario names must be unique")
    checks = {
        "annual_logit_gain must be non-negative": assumptions["annual_logit_gain"]
        < 0,
        "total_turnover_rate_pct must be between 0 and 100": ~assumptions[
            "total_turnover_rate_pct"
        ].between(0, 100, inclusive="neither"),
        "nev_relative_retirement_weight must be between 0 and 1": ~assumptions[
            "nev_relative_retirement_weight"
        ].between(0, 1, inclusive="both"),
        "annual domestic inflow growth must exceed -100%": assumptions[
            "annual_domestic_inflow_growth_pct"
        ]
        <= -100,
    }
    for message, mask in checks.items():
        if mask.any():
            scenarios = assumptions.loc[mask, "scenario"].tolist()
            raise FleetTurnoverError(f"{message}: {scenarios}")


def simulate_fleet_turnover(
    fleet: pd.DataFrame,
    export_metrics: pd.DataFrame,
    assumptions: pd.DataFrame,
    *,
    anchor_year: int = 2025,
    end_year: int = 2035,
) -> pd.DataFrame:
    """Run auditable annual stock-flow scenarios after an observed anchor year.

    CAAM industry deliveries less enterprise-reported exports are used only as
    a domestic-inflow proxy. Total retirements are a fixed scenario percentage
    of opening fleet stock. Because the registered NEV fleet is comparatively
    young, its retirement allocation receives an explicit relative weight.
    """

    if end_year <= anchor_year:
        raise FleetTurnoverError("end_year must be after anchor_year")
    _require_columns(
        fleet,
        {"period", "auto_stock_m", "nev_stock_m"},
        "fleet snapshot",
    )
    _require_columns(
        export_metrics,
        {
            "year",
            "non_export_total_sales_proxy_m",
            "non_export_nev_sales_proxy_m",
        },
        "export metrics",
    )
    _require_columns(
        assumptions,
        {
            "scenario",
            "annual_logit_gain",
            "total_turnover_rate_pct",
            "nev_relative_retirement_weight",
            "annual_domestic_inflow_growth_pct",
            "description",
        },
        "fleet assumptions",
    )
    _validate_assumptions(assumptions)

    anchor_period = f"{anchor_year}-12-31"
    fleet_anchor = fleet.loc[fleet["period"] == anchor_period]
    flow_anchor = export_metrics.loc[export_metrics["year"] == anchor_year]
    if len(fleet_anchor) != 1 or len(flow_anchor) != 1:
        raise FleetTurnoverError(
            f"expected one fleet and one domestic-inflow anchor for {anchor_year}"
        )

    auto_stock_m = float(fleet_anchor.iloc[0]["auto_stock_m"])
    nev_stock_m = float(fleet_anchor.iloc[0]["nev_stock_m"])
    ice_stock_m = auto_stock_m - nev_stock_m
    domestic_inflow_anchor_m = float(
        flow_anchor.iloc[0]["non_export_total_sales_proxy_m"]
    )
    nev_inflow_anchor_m = float(flow_anchor.iloc[0]["non_export_nev_sales_proxy_m"])
    if not 0 < nev_stock_m < auto_stock_m:
        raise FleetTurnoverError("anchor NEV stock must be within total auto stock")
    if not 0 < nev_inflow_anchor_m < domestic_inflow_anchor_m:
        raise FleetTurnoverError("anchor NEV inflow must be within total inflow")
    anchor_nev_inflow_share_pct = (
        nev_inflow_anchor_m / domestic_inflow_anchor_m * 100
    )

    rows: list[dict[str, float | int | str]] = []
    for assumption in assumptions.itertuples(index=False):
        opening_nev_m = nev_stock_m
        opening_ice_m = ice_stock_m
        for year in range(anchor_year + 1, end_year + 1):
            years_ahead = year - anchor_year
            domestic_inflow_m = domestic_inflow_anchor_m * (
                1 + assumption.annual_domestic_inflow_growth_pct / 100
            ) ** years_ahead
            nev_inflow_share_pct = project_logit_share(
                anchor_nev_inflow_share_pct,
                years_ahead,
                assumption.annual_logit_gain,
            )
            nev_inflow_m = domestic_inflow_m * nev_inflow_share_pct / 100
            ice_inflow_m = domestic_inflow_m - nev_inflow_m

            opening_total_m = opening_nev_m + opening_ice_m
            total_retirements_m = (
                opening_total_m * assumption.total_turnover_rate_pct / 100
            )
            weighted_nev = (
                opening_nev_m * assumption.nev_relative_retirement_weight
            )
            weighted_total = weighted_nev + opening_ice_m
            if weighted_total <= 0:
                raise FleetTurnoverError("retirement allocation denominator is zero")
            nev_retirements_m = total_retirements_m * weighted_nev / weighted_total
            ice_retirements_m = total_retirements_m - nev_retirements_m
            if (
                nev_retirements_m > opening_nev_m
                or ice_retirements_m > opening_ice_m
            ):
                raise FleetTurnoverError(
                    f"retirements exceed opening stock for {assumption.scenario} {year}"
                )

            ending_nev_m = opening_nev_m + nev_inflow_m - nev_retirements_m
            ending_ice_m = opening_ice_m + ice_inflow_m - ice_retirements_m
            ending_total_m = ending_nev_m + ending_ice_m
            accounting_gap_m = ending_total_m - (
                opening_total_m + domestic_inflow_m - total_retirements_m
            )
            rows.append(
                {
                    "scenario": assumption.scenario,
                    "year": year,
                    "opening_nev_stock_m": opening_nev_m,
                    "opening_ice_stock_m": opening_ice_m,
                    "domestic_inflow_m": domestic_inflow_m,
                    "nev_inflow_share_pct": nev_inflow_share_pct,
                    "nev_inflow_m": nev_inflow_m,
                    "ice_inflow_m": ice_inflow_m,
                    "total_retirements_m": total_retirements_m,
                    "nev_retirements_m": nev_retirements_m,
                    "ice_retirements_m": ice_retirements_m,
                    "nev_stock_m": ending_nev_m,
                    "ice_stock_m": ending_ice_m,
                    "total_auto_stock_m": ending_total_m,
                    "nev_fleet_share_pct": ending_nev_m / ending_total_m * 100,
                    "annual_logit_gain": assumption.annual_logit_gain,
                    "total_turnover_rate_pct": assumption.total_turnover_rate_pct,
                    "nev_relative_retirement_weight": (
                        assumption.nev_relative_retirement_weight
                    ),
                    "annual_domestic_inflow_growth_pct": (
                        assumption.annual_domestic_inflow_growth_pct
                    ),
                    "accounting_gap_m": accounting_gap_m,
                }
            )
            opening_nev_m = ending_nev_m
            opening_ice_m = ending_ice_m

    result = pd.DataFrame(rows)
    if (result[["nev_stock_m", "ice_stock_m", "total_auto_stock_m"]] < 0).any(
        axis=None
    ):
        raise FleetTurnoverError("model generated a negative stock")
    if not result["nev_fleet_share_pct"].between(0, 100).all():
        raise FleetTurnoverError("model generated an invalid fleet share")
    if result["accounting_gap_m"].abs().max() > 1e-9:
        raise FleetTurnoverError("stock-flow accounting identity failed")
    return result
