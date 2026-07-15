# Past the Tipping Point, Not Yet Transformed

**China's NEV sales, fleet, and charging transition, 2015–2026**

![First-look dashboard](figures/first_look_dashboard.png)

China's new-energy vehicle transition has crossed the domestic new-sales
tipping point, but it has not yet transformed the vehicles already on the road.
In 2025, NEVs were **50.8% of domestic new-vehicle sales** and only **12.0% of
the registered automobile fleet**. That 38.8 percentage-point flow–stock gap is
the project's central story.

## Open these first

- **Rendered report:** `docs/index.html`
- **Quarto source:** `index.qmd`
- **Executed notebook:** `notebooks/01_exploration.ipynb`
- **Bibliography:** `references.bib`
- **Source audit trail:** `data/manual/source_register.csv`
- **Roadmap:** `PROJECT_ROADMAP.md`

## Research question

How quickly is China's dominance of new-energy vehicles in new-vehicle sales
translating into the on-road fleet, and has charging infrastructure kept pace?

The work is descriptive and scenario-based. It does not claim that charging
construction caused adoption.

## First results

- NEV sales grew from 0.331 million in 2015 to 16.490 million in 2025: a
  **47.8% compound annual growth rate**.
- The NEV share of total CAAM automobile sales rose from 1.3% to 47.9%.
- NEVs produced **122.3% of total net market growth in 2025** because estimated
  non-NEV sales fell by 0.66 million vehicles.
- China had 20.092 million charging connectors at end-2025; 76.5% were private.
- By May 2026, 22.497 million connectors equaled 80.3% of the official end-2027
  target of at least 28 million.
- PHEV/range-extender share of NEV deliveries rose from 18.4% in 2020 to 40.0%
  in 2024.
- NEVs reached 36.8% of automobile exports in 2025; sales minus exports
  independently reproduces the reported 50.8% domestic-share result as a proxy.
- The fleet-turnover sensitivities place the 2035 NEV fleet share between 50.2%
  and 63.3%; the bounded sales-share backtest has a 5.34 percentage-point MAE.

These claims, their formulas, and their definition limits are documented in the
report and notebook. The 2025 charging methodology break is marked rather than
hidden.

## Repository map

```text
china-nev-transition/
├── README.md                   # Project front door
├── index.qmd                   # Cited Quarto report
├── references.bib              # BibTeX references
├── _quarto.yml                 # Website configuration
├── notebooks/
│   └── 01_exploration.ipynb    # Executed Python analysis
├── data/
│   ├── README.md               # Definition and provenance rules
│   ├── manual/source_register.csv
│   └── processed/              # Inputs and code-derived outputs
├── src/
│   ├── metrics.py              # Share, growth, CAGR, and ratio formulas
│   └── scenarios.py            # Bounded log-odds scenarios
├── scripts/
│   ├── build_analysis.py       # Tables and figures
│   └── build_notebook.py       # Notebook cell source
├── tests/                      # Standard-library unit tests
├── figures/                    # Rebuilt analysis figures
├── docs/                       # Rendered GitHub Pages site
├── notes/research-log.md       # Dated analytical decisions
└── .github/workflows/          # Test and Pages publication workflow
```

## Reproduce locally

Python 3.12 and Quarto are the reference tools. The canonical Python
environment is `pyproject.toml` plus `uv.lock`; `requirements.txt` remains
as a compatibility list for tools that only support pip.

On Windows, install uv and run:

```powershell
.scriptsootstrap.ps1
```

The bootstrap creates `.venv`, installs the exact locked packages, and verifies
pandas, NumPy, Matplotlib, and the notebook libraries. No activation is needed.

For a complete rebuild and verification:

```powershell
.scriptsebuild.ps1
```

The equivalent cross-platform sequence is:

```bash
uv sync --frozen --python 3.12
uv run --frozen python scripts/build_analysis.py
uv run --frozen python scripts/build_notebook.py
uv run --frozen python -m nbconvert --to notebook --execute --inplace notebooks/01_exploration.ipynb --ExecutePreprocessor.timeout=120
uv run --frozen python -m unittest discover -s tests -v
quarto render
uv run --frozen python scripts/validate_project.py
```

Use `python -m nbconvert` inside the locked environment. On systems with another
global Jupyter installation, `python -m jupyter nbconvert` can select the wrong
kernel and miss project packages such as pandas.

## Data discipline

- Sales, production, exports, registrations, and fleet stock remain separate.
- Total-sales share and domestic-sales share remain separate.
- NEV and internationally defined electric passenger cars remain separate.
- Charging connectors and charging stations remain separate.
- Reported observations and calculated indicators remain separate.
- The revised NEA charging series is not silently spliced to the old scope.

Read `data/README.md` before adding or changing a value.

## Git history

The repository was built through real commits rather than one final file dump.
Inspect the complete trace with:

```bash
git log --oneline --decorate --graph --all
```

Commit subjects follow a simple convention: `chore`, `docs`, `data`,
`analysis`, `test`, `ci`, and `release`.

## Publication

The canonical repository is [`hyang9689-hash/china-nev-transition`](https://github.com/hyang9689-hash/china-nev-transition),
with the site targeted at
[`hyang9689-hash.github.io/china-nev-transition`](https://hyang9689-hash.github.io/china-nev-transition/).
GitHub Actions rebuilds the analysis and notebook, runs the full test suite,
renders Quarto, validates the artifacts, and deploys GitHub Pages. The exact
submission commands, milestone commits, workflow run, and live-site verification
are recorded in `PUBLICATION_LOG.md`.

## License and citation

Code is released under the MIT License. Source data retain their original terms
and attribution. Citation metadata identify **ANDYLALALA**, version **0.2.0**,
and the canonical repository and site URLs in `CITATION.cff`.
