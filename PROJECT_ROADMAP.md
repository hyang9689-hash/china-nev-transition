# Project roadmap

The repository already contains a complete first-look vertical slice: source
register, annual data, Python math, figures, executed notebook, Quarto report,
tests, rendered site, and Git history. The next milestones deepen the evidence
rather than change the question.

## Day 1 - Foundation and first look (complete)

- Define the question and non-causal scope.
- Build the folder and traceable Git history.
- Add annual sales, fleet, charging, and current-pulse tables.
- Produce the signature flow–stock dashboard.
- Create and execute the notebook.
- Render the cited Quarto website.

Exit test: a new reader can understand the argument in five minutes and trace
every headline value to a source ID.

## Day 2 - Source acquisition and double entry (complete)

- Independently re-enter all pre-2021 CAAM chart values.
- Archive source captures where licensing permits.
- Add SHA-256 checksums and a raw-file manifest.
- Record correction rules rather than overwriting silently.

Exit test: every manually transcribed number has two checks.

## Day 3 - Data audit and definitions (complete)

- Add schema tests for years, units, nulls, uniqueness, and ranges.
- Reconcile civilian-vehicle and registered-automobile denominators.
- Add a machine-readable data dictionary.
- Label reported versus derived fields in every table.

Exit test: a definition mismatch fails loudly.

## Day 4 - Historical market analysis (complete)

- Add BEV, PHEV/range-extender, and fuel-cell composition.
- Identify structural break candidates without overclaiming causality.
- Add accessible figures and audited descriptive tables.

Exit test: the report explains both market scale and technology mix.

## Day 5 - Fleet and charging module

- Build the consistent monthly charging series from June 2025 onward.
- Compare public/private connector growth and rated power.
- Add fleet-to-connector ratios with sensitivity to the denominator.

Exit test: no old-scope/new-scope splice remains in an analytical series.

## Day 6 - Export module (complete)

- Separate total, domestic, and export deliveries.
- Calculate the NEV share of exports and export contribution to growth.
- Add destination data only if a stable official source is available.

Exit test: domestic adoption and export expansion cannot be confused.

## Day 7 - Scenarios and validation (complete)

- Fit only models that remain bounded between 0% and 100%.
- Train through 2022; report 2023–2025 mean absolute error.
- Add conservative, baseline, and faster fleet-turnover assumptions.
- Report sensitivity, not false precision.

Exit test: every scenario has explicit assumptions and an out-of-sample check.

## Day 8 - Quality and clean rebuild (complete)

- [x] Run tests in a fresh Python environment.
- [x] Execute the notebook from top to bottom.
- [x] Render the website and final PDF from source.
- [x] Check links, citations, metadata, PDF boundaries, and embedded fonts.

Exit test: passed on 2026-07-18; one documented command rebuilt all public
outputs and passed 20 tests plus 8 project-integrity checks.

## Day 9 - Publication candidate

- [x] Finalize author, citation, and canonical repository metadata.
- [x] Create the GitHub repository and push `main`.
- [x] Enable GitHub Pages from Actions.
- [x] Verify the public report, notebook, figures, links, and HTTPS responses.

Exit test: passed on 2026-07-15 with a clean public URL and green workflow run.

## Day 10 - Version 1.0 course release (complete)

- [x] Freeze the data vintage and update the changelog.
- [x] Add final limitations and reproducibility statements.
- [x] Add the root QMD/PDF course report and automated submission checks.
- [x] Prepare the annotated `v1.0.0` tag for the final verified commit.

Exit test: passed on 2026-07-18; the 1.0.0 course package can be cited and
reproduced independently from the repository.

