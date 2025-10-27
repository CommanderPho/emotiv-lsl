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

# Launch the viewer component
Write-Host "Starting BSL Viewers..." -ForegroundColor Cyan
# Start-CommandWindow -Title "BSL EEG Viewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --stream_name 'Epoc X' --record_dir '\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings - Any\EEG Recordings - Dropbox\EmotivEpocX_EEGRecordings' --bp_low 1.0 --bp_high 58.0;"
# Start-CommandWindow -Title "BSL MotionViewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --stream_name 'Epoc X Motion' --record_dir '//vmware-host/Shared Folders/Emotiv Epoc EEG Project/EEG Recordings - Any/EEG Recordings - Dropbox/EmotivEpocX_EEGRecordings/MOTION_RECORDINGS' --bp_off;"

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


# Activate the lsl_env environment and run the bsl_stream_viewer
try {
    Write-Host "Activating lsl_env environment and starting bsl_stream_viewer..." -ForegroundColor Cyan
    Start-CommandWindow -Title "BSL EEG Viewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --stream_name 'Epoc X' --record_dir '$record_dir' --bp_low 1.0 --bp_high 58.0;"
    Start-CommandWindow -Title "BSL MotionViewer" -Command "cd '$repoRoot'; micromamba activate lsl_env; bsl_stream_viewer --stream_name 'Epoc X Motion' --record_dir '$record_dir/MOTION_RECORDINGS' --bp_off --CAR_off;"

    Write-Host "All components launched successfully!" -ForegroundColor Green

}
catch {
    Write-Host "Failed to run the application. Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure micromamba is installed and lsl_env environment exists." -ForegroundColor Yellow
}

