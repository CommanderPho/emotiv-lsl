# Start-Service.ps1

if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
# Starts the specified service

$serviceName = "EmotivCortexServiceV2"

try {
    Start-Service -Name $serviceName -ErrorAction Stop
    Write-Host "Service '$serviceName' started successfully."
}
catch {
    Write-Host "Failed to start service '$serviceName': $_"
}

# Windows Powershell launch the program "C:\Program Files\EmotivApps\EMOTIV Launcher.exe" with the "Start in:" of "C:\Program Files\EmotivApps"
# Monitor the opened program and the user closes the program, run another script
$process = Get-Process -Name "EMOTIV Launcher"
$process.WaitForExit()
Start-Process -FilePath "C:\Program Files\EmotivApps\EMOTIV Launcher.exe" -WorkingDirectory "C:\Program Files\EmotivApps"



