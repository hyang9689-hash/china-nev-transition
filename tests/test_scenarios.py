import unittest

from src.scenarios import inverse_logit, logit, project_logit_share, scenario_table


class ScenarioTests(unittest.TestCase):
    def test_logit_round_trip(self) -> None:
        for probability in (0.1, 0.5, 0.9):
            with self.subTest(probability=probability):
                self.assertAlmostEqual(inverse_logit(logit(probability)), probability)

    def test_projection_is_anchored_and_bounded(self) -> None:
        self.assertAlmostEqual(project_logit_share(47.936, 0, 0.25), 47.936)
        projected = project_logit_share(47.936, 5, 0.25)
        self.assertGreater(projected, 47.936)
        self.assertLess(projected, 100)

    def test_scenario_table_shape(self) -> None:
        table = scenario_table(2025, 47.936, 2030, {"slow": 0.15, "fast": 0.35})
        self.assertEqual(table.shape[0], 12)
        self.assertEqual(set(table["scenario"]), {"slow", "fast"})

    def test_invalid_probability_fails(self) -> None:
        with self.assertRaises(ValueError):
            logit(1.0)


if __name__ == "__main__":
    unittest.main()
