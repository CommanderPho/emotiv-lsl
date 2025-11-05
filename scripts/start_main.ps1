#!/usr/bin/env powershell

# Direct Windows Terminal launcher for Emotiv LSL
$currentDir = Get-Location

# Direct launcher for Emotiv LSL
Write-Host "Launching Emotiv LSL components..." -ForegroundColor Green

Write-Host "Stopping Official Emotiv services..." -ForegroundColor Yellow
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
# Start-Process powershell -Verb RunAs
Stop-Service -Name "Emotiv*" -Verbose

# Get the absolute path to the repository root directory
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot


# Load helpers
. "$PSScriptRoot\helpers.ps1"

# Resolve activation command (prefers local .venv; falls back to micromamba)
$activation = Get-PythonEnvActivationCommand -RepoRoot $repoRoot

# Launch the server component
# Write-Host "Starting LSL Server..." -ForegroundColor Cyan
# Start-CommandWindow -Title "LSL Server" -Command "cd '$repoRoot'; $activation; python '$repoRoot\main.py'"


# Activate the lsl_env environment and run the main.py script
try {
    Write-Host "Activating Python environment and starting main.py..." -ForegroundColor Cyan
    Invoke-Expression $activation
    python main.py
}
catch {
    Write-Host "Failed to run the application. Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure correct Python environment is being activated (and if using mamba, that micromamba is installed and lsl_env environment exists)." -ForegroundColor Yellow
}
