# Stop Emotiv Services Script
# This script stops the Emotiv Cortex and Cloud Sync services

Write-Host "Stopping Official Emotiv services..." -ForegroundColor Yellow
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }

# Start-Process powershell -Verb RunAs
Stop-Service -Name "Emotiv*" -Verbose

# # Array of service names to stop
# $services = @(
#     "EmotivCortexServiceV2",
#     "EmotivCloudSyncService"
# )

# foreach ($serviceName in $services) {
#     try {
#         # Check if service exists
#         $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
        
#         if ($service) {
#             if ($service.Status -eq "Running") {
#                 Write-Host "Stopping service: $serviceName" -ForegroundColor Cyan
#                 Stop-Service -Name $serviceName -Force
#                 Write-Host "Service $serviceName stopped successfully" -ForegroundColor Green
#             } else {
#                 Write-Host "Service $serviceName is already stopped (Status: $($service.Status))" -ForegroundColor Gray
#             }
#         } else {
#             Write-Host "Service $serviceName not found" -ForegroundColor Red
#         }
#     }
#     catch {
#         Write-Host "Error stopping service $serviceName`: $($_.Exception.Message)" -ForegroundColor Red
#     }
# }

Write-Host "Script completed" -ForegroundColor Yellow

