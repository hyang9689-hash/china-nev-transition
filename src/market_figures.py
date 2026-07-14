"""Figures for the powertrain-composition and export extensions."""

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
GOLD = "#F3B61F"
SLATE = "#627D98"
PALE = "#E8EEF2"
INK = "#243B53"
GRID = "#D9E2EC"


def _style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=SLATE, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.75)
    ax.set_axisbelow(True)


def build_market_extension_figure(
    powertrain: pd.DataFrame,
    exports: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot the changing powertrain mix and automobile export scale."""

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.labelcolor": SLATE,
            "text.color": INK,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8))
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(
        left=0.08, right=0.93, top=0.79, bottom=0.17, wspace=0.30
    )
    fig.suptitle(
        "China's NEV market is diversifying as exports scale",
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
        "PHEVs gained share within a rapidly expanding market; NEVs reached "
        "36.8% of automobile exports in 2025.",
        color=SLATE,
        fontsize=10.5,
    )

    ax = axes[0]
    _style_axis(ax)
    years = powertrain["year"].to_numpy()
    ax.bar(
        years,
        powertrain["bev_sales_m"],
        color=TEAL,
        width=0.68,
        label="BEV",
    )
    ax.bar(
        years,
        powertrain["phev_sales_m"],
        bottom=powertrain["bev_sales_m"],
        color=ORANGE,
        width=0.68,
        label="PHEV / range-extender",
    )
    ax.bar(
        years,
        powertrain["fcev_sales_m"],
        bottom=powertrain["bev_sales_m"] + powertrain["phev_sales_m"],
        color=GOLD,
        width=0.68,
        label="FCEV",
    )
    ax.set_title(
        "A. PHEVs gained share within NEV sales",
        loc="left",
        color=NAVY,
        fontsize=12,
    )
    ax.set_ylabel("Million vehicles")
    ax.set_xticks(years)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.text(
        0.98,
        0.07,
        f"PHEV share: {powertrain.iloc[0]['phev_share_of_nev_pct']:.1f}% to "
        f"{powertrain.iloc[-1]['phev_share_of_nev_pct']:.1f}%",
        transform=ax.transAxes,
        ha="right",
        color=NAVY,
        fontsize=9,
        fontweight="bold",
    )

    ax = axes[1]
    _style_axis(ax)
    years = exports["year"].to_numpy()
    ax.bar(
        years,
        exports["total_auto_exports_m"],
        color=PALE,
        width=0.68,
        label="All auto exports",
    )
    ax.bar(
        years,
        exports["nev_exports_m"],
        color=ORANGE,
        width=0.68,
        label="NEV exports",
    )
    ax.set_title(
        "B. NEVs became a larger export component",
        loc="left",
        color=NAVY,
        fontsize=12,
    )
    ax.set_ylabel("Million vehicles")
    ax.set_xticks(years)
    share_axis = ax.twinx()
    share_axis.plot(
        years,
        exports["nev_share_of_exports_pct"],
        color=NAVY,
        marker="o",
        linewidth=2.2,
        label="NEV share of exports",
    )
    share_axis.set_ylim(0, 45)
    share_axis.set_ylabel("NEV share of exports", color=NAVY)
    share_axis.yaxis.set_major_formatter(PercentFormatter())
    share_axis.tick_params(colors=NAVY, labelsize=9)
    share_axis.spines[["top", "left"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    share_axis.legend(frameon=False, fontsize=8.5, loc="upper center")

    fig.text(
        0.06,
        0.055,
        "Sources: MIIT, CAAM, NBS annual automobile-industry releases. "
        "Rounded components may differ from reported totals by 0.001m.",
        color=SLATE,
        fontsize=8.2,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, facecolor="white")
    plt.close(fig)
