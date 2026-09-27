# Turn an old Windows tablet into a full-screen, always-on display (kiosk-style).
#
# WHAT THIS IS, AND WHAT IT DELIBERATELY IS NOT:
#
# It does NOT try to make Windows behave like a tablet OS. Windows 11 removed
# the Windows 10 "Tablet Mode" toggle, and fighting the shell is a losing game.
# Instead it puts ONE full-screen touch UI on top of Windows and hides
# everything else. That is what a tablet actually is from the user's side.
#
# It also does NOT use Assigned Access / kiosk accounts. Those lock an account
# to a single app and are genuinely hard to undo from the device if something
# goes wrong - a bad outcome on a machine with no working remote shell. This is
# the light version: a startup shortcut and a browser flag. Alt+F4 exits, and
# TABLET-MODE-OFF.cmd removes it completely.
#
# THE REAL PAYOFF: once the display is a web page, the tablet never needs to be
# touched again to change what it shows. Update the web app, the tablet follows.
# That routes around the remote-control problem instead of solving it.
#
# ASCII only on purpose: PowerShell 5.1 reads .ps1 as ANSI without a BOM.

param(
  [string]$Url = "",
  [switch]$Off
)

$ErrorActionPreference = 'Stop'
$startup  = [Environment]::GetFolderPath('Startup')
$lnkPath  = Join-Path $startup 'home-display-kiosk.lnk'
$cfgPath  = Join-Path $env:LOCALAPPDATA 'home-display-kiosk-url.txt'

function Find-Edge {
  $c = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
  )
  foreach($p in $c){ if(Test-Path $p){ return $p } }
  return $null
}

if($Off){
  if(Test-Path $lnkPath){ Remove-Item $lnkPath -Force; Write-Host "Removed startup entry." }
  else { Write-Host "No startup entry was present." }
  Write-Host ""
  Write-Host "Tablet mode is OFF. Nothing else was changed - no power settings,"
  Write-Host "no kiosk account, no registry. Reboot to confirm a normal desktop."
  return
}

if(-not $Url){
  Write-Host "Which URL should the tablet display full screen?"
  Write-Host "Examples: a dashboard, a calendar page, a photo slideshow, a local file:/// path."
  $Url = Read-Host "URL"
}
if(-not $Url){ Write-Host "No URL given. Nothing changed."; return }

$edge = Find-Edge
if(-not $edge){
  Write-Host "Microsoft Edge was not found in the usual locations."
  Write-Host "Checked:"
  Write-Host "  $env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
  Write-Host "  ${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
  Write-Host "Install Edge, or edit this script to point at Chrome instead."
  return
}

# --kiosk            full screen, no chrome, no address bar
# --edge-kiosk-type  fullscreen (not the public-browsing variant)
# --no-first-run     skip the welcome flow on a fresh profile
# --disable-features  stop the first-run and default-browser nags
$argLine = '--kiosk "{0}" --edge-kiosk-type=fullscreen --no-first-run --disable-features=msEdgeWelcomePage' -f $Url

$sh  = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($lnkPath)
$lnk.TargetPath       = $edge
$lnk.Arguments        = $argLine
$lnk.Description      = 'Home display kiosk - remove this shortcut to disable'
$lnk.WindowStyle      = 3          # maximized
$lnk.Save()

Set-Content -Path $cfgPath -Value $Url -Encoding utf8

Write-Host ""
Write-Host "Tablet mode is ON."
Write-Host "  URL       : $Url"
Write-Host "  Browser   : $edge"
Write-Host "  Startup   : $lnkPath"
Write-Host ""
Write-Host "It launches on next sign-in. To try it right now without rebooting:"
Write-Host "  Start-Process '$edge' -ArgumentList '$argLine'"
Write-Host ""
Write-Host "Alt+F4 exits. TABLET-MODE-OFF.cmd removes it."
Write-Host ""
Write-Host "STILL TO DO BY HAND, because they need Settings and cannot be"
Write-Host "scripted safely on a machine with no remote shell:"
Write-Host "  1. Auto sign-in, so a reboot lands straight on the display."
Write-Host "     Run: netplwiz   then untick 'Users must enter a user name...'"
Write-Host "     Only do this if the tablet is physically somewhere safe."
Write-Host "  2. Settings > System > Power - set screen timeout to Never on AC."
Write-Host "     KEEP-AWAKE.cmd covers sleep; the SCREEN is a separate setting,"
Write-Host "     and on a modern-standby machine a dark screen leads to sleep."
Write-Host "  3. Settings > Personalization > Taskbar - auto-hide, so a stray"
Write-Host "     swipe does not reveal a desktop."
