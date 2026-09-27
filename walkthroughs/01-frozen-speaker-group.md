# Spotify kept freezing on the whole-house speakers

**Skill:** [`speaker-checkup`](../skills/speaker-checkup/SKILL.md)

## The problem

Six Google Nest devices around the house: two Nest Audio, two Nest Mini, a Nest Wifi
point with a speaker, and a Nest Hub with a screen. Two speaker groups, "All Speakers"
and "Whole House". Playing Spotify to a single speaker was fine. Playing to a group kept
getting stuck: it would pick the group and then nothing played.

## What the agent did

1. **Found everything on the Wi-Fi** with `pychromecast`: six speakers, two groups.
2. **Read each one's status.** Five speakers answered. The Nest Hub and **both groups**
   timed out.
3. **Probed the Hub directly.** It was powered on, on the Wi-Fi, and its setup page (port
   8008) answered normally, uptime 3.4 days. But its cast port (8009), the one Spotify
   talks to, was **closed**.
4. **Connected the dots.** Both groups were being hosted by the Hub. A speaker group
   plays through one *leader* device that takes the stream and syncs the others, and
   Google had made the Hub the leader because it's the most capable device in the house.

## Why it's sneaky

If the Hub had been completely off, the other speakers would have picked a new leader.
But it was **half-alive**: still on the network, still looking fine, just not taking
casts. So everyone kept waiting on it.

## The fix

- Unplug the Hub for ten seconds and plug it back in. That's the one step that needs a human;
  there's no local way to restart a Nest.
- Re-check: all six speakers and both groups answered. After the restart Google had
  moved the group's leader to the Nest Wifi point on its own.
- Set every speaker to the same volume in one command, then moved the song that was
  already playing on the phone over to "Whole House", mid-song, through the Spotify
  desktop app.

## What came out of it

- A checkup script that prints **FROZEN** for exactly this failure.
- Two one-word routines: `work` (music at 33%, quiet enough to leave on during video
  calls) and `leisure` (37%). Tested by ear, in a real room, during a real workday.
