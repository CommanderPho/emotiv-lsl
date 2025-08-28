#!/usr/bin/env powershell

# Direct launcher for Emotiv LSL
Write-Host "Launching Emotiv LSL components..." -ForegroundColor Green

Write-Host "Stopping Official Emotiv services..." -ForegroundColor Yellow
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
# Start-Process powershell -Verb RunAs
Stop-Service -Name "Emotiv*" -Verbose

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
Write-Host "Starting BSL Recorders..." -ForegroundColor Cyan
Start-CommandWindow -Title "BSL EEG Recorder" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_recorder --stream_name 'Epoc X' -d '\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings - Any\EEG Recordings - Dropbox\EmotivEpocX_EEGRecordings';"
Start-CommandWindow -Title "BSL MotionRecorder" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_recorder --stream_name 'Epoc X Motion' -d '//vmware-host/Shared Folders/Emotiv Epoc EEG Project/EEG Recordings - Any/EEG Recordings - Dropbox/EmotivEpocX_EEGRecordings/MOTION_RECORDINGS';"

Write-Host "All components launched successfully!" -ForegroundColor Green
