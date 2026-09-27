# spotify_to.ps1 - put Spotify on a speaker or group, optionally a library station, shuffled.
#   powershell -File spotify_to.ps1 "WHOLE HOUSE"
#   powershell -File spotify_to.ps1 "WHOLE HOUSE" "My Favorite Radio" -Shuffle
# The second argument is any playlist/station name in Your Library (sidebar "Play <name>").
# -Shuffle turns shuffle on and skips 1-3 tracks so each run starts somewhere different.
#
# Lessons baked in (2026-09-27):
#  - A minimized Spotify window (160x28) exposes the buttons but the device picker never
#    opens. Maximize first.
#  - "Playing on WHOLE HOUSE" can be stale: Spotify thinks it's connected while the speakers
#    sit idle. So the target is always re-picked from the device list, never trusted.
#  - "Connect to a device" and "Enable Shuffle" don't support Invoke: real mouse clicks.
param([string]$Target = "WHOLE HOUSE", [string]$Play = "", [switch]$Shuffle)
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type -Namespace SpTo -Name U -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int e); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);'
$A=[System.Windows.Automation.AutomationElement]; $S=[System.Windows.Automation.TreeScope]
$p = Get-Process Spotify -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Start-Process "spotify:"; Start-Sleep -Seconds 8; $p = Get-Process Spotify | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1 }
[void][SpTo.U]::ShowWindow($p.MainWindowHandle, 3); Start-Sleep -Seconds 2
$root = $A::FromHandle($p.MainWindowHandle)
function Find($name) { $root.FindFirst($S::Descendants, (New-Object System.Windows.Automation.PropertyCondition($A::NameProperty, $name))) }
function Click($e) {
  [void][SpTo.U]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Milliseconds 400
  $r = $e.Current.BoundingRectangle
  [void][SpTo.U]::SetCursorPos([int]($r.X + $r.Width / 2), [int]($r.Y + $r.Height / 2)); Start-Sleep -Milliseconds 150
  [SpTo.U]::mouse_event(2,0,0,0,0); [SpTo.U]::mouse_event(4,0,0,0,0)
}
function Press($e) { try { $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke() } catch { Click $e } }

# 1. start the station if asked and it isn't already playing
if ($Play -and -not (Find "Pause $Play")) {
  $pl = Find "Play $Play"
  if ($pl) { Press $pl; Start-Sleep -Seconds 5 } else { "'$Play' not found in Your Library sidebar" }
}
# 2. always (re)pick the target from the device list
$dev = Find "$Target Google Cast"
if (-not $dev) { $c = Find "Connect to a device"; if ($c) { Click $c; Start-Sleep -Seconds 4 }; $dev = Find "$Target Google Cast" }
if (-not $dev) { "device '$Target' not in Spotify's list"; exit 1 }
Press $dev; Start-Sleep -Seconds 10
# 3. shuffle and a random start point
if ($Shuffle) {
  $sh = $root.FindAll($S::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | Where-Object { $_.Current.Name -like 'Enable Shuffle*' } | Select-Object -First 1
  if ($sh) { Press $sh; Start-Sleep -Seconds 2 }
  1..(Get-Random -Minimum 1 -Maximum 4) | ForEach-Object { $n = Find "Next"; if ($n) { Press $n; Start-Sleep -Seconds 2 } }
}
# 4. make sure it's actually playing, then report
if ((Find "Play") -and -not (Find "Pause")) { Press (Find "Play"); Start-Sleep -Seconds 2 }
$root.FindAll($S::Descendants, (New-Object System.Windows.Automation.PropertyCondition($A::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button))) |
  ForEach-Object { $_.Current.Name } | Where-Object { $_ -match '^Playing on|Shuffle for' } | Select-Object -Unique
$p.Refresh(); "now playing: " + $p.MainWindowTitle
