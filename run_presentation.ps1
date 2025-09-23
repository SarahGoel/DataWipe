$ErrorActionPreference = 'Stop'

Write-Host "=== ZeroTrace Presentation Runner ===" -ForegroundColor Cyan

# Determine repository root based on this script location
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

# Resolve Python
$pythonCmd = $null
try {
  $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
} catch {}
if (-not $pythonCmd) {
  try {
    $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue).Source
  } catch {}
}
if (-not $pythonCmd) {
  Write-Warning "Python not found. Install Python 3 (winget install -e --id Python.Python.3) and rerun."
  exit 1
}

# Resolve npm (prefer absolute npm.cmd if available)
$npmCandidates = @(
  "C:\Program Files\nodejs\npm.cmd",
  (Join-Path $env:APPDATA "npm\npm.cmd")
)
$npmPath = $npmCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $npmPath) {
  try {
    $npmPath = (Get-Command npm -ErrorAction SilentlyContinue).Source
  } catch {}
}
if (-not $npmPath) {
  Write-Warning "npm not found. Please install Node.js LTS from https://nodejs.org and rerun."
  exit 1
}

# Install Python dependencies (root requirements)
Write-Host "[0/3] Installing Python dependencies ..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip
& $pythonCmd -m pip install -r (Join-Path $repoRoot 'requirements.txt')

# Build frontend (vite)
Write-Host "[1/3] Building frontend (vite) ..." -ForegroundColor Yellow
Push-Location (Join-Path $repoRoot 'frontend\web')
& $npmPath install
& $npmPath run build
# Verify build output exists
$distIndex = Join-Path (Join-Path $repoRoot 'frontend\web\dist') 'index.html'
if (-not (Test-Path $distIndex)) {
  Write-Warning "Vite build did not produce dist/index.html. Retrying clean build..."
  # Clean and rebuild
  if (Test-Path (Join-Path $repoRoot 'frontend\web\dist')) { Remove-Item -Recurse -Force (Join-Path $repoRoot 'frontend\web\dist') }
  & $npmPath run build
}
if (-not (Test-Path $distIndex)) {
  Pop-Location
  Write-Error "Frontend build missing at $distIndex. Please review build errors above."
  exit 1
}
Pop-Location

# Start backend server (serves built frontend at http://127.0.0.1:8000)
Write-Host "[2/3] Starting backend (FastAPI) on http://127.0.0.1:8000 ..." -ForegroundColor Yellow

# Open browser after small delay
Start-Job -ScriptBlock {
  Start-Sleep -Seconds 2
  Start-Process "http://127.0.0.1:8000"
} | Out-Null

# Run uvicorn in this console
Write-Host "[3/3] Backend logs:" -ForegroundColor Yellow
Set-Location (Join-Path $repoRoot 'backend')
if ($pythonCmd -like '*py.exe') {
  & $pythonCmd -3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
} else {
  & $pythonCmd -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
}


