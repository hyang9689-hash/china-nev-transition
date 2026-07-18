# Changelog

All notable changes are documented here. Dates use ISO 8601.

## [Unreleased]

### Planned

- Build a consistent monthly charging series from June 2025 onward.
- Add destination-level export data only if a stable official series is found.
- Replace aggregate turnover sensitivities with age-cohort survival modeling
  when suitable registration cohorts become available.

## [1.0.0] - 2026-07-18

### Added

- Root `final_report.qmd` and rendered `final_report.pdf` aligned to the
  SUM26001 final-report rubric.
- Submission-package validation for required files, README links, ignore rules,
  report sections, citations, PDF integrity, and unresolved student metadata.
- Final PDF rendering in the one-command rebuild and GitHub Actions workflow.

### Changed

- Standardized public authorship as Yang Haoyuan (杨皓元).
- Expanded the README with project evolution, objectives, progress,
  bottlenecks, lessons, member information, and report links.
- Prepared the repository metadata for the final 1.0.0 course release.
- Pinned Quarto 1.9.38 and made notebook cell/table IDs and execution metadata
  deterministic across repeated local and CI rebuilds.

## [0.2.0] - 2026-07-15

### Added

- Independent double-entry audit of all 2015-2020 manual sales values.
- Redistribution-safe source evidence archive with SHA-256 checksums.
- Machine-readable contracts for 11 source, assumption, and output datasets.
- BEV/PHEV/FCEV composition and 2021-2025 automobile export analysis.
- Transparent 2026-2035 fleet-turnover sensitivities and accounting tests.
- Held-out 2023-2025 log-odds backtest with reported absolute errors.
- Locked Python 3.12 environment, bootstrap script, and clean-rebuild command.

### Changed

- Expanded the report, figures, and executed notebook for the new modules.
- Aligned local and GitHub Actions builds on the same uv lockfile.
- Replaced publication placeholders with the verified GitHub identity.
- Removed accidental root-level README render artifacts.

### Verified

- Twenty unit, schema, reconciliation, and stock-flow tests pass.
- The expanded notebook contains seven executed code cells and no stored errors.

## [0.1.0] — 2026-07-12

### Added

- Reproducible project scaffold and source protocol.
- CAAM annual automobile and NEV sales series for 2015–2025.
- Official 2024–2026 fleet, charging, target, and current-pulse snapshots.
- Reusable Python metrics and bounded scenario functions.
- Standard-library unit tests.
- Executed Jupyter notebook with formulas, tables, and figures.
- Cited Quarto report and rendered HTML website.
- GitHub Pages test-and-publication workflow.

### Methodology

- Separated domestic share, total CAAM share, registrations, and fleet stock.
- Marked the 2025 NEA charging scope break and used the official reported YoY
  rate instead of calculating across incompatible endpoints.
