import unittest
from pathlib import Path

import pandas as pd

from src.market_extensions import (
    MarketExtensionError,
    derive_export_metrics,
    derive_powertrain_mix,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"


class MarketExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.annual = pd.read_csv(DATA / "china_auto_market_2015_2025.csv")
        cls.powertrain = pd.read_csv(DATA / "nev_powertrain_sales_2020_2024.csv")
        cls.exports = pd.read_csv(DATA / "auto_exports_2021_2025.csv")

    def test_powertrain_components_reconcile(self) -> None:
        result = derive_powertrain_mix(self.powertrain, self.annual)
        self.assertEqual(result["year"].tolist(), list(range(2020, 2025)))
        self.assertLessEqual(
            result["component_reconciliation_gap_m"].abs().max(), 0.002
        )
        component_share = result[
            [
                "bev_share_of_nev_pct",
                "phev_share_of_nev_pct",
                "fcev_share_of_nev_pct",
            ]
        ].sum(axis=1)
        self.assertTrue(component_share.between(99.98, 100.02).all())

    def test_exports_are_bounded_and_proxies_are_labelled(self) -> None:
        result = derive_export_metrics(self.exports, self.annual)
        self.assertEqual(result["year"].tolist(), list(range(2021, 2026)))
        self.assertTrue(
            (result["nev_exports_m"] <= result["total_auto_exports_m"]).all()
        )
        self.assertTrue(result["non_export_nev_share_proxy_pct"].between(0, 100).all())
        self.assertAlmostEqual(
            result.loc[result["year"] == 2025, "nev_share_of_exports_pct"].iloc[0],
            36.841,
            places=3,
        )

    def test_bad_powertrain_reconciliation_fails(self) -> None:
        bad = self.powertrain.copy()
        bad.loc[bad["year"] == 2024, "bev_sales_m"] += 0.1
        with self.assertRaisesRegex(MarketExtensionError, "do not reconcile"):
            derive_powertrain_mix(bad, self.annual)

    def test_impossible_export_volume_fails(self) -> None:
        bad = self.exports.copy()
        bad.loc[bad["year"] == 2025, "nev_exports_m"] = 8.0
        with self.assertRaisesRegex(MarketExtensionError, "NEV exports exceed"):
            derive_export_metrics(bad, self.annual)


if __name__ == "__main__":
    unittest.main()
