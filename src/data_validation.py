"""Schema, provenance, and checksum validation for project data."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


class DataValidationError(AssertionError):
    """Raised when a project data contract is violated."""


def load_dictionary(root: Path) -> dict[str, Any]:
    path = root / "data" / "schema" / "datasets.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce(raw: str, field: str, field_type: str) -> Any:
    try:
        if field_type == "string":
            return raw
        if field_type == "integer":
            value = int(raw)
            if str(value) != raw.strip():
                raise ValueError("not a canonical integer")
            return value
        if field_type == "number":
            return float(raw)
        if field_type == "date":
            return date.fromisoformat(raw)
    except ValueError as exc:
        raise DataValidationError(
            f"Field {field!r} expected {field_type}, got {raw!r}"
        ) from exc
    raise DataValidationError(f"Unsupported field type {field_type!r}")


def _validate_value(value: Any, raw: str, field: str, config: dict[str, Any]) -> None:
    if "minimum" in config and value < config["minimum"]:
        raise DataValidationError(
            f"Field {field!r} value {raw!r} is below {config['minimum']}"
        )
    if "maximum" in config and value > config["maximum"]:
        raise DataValidationError(
            f"Field {field!r} value {raw!r} is above {config['maximum']}"
        )
    if "enum" in config and value not in config["enum"]:
        raise DataValidationError(
            f"Field {field!r} value {raw!r} is not in {config['enum']}"
        )
    if "pattern" in config and not re.fullmatch(config["pattern"], raw):
        raise DataValidationError(
            f"Field {field!r} value {raw!r} does not match {config['pattern']!r}"
        )


def _read_and_validate_table(
    root: Path, relative_path: str, spec: dict[str, Any]
) -> list[dict[str, Any]]:
    path = root / relative_path
    if not path.is_file():
        raise DataValidationError(f"Declared dataset is missing: {relative_path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        expected_header = list(spec["columns"])
        if reader.fieldnames != expected_header:
            raise DataValidationError(
                f"{relative_path} header {reader.fieldnames} != {expected_header}"
            )
        raw_rows = list(reader)

    typed_rows: list[dict[str, Any]] = []
    for row_number, row in enumerate(raw_rows, start=2):
        typed: dict[str, Any] = {}
        for field, config in spec["columns"].items():
            raw = row[field].strip()
            if raw == "":
                if not config["nullable"]:
                    raise DataValidationError(
                        f"{relative_path}:{row_number} field {field!r} is null"
                    )
                typed[field] = None
                continue
            value = _coerce(raw, field, config["type"])
            _validate_value(value, raw, field, config)
            typed[field] = value
        typed_rows.append(typed)

    primary_key = spec.get("primary_key", [])
    if primary_key:
        keys = [tuple(row[field] for field in primary_key) for row in typed_rows]
        if len(keys) != len(set(keys)):
            raise DataValidationError(
                f"{relative_path} has duplicate primary key {primary_key}"
            )

    for rule in spec.get("row_rules", []):
        left = rule["left"]
        right = rule["right"]
        operator = rule["operator"]
        for row_number, row in enumerate(typed_rows, start=2):
            if rule.get("skip_null") and (
                row[left] is None or row[right] is None
            ):
                continue
            if operator == "<=" and not row[left] <= row[right]:
                raise DataValidationError(
                    f"{relative_path}:{row_number} violates {left} <= {right}"
                )
            if operator != "<=":
                raise DataValidationError(f"Unsupported row-rule operator {operator}")

    sequence = spec.get("expected_integer_sequence")
    if sequence:
        observed = [row[sequence["column"]] for row in typed_rows]
        expected = list(range(sequence["start"], sequence["end"] + 1))
        if observed != expected:
            raise DataValidationError(
                f"{relative_path} {sequence['column']} sequence is {observed}, "
                f"expected {expected}"
            )
    return typed_rows


def _validate_foreign_keys(
    dictionary: dict[str, Any], tables: dict[str, list[dict[str, Any]]]
) -> None:
    for relative_path, spec in dictionary["datasets"].items():
        for field, config in spec["columns"].items():
            reference = config.get("foreign_key")
            if not reference:
                continue
            target_path, target_field = reference.split(":", maxsplit=1)
            allowed = {row[target_field] for row in tables[target_path]}
            unknown = sorted(
                {
                    row[field]
                    for row in tables[relative_path]
                    if row[field] is not None and row[field] not in allowed
                }
            )
            if unknown:
                raise DataValidationError(
                    f"{relative_path}.{field} has unknown references: {unknown}"
                )


def _validate_archive(root: Path, source_rows: list[dict[str, Any]]) -> None:
    manifest_path = root / "data" / "raw" / "manifest.csv"
    with manifest_path.open(newline="", encoding="utf-8-sig") as handle:
        manifest = list(csv.DictReader(handle))
    sources = {row["source_id"]: row for row in source_rows}
    seen_paths: set[str] = set()
    for row in manifest:
        relative_path = row["relative_path"]
        if relative_path in seen_paths:
            raise DataValidationError(f"Duplicate manifest path: {relative_path}")
        seen_paths.add(relative_path)
        path = root / relative_path
        if not path.is_file():
            raise DataValidationError(f"Manifest file is missing: {relative_path}")
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != row["sha256"] or len(payload) != int(row["bytes"]):
            raise DataValidationError(f"Checksum mismatch: {relative_path}")
        source_id = row["source_id"]
        if source_id not in sources:
            raise DataValidationError(f"Manifest source is unregistered: {source_id}")
        if row["url"] != sources[source_id]["url"]:
            raise DataValidationError(f"Manifest URL differs for {source_id}")


def validate_project_data(root: Path) -> dict[str, list[dict[str, Any]]]:
    """Validate every declared dataset and all cross-file integrity rules."""

    dictionary = load_dictionary(root)
    if dictionary.get("schema_version") != "1.0.0":
        raise DataValidationError("Unsupported data dictionary version")
    tables = {
        relative_path: _read_and_validate_table(root, relative_path, spec)
        for relative_path, spec in dictionary["datasets"].items()
    }
    _validate_foreign_keys(dictionary, tables)
    audit = tables["data/manual/pre2021_double_entry.csv"]
    if any(row["status"] != "pass" for row in audit):
        raise DataValidationError("The pre-2021 independent audit contains failures")
    _validate_archive(root, tables["data/manual/source_register.csv"])
    return tables
