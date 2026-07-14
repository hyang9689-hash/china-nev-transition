import unittest
from pathlib import Path

import pandas as pd

from src.fleet_turnover import FleetTurnoverError, simulate_fleet_turnover
from src.scenario_validation import backtest_logit_trend


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class FleetTurnoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fleet = pd.read_csv(DATA / "processed" / "fleet_charging_snapshot.csv")
        cls.exports = pd.read_csv(DATA / "processed" / "export_metrics.csv")
        cls.assumptions = pd.read_csv(
            DATA / "manual" / "fleet_turnover_assumptions.csv"
        )
        cls.annual = pd.read_csv(
            DATA / "processed" / "china_auto_market_2015_2025.csv"
        )

    def test_model_shape_bounds_and_ordering(self) -> None:
        result = simulate_fleet_turnover(
            self.fleet, self.exports, self.assumptions
        )
        self.assertEqual(result.shape[0], 30)
        self.assertEqual(set(result["year"]), set(range(2026, 2036)))
        self.assertTrue(result["nev_fleet_share_pct"].between(0, 100).all())
        final = result.loc[result["year"] == 2035].set_index("scenario")
        self.assertLess(
            final.loc["Conservative", "nev_fleet_share_pct"],
            final.loc["Baseline", "nev_fleet_share_pct"],
        )
        self.assertLess(
            final.loc["Baseline", "nev_fleet_share_pct"],
            final.loc["Accelerated", "nev_fleet_share_pct"],
        )

    def test_every_row_satisfies_stock_flow_accounting(self) -> None:
        result = simulate_fleet_turnover(
            self.fleet, self.exports, self.assumptions
        )
        nev_expected = (
            result["opening_nev_stock_m"]
            + result["nev_inflow_m"]
            - result["nev_retirements_m"]
        )
        ice_expected = (
            result["opening_ice_stock_m"]
            + result["ice_inflow_m"]
            - result["ice_retirements_m"]
        )
        self.assertLess((result["nev_stock_m"] - nev_expected).abs().max(), 1e-9)
        self.assertLess((result["ice_stock_m"] - ice_expected).abs().max(), 1e-9)
        self.assertLess(result["accounting_gap_m"].abs().max(), 1e-9)

    def test_invalid_turnover_rate_fails(self) -> None:
        bad = self.assumptions.copy()
        bad.loc[bad["scenario"] == "Baseline", "total_turnover_rate_pct"] = 101
        with self.assertRaisesRegex(FleetTurnoverError, "between 0 and 100"):
            simulate_fleet_turnover(self.fleet, self.exports, bad)

    def test_held_out_sales_share_backtest(self) -> None:
        result = backtest_logit_trend(self.annual)
        self.assertEqual(result["year"].tolist(), [2023, 2024, 2025])
        self.assertAlmostEqual(result["absolute_error_pp"].mean(), 5.3369, places=3)
        self.assertTrue(result["predicted_nev_share_pct"].between(0, 100).all())


if __name__ == "__main__":
    unittest.main()
