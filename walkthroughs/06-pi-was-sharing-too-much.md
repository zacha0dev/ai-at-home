# The Raspberry Pi was sharing more than it should

**Skill:** [`pi-home-server`](../skills/pi-home-server/SKILL.md)

## The setup

A Raspberry Pi running a few always-on jobs: a news collector every 30 minutes, a small
status dashboard for the home network, and a couple of Docker services. The agent managed
it over SSH from the laptop.

## The finding

While checking the dashboard, the agent noticed the Pi's web server was pointed at the
**whole project folder**, not just the page. Anyone on the home Wi-Fi could browse every
file, including a service's credentials file. On a typical home network that means the smart
speakers, the TVs, every phone and every guest.

## The fix

1. **Serve one dedicated folder** that only ever contains the generated page.
2. **Deploy by allowlist.** The deploy script now names exactly which files may be copied
   to the Pi, and names the never-ship files explicitly. "Copy everything except the bad
   bits" fails the moment someone adds a new sensitive file; an allowlist fails safe.
3. **Check after every deploy** that the served folder doesn't contain words that must
   never be public, and fail loudly if it does.

## A second quiet failure

A scheduled job on the Pi had been failing every run for days: it imported a Python
library that was installed on the laptop but never on the Pi, and its output went to
`/dev/null`. Nobody noticed until its data looked stale. Now every job logs to a file,
and "is the data fresh?" is part of the health check.
