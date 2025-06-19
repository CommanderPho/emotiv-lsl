#!/usr/bin/env powershell

# Direct Windows Terminal launcher for Emotiv LSL
Write-Host "Launching Emotiv LSL in Windows Terminal..." -ForegroundColor Green

$currentDir = Get-Location

# Force launch Windows Terminal directly
try {
    # Method 1: Try using Windows Terminal via Windows Apps
    $command = "wt --window 0 new-tab --title `"LSL Server`" powershell -NoExit -Command `"cd '$currentDir'; micromamba activate lsl_env; python main.py`" ; new-tab --title `"BSL Viewer`" powershell -NoExit -Command `"cd '$currentDir'; micromamba activate lsl_env; Start-Sleep 5; bsl_stream_viewer`""
    
    Invoke-Expression $command
    Write-Host "Successfully launched Windows Terminal!" -ForegroundColor Green
}
catch {
    Write-Host "Method 1 failed, trying alternative..." -ForegroundColor Yellow
    
    try {
        # Method 2: Direct execution
        & "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe" --window 0 new-tab --title "LSL Server" powershell -NoExit -Command "cd '$currentDir'; micromamba activate lsl_env; python main.py" `; new-tab --title "BSL Viewer" powershell -NoExit -Command "cd '$currentDir'; micromamba activate lsl_env; Start-Sleep 5; bsl_stream_viewer"
        Write-Host "Successfully launched Windows Terminal (Method 2)!" -ForegroundColor Green
    }
    catch {
        Write-Host "Windows Terminal launch failed. Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please ensure Windows Terminal is installed from Microsoft Store." -ForegroundColor Yellow
    }
}
