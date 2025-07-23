#!/usr/bin/env powershell

# Direct launcher for Emotiv LSL
Write-Host "Launching Emotiv LSL components..." -ForegroundColor Green

# Get the absolute path to the repository root directory
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot

# Function to create a new PowerShell window with a command
function Start-CommandWindow {
    param (
        [string]$Title,
        [string]$Command
    )
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", 
        "Write-Host 'Starting $Title...' -ForegroundColor Cyan; $Command" -WindowStyle Normal
}

# Launch the server component
Write-Host "Starting LSL Server..." -ForegroundColor Cyan
Start-CommandWindow -Title "LSL Server" -Command "cd '$repoRoot'; micromamba activate lsl_env; python '$repoRoot\main.py'"

# Wait a moment for the server to initialize
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Launch the viewer component
Write-Host "Starting BSL Viewer..." -ForegroundColor Cyan
Start-CommandWindow -Title "BSL Viewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --dir '\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings - Any\EEG Recordings - Dropbox\EmotivEpocX_EEGRecordings'"

Write-Host "All components launched successfully!" -ForegroundColor Green
