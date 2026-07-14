$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    Write-Host "`n==> $Label"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Run scripts/bootstrap.ps1 for setup instructions."
}
if (-not (Get-Command quarto -ErrorAction SilentlyContinue)) {
    throw "Quarto is required to render the site."
}

Invoke-Step "Sync locked Python environment" {
    uv sync --frozen --python 3.12
}
Invoke-Step "Rebuild data products and figures" {
    uv run --frozen python scripts/build_analysis.py
}
Invoke-Step "Regenerate notebook source" {
    uv run --frozen python scripts/build_notebook.py
}
Invoke-Step "Execute notebook" {
    uv run --frozen python -m nbconvert --to notebook --execute --inplace `
        notebooks/01_exploration.ipynb --ExecutePreprocessor.timeout=120
}
Invoke-Step "Run unit and schema tests" {
    uv run --frozen python -m unittest discover -s tests -v
}
Invoke-Step "Render Quarto site" {
    quarto render
}
Invoke-Step "Validate project and rendered outputs" {
    uv run --frozen python scripts/validate_project.py
}

Write-Host "`nClean rebuild completed successfully."
