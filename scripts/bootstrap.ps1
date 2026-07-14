$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/"
}

Write-Host "Creating the locked Python 3.12 environment..."
uv sync --frozen --python 3.12
if ($LASTEXITCODE -ne 0) {
    throw "uv sync failed with exit code $LASTEXITCODE"
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"
& $Python -c "import matplotlib, nbclient, nbformat, numpy, pandas; print('Python environment ready'); print('pandas', pandas.__version__); print('numpy', numpy.__version__); print('matplotlib', matplotlib.__version__)"
if ($LASTEXITCODE -ne 0) {
    throw "Dependency import check failed with exit code $LASTEXITCODE"
}

if (Get-Command quarto -ErrorAction SilentlyContinue) {
    Write-Host "Quarto $(quarto --version) is available."
} else {
    Write-Warning "Python is ready, but Quarto is not on PATH; site rendering will be unavailable."
}
