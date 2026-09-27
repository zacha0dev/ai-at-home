---
name: robot-vacuum-home-assistant
description: Put a cloud-only robot vacuum (Dreame / Dreamehome, also Xiaomi and Mova) under your AI agent's control through Home Assistant on a Raspberry Pi - find it on the network, install Home Assistant and the vacuum integration, get an access token safely, then start, stop, dock, clean rooms, read every sensor, and recover when it gets lost. Use for "control my robot vacuum from the computer", "start the vacuum", "my vacuum is lost", or "set up Home Assistant for my vacuum".
---

# Robot vacuum through Home Assistant

## 1. Find it (quiet devices hide)

Many robot vacuums answer no pings, announce nothing on mDNS, and sleep their Wi-Fi on the
dock. A normal network scan misses them. The trick that works: **run a watch that sweeps
the network every ~10 s, then power-cycle the robot.** It's chatty while rejoining Wi-Fi,
and it usually shows up within a minute with a hostname like `dreame_vacuum_r2564z`.
That suffix is the model code: look it up in the integration's supported-devices list.

Then probe it: if every local port is closed (and the Xiaomi miIO "hello" on UDP 54321 gets
no reply), it's **cloud-only**, and all control goes through the maker's cloud. That's fine;
Home Assistant becomes the automation layer on top.

## 2. Home Assistant on a Raspberry Pi (Docker)

```
docker run -d --name homeassistant --restart=unless-stopped -e TZ=<your/zone> \
  -v $HOME/homeassistant:/config -v /run/dbus:/run/dbus:ro --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

Open `http://<pi>.local:8123`. **The owner** creates the Home Assistant account (the agent
never makes accounts or types passwords). Setting the town rather than a street address is
enough for weather and sun times. Leave analytics off. HA will already discover
speakers, TVs and thermostats on the network.

## 3. The vacuum integration: pick the right version

[Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) supports Dreame, Xiaomi
and Mova robots. **Check which account type your robot uses:**
- Stable 1.x logs in with a **Xiaomi Mi Home** account or a local token only.
- The **2.0 betas** add **"Dreamehome Account"** (and Movahome / Trouver) logins. A robot
  that lives in the Dreamehome app needs the beta.

Install by unzipping the release's `dreame_vacuum.zip` into
`~/homeassistant/custom_components/dreame_vacuum/`, then **restart the container**: custom
integrations only load at startup. Add it in Settings -> Devices & services -> Add
integration -> "Dreame Vacuum". **Set the server country** (it defaulted to `eu`). The owner
types the app login.

If the owner doesn't know the app password: set it **in the phone app** (Profile ->
Account). The Dreamehome web login's phone verification failed for a US account.

## 4. A token for the agent, without it ever showing

HA -> your profile -> Security -> **Create token**. Then use the dialog's **Copy** button
and move it straight from the clipboard into a private file, then clear the clipboard:

```powershell
$t = (Get-Clipboard -Raw).Trim()
[IO.File]::WriteAllText("$env:USERPROFILE\.config\home-assistant\token", $t)
icacls "$env:USERPROFILE\.config\home-assistant\token" /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
Set-Clipboard -Value ' '
```

What didn't work, so you can skip it: a browser `fetch` from the (http) HA page to
127.0.0.1 is blocked by Private Network Access, and opening a temporary receiver on the
network is the kind of thing a careful agent should refuse.

## 5. Drive it

```
set HA_URL=http://<pi>.local:8123
set HA_VACUUM=vacuum.<your_robot>
python ha.py status            # state, battery, errors, parts left, rooms
python ha.py start | pause | stop | dock | locate
python ha.py rooms 1 3         # clean rooms by id
python ha.py call <domain> <service> '<json>'
```

You get ~50+ live readings: state, current room, errors, battery, brush / filter / wheel
life in hours, lifetime stats, switches (carpet boost, obstacle avoidance, do-not-disturb,
child lock), suction level, speaker volume, and a **live map image** at
`/api/camera_proxy/camera.<robot>_map`.

**Starting a robot is a physical action in someone's home:** do it when they ask.

## 6. When things go wrong (from the first real test)

- **Errors clear themselves in seconds.** Read the reason from history, not the current
  state: `/api/history/period/<start>?filter_entity_id=sensor.<robot>_error`.
- **"drop"** = the cliff sensors saw a ledge. On a flat floor that usually means **dirty cliff
  sensors**: wipe the little windows under the front bumper.
- **"returning" for minutes** = it's hunting for the dock. Pull the **map image**: if it's a
  fresh partial map with **no dock on it**, the robot has lost its position. **Pause it** so it
  stays put, **locate** it (it speaks), carry it home, and restore the saved map in the app
  if needed.
- Driving it manually through furniture while it's lost isn't worth it. Picking it up is
  faster.
- Before handing a long-idle robot a job: clean cliff sensors, wheels, brushes and the
  charging contacts.
