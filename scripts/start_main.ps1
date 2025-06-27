#!/usr/bin/env powershell

# Direct Windows Terminal launcher for Emotiv LSL
$currentDir = Get-Location

# Activate the lsl_env environment and run the main.py script
try {
    Write-Host "Activating lsl_env environment and starting main.py..." -ForegroundColor Cyan
    micromamba activate lsl_env
    python main.py
}
catch {
    Write-Host "Failed to run the application. Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure micromamba is installed and lsl_env environment exists." -ForegroundColor Yellow
}
