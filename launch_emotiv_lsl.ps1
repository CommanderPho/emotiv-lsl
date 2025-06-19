#!/usr/bin/env powershell

# PowerShell script to launch Emotiv LSL server and viewer in separate terminals
# Usage: .\launch_emotiv_lsl.ps1

Write-Host "Launching Emotiv LSL Server and Viewer..." -ForegroundColor Green

# Get the current directory (should be the emotiv-lsl directory)
$currentDir = Get-Location

# Check if Windows Terminal is available
$wtAvailable = Get-Command "wt" -ErrorAction SilentlyContinue

if ($wtAvailable) {
    Write-Host "Using Windows Terminal..." -ForegroundColor Yellow
    
    # Launch Windows Terminal with two tabs
    # Tab 1: LSL Server
    # Tab 2: BSL Stream Viewer
    Start-Process "wt" -ArgumentList @(
        "--window", "0",
        "new-tab", "--title", "LSL Server", "powershell", "-NoExit", "-Command", 
        "cd '$currentDir'; micromamba activate lsl_env; python main.py",
        ";",
        "new-tab", "--title", "BSL Viewer", "powershell", "-NoExit", "-Command",
        "cd '$currentDir'; micromamba activate lsl_env; Start-Sleep -Seconds 3; bsl_stream_viewer"
    )
} else {
    Write-Host "Windows Terminal not found. Using separate PowerShell windows..." -ForegroundColor Yellow
    
    # Launch LSL Server in first PowerShell window
    Start-Process "powershell" -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$currentDir'; Write-Host 'Starting LSL Server...' -ForegroundColor Green; micromamba activate lsl_env; python main.py"
    ) -WorkingDirectory $currentDir
    
    # Wait a moment for the server to start
    Start-Sleep -Seconds 2
    
    # Launch BSL Stream Viewer in second PowerShell window
    Start-Process "powershell" -ArgumentList @(
        "-NoExit", 
        "-Command",
        "Set-Location '$currentDir'; Write-Host 'Starting BSL Stream Viewer...' -ForegroundColor Blue; micromamba activate lsl_env; Start-Sleep -Seconds 3; bsl_stream_viewer"
    ) -WorkingDirectory $currentDir
}

Write-Host "Launched Emotiv LSL components!" -ForegroundColor Green
Write-Host "Server window: Running 'python main.py'" -ForegroundColor Cyan
Write-Host "Viewer window: Running 'bsl_stream_viewer'" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Make sure your Emotiv headset is connected and powered on." -ForegroundColor Yellow
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")