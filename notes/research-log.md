# Research log

## 2026-07-12 — Project foundation

- Replaced a vague survey-style topic with an observable automobile-market
  transition.
- Selected the central contrast: NEVs were 50.8% of domestic new-vehicle sales
  in 2025 but only 12.01% of the registered automobile fleet at year end.
- Chose a descriptive and scenario-based design. The project will not infer
  that charging facilities caused vehicle adoption.
- Recorded the 2025 charging-data methodology break and prohibited silent
  splicing of incompatible monthly series.
- Kept the latest H1 2026 market pulse separate from complete annual data.

### Next audit

On Day 2, archive source captures where redistribution permits, calculate
checksums, and independently double-check every pre-2021 chart transcription.

## 2026-07-12 — First-look verification

- All 8 unit tests passed.
- All 5 notebook code cells executed with 0 stored errors.
- Quarto rendered both the report and notebook pages to `docs/`.
- The signature dashboard was visually checked at full resolution.
- The repository contains separate commits for scaffold, source protocol, data,
  analysis, notebook, report, documentation, and CI.
- No Git remote is configured; publication remains under the author's control.

## 2026-07-14 - Pre-2021 independent double entry

- Re-entered the 2015-2020 automobile and NEV sales observations from eight
  independent government or ministry publications rather than from the two
  original CAAM historical charts.
- All 12 observations passed their declared precision tolerances.
- The only non-zero difference is the harmless rounding of 2015 automobile
  sales from 24.5976 million to the stored 24.598 million.
- The complete comparison is stored in `data/manual/pre2021_double_entry.csv`;
  the verification URLs have distinct source IDs in the source register.


## 2026-07-14 - Powertrain composition and exports

- Added a 2020-2024 BEV/PHEV/FCEV composition series from MIIT, CAAM, and NBS
  annual industry releases. Published component sums reconcile to total NEV
  deliveries within 0.001 million vehicles.
- Deliberately stopped the composition series at 2024 because a consistent,
  independently verifiable 2025 component split was not established.
- Added 2021-2025 total automobile and NEV export volumes. These are
  enterprise-reported industry exports, not customs declarations.
- Labelled sales minus exports as a non-export residual proxy. It cross-checks
  the reported 2025 domestic share but is not presented as a retail measure.
- Archived evidence notes and regenerated SHA-256 checksums before analysis.

## 2026-07-14 - Fleet-turnover model

- Anchored the model to end-2025 registered stock and the 2025 non-export
  residual inflow proxy; future rows are explicitly labelled as scenarios.
- Held annual domestic inflow constant and varied total fleet turnover from
  5.5% to 7.0% to expose sensitivity rather than imply false precision.
- Used a 0.25 relative NEV retirement-allocation weight because the current NEV
  stock is younger than the non-NEV stock.
- Added component and total stock-flow accounting tests for all 30 scenario
  rows.
- Fitted a log-odds trend only through 2022 and recorded a 5.34 percentage-point
  MAE on 2023-2025; all held-out predictions were below the observations.
