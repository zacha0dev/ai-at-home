# keep-awake.ps1 - hold the machine awake until a wall-clock time, then let go.
# Read-only on the system: it asserts a power request for its own process and
# drops it on exit. No power plan or setting is changed.
param(
    [Parameter(Mandatory = $true)][datetime]$Until,
    [string]$LogPath = "$env:TEMP\keep-awake.log"
)

$sig = '[DllImport("kernel32.dll", SetLastError=true)] public static extern uint SetThreadExecutionState(uint esFlags);'
Add-Type -MemberDefinition $sig -Name 'Power' -Namespace 'Win32' | Out-Null

$ES_CONTINUOUS      = [uint32]'0x80000000'
$ES_SYSTEM_REQUIRED = [uint32]'0x00000001'

function Write-Log($msg) {
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    Add-Content -Path $LogPath -Value ($stamp + '  ' + $msg) -Encoding utf8
}

Write-Log ('HOLD START  pid=' + $PID + '  release at ' + $Until.ToString('yyyy-MM-dd HH:mm:ss'))

$lastBeat = [datetime]::MinValue
try {
    while ((Get-Date) -lt $Until) {
        # Re-assert every minute. ES_CONTINUOUS alone would persist, but
        # re-asserting survives anything that clears it out from under us.
        $r = [Win32.Power]::SetThreadExecutionState($ES_CONTINUOUS -bor $ES_SYSTEM_REQUIRED)
        if ($r -eq 0) { Write-Log 'WARN  SetThreadExecutionState returned 0' }

        # Heartbeat every 15 min, so the log proves the hold held all night
        # rather than only proving it started. A gap in the beats is the
        # signature of a sleep that got through, or of the process dying.
        if (((Get-Date) - $lastBeat).TotalMinutes -ge 15) {
            $left = [math]::Round(($Until - (Get-Date)).TotalHours, 2)
            Write-Log ('beat  ok  rc=' + $r + '  ' + $left + 'h left')
            $lastBeat = Get-Date
        }
        Start-Sleep -Seconds 60
    }
    Write-Log ('RELEASE  reached ' + $Until.ToString('HH:mm') + ' - machine may sleep normally now')
}
finally {
    # Drop the request however we exit: timer, Ctrl-C, or kill.
    [void][Win32.Power]::SetThreadExecutionState($ES_CONTINUOUS)
    Write-Log ('HOLD END  pid=' + $PID)
}
