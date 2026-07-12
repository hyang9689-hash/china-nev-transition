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

        **Exploration notebook · China NEV transition · data vintage 2026-07-12**

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
        from IPython.display import Image, display

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

        display(
            annual[["year", "total_auto_sales_m", "nev_sales_m", "nev_share_total_sales_pct", "nev_sales_yoy_pct"]]
            .round(2)
            .style.format({
                "total_auto_sales_m": "{:.2f}",
                "nev_sales_m": "{:.2f}",
                "nev_share_total_sales_pct": "{:.1f}%",
                "nev_sales_yoy_pct": "{:.1f}%",
            })
        )
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
        display(
            scenarios.pivot(index="year", columns="scenario", values="nev_share_pct")
            .round(1)
            .style.format("{:.1f}%")
        )
        display(Image(filename=str(ROOT / "figures" / "scenario_paths.png"), width=900))
        """
    ),
    markdown(
        """
        ## 4. Limits and next checks

        - The pre-2021 annual series was manually transcribed from CAAM charts
          and will receive an independent second-entry audit.
        - NEA changed its charging statistical scope in 2025. The 2024 and 2025
          level bars are shown with a visible break; the project uses NEA's
          reported 49.7% YoY rate rather than calculating a misleading rate
          from incompatible endpoints.
        - Sales, production, exports, registrations, and fleet stock are not
          interchangeable.
        - The 2030 paths are transparent sensitivity scenarios. They are not
          probabilities and do not identify causes.
        """
    ),
]

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11+"},
    },
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, OUTPUT)
print(f"Wrote {OUTPUT}")
