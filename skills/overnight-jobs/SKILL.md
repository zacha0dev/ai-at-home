---
name: overnight-jobs
description: Leave a Windows laptop running AI agent jobs overnight, unattended - keep it awake only until a set time, prove in the morning that it actually stayed awake, and keep the session reachable from your phone. Use for "run this overnight", "don't let the laptop sleep", "did it stay on all night?", or "can I check on the job from my phone?".
---

# Running jobs overnight, unattended

Two separate things have to be true, and they fail differently:
1. **The machine stays awake**, or the jobs stop.
2. **The session is reachable**, or the jobs run fine and you're blind until morning.

## Staying awake

**Check first whether there's anything to solve:**
`powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE` shows the AC and battery sleep
timeouts. On many laptops, **plugged in = never sleeps** already. The hold below
mostly matters on battery.

**The hold** (`keep-awake.ps1`): asserts a Windows power request for its own process and
drops it at a wall-clock time. It changes no setting and edits no power plan; Windows
releases the request when the process exits, so killing it is always safe.

```powershell
Start-Process powershell.exe -WindowStyle Hidden -ArgumentList `
  @("-NoProfile","-ExecutionPolicy","Bypass","-File","keep-awake.ps1","-Until","2026-10-01T08:00:00")
```

It logs to `%TEMP%\keep-awake.log` with a **heartbeat every 15 minutes**. A log that only
says "started" proves nothing at 7 AM; **a gap in the heartbeats is the finding.**

**Proving it with the OS:** in an *elevated* prompt, `powercfg /requests` should list
`SYSTEM: [PROCESS] ...powershell.exe`. `DISPLAY: None` is expected (the screen still sleeps;
jobs run behind a dark panel).

**What no power request overrides:** closing the lid. Leave it open.

## Being reachable from your phone (Claude Code)

- `claude --remote-control "job runner"` (or `/remote-control` inside a session) makes a
  *live local* session reachable from the Claude app on other devices.
- **Remote Control doesn't keep a session alive.** If the terminal closes or the machine
  sleeps, it shows as offline. That's why staying awake and being reachable are separate problems.
- **To know which sessions are really connected, ask them.** A one-line message and a reply proves
  the link both ways. Status files and "sent successfully" results can be stale or
  generic; one session was declared connected by both and wasn't.

## The gotcha that cost the most time

**Windows PowerShell 5.1 can't end a here-string (`@'...'@`) in a file saved with LF-only
line endings.** The script dies instantly and the error points ~30 lines away from the real
cause. Avoid here-strings in scripts meant for 5.1, and normalize to CRLF + syntax-check
before launching anything long-running:

```powershell
$t = [IO.File]::ReadAllText($f).Replace("`r`n","`n").Replace("`n","`r`n")
[IO.File]::WriteAllText($f, $t, (New-Object Text.UTF8Encoding($false)))
$errs = $null; [void][Management.Automation.Language.Parser]::ParseFile($f, [ref]$null, [ref]$errs); $errs
```

## Before you walk away

- [ ] Plugged in? Then sleep may already be "never". Check.
- [ ] On battery: start `keep-awake.ps1` with a release time.
- [ ] Confirm with `powercfg /requests` in an elevated prompt.
- [ ] Lid open.
- [ ] Ping each session you want reachable and **wait for its reply**.
- [ ] In the morning, read the heartbeat log for gaps, not just for a start line.
