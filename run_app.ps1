<#
.SYNOPSIS
    Personal Finance Advisor Bot - PowerShell Browser Launcher
.DESCRIPTION
    Activates python environment if present, runs the server, and opens default browser.
#>

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "            Personal Finance Advisor Bot - Browser Launcher           " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Activate virtual environment if present
if (Test-Path "$ScriptDir\venv\Scripts\Activate.ps1") {
    Write-Host "[OK] Activating virtual environment (venv)..." -ForegroundColor Green
    & "$ScriptDir\venv\Scripts\Activate.ps1"
} elseif (Test-Path "$ScriptDir\.venv\Scripts\Activate.ps1") {
    Write-Host "[OK] Activating virtual environment (.venv)..." -ForegroundColor Green
    & "$ScriptDir\.venv\Scripts\Activate.ps1"
}

# 2. Run the Python launcher
Write-Host "[OK] Launching Flask server and opening your default browser..." -ForegroundColor Green
python run_app.py
