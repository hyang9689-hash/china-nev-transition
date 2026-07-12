# Data guide and provenance protocol

Data vintage: **2026-07-12**. All numeric files in this repository use UTF-8
CSV and keep reported values separate from derived indicators.

## Files

- `manual/source_register.csv` is the audit trail: publisher, title, date,
  URL, coverage, and definition warnings.
- `processed/china_auto_market_2015_2025.csv` contains annual CAAM automobile
  and NEV sales in millions of vehicles.
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

## Manual-entry protocol

Each value was transcribed from a named source, checked against the displayed
unit, converted to millions only when necessary, and assigned a source ID.
Derived values (shares, growth rates, CAGR, ratios, and gaps) are calculated in
code rather than typed into the source tables.

