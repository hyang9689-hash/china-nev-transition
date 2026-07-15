"""Rebuild derived tables and the project's first-look figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import (  # noqa: E402
    cagr,
    growth_contribution,
    percent_change,
    percentage_point_gap,
    ratio,
    share,
)
from src.market_extensions import (  # noqa: E402
    derive_export_metrics,
    derive_powertrain_mix,
)
from src.fleet_figures import build_fleet_turnover_figure  # noqa: E402
from src.fleet_turnover import simulate_fleet_turnover  # noqa: E402
from src.market_figures import build_market_extension_figure  # noqa: E402
from src.scenario_validation import backtest_logit_trend  # noqa: E402
from src.scenarios import scenario_table  # noqa: E402

DATA = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

NAVY = "#102A43"
ORANGE = "#E4572E"
TEAL = "#178F8F"
GOLD = "#F3B61F"
SLATE = "#627D98"
PALE = "#E8EEF2"
INK = "#243B53"
GRID = "#D9E2EC"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    annual = pd.read_csv(DATA / "china_auto_market_2015_2025.csv")
    fleet = pd.read_csv(DATA / "fleet_charging_snapshot.csv")
    pulse = pd.read_csv(DATA / "current_market_pulse.csv")
    targets = pd.read_csv(DATA / "policy_targets.csv")
    return annual, fleet, pulse, targets


def derive_annual(annual: pd.DataFrame) -> pd.DataFrame:
    result = annual.copy()
    result["nev_share_total_sales_pct"] = (
        result["nev_sales_m"] / result["total_auto_sales_m"] * 100
    )
    result["nev_sales_yoy_pct"] = result["nev_sales_m"].pct_change() * 100
    result["total_sales_yoy_pct"] = result["total_auto_sales_m"].pct_change() * 100
    result["non_nev_sales_m"] = result["total_auto_sales_m"] - result["nev_sales_m"]
    result.to_csv(DATA / "derived_annual_metrics.csv", index=False, float_format="%.4f")
    return result


def derive_key_metrics(
    annual: pd.DataFrame,
    fleet: pd.DataFrame,
    pulse: pd.DataFrame,
    targets: pd.DataFrame,
) -> pd.DataFrame:
    row_2024 = annual.loc[annual["year"] == 2024].iloc[0]
    row_2025 = annual.loc[annual["year"] == 2025].iloc[0]
    infra_2024 = fleet.loc[fleet["period"] == "2024-12-31"].iloc[0]
    infra_2025 = fleet.loc[fleet["period"] == "2025-12-31"].iloc[0]
    infra_latest = fleet.loc[fleet["period"] == "2026-05-31"].iloc[0]
    domestic_share = pulse.loc[
        (pulse["period"] == "2025")
        & (pulse["scope"] == "domestic_new_vehicle_sales"),
        "nev_share_reported_pct",
    ].iloc[0]
    fleet_share = share(infra_2025["nev_stock_m"], infra_2025["auto_stock_m"])
    facility_target = targets.loc[
        targets["metric"] == "total_charging_facilities", "target_value"
    ].iloc[0]

    total_change = row_2025["total_auto_sales_m"] - row_2024["total_auto_sales_m"]
    nev_change = row_2025["nev_sales_m"] - row_2024["nev_sales_m"]
    non_nev_change = (
        row_2025["total_auto_sales_m"]
        - row_2025["nev_sales_m"]
        - row_2024["total_auto_sales_m"]
        + row_2024["nev_sales_m"]
    )

    rows = [
        ("nev_sales_cagr_2015_2025", cagr(annual.iloc[0]["nev_sales_m"], row_2025["nev_sales_m"], 10), "percent", "CAGR"),
        ("nev_share_total_sales_2025", share(row_2025["nev_sales_m"], row_2025["total_auto_sales_m"]), "percent", "NEV sales / total CAAM automobile sales"),
        ("nev_share_domestic_sales_2025", domestic_share, "percent", "source-reported domestic new-vehicle share"),
        ("nev_fleet_share_2025", fleet_share, "percent", "NEV stock / civilian automobile stock"),
        ("sales_flow_minus_fleet_stock_gap", percentage_point_gap(domestic_share, fleet_share), "percentage_points", "domestic new-sales share - fleet share"),
        ("charging_growth_reported_2025", infra_2025["charging_yoy_reported_pct"], "percent", "source-reported YoY after NEA scope adjustment"),
        ("nev_stock_growth_2024_2025", percent_change(infra_2025["nev_stock_m"], infra_2024["nev_stock_m"]), "percent", "year-end registered NEV stock"),
        ("nevs_per_total_connector_2025", ratio(infra_2025["nev_stock_m"], infra_2025["charging_total_m"]), "ratio", "registered NEVs / all connectors"),
        ("nevs_per_public_connector_2025", ratio(infra_2025["nev_stock_m"], infra_2025["charging_public_m"]), "ratio", "registered NEVs / public connectors"),
        ("charging_target_progress_may_2026", share(infra_latest["charging_total_m"], facility_target), "percent", "latest connector stock / 2027 target"),
        ("charging_cagr_needed_2025_2027", cagr(infra_2025["charging_total_m"], facility_target, 2), "percent", "CAGR from end-2025 to end-2027 target"),
        ("nev_contribution_to_net_market_growth_2025", growth_contribution(nev_change, total_change), "percent", "NEV sales change / total sales change"),
        ("non_nev_sales_change_2024_2025", non_nev_change, "million_vehicles", "derived residual change"),
    ]
    metrics = pd.DataFrame(rows, columns=["metric", "value", "unit", "formula_or_scope"])
    metrics.to_csv(DATA / "key_metrics.csv", index=False, float_format="%.4f")
    return metrics


def style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=SLATE, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.75)
    ax.set_axisbelow(True)


def build_dashboard(
    annual: pd.DataFrame,
    fleet: pd.DataFrame,
    pulse: pd.DataFrame,
    targets: pd.DataFrame,
    metrics: pd.DataFrame,
) -> None:
    metric = metrics.set_index("metric")["value"]
    years = annual["year"].to_numpy()

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.labelcolor": SLATE,
            "text.color": INK,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=False)
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.12, right=0.97, top=0.84, bottom=0.11, hspace=0.48, wspace=0.28)
    fig.suptitle(
        "China's NEV transition has crossed the domestic-sales tipping point",
        x=0.07,
        y=0.965,
        ha="left",
        fontsize=24,
        color=NAVY,
        fontweight="bold",
    )
    fig.text(
        0.07,
        0.915,
        "New sales are changing faster than the vehicles already on the road — and charging capacity is racing to catch up.",
        ha="left",
        fontsize=12.5,
        color=SLATE,
    )

    # A — annual market volumes
    ax = axes[0, 0]
    style_axis(ax)
    ax.bar(years, annual["total_auto_sales_m"], color=PALE, width=0.72, label="All automobile sales")
    ax.bar(years, annual["nev_sales_m"], color=ORANGE, width=0.72, label="NEV sales")
    ax.set_title("A. NEVs moved from niche to market-scale", loc="left", color=NAVY, fontsize=13)
    ax.set_ylabel("Million vehicles")
    ax.set_xticks(years[::2])
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    ax.text(2025, 16.9, "16.49m", ha="center", va="bottom", color=ORANGE, fontweight="bold", fontsize=10)
    ax.text(2025, 34.8, "34.40m total", ha="center", va="bottom", color=SLATE, fontsize=9)

    # B — share of total CAAM sales
    ax = axes[0, 1]
    style_axis(ax)
    share_series = annual["nev_share_total_sales_pct"].to_numpy()
    ax.fill_between(years, share_series, color=ORANGE, alpha=0.13)
    ax.plot(years, share_series, color=ORANGE, marker="o", linewidth=2.8, markersize=5)
    ax.axhline(50, color=SLATE, linestyle=(0, (4, 4)), linewidth=1.2)
    ax.set_title("B. Total-sales share approached one half", loc="left", color=NAVY, fontsize=13)
    ax.set_ylabel("NEV share of total CAAM sales")
    ax.set_xticks(years[::2])
    ax.set_ylim(0, 57)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.annotate("1.3%", (2015, share_series[0]), xytext=(2015.2, 8), color=SLATE, fontsize=9)
    ax.annotate(
        "47.9%",
        (2025, share_series[-1]),
        xytext=(2023.8, 53),
        arrowprops={"arrowstyle": "-", "color": ORANGE},
        color=ORANGE,
        fontweight="bold",
        fontsize=11,
    )
    ax.text(2015, 51.3, "50% reference", color=SLATE, fontsize=8.5)

    # C — new-sales flow versus fleet stock
    ax = axes[1, 0]
    style_axis(ax)
    domestic = metric["nev_share_domestic_sales_2025"]
    fleet_share = metric["nev_fleet_share_2025"]
    categories = ["Domestic new sales", "Registered fleet"]
    values = [domestic, fleet_share]
    colors = [ORANGE, TEAL]
    bars = ax.barh(categories, values, color=colors, height=0.48)
    ax.invert_yaxis()
    ax.set_xlim(0, 60)
    ax.xaxis.set_major_formatter(PercentFormatter())
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.75)
    ax.grid(axis="y", visible=False)
    ax.set_title("C. The transition is a flow–stock story", loc="left", color=NAVY, fontsize=13)
    for bar, value in zip(bars, values, strict=True):
        ax.text(value + 1, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontweight="bold", color=INK)
    ax.text(
        0.98,
        0.07,
        f"Gap: {metric['sales_flow_minus_fleet_stock_gap']:.1f} percentage points",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color=NAVY,
        fontweight="bold",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "#F7FAFC", "edgecolor": GRID},
    )

    # D — charging facilities and target
    ax = axes[1, 1]
    style_axis(ax)
    charging = fleet.dropna(subset=["charging_total_m"]).copy()
    labels = ["End 2024", "End 2025", "May 2026"]
    values = charging["charging_total_m"].to_numpy()
    bars = ax.bar(labels, values, color=[PALE, TEAL, NAVY], width=0.58)
    target = targets.loc[targets["metric"] == "total_charging_facilities", "target_value"].iloc[0]
    ax.axhline(target, color=GOLD, linewidth=2, linestyle=(0, (5, 4)))
    ax.set_ylim(0, 31)
    ax.set_ylabel("Million charging connectors")
    ax.set_title("D. Charging stock passed 20 million", loc="left", color=NAVY, fontsize=13)
    for bar, value in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.7, f"{value:.1f}m", ha="center", fontweight="bold", color=INK)
    ax.axvline(0.5, color=SLATE, linewidth=1.0, linestyle=(0, (2, 3)), alpha=0.8)
    ax.text(0.54, 16.0, "NEA scope\nbreak", color=SLATE, fontsize=8.2, ha="left")
    ax.text(1.98, target + 0.6, "2027 target: ≥28m", ha="right", color="#8A6D00", fontweight="bold", fontsize=9)
    ax.text(
        0.03,
        0.82,
        f"Official 2025 YoY: +{metric['charging_growth_reported_2025']:.1f}%\nMay 2026: {metric['charging_target_progress_may_2026']:.1f}% of target",
        transform=ax.transAxes,
        va="top",
        color=SLATE,
        fontsize=9,
    )

    fig.text(
        0.07,
        0.035,
        "Sources: CAAM/MIIT, National Bureau of Statistics, Ministry of Public Security, National Energy Administration, NDRC. Data vintage: 14 July 2026.",
        ha="left",
        color=SLATE,
        fontsize=8.5,
    )
    fig.text(
        0.97,
        0.035,
        "NEV = BEV + PHEV/range-extender + fuel-cell; passenger and commercial vehicles",
        ha="right",
        color=SLATE,
        fontsize=8.5,
    )
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "first_look_dashboard.png", dpi=180, facecolor="white")
    plt.close(fig)


def build_scenario_figure(annual: pd.DataFrame, pulse: pd.DataFrame) -> pd.DataFrame:
    anchor_share = annual.loc[annual["year"] == 2025, "nev_share_total_sales_pct"].iloc[0]
    gains = {"Slower": 0.15, "Baseline": 0.25, "Faster": 0.35}
    scenarios = scenario_table(2025, anchor_share, 2030, gains)
    scenarios.to_csv(DATA / "scenario_shares_2025_2030.csv", index=False, float_format="%.4f")

    colors = {"Slower": SLATE, "Baseline": TEAL, "Faster": ORANGE}
    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.patch.set_facecolor("white")
    style_axis(ax)
    ax.plot(
        annual["year"],
        annual["nev_share_total_sales_pct"],
        color=NAVY,
        linewidth=2.8,
        marker="o",
        label="Observed annual share",
    )
    for name, frame in scenarios.groupby("scenario", sort=False):
        ax.plot(
            frame["year"],
            frame["nev_share_pct"],
            color=colors[name],
            linewidth=2.3,
            linestyle="--",
            label=f"{name} scenario",
        )
    h1 = pulse.loc[pulse["period"] == "2026-H1"].iloc[0]
    june = pulse.loc[pulse["period"] == "2026-06"].iloc[0]
    ax.scatter([2026], [h1["nev_share_reported_pct"]], marker="s", s=70, color=GOLD, edgecolor=NAVY, zorder=5, label="2026 H1 (partial year)")
    ax.scatter([2026.08], [june["nev_share_reported_pct"]], marker="^", s=75, color=ORANGE, edgecolor=NAVY, zorder=5, label="June 2026 (single month)")
    fig.suptitle(
        "Illustrative NEV-share paths to 2030",
        x=0.08,
        y=0.975,
        ha="left",
        color=NAVY,
        fontsize=17,
        fontweight="bold",
    )
    fig.text(
        0.08,
        0.93,
        "Log-odds scenarios anchored to the 2025 total-sales share; not a causal forecast",
        color=SLATE,
        fontsize=10,
    )
    ax.set_ylabel("NEV share of total CAAM sales")
    ax.set_xlabel("Year")
    ax.set_xlim(2015, 2030.3)
    ax.set_ylim(0, 95)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.legend(frameon=False, ncol=2, fontsize=8.5, loc="upper left")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(FIGURES / "scenario_paths.png", dpi=180, facecolor="white")
    plt.close(fig)
    return scenarios


def main() -> None:
    annual_raw, fleet, pulse, targets = load_inputs()
    annual = derive_annual(annual_raw)
    powertrain_raw = pd.read_csv(DATA / "nev_powertrain_sales_2020_2024.csv")
    exports_raw = pd.read_csv(DATA / "auto_exports_2021_2025.csv")
    assumptions = pd.read_csv(
        ROOT / "data" / "manual" / "fleet_turnover_assumptions.csv"
    )
    powertrain = derive_powertrain_mix(powertrain_raw, annual)
    exports = derive_export_metrics(exports_raw, annual)
    fleet_scenarios = simulate_fleet_turnover(fleet, exports, assumptions)
    backtest = backtest_logit_trend(annual)
    powertrain.to_csv(
        DATA / "powertrain_mix_metrics.csv", index=False, float_format="%.4f"
    )
    exports.to_csv(DATA / "export_metrics.csv", index=False, float_format="%.4f")
    fleet_scenarios.to_csv(
        DATA / "fleet_turnover_scenarios.csv", index=False, float_format="%.4f"
    )
    backtest.to_csv(
        DATA / "sales_share_backtest_2023_2025.csv",
        index=False,
        float_format="%.4f",
    )
    metrics = derive_key_metrics(annual, fleet, pulse, targets)
    build_dashboard(annual, fleet, pulse, targets, metrics)
    build_scenario_figure(annual, pulse)
    build_market_extension_figure(
        powertrain, exports, FIGURES / "powertrain_exports.png"
    )
    fleet_anchor = fleet.loc[fleet["period"] == "2025-12-31"].iloc[0]
    flow_anchor = exports.loc[exports["year"] == 2025].iloc[0]
    build_fleet_turnover_figure(
        fleet_scenarios,
        anchor_year=2025,
        anchor_inflow_share_pct=(
            flow_anchor["non_export_nev_sales_proxy_m"]
            / flow_anchor["non_export_total_sales_proxy_m"]
            * 100
        ),
        anchor_fleet_share_pct=(
            fleet_anchor["nev_stock_m"] / fleet_anchor["auto_stock_m"] * 100
        ),
        output_path=FIGURES / "fleet_turnover_scenarios.png",
    )
    print(f"Built {len(annual)} annual observations and {len(metrics)} key metrics.")
    print(f"Built {len(powertrain)} powertrain rows and {len(exports)} export rows.")
    print(
        f"Built {len(fleet_scenarios)} fleet-scenario rows; "
        f"held-out sales-share MAE is {backtest['absolute_error_pp'].mean():.2f} pp."
    )
    print(f"Figures written to {FIGURES}")


if __name__ == "__main__":
    main()
