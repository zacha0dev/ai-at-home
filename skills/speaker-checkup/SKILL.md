---
name: speaker-checkup
description: Check up on Google Home / Nest speakers from a computer on the same Wi-Fi - find every speaker and speaker group, spot a frozen device, set volume everywhere, move Spotify to a speaker or the whole house, and run one-word routines. Use for "check my speakers", "set everything to 35%", "Spotify is stuck on the speakers", "play music in the whole house", or "work mode" / "leisure mode".
---

# Speaker checkup

Works on the local network only. No Google account, no cloud API, no sign-in.

## Setup (once)

```
pip install pychromecast
```

The Spotify part uses the **Spotify desktop app on Windows** (driven through Windows UI
Automation). Everything else runs on any OS.

## Checkup and volume

```
python speakers.py                 # every speaker and group: app, volume, what's playing
python speakers.py --volume 0.35   # set every speaker and group, then show status
```

A device that is on the Wi-Fi but won't connect prints **FROZEN**. See below.

## "Spotify keeps getting stuck on the speaker group" - the usual cause

A speaker group plays through one **leader** device. The phone or computer sends the
music to the leader, and the leader relays it to the others and keeps them in sync.
Google picks the leader, usually the most powerful device in the group (often a Nest Hub).

The failure: the leader is **half-alive**. It's on the Wi-Fi and answers its setup page
(port 8008), but its cast service (port 8009) has frozen. The rest of the group still
treats it as the leader, so group playback hangs. A *fully* offline leader gets
replaced automatically; a half-alive one doesn't, which is why this one is so confusing.

- **Spot it:** `speakers.py` prints `FROZEN ... cast port closed` for that device, and
  every group that device leads errors out too.
- **Fix:** restart that one device: unplug it for ~10 seconds, or Google Home app ->
  device -> Settings -> Restart. There is no local API that restarts a Nest (the old
  `/setup/reboot` endpoint was locked down years ago), so this step needs a human hand.
- **After the restart:** run `speakers.py --volume <yours>` again (a rebooted device can
  come back at its old volume), then move Spotify back. The group may pick a new leader;
  `speakers.py` shows each group's current leader IP.
- **If it keeps happening:** make a group that leaves the flaky device out, so a steadier
  speaker leads. Groups can only be edited in the Google Home app.

## Move Spotify to the speakers

```
powershell -File spotify_to.ps1 "WHOLE HOUSE"
powershell -File spotify_to.ps1 "WHOLE HOUSE" "My Favorite Radio"
```

Routines **shuffle and skip 1-3 tracks** so they don't start the same way every time, and
they check the speakers really report Spotify, reconnecting once if not: Spotify can say
"Playing on WHOLE HOUSE" while the group sits idle. A **minimized** Spotify window still
exposes its buttons, but the device picker won't open; the script maximizes it first.

This **moves what's already playing**: the same song, at the same second, from your phone
or wherever it was. The second argument starts a playlist or radio station from Your
Library first, by name. It confirms with the app's `Playing on <name>` label.

How it works: the device picker button is `Connect to a device`; each speaker appears as
a button named `<name> Google Cast`. Those support UI Automation's Invoke.

**UI Automation gotchas** (Spotify desktop app, 2026):
- `Connect to a device`, `Save to Your Library` and `More options` do **not** support
  Invoke. Click the centre of their bounding box instead.
- "Share -> Copy link" from a playlist page's menu can copy the *song* link, not the
  playlist. Starting a library item by its sidebar `Play <name>` button avoids needing
  the link at all.
- The Store version of the app has no command-line switches; `Start-Process spotify:playlist:<id>`
  opens a page, and UI Automation does the rest.

## Control Spotify without the screen: Home Assistant (no screen)

The desktop-app method takes over the screen for ~20 seconds. If you run Home Assistant
(see `robot-vacuum-home-assistant` for a Pi setup), add its **Spotify** integration and the
agent can do it all in the background:

1. developer.spotify.com -> Create app: any name, redirect URI
   `https://my.home-assistant.io/redirect/oauth`, tick **Web API**, accept the terms, Save.
2. Home Assistant -> Add integration -> Spotify -> paste the app's Client ID and Client Secret
   (you paste them, not the agent) -> approve in Spotify.
3. The first time, my.home-assistant.io asks for your Home Assistant address: enter your
   local URL (e.g. `http://<pi>.local:8123`), then **Link account**.

Then: `media_player.select_source` (speaker group), `shuffle_set`, `play_media` with
`spotify:playlist:<id>`, `media_next_track`, and `volume_set` on the cast group, all over
HA's REST API. **Limit:** Spotify-made stations and radios ("Daily Mix", "<song> Radio") are
hidden from the API; they can be resumed but not started. Use your own playlists for routines.

## Routines

```
python routine.py work      # background music, low enough for video calls
python routine.py leisure
python routine.py list
```

Edit `ROUTINES` in `routine.py`: target speaker or group, a station saved in Your
Library, and a volume. Tested tip: **about 33%** keeps music going in the background of a
Teams or Zoom call, even unmuted, and 35-37% is a comfortable "just relaxing" level on
Nest Audio / Nest Mini.

## Limits

- Voice commands can't be scripted; there's no local way to make a Nest "hear" something.
- The agent does not pull a Spotify login token out of the browser to call the Web API,
  which is why playback control goes through the desktop app.
- A "dumb" AC or TV (infrared remote only) needs an IR bridge (e.g. a Broadlink) linked in
  Google Home before any of this can reach it.
