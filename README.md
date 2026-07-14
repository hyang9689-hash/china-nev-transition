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

Python 3.12 is the reference version. Quarto is required only for the website.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/build_analysis.py
python scripts/build_notebook.py
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_exploration.ipynb
python -m unittest discover -s tests -v
quarto render
python scripts/validate_project.py
```

On macOS or Linux, activate with `source .venv/bin/activate`.

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

No remote has been added and nothing has been uploaded. Replace the author and
GitHub username placeholders, then follow `GITHUB_PUBLISHING.md`. The included
workflow tests the analysis, renders Quarto, and can deploy the `docs/` artifact
through GitHub Pages after you enable Pages in the repository settings.

## License and citation

Code is released under the MIT License. Source data retain their original terms
and attribution. Update `CITATION.cff` with your name and final repository URL
before the first public release.
