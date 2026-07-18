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
        ".gitignore",
        "README.md",
        "final_report.qmd",
        "final_report.pdf",
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
    expected_ids = [f"cell-{index:02d}" for index in range(1, len(notebook.cells) + 1)]
    actual_ids = [cell.get("id") for cell in notebook.cells]
    assert actual_ids == expected_ids, "Notebook cell IDs must be deterministic"
    assert all(cell.execution_count is not None for cell in code_cells)
    assert all("execution" not in cell.metadata for cell in code_cells), (
        "Notebook execution timing metadata must be disabled for reproducible diffs"
    )
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]
    assert not errors, f"Notebook stores {len(errors)} execution errors"


def check_citations() -> None:
    qmd = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("index.qmd", "final_report.qmd")
    )
    bib = (ROOT / "references.bib").read_text(encoding="utf-8")
    cited = set(re.findall(r"@([A-Za-z0-9_:-]+)", qmd))
    available = set(re.findall(r"@\w+\{([^,]+),", bib))
    missing = sorted(cited - available)
    assert not missing, f"Citation keys absent from references.bib: {missing}"


def check_course_submission_package() -> None:
    required_ignore_patterns = {
        "*_files/",
        "*_cache/",
        ".quarto/",
        ".quarto_preview/",
        "_freeze/",
        "*.csv",
        "*.docx",
        "*.quarto_ipynb",
        "*.quarto_ipynb_*",
    }
    ignore_lines = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing_patterns = sorted(required_ignore_patterns - ignore_lines)
    assert not missing_patterns, (
        "Course-required .gitignore patterns are missing: "
        f"{missing_patterns}"
    )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_links = {
        "[final_report.pdf](final_report.pdf)",
        "[final_report.qmd](final_report.qmd)",
    }
    missing_links = sorted(link for link in required_links if link not in readme)
    assert not missing_links, f"README is missing report links: {missing_links}"

    missing_local_links = []
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        candidate = ROOT / unquote(parsed.path)
        if not candidate.exists():
            missing_local_links.append(target)
    assert not missing_local_links, (
        f"README local links do not exist: {sorted(missing_local_links)}"
    )

    required_readme_sections = {
        "## Course submission",
        "## Member and contribution",
        "## Problem statement and objectives",
        "## Progress made",
        "## Main results",
        "## Bottlenecks and accommodations",
        "## Lessons learned",
    }
    missing_readme_sections = sorted(
        heading for heading in required_readme_sections if heading not in readme
    )
    assert not missing_readme_sections, (
        "README is missing course-required sections: "
        f"{missing_readme_sections}"
    )

    report_qmd = (ROOT / "final_report.qmd").read_text(encoding="utf-8")
    required_sections = {
        "# Problem statement and objectives",
        "# Results",
        "# Bottlenecks and accommodations",
        "# Individual contribution and lessons learned",
        "# Conclusion",
    }
    missing_sections = sorted(
        heading for heading in required_sections if heading not in report_qmd
    )
    assert not missing_sections, f"Final report is missing sections: {missing_sections}"

    active_metadata = {
        "README.md": readme,
        "final_report.qmd": report_qmd,
        "index.qmd": (ROOT / "index.qmd").read_text(encoding="utf-8"),
        "CITATION.cff": (ROOT / "CITATION.cff").read_text(encoding="utf-8"),
        "LICENSE": (ROOT / "LICENSE").read_text(encoding="utf-8"),
        "pyproject.toml": (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
    }
    forbidden_tokens = {
        "STUDENT_ID_REQUIRED",
        "ANDYLALALA",
        "YOUR_GITHUB_USERNAME",
        "YOUR_NAME",
    }
    unresolved = sorted(
        f"{name}: {token}"
        for name, text in active_metadata.items()
        for token in forbidden_tokens
        if token in text
    )
    assert not unresolved, f"Unresolved submission metadata: {unresolved}"

    assert all(
        "Yang Haoyuan" in active_metadata[name]
        for name in ("README.md", "final_report.qmd", "index.qmd", "LICENSE", "pyproject.toml")
    ), "Active project metadata must identify Yang Haoyuan consistently"
    assert 'family-names: "Yang"' in active_metadata["CITATION.cff"]
    assert 'given-names: "Haoyuan"' in active_metadata["CITATION.cff"]
    assert 'version = "1.0.0"' in active_metadata["pyproject.toml"]
    assert "version: 1.0.0" in active_metadata["CITATION.cff"]

    report_pdf = ROOT / "final_report.pdf"
    pdf_bytes = report_pdf.read_bytes()
    assert pdf_bytes.startswith(b"%PDF-"), "final_report.pdf is not a valid PDF file"
    assert len(pdf_bytes) >= 100_000, (
        "final_report.pdf is unexpectedly small; render it from final_report.qmd"
    )


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
        check_course_submission_package,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"Project integrity: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
