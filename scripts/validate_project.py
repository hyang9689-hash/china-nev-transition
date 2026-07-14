"""Run cross-file integrity checks that unit tests alone cannot cover."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT))

from src.data_validation import validate_project_data  # noqa: E402


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        for name in ("href", "src"):
            value = attr_map.get(name)
            if value:
                self.references.add(value)


def check_required_files() -> None:
    required = [
        "README.md",
        "index.qmd",
        "references.bib",
        "notebooks/01_exploration.ipynb",
        "data/manual/source_register.csv",
        "figures/first_look_dashboard.png",
        "docs/index.html",
        "docs/notebooks/01_exploration.html",
        "data/schema/datasets.json",
        "data/manual/pre2021_double_entry.csv",
        "data/raw/manifest.csv",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    assert not missing, f"Missing required files: {missing}"


def check_data_contract() -> None:
    validate_project_data(ROOT)


def check_source_ids() -> None:
    register = pd.read_csv(DATA / "manual" / "source_register.csv")
    assert register["source_id"].is_unique, "Source-register IDs must be unique"
    known = set(register["source_id"])
    used: set[str] = set()
    for csv_path in (DATA / "processed").glob("*.csv"):
        frame = pd.read_csv(csv_path)
        for column in frame.columns:
            if column == "source_id" or column.endswith("_source_id"):
                used.update(frame[column].dropna().astype(str).loc[lambda s: s.ne("")])
    unknown = sorted(used - known)
    assert not unknown, f"Unregistered source IDs: {unknown}"


def check_annual_series() -> None:
    annual = pd.read_csv(DATA / "processed" / "china_auto_market_2015_2025.csv")
    assert annual["year"].tolist() == list(range(2015, 2026))
    assert annual["year"].is_unique
    assert (annual[["total_auto_sales_m", "nev_sales_m"]] > 0).all().all()
    assert (annual["nev_sales_m"] <= annual["total_auto_sales_m"]).all()


def check_notebook() -> None:
    notebook = nbformat.read(ROOT / "notebooks" / "01_exploration.ipynb", as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert code_cells, "Notebook must contain code cells"
    assert all(cell.execution_count is not None for cell in code_cells)
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]
    assert not errors, f"Notebook stores {len(errors)} execution errors"


def check_citations() -> None:
    qmd = (ROOT / "index.qmd").read_text(encoding="utf-8")
    bib = (ROOT / "references.bib").read_text(encoding="utf-8")
    cited = set(re.findall(r"@([A-Za-z0-9_:-]+)", qmd))
    available = set(re.findall(r"@\w+\{([^,]+),", bib))
    missing = sorted(cited - available)
    assert not missing, f"Citation keys absent from references.bib: {missing}"


def check_rendered_links() -> None:
    missing: list[str] = []
    for html_path in [DOCS / "index.html", DOCS / "notebooks" / "01_exploration.html"]:
        parser = AssetParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local_path = unquote(parsed.path)
            if local_path.startswith("/"):
                candidate = DOCS / local_path.lstrip("/")
            else:
                candidate = html_path.parent / local_path
            if not candidate.exists():
                missing.append(f"{html_path.relative_to(ROOT)} -> {reference}")
    assert not missing, "Missing rendered assets:\n" + "\n".join(sorted(missing))


def main() -> None:
    checks = [
        check_required_files,
        check_data_contract,
        check_source_ids,
        check_annual_series,
        check_notebook,
        check_citations,
        check_rendered_links,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"Project integrity: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()

