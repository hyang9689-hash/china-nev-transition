import unittest

from src.metrics import (
    cagr,
    growth_contribution,
    percent_change,
    percentage_point_gap,
    ratio,
    share,
)


class MetricsTests(unittest.TestCase):
    def test_share_and_gap(self) -> None:
        self.assertAlmostEqual(share(16.49, 34.40), 47.9360465, places=6)
        self.assertAlmostEqual(percentage_point_gap(50.8, 12.01), 38.79)

    def test_growth_formulas(self) -> None:
        self.assertAlmostEqual(percent_change(149.7, 100), 49.7, places=6)
        self.assertAlmostEqual(cagr(20.092, 28.0, 2), 18.0503913, places=6)

    def test_ratios_and_contribution(self) -> None:
        self.assertAlmostEqual(ratio(43.97, 20.092), 2.1884332, places=6)
        self.assertAlmostEqual(growth_contribution(3.624, 2.964), 122.2672065, places=6)

    def test_zero_or_negative_denominators_fail(self) -> None:
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    share(1, value)
                with self.assertRaises(ValueError):
                    percent_change(1, value)


if __name__ == "__main__":
    unittest.main()
