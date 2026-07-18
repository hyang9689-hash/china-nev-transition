"""Generate the exploration notebook from version-controlled cell sources."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "01_exploration.ipynb"


def markdown(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(dedent(text).strip())


cells = [
    markdown(
        """
        # Past the Tipping Point, Not Yet Transformed

        **Exploration notebook · China NEV transition · data vintage 2026-07-14**

        Central question: *How quickly is China's dominance of new-energy
        vehicles in new-vehicle sales translating into the on-road fleet, and
        has charging infrastructure kept pace?*

        The notebook keeps annual observations, partial-year observations,
        registered fleet stock, and charging connectors in separate tables.
        """
    ),
    code(
        """
        from pathlib import Path
        import sys

        import pandas as pd
        from IPython.display import HTML, Image, display

        ROOT = Path.cwd()
        if ROOT.name == "notebooks":
            ROOT = ROOT.parent
        sys.path.insert(0, str(ROOT))

        from src.metrics import cagr, growth_contribution, percent_change, ratio, share
        from src.scenarios import scenario_table

        DATA = ROOT / "data" / "processed"
        annual = pd.read_csv(DATA / "china_auto_market_2015_2025.csv")
        fleet = pd.read_csv(DATA / "fleet_charging_snapshot.csv")
        pulse = pd.read_csv(DATA / "current_market_pulse.csv")
        targets = pd.read_csv(DATA / "policy_targets.csv")

        print(f"Loaded {len(annual)} complete annual observations: {annual.year.min()}-{annual.year.max()}")
        """
    ),
    markdown(
        r"""
        ## 1. Basic mathematics

        The core calculations are intentionally transparent:

        $$\text{NEV share}_t = \frac{\text{NEV sales}_t}{\text{total automobile sales}_t} \times 100$$

        $$\text{YoY growth}_t = \left(\frac{x_t}{x_{t-1}} - 1\right) \times 100$$

        $$\text{CAGR} = \left(\frac{x_{end}}{x_{start}}\right)^{1/n} - 1$$

        A growth contribution above 100% is possible: it means the growing
        component more than explains total net growth while another component
        contracted.
        """
    ),
    code(
        """
        annual = annual.assign(
            nev_share_total_sales_pct=lambda x: 100 * x.nev_sales_m / x.total_auto_sales_m,
            nev_sales_yoy_pct=lambda x: x.nev_sales_m.pct_change() * 100,
            non_nev_sales_m=lambda x: x.total_auto_sales_m - x.nev_sales_m,
        )

        annual_table = (
            annual[["year", "total_auto_sales_m", "nev_sales_m", "nev_share_total_sales_pct", "nev_sales_yoy_pct"]]
            .round(2)
            .style.set_uuid("annual-market")
            .format({
                "total_auto_sales_m": "{:.2f}",
                "nev_sales_m": "{:.2f}",
                "nev_share_total_sales_pct": "{:.1f}%",
                "nev_sales_yoy_pct": "{:.1f}%",
            })
        )
        display(HTML(annual_table.to_html()))
        """
    ),
    markdown(
        """
        ## 2. The first results

        The 2025 total-sales share (47.9%) and the separately reported domestic
        new-sales share (50.8%) use different denominators. The registered fleet
        share (12.0%) is a stock measure. Keeping those definitions visible is
        part of the analysis, not a footnote added at the end.
        """
    ),
    code(
        """
        y2024 = annual.loc[annual.year == 2024].iloc[0]
        y2025 = annual.loc[annual.year == 2025].iloc[0]
        f2025 = fleet.loc[fleet.period == "2025-12-31"].iloc[0]

        nev_cagr = cagr(annual.iloc[0].nev_sales_m, y2025.nev_sales_m, 10)
        total_share = share(y2025.nev_sales_m, y2025.total_auto_sales_m)
        fleet_share = share(f2025.nev_stock_m, f2025.auto_stock_m)
        domestic_share = pulse.loc[
            (pulse.period == "2025") & (pulse.scope == "domestic_new_vehicle_sales"),
            "nev_share_reported_pct",
        ].iloc[0]

        total_growth = y2025.total_auto_sales_m - y2024.total_auto_sales_m
        nev_growth = y2025.nev_sales_m - y2024.nev_sales_m
        non_nev_change = (
            y2025.total_auto_sales_m - y2025.nev_sales_m
            - y2024.total_auto_sales_m + y2024.nev_sales_m
        )

        summary = pd.DataFrame(
            {
                "Result": [
                    "NEV sales CAGR, 2015–2025",
                    "NEV share of total CAAM sales, 2025",
                    "NEV share of domestic new sales, 2025",
                    "NEV share of registered fleet, 2025",
                    "Domestic-sales flow minus fleet-stock gap",
                    "NEV contribution to 2025 net market growth",
                    "Change in non-NEV sales, 2024–2025",
                ],
                "Value": [
                    f"{nev_cagr:.1f}%",
                    f"{total_share:.1f}%",
                    f"{domestic_share:.1f}%",
                    f"{fleet_share:.1f}%",
                    f"{domestic_share - fleet_share:.1f} pp",
                    f"{growth_contribution(nev_growth, total_growth):.1f}%",
                    f"{non_nev_change:.2f} million",
                ],
            }
        )
        display(summary)
        """
    ),
    markdown(
        """
        **Interpretation.** NEV sales grew at roughly 47.8% per year across the
        decade. In 2025 they generated more than all net automobile-market
        growth (122.3%) because estimated non-NEV sales fell by 0.66 million.
        This is descriptive accounting, not a causal claim.
        """
    ),
    code(
        """
        display(Image(filename=str(ROOT / "figures" / "first_look_dashboard.png"), width=1100))
        """
    ),
    markdown(
        r"""
        ## 3. A bounded scenario, not a confident forecast

        A linear extrapolation can exceed 100%, so the scenario uses log-odds:

        $$\operatorname{logit}(p_{t+h}) = \operatorname{logit}(p_t) + h g$$

        Here $g$ is an explicit annual increment, not an estimated causal
        effect. Three values illustrate slower, baseline, and faster paths.
        """
    ),
    code(
        """
        scenarios = scenario_table(
            anchor_year=2025,
            anchor_share=total_share,
            end_year=2030,
            annual_logit_gains={"Slower": 0.15, "Baseline": 0.25, "Faster": 0.35},
        )
        scenario_table_html = (
            scenarios.pivot(index="year", columns="scenario", values="nev_share_pct")
            .round(1)
            .style.set_uuid("scenario-shares")
            .format("{:.1f}%")
        )
        display(HTML(scenario_table_html.to_html()))
        display(Image(filename=str(ROOT / "figures" / "scenario_paths.png"), width=900))
        """
    ),
    markdown(
        """
        ## 4. Powertrain composition and exports

        Reported powertrain components are reconciled to annual NEV totals
        within published rounding. Exports are enterprise-reported industry
        volumes; sales minus exports is labelled as a residual proxy rather
        than as a separately observed domestic-retail series.
        """
    ),
    code(
        """
        powertrain = pd.read_csv(DATA / "powertrain_mix_metrics.csv")
        exports = pd.read_csv(DATA / "export_metrics.csv")

        display(
            powertrain.loc[
                powertrain.year.isin([2020, 2024]),
                [
                    "year",
                    "bev_sales_m",
                    "phev_sales_m",
                    "bev_share_of_nev_pct",
                    "phev_share_of_nev_pct",
                    "component_reconciliation_gap_m",
                ],
            ].round(2)
        )
        display(
            exports[
                [
                    "year",
                    "total_auto_exports_m",
                    "nev_exports_m",
                    "nev_share_of_exports_pct",
                    "non_export_nev_share_proxy_pct",
                ]
            ].round(2)
        )
        display(Image(filename=str(ROOT / "figures" / "powertrain_exports.png"), width=1100))
        """
    ),
    markdown(
        """
        ## 5. Fleet-turnover sensitivities and held-out check

        The stock-flow model starts from end-2025 registered stock, holds the
        domestic-inflow proxy constant, and makes every turnover rate and
        retirement-allocation weight explicit. The model output is a
        sensitivity calculation, not a registration forecast.
        """
    ),
    code(
        """
        fleet_model = pd.read_csv(DATA / "fleet_turnover_scenarios.csv")
        backtest = pd.read_csv(DATA / "sales_share_backtest_2023_2025.csv")

        endpoints = fleet_model.loc[
            fleet_model.year.isin([2030, 2035]),
            [
                "scenario",
                "year",
                "nev_inflow_share_pct",
                "nev_fleet_share_pct",
                "nev_stock_m",
                "total_auto_stock_m",
            ],
        ].copy()
        display(endpoints.round(1))
        display(backtest.round(2))
        print(f"Held-out 2023-2025 MAE: {backtest.absolute_error_pp.mean():.2f} percentage points")
        display(Image(filename=str(ROOT / "figures" / "fleet_turnover_scenarios.png"), width=1100))
        """
    ),
    markdown(
        """
        ## 6. Limits and audit status

        - The independent second-entry audit passed all 12 pre-2021 values.
        - Archived evidence notes are pinned by SHA-256 checksums.
        - NEA changed its charging statistical scope in 2025; incompatible
          endpoints are not used to calculate a spurious growth rate.
        - The powertrain composition series stops at 2024 because a consistent
          independently verifiable 2025 split was not established.
        - Sales, exports, registrations, fleet stock, and scenario output remain
          separate statistical concepts.
        - The sales-share paths and fleet outputs are transparent sensitivities;
          they are not probabilities, causal estimates, or registration forecasts.
        """
    ),
]

for index, cell in enumerate(cells, start=1):
    cell["id"] = f"cell-{index:02d}"

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12"},
    },
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, OUTPUT)
print(f"Wrote {OUTPUT}")
