# Data guide and provenance protocol

Data vintage: **2026-07-12**. All numeric files in this repository use UTF-8
CSV and keep reported values separate from derived indicators.

## Files

- `schema/datasets.json` is the executable field dictionary and data contract.
- `manual/source_register.csv` is the audit trail: publisher, title, date,
  URL, coverage, and definition warnings.
- `processed/china_auto_market_2015_2025.csv` contains annual CAAM automobile
  and NEV sales in millions of vehicles.
- `processed/nev_powertrain_sales_2020_2024.csv` separates reported NEV
  deliveries into BEV, PHEV/range-extender, and fuel-cell components.
- `processed/auto_exports_2021_2025.csv` contains CAAM/MIIT automobile and NEV
  exports in millions of vehicles.
- `processed/powertrain_mix_metrics.csv` and `processed/export_metrics.csv` are
  generated outputs; the latter labels sales-minus-exports as a residual proxy,
  not as a separately reported domestic-sales series.
- `processed/fleet_charging_snapshot.csv` contains year-end fleet and charging
  observations plus the latest charging observation available on the data
  vintage date.
- `processed/current_market_pulse.csv` keeps complete-year observations
  separate from partial-year and single-month observations.
- `processed/policy_targets.csv` records official future targets; targets are
  never treated as observations.

## Non-negotiable definition rules

1. **Sales are not registrations.** CAAM sales are industry deliveries.
   Registered fleet data come from public-security statistics.
2. **Total sales and domestic sales differ.** The 47.9% 2025 share is
   `16.49 / 34.40` using total CAAM sales. The separately reported 50.8% figure
   refers to domestic new-vehicle sales. They must not be plotted as the same
   series.
3. **NEV is broader than electric passenger cars.** China's NEV category
   includes battery electric, plug-in hybrid/range-extended, and fuel-cell
   passenger and commercial vehicles.
4. **Connectors are not stations.** NEA charging observations count charging
   facilities/connectors (often translated as charging “guns”), not sites.
5. **The charging methodology changed in 2025.** NEA introduced a new national
   reporting system and adjusted the statistical scope. Public/private monthly
   comparisons should use June 2025 onward unless a bridge is documented.
6. **NBS production is not CAAM production.** Their 2025 NEV production totals
   differ because the statistical systems differ. This project does not average
   them.
7. **Exports are enterprise-reported volumes, not customs declarations.**
   Subtracting them from CAAM industry deliveries produces a useful non-export
   residual proxy, but not an independently observed domestic retail series.

## Manual-entry protocol

Each value was transcribed from a named source, checked against the displayed
unit, converted to millions only when necessary, and assigned a source ID.
Derived values (shares, growth rates, CAGR, ratios, and gaps) are calculated in
code rather than typed into the source tables.

- `manual/pre2021_double_entry.csv` records the independent second entry for
  every 2015-2020 automobile and NEV sales observation.
- `raw/source_snapshots/` contains redistribution-safe evidence records;
  `raw/manifest.csv` pins every snapshot with a SHA-256 checksum.
