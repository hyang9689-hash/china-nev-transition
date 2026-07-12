# Contributing

This is a data-first research repository. A correct-looking chart is not enough;
definitions and provenance must survive review.

## Before changing data

1. Read `data/README.md`.
2. Add or update the source in `data/manual/source_register.csv`.
3. Preserve the publisher's original unit and definition in your notes.
4. Keep observations separate from calculated indicators.
5. Record methodology breaks explicitly.
6. Rebuild the analysis and run all tests.

## Verification commands

```bash
python scripts/build_analysis.py
python -m unittest discover -s tests -v
quarto render
```

If the notebook source changes, regenerate and execute it before committing.

## Commit subjects

Use an imperative subject with a narrow type, for example:

```text
data: add June 2025 charging methodology baseline
analysis: calculate public connector power growth
docs: explain domestic and total sales denominators
test: reject duplicate annual observations
```

Do not combine unrelated research, data, analysis, and formatting changes in a
single commit.

