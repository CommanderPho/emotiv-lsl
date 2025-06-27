#!/usr/bin/env powershell

# Direct Windows Terminal launcher for Emotiv LSL
$currentDir = Get-Location

# Activate the lsl_env environment and run the bsl_stream_viewer
try {
    Write-Host "Activating lsl_env environment and starting bsl_stream_viewer..." -ForegroundColor Cyan
    micromamba activate lsl_env; bsl_stream_viewer
}
catch {
    Write-Host "Failed to run the application. Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure micromamba is installed and lsl_env environment exists." -ForegroundColor Yellow
}
