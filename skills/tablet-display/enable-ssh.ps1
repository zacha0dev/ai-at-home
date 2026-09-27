# Enables the built-in Windows OpenSSH server so this machine can be driven
# remotely. MUST be run as Administrator. Nothing is downloaded - OpenSSH is
# already part of Windows, this just turns it on.
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
if(-not (New-Object Security.Principal.WindowsPrincipal $id).IsInRole('Administrators')){
  Write-Host "NOT ELEVATED. Right-click ENABLE-SSH.cmd and choose 'Run as administrator'." -ForegroundColor Red
  Read-Host "Enter to exit"; exit 1
}

Write-Host "Installing OpenSSH Server (already part of Windows)..." -ForegroundColor Cyan
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null

Set-Service -Name sshd -StartupType Automatic
Start-Service sshd

if(-not (Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue)){
  New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
}

Write-Host ""
Write-Host "  DONE." -ForegroundColor Green
"  service : {0}" -f (Get-Service sshd).Status
"  host    : {0}" -f $env:COMPUTERNAME
"  user    : {0}" -f $env:USERNAME
"  ip      : {0}" -f ((Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like '192.168.*'} | Select-Object -First 1).IPAddress)
Write-Host ""
Write-Host "  Tell Claude the host and user above. Do NOT paste your password." -ForegroundColor Yellow
Read-Host "Enter to close"
