# spotify_to.ps1 - move Spotify to a speaker or group, optionally starting a library item.
#   powershell -File spotify_to.ps1 "WHOLE HOUSE"
#   powershell -File spotify_to.ps1 "WHOLE HOUSE" "My Favorite Radio"
# The second argument is any playlist/station name in Your Library (sidebar "Play <name>").
# Uses the Spotify desktop app (Store app) through UI Automation. The playback moves
# with its position intact; nothing restarts. Prints the "Playing on ..." line after.
param([string]$Target = "WHOLE HOUSE", [string]$Play = "")
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$A=[System.Windows.Automation.AutomationElement]; $S=[System.Windows.Automation.TreeScope]
$p = Get-Process Spotify -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Start-Process "spotify:"; Start-Sleep -Seconds 8; $p = Get-Process Spotify | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1 }
$root = $A::FromHandle($p.MainWindowHandle)
function Find($name) { $root.FindFirst($S::Descendants, (New-Object System.Windows.Automation.PropertyCondition($A::NameProperty, $name))) }
if (-not (Find "Playing on $Target")) {
  $dev = Find "$Target Google Cast"
  if (-not $dev) {
    $c = Find "Connect to a device"   # finding it opens the picker; Invoke is unsupported
    try { $c.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke() } catch {}
    Start-Sleep -Seconds 3; $dev = Find "$Target Google Cast"
  }
  if (-not $dev) { "device '$Target' not in Spotify's list"; exit 1 }
  $dev.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
  Start-Sleep -Seconds 8
}
if ($Play -and -not (Find "Pause $Play")) {
  $pl = Find "Play $Play"
  if ($pl) { $pl.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Seconds 5 }
  else { "'$Play' not found in Your Library sidebar" }
}
$root.FindAll($S::Descendants, (New-Object System.Windows.Automation.PropertyCondition($A::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button))) |
  ForEach-Object { $_.Current.Name } | Where-Object { $_ -match '^Playing on' } | Select-Object -First 1
