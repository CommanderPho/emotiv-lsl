# Start Emotiv Services Script
# This script starts the Emotiv Cortex and Cloud Sync services

Write-Host "Starting Official Emotiv services..." -ForegroundColor Yellow

# Array of service names to start
$services = @(
    "EmotivCortexServiceV2",
    "EmotivCloudSyncService"
)

foreach ($serviceName in $services) {
    try {
        # Check if service exists
        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
        
        if ($service) {
            if ($service.Status -eq "Stopped") {
                Write-Host "Starting service: $serviceName" -ForegroundColor Cyan
                Start-Service -Name $serviceName
                Write-Host "Service $serviceName started successfully" -ForegroundColor Green
            } elseif ($service.Status -eq "Running") {
                Write-Host "Service $serviceName is already running" -ForegroundColor Gray
            } else {
                Write-Host "Service $serviceName status: $($service.Status)" -ForegroundColor Yellow
                Write-Host "Attempting to start service: $serviceName" -ForegroundColor Cyan
                Start-Service -Name $serviceName
                Write-Host "Service $serviceName started successfully" -ForegroundColor Green
            }
        } else {
            Write-Host "Service $serviceName not found" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Error starting service $serviceName`: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "Script completed" -ForegroundColor Yellow
