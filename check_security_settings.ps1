# Windows Security and Network Configuration Check
# Run this script to identify potential issues blocking Streamlit

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host " Windows Security & Network Configuration Check" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
Write-Host "Administrator Status: " -NoNewline
if ($isAdmin) {
    Write-Host "ADMIN" -ForegroundColor Green
} else {
    Write-Host "USER (Run as Admin for full checks)" -ForegroundColor Yellow
}
Write-Host ""

# Check Windows Defender status
Write-Host "Windows Defender Status:" -ForegroundColor Yellow
try {
    $defenderStatus = Get-MpComputerStatus
    Write-Host "  Real-time Protection: $($defenderStatus.RealTimeProtectionEnabled)" -ForegroundColor $(if($defenderStatus.RealTimeProtectionEnabled) {"Red"} else {"Green"})
    Write-Host "  Network Protection: $($defenderStatus.NetworkProtectionStatus)" -ForegroundColor $(if($defenderStatus.NetworkProtectionStatus -eq "Enabled") {"Red"} else {"Green"})
} catch {
    Write-Host "  Cannot check Defender status (may require admin)" -ForegroundColor Yellow
}
Write-Host ""

# Check Windows Firewall
Write-Host "Windows Firewall Status:" -ForegroundColor Yellow
try {
    $firewallProfiles = Get-NetFirewallProfile
    foreach ($profile in $firewallProfiles) {
        Write-Host "  $($profile.Name): $($profile.Enabled)" -ForegroundColor $(if($profile.Enabled) {"Red"} else {"Green"})
    }
} catch {
    Write-Host "  Cannot check firewall status" -ForegroundColor Red
}
Write-Host ""

# Check port availability
Write-Host "Checking Common Streamlit Ports:" -ForegroundColor Yellow
$ports = @(8501, 8502, 8503, 8504, 8505, 8506, 8507)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet
    $status = if ($connection) {"OCCUPIED"} else {"AVAILABLE"}
    $color = if ($connection) {"Red"} else {"Green"}
    Write-Host "  Port $port: $status" -ForegroundColor $color
}
Write-Host ""

# Check network adapters
Write-Host "Network Adapter Status:" -ForegroundColor Yellow
$adapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
foreach ($adapter in $adapters) {
    Write-Host "  $($adapter.Name): $($adapter.Status)" -ForegroundColor Green
}
Write-Host ""

# Recommendations
Write-Host "RECOMMENDATIONS:" -ForegroundColor Cyan
Write-Host "1. If real-time protection is enabled, try temporarily disabling it" -ForegroundColor White
Write-Host "2. If firewall is blocking, add Python.exe to exceptions" -ForegroundColor White
Write-Host "3. Run PowerShell as Administrator" -ForegroundColor White
Write-Host "4. Try the batch file: run_streamlit_admin.bat" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
