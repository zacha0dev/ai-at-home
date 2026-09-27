# ai-at-home

Real, everyday things I automate with an AI agent at home, packaged so you can do them too.

Each folder in `skills/` is a drop-in **Claude Code skill**: a `SKILL.md` that teaches the
agent how to do the job safely, plus any small scripts it runs. Each file in
`walkthroughs/` tells the story in plain English: the problem, what the agent did, what
broke, and what finally worked.

None of this is theory. Every skill here came out of a real session on a real house, a
real music library or a real inbox, and it kept the lessons from the parts that went wrong.

## What's inside

| Skill | What it does | Needs |
|---|---|---|
| [`speaker-checkup`](skills/speaker-checkup/SKILL.md) | Finds every Google Home / Nest speaker and group on your Wi-Fi, spots a frozen one, sets volume everywhere, moves Spotify to the whole house, runs one-word routines ("work", "leisure") | Python, `pychromecast`; Windows + Spotify desktop app for the Spotify part |
| [`spotify-library`](skills/spotify-library/SKILL.md) | Exports your whole Spotify library and every playlist into plain files, builds new playlists in bulk, and reviews songs by their *message* | a browser signed in to Spotify; Spotify desktop app |
| [`music-mood-grouping`](skills/music-mood-grouping/SKILL.md) | Sorts songs by mood (energy × brightness) and activity (focus, workout, drive...) using free audio data | a track export |
| [`playlist-flow`](skills/playlist-flow/SKILL.md) | Orders a playlist so it *flows*: an energy arc, smooth tempo steps and compatible keys, like a DJ set | Python |
| [`keep-the-beat`](skills/keep-the-beat/SKILL.md) | For songs you love the sound of but not the words: find the instrumental, dub, sample or a sound-alike with a better message | nothing |
| [`inbox-cleanup`](skills/inbox-cleanup/SKILL.md) | Digs a buried inbox out: separates real spam and scams from legit bulk mail, blocks the scammers, keeps every receipt | a mail connector (Microsoft Graph / Outlook) or a browser |
| [`tv-from-laptop`](skills/tv-from-laptop/SKILL.md) | Diagnoses a slow Android / Google TV from the laptop, reboots it, clears crash-looping apps, sets volume, sends remote keys | `adb` (Android platform-tools) |
| [`tablet-display`](skills/tablet-display/SKILL.md) | Turns an old Windows tablet into an always-on display: remote access with no keyboard, no sleeping, a web page full screen on every sign-in | Windows 10/11 Pro tablet |
| [`pi-home-server`](skills/pi-home-server/SKILL.md) | Runs a Raspberry Pi as a small home server: a 24/7 news collector, a dashboard on the home network, and deploying to it safely | Raspberry Pi, Python 3 |
| [`overnight-jobs`](skills/overnight-jobs/SKILL.md) | Leaves a Windows laptop running agent jobs overnight: awake until a set time, proof in the morning, reachable from your phone | Windows, PowerShell |

| Walkthrough | The story |
|---|---|
| [Spotify kept freezing on the whole-house speakers](walkthroughs/01-frozen-speaker-group.md) | a "half-alive" Nest Hub, and why that's worse than a dead one |
| [Turning a messy Spotify library into 9 playlists that flow](walkthroughs/02-spotify-library-cleanup.md) | 1,800 songs sorted by mood and message, then ordered by tempo and key |
| [Digging out of 1,400 emails](walkthroughs/03-inbox-dig-out.md) | throttled APIs, fake government filing scams, and the "keep one month" rule |
| [The TV was "loading funny"](walkthroughs/04-tv-loading-funny.md) | 86 days of uptime, 1,100 zombie processes, and one reboot |
| [An old Surface tablet became an always-on display](walkthroughs/05-old-tablet-display.md) | six taps, one firewall rule, and why ping lies |
| [The Raspberry Pi was sharing more than it should](walkthroughs/06-pi-was-sharing-too-much.md) | a whole folder on the home network, and deploying by allowlist |

## Use a skill

1. Install [Claude Code](https://claude.com/claude-code).
2. Copy a skill folder into your project's `.claude/skills/` (or `~/.claude/skills/` to use
   it everywhere):
   ```
   cp -r skills/speaker-checkup ~/.claude/skills/
   ```
3. Ask for the thing in plain words: *"check on my speakers"*, *"sort my playlists by mood"*,
   *"clean up my inbox"*. The agent picks up the skill on its own.

## Ground rules every skill follows

- **You stay in charge of anything that can't be undone.** Deleting mail, removing songs
  and changing account settings happen only after you've seen the exact list.
- **Move, don't destroy.** Mail goes to Deleted Items, songs go to an Archive playlist.
- **No passwords, no tokens.** The agent never signs in for you and never lifts a login
  token out of a browser. It works with what you're already signed in to.
- **Receipts are sacred.** A cleanup never touches statements, receipts, bills or tickets.
- **Write down what you learn.** Every skill ends with the gotchas that cost real time, so
  the next run doesn't pay for them again.

## Questions this answers

- **Why does Spotify get stuck when I play to a Google Home speaker group?** Usually the
  group's leader device (often a Nest Hub) is half-frozen: online, but its cast service is
  down. Restart that one device. [Walkthrough](walkthroughs/01-frozen-speaker-group.md)
- **Can I set the volume on all my Nest speakers at once?** Yes, from any computer on the
  same Wi-Fi with `pychromecast`, no Google sign-in needed. [`speaker-checkup`](skills/speaker-checkup/SKILL.md)
- **How do I export all my Spotify playlists to a file?** Read them from the web player
  you're already signed in to, and save a dated snapshot. [`spotify-library`](skills/spotify-library/SKILL.md)
- **How do I sort my music by mood or make a playlist flow like a DJ set?** Energy and
  brightness for mood; an energy arc, small tempo steps and Camelot-compatible keys for
  order. [`music-mood-grouping`](skills/music-mood-grouping/SKILL.md), [`playlist-flow`](skills/playlist-flow/SKILL.md)
- **Spotify's audio-features API is closed. What now?** ReccoBeats is a free, keyless
  alternative that takes Spotify track IDs. [`features.py`](skills/playlist-flow/features.py)
- **How do I clean up thousands of emails without losing receipts?** Separate scams from
  legit bulk mail, block scam domains, clear notifications older than a month, never touch
  records. [`inbox-cleanup`](skills/inbox-cleanup/SKILL.md)
- **Is that "annual report filing" email about my LLC real?** Almost always a scam if it's
  not from your state's own website. [`inbox-cleanup`](skills/inbox-cleanup/SKILL.md#scams-to-recognize)
- **Why does Microsoft Graph keep returning 429 when I move or mark emails?** Mailbox
  concurrency throttling: one call at a time, about 4 messages per mark-as-read call.
- **Why is my Google TV / Android TV so slow?** Often weeks of uptime plus a crash-looping
  app after an auto-update. Check it over ADB, then reboot. [Walkthrough](walkthroughs/04-tv-loading-funny.md)
- **Can I turn my TV on from my computer?** Usually off yes, on no: many TVs drop off the
  network in standby. Use a linked smart speaker or HDMI-CEC. [`tv-from-laptop`](skills/tv-from-laptop/SKILL.md)
- **How do I turn an old Surface or Windows tablet into a wall display?** Remote Desktop
  (six taps), stop modern-standby sleep on AC, Edge in kiosk mode at sign-in. [`tablet-display`](skills/tablet-display/SKILL.md)
- **Why won't SSH connect to Windows even though sshd is running?** The firewall rule may
  only apply to Private networks while your Wi-Fi is Public. [`tablet-display`](skills/tablet-display/SKILL.md#2-ssh-with-a-key-so-the-agent-can-run-things-on-it)
- **What should I run on a Raspberry Pi at home?** A news collector, a dashboard, Docker
  services, deployed by allowlist. [`pi-home-server`](skills/pi-home-server/SKILL.md)
- **How do I keep a Windows laptop awake overnight for an AI job, and prove it stayed
  awake?** A timed power request with a heartbeat log, plus `powercfg /requests`. [`overnight-jobs`](skills/overnight-jobs/SKILL.md)

## Status

Growing. Next up:

- **Home lab into the cloud:** connect the home Raspberry Pi securely into your own Azure
  environment through a tunnel, so the home lab extends into the cloud. It's the bridge from
  this repo to hands-on Azure labs in
  [zallen-cloud-labs](https://github.com/zacha0dev/zallen-cloud-labs).
- More walkthroughs as new home projects happen.

MIT licensed. Built by [@zacha0dev](https://github.com/zacha0dev) with Claude.
