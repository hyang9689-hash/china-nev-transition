import csv
import tempfile
import unittest
from pathlib import Path

from src.data_validation import (
    DataValidationError,
    _read_and_validate_table,
    load_dictionary,
    validate_project_data,
)


ROOT = Path(__file__).resolve().parents[1]


class DataSchemaTests(unittest.TestCase):
    def test_all_declared_datasets_and_cross_file_rules_pass(self) -> None:
        tables = validate_project_data(ROOT)
        self.assertEqual(len(tables), 6)
        self.assertEqual(
            len(tables["data/manual/pre2021_double_entry.csv"]), 12
        )

    def test_every_dictionary_field_is_documented(self) -> None:
        dictionary = load_dictionary(ROOT)
        for dataset, spec in dictionary["datasets"].items():
            with self.subTest(dataset=dataset):
                self.assertTrue(spec["primary_key"])
            for field, config in spec["columns"].items():
                with self.subTest(dataset=dataset, field=field):
                    self.assertIn("type", config)
                    self.assertIn("nullable", config)
                    self.assertIn("unit", config)
                    self.assertIn("role", config)
                    self.assertTrue(config.get("description"))

    def test_duplicate_primary_key_fails(self) -> None:
        dictionary = load_dictionary(ROOT)
        spec = dictionary["datasets"][
            "data/processed/china_auto_market_2015_2025.csv"
        ]
        rows = [
            {
                "year": "2015",
                "total_auto_sales_m": "24.598",
                "nev_sales_m": "0.3311",
                "total_sales_source_id": "caam2021autoseries",
                "nev_sales_source_id": "caam2021nevseries",
            }
        ] * 2
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "annual.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(spec["columns"]))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(DataValidationError, "duplicate primary key"):
                _read_and_validate_table(root, "annual.csv", spec)

    def test_range_violation_fails(self) -> None:
        dictionary = load_dictionary(ROOT)
        spec = dictionary["datasets"][
            "data/processed/china_auto_market_2015_2025.csv"
        ]
        row = {
            "year": "2030",
            "total_auto_sales_m": "24.598",
            "nev_sales_m": "0.3311",
            "total_sales_source_id": "caam2021autoseries",
            "nev_sales_source_id": "caam2021nevseries",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "annual.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(spec["columns"]))
                writer.writeheader()
                writer.writerow(row)
            with self.assertRaisesRegex(DataValidationError, "above 2025"):
                _read_and_validate_table(root, "annual.csv", spec)


if __name__ == "__main__":
    unittest.main()
