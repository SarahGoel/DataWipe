$ErrorActionPreference = 'Stop'

Write-Host "=== ZeroTrace Presentation Runner ===" -ForegroundColor Cyan

# Determine repository root based on this script location
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

# Locate npm.cmd (bypass PowerShell script policy)
$npmCandidates = @(
  "C:\Program Files\nodejs\npm.cmd",
  (Join-Path $env:APPDATA "npm\npm.cmd")
)
$npmPath = $npmCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $npmPath) {
  Write-Warning "npm.cmd not found. Please install Node.js LTS from https://nodejs.org and rerun."
  exit 1
}

# Build frontend (silent if already built)
Write-Host "[1/2] Building frontend (vite) ..." -ForegroundColor Yellow
Push-Location (Join-Path $repoRoot 'frontend\web')
& $npmPath run build
Pop-Location

# Start backend server (serves built frontend at http://127.0.0.1:8000)
Write-Host "[2/2] Starting backend (FastAPI) on http://127.0.0.1:8000 ..." -ForegroundColor Yellow

# Open browser after small delay
Start-Job -ScriptBlock {
  Start-Sleep -Seconds 2
  Start-Process "http://127.0.0.1:8000"
} | Out-Null

# Run uvicorn in this console
Set-Location (Join-Path $repoRoot 'backend')
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload


