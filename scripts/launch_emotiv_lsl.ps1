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

# Load helpers
. "$PSScriptRoot\helpers.ps1"

# Resolve activation command (prefers local .venv; falls back to micromamba)
$activation = Get-PythonEnvActivationCommand -RepoRoot $repoRoot

# Function to create a new PowerShell window with a command
function Start-CommandWindow {
    param (
        [string]$Title,
        [string]$Command
    )
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", 
        "Write-Host 'Starting $Title...' -ForegroundColor Cyan; $Command" -WindowStyle Normal
}

## Check which of the record_dir's exist on the current computer, and choose that one:
# Define possible recording directories
$possible_record_dirs = @(
    "E:\Dropbox (Personal)\Databases\UnparsedData\EmotivEpocX_EEGRecordings",
    "\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings - Any\EEG Recordings - Dropbox\EmotivEpocX_EEGRecordings"
)

# Pick the first existing directory
$record_dir = $possible_record_dirs | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $record_dir) {
    Write-Host "⚠️  No valid recording directory found!" -ForegroundColor Red
    exit 1
}

Write-Host "Using record directory: $record_dir" -ForegroundColor Yellow


# Launch the server component
Write-Host "Starting LSL Server..." -ForegroundColor Cyan
Start-CommandWindow -Title "LSL Server" -Command "cd '$repoRoot'; $activation; python '$repoRoot\main.py'"

# Wait a moment for the server to initialize
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Launch the viewer component
Write-Host "Starting BSL Viewers..." -ForegroundColor Cyan
# Start-CommandWindow -Title "BSL EEG Viewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --stream_name 'Epoc X' --record_dir '\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings - Any\EEG Recordings - Dropbox\EmotivEpocX_EEGRecordings' --bp_low 1.0 --bp_high 58.0;"
# Start-CommandWindow -Title "BSL MotionViewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --stream_name 'Epoc X Motion' --record_dir '//vmware-host/Shared Folders/Emotiv Epoc EEG Project/EEG Recordings - Any/EEG Recordings - Dropbox/EmotivEpocX_EEGRecordings/MOTION_RECORDINGS' --bp_off;"

Start-CommandWindow -Title "BSL EEG Viewer" -Command "cd '$repoRoot'; $activation; bsl_stream_viewer --stream_name 'Epoc X' --record_dir '$record_dir' --bp_low 1.0 --bp_high 58.0;"
Start-CommandWindow -Title "BSL MotionViewer" -Command "cd '$repoRoot'; $activation; bsl_stream_viewer --stream_name 'Epoc X Motion' --record_dir '$record_dir/MOTION_RECORDINGS' --bp_off --CAR_off;"

Write-Host "All components launched successfully!" -ForegroundColor Green
