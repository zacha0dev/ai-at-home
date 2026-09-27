---
name: pi-home-server
description: Set up and run a Raspberry Pi as a small always-on home server that an AI agent manages over SSH - a 24/7 news collector, a dashboard page on the home network, Docker services - and deploy to it safely with an allowlist. Use for "set up my Raspberry Pi", "run this on the Pi 24/7", "put a dashboard on my home network", or "is my Pi exposing anything it shouldn't?".
---

# Raspberry Pi home server

## Get the agent in (once)

- Raspberry Pi OS (64-bit), SSH enabled in Raspberry Pi Imager's settings, **key login**
  (no password). Then `ssh pi@<hostname>.local` from the laptop.
- Write down the hostname, user and key file in your notes. Old hostnames linger in
  `known_hosts` and send you chasing a box that no longer exists.
- Docker: `curl -fsSL https://get.docker.com | sh`, add your user to the `docker` group,
  log in again.

## A 24/7 news collector (`news.py`)

A good first always-on job: standard-library Python, public RSS feeds, no keys.

```
python3 news.py            # fetch once
python3 news.py --top 5    # what's top in the last 24h
crontab -e                 # add:  */30 * * * * cd $HOME/news-desk && /usr/bin/python3 news.py >> run.log 2>&1
```

- **Lanes** (ai, world, economy, science by default) and **keyword weights** live at the
  top of the file. A ranking you can read is a ranking you can trust.
- Keeps 14 days, written **atomically** (write a temp file, then rename), because a
  half-written store is worse than a stale one.
- **Fetching, not notifying.** It keeps itself current; your agent reads `store.json`
  when you ask "what happened today?". Nothing pings you.

## A dashboard on the home network

Generate a static HTML page on a timer and serve **one folder** with a tiny web server
(e.g. a systemd service running `python3 -m http.server 8090 --directory ~/web`).
Browse to `http://<hostname>.local:8090/` from any device at home.

## The safety lesson: deploy with an allowlist

A real finding: the Pi was **serving its whole project folder over HTTP with no
authentication**, including a bot's credentials file, to every device on the network
(Nest speakers, TVs, phones, guests). Two fixes, both worth copying:

1. **Serve a dedicated folder** that only ever holds the generated page, never the project.
2. **Deploy by allowlist, not by "copy everything except..."** A deploy script that names
   exactly which files may go (docs, code, public data) fails safe when someone adds a new
   sensitive file. An rsync with excludes fails open. Also list the never-ship files by
   name in the script, so the decision is visible.

Add one more check to the deploy: after generating the page, grep the served folder for
words that must never appear there (account names, balances, "password", key file
names) and fail loudly if any match.

## Housekeeping

- `uptime`, `df -h`, `docker ps`, and `crontab -l` make a 10-second health check.
- A cron job that fails does so silently. Log to a file (`>> run.log 2>&1`) and look at
  the last line, or have the job write a "last run" timestamp you can check.
- Check that a job's dependencies are installed *on the Pi*. A script that imports a
  library installed only on the laptop fails every run, quietly.
