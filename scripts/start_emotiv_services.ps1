# Start-Service.ps1
# Starts the specified service

$serviceName = "EmotivCortexServiceV2"

try {
    Start-Service -Name $serviceName -ErrorAction Stop
    Write-Host "Service '$serviceName' started successfully."
}
catch {
    Write-Host "Failed to start service '$serviceName': $_"
}
