"""Visualization for fleet-turnover sensitivity scenarios."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd
from matplotlib.ticker import PercentFormatter

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


NAVY = "#102A43"
ORANGE = "#E4572E"
TEAL = "#178F8F"
SLATE = "#627D98"
GRID = "#D9E2EC"
COLORS = {"Conservative": SLATE, "Baseline": TEAL, "Accelerated": ORANGE}


def _style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=SLATE, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.75)
    ax.set_axisbelow(True)


def build_fleet_turnover_figure(
    scenarios: pd.DataFrame,
    *,
    anchor_year: int,
    anchor_inflow_share_pct: float,
    anchor_fleet_share_pct: float,
    output_path: Path,
) -> None:
    """Compare projected annual inflow shares with slower-moving fleet shares."""

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.labelcolor": SLATE,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8), sharex=True)
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.08, right=0.97, top=0.79, bottom=0.16, wspace=0.24)
    fig.suptitle(
        "Fleet turnover keeps the stock transition behind the sales flow",
        x=0.06,
        y=0.96,
        ha="left",
        color=NAVY,
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.06,
        0.895,
        "Transparent 2026-2035 sensitivities anchored to observed end-2025 stock; not a forecast.",
        color=SLATE,
        fontsize=10.5,
    )

    for ax in axes:
        _style_axis(ax)
        ax.set_ylim(0, 105)
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax.set_xlabel("Year")

    axes[0].set_title(
        "A. NEV share of annual domestic-inflow proxy",
        loc="left",
        color=NAVY,
        fontsize=12,
    )
    axes[1].set_title(
        "B. NEV share of registered fleet stock",
        loc="left",
        color=NAVY,
        fontsize=12,
    )
    axes[0].set_ylabel("NEV share")

    for name, frame in scenarios.groupby("scenario", sort=False):
        color = COLORS.get(name, NAVY)
        years = [anchor_year, *frame["year"].astype(int).tolist()]
        flow = [anchor_inflow_share_pct, *frame["nev_inflow_share_pct"].tolist()]
        fleet = [anchor_fleet_share_pct, *frame["nev_fleet_share_pct"].tolist()]
        axes[0].plot(years, flow, color=color, linewidth=2.5, label=name)
        axes[1].plot(years, fleet, color=color, linewidth=2.5, label=name)

    axes[0].scatter(
        [anchor_year], [anchor_inflow_share_pct], color=NAVY, s=42, zorder=5
    )
    axes[1].scatter(
        [anchor_year], [anchor_fleet_share_pct], color=NAVY, s=42, zorder=5
    )
    axes[0].text(
        anchor_year + 0.15,
        anchor_inflow_share_pct + 2,
        f"{anchor_inflow_share_pct:.1f}% anchor",
        color=NAVY,
        fontsize=8.5,
    )
    axes[1].text(
        anchor_year + 0.15,
        anchor_fleet_share_pct + 2,
        f"{anchor_fleet_share_pct:.1f}% anchor",
        color=NAVY,
        fontsize=8.5,
    )
    axes[0].legend(frameon=False, fontsize=9, loc="upper left")
    axes[1].legend(frameon=False, fontsize=9, loc="upper left")

    fig.text(
        0.06,
        0.05,
        "Assumptions: constant 2025 domestic-inflow proxy; 5.5%-7.0% annual turnover; "
        "NEV retirement allocation weighted at 0.25x ICE because the NEV stock is younger.",
        color=SLATE,
        fontsize=8.2,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, facecolor="white")
    plt.close(fig)
