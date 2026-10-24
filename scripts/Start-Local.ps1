param(
    [ValidateSet('WebUI', 'API')]
    [string]$Service = 'WebUI'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw 'Project environment missing. Run python -m uv sync --frozen --python 3.12 --all-extras from the project root.'
}
if (-not (Test-Path (Join-Path $root 'config.toml'))) {
    throw 'Local configuration missing. Run .\.venv\Scripts\python.exe .\scripts\configure_windows.py first.'
}

$env:PYTHONUTF8 = '1'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
Push-Location $root
try {
    if ($Service -eq 'API') {
        & $python main.py
    } else {
        & $python -m streamlit run .\webui\Main.py `
            --server.address=127.0.0.1 --server.port=8501 `
            --server.headless=true --browser.gatherUsageStats=false
    }
    if ($LASTEXITCODE -ne 0) {
        throw "$Service exited with code $LASTEXITCODE."
    }
} finally {
    Pop-Location
}
