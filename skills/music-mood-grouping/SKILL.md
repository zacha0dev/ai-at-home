---
name: music-mood-grouping
description: Sort songs into mood and activity groups (morning, focus, workout, drive, party, wind-down) from energy, brightness and tempo, with a message check first. Use for "sort my music by mood", "make me a workout / focus playlist from my library", or before building new playlists.
---


# Mood and activity grouping

Every song gets **two tags**: a mood corner and an activity. Groups are built from the
tags, never from the playlist a song happens to live in today.

## 1. Mood corner (Thayer / Russell model)

Two axes, from the song's sound: **energy** (calm to intense) and **valence** (dark to
bright). Four corners:

| Corner | Energy | Valence | Use it? |
|---|---|---|---|
| **Exuberant** | high | high | yes - party, workout, drive |
| **Content** | low | high | yes - morning, focus, wind-down |
| **Frantic** | high | low | only as fuel (heavy workout), never for mood |
| **Low** | low | low | **leave out** - this is the corner that pulls mood down |

Songs near the middle of both axes are ambiguous; tag them by activity only.

Numbers, when available (0-1 scale): energy >= 0.65 is high, <= 0.4 low; valence >= 0.55
bright, <= 0.35 dark. Energy is reliable; valence is only moderately reliable; ignore
danceability (weak against human ratings).

## 2. Activity

| Activity | Energy | Valence | Tempo | Notes |
|---|---|---|---|---|
| **Morning** | mid | high | 95-120 | gentle start, feel-good country, city pop, Kygo |
| **Focus** | low-mid | any bright | any | instrumental or low vocals: jazz, city pop, deep house, lo-fi |
| **Workout** | high | high, or Frantic only if it's motivating | **120-140 BPM** | gains flatten above ~140; hard efforts 135-140 |
| **Drive** | mid-high | high | 100-130 | country road songs, rock anthems, melodic house |
| **Party** | high | high | 120-130 house / any | EDM, house, party rap that passes the message check |
| **Wind-down** | low | mid-high | < 100 | ambient, jazz ballads, chill sets |

A song can have one activity. If it truly fits two, pick where it is **best**.

## 3. Message filter (runs before grouping)

Sound tags say nothing about lyrics. Every vocal track also gets a message verdict from
the `keep-the-beat` skill: **uplifting / neutral / tears down**. Tears-down songs never
go into a group as-is - they go to the keep-the-beat process first.

## 4. Where the numbers come from (2026)

- **Spotify's audio-features API is closed** to apps created after Nov 27 2024. Don't
  plan around it.
- **ReccoBeats** (free, no key): takes Spotify track IDs, returns energy, valence, tempo,
  key, instrumentalness, speechiness. Rate limited with 429 + Retry-After; go slow.
  Track IDs come from the `spotify-library` export. `playlist-flow/features.py` fetches them.
- **Tunebat** (website) for spot checks; **GetSongBPM** API for BPM/key (free key,
  requires a visible backlink - only if publishing).
- **No numbers?** Tag from knowledge of the song and mark `(est)`. Genre is a decent
  prior: house 120-128, techno 125-140, country 70-110 or 140+ half-time, metalcore
  high energy.

## 5. Output

Write the tags to `records/spotify/tags-YYYY-MM-DD.md` (or a JSON beside the snapshot):
`title | artist | corner | activity | energy | valence | bpm | key | message | source`.
Then propose groups as playlists, e.g. *Morning Country*, *Focus - City Pop & Jazz*,
*Workout 125-140*, *Drive*, *House Party*, *Wind-down*. Show the owner the proposed lists
before creating anything in Spotify.
