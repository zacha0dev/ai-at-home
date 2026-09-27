---
name: playlist-flow
description: Put a playlist in a good listening order - energy arc, tempo steps, compatible keys, genre transitions - and apply it. Use for "make this playlist flow", "order this like a DJ set", "sort by tempo and key", or after music-mood-grouping builds a new group.
---


# Playlist flow

Mood fit matters more than perfect transitions (listeners rank order as a minor factor),
so group first (`music-mood-grouping`), then order. Don't over-engineer.

## 1. Shape: the energy arc

- **Open strong** - put a well-liked, bright track first.
- **Build** to a peak around 60-75% of the way through.
- **Vary the direction** - real albums alternate up and down more than they slope
  smoothly; avoid ten tracks in a row at the same energy.
- **Land calmer** - the last 10-15% cools down (unless it's a party list meant to loop).
- **Workout:** warm-up (~100-120 BPM) -> work (125-140) -> cool-down (< 110).
- **Focus / wind-down:** keep it flat and low; no sudden spikes.

## 2. Tempo steps

- Within **~4%** BPM: seamless.
- **4-8%**: fine if the energy stays similar.
- **> 8%**: bridge it - a half/double-time match counts (87 and 174 BPM are compatible),
  or put a track with a soft intro between them.
- For a normal streaming playlist, a 2:1 ratio is compatible.

## 3. Keys (Camelot wheel)

Keys are written as Camelot codes (1A-12A minor, 1B-12B major).

- **Safe:** same code; +/-1 on the same letter (8A -> 9A); same number, other letter
  (8A <-> 8B).
- **Energy lift:** +2 or +7 (8A -> 10A / 3A). **Energy drop:** -2.
- **Diagonal** (8B -> 9A) works; +4 is adventurous.
- Key clashes matter most in blended mixes and between long melodic intros/outros;
  they matter little across a hard cut.

## 4. Genre and era

Change **one thing at a time** per transition - genre, era, or tempo band - and use a
bridge track when two change at once (e.g. country -> country-EDM crossover like
*Beautiful Drug (Avicii remix)* -> house).

## 5. Let Spotify do the fine ordering

You can hand the last step to Spotify (Premium):
- **Mix** (Aug 2025): adds transitions (Auto, Fade, Rise...) and shows BPM and key in the
  playlist.
- **Smart Reorder** (Feb 2026): Mix -> Edit -> Smart Reorder reorders by BPM and key.

Workflow: build the arc (sections: opener, build, peak, cool-down) here; let Smart
Reorder polish within a section if you like the result; keep the opener and closer
pinned by hand.

## 6. Output

A numbered order with a short reason per section, e.g.
`1-4 warm-up (100-115 BPM, 8A-9B) | 5-14 build | 15-20 peak (128-132) | 21-24 cool-down`.
Reordering the real playlist in Spotify is a change to the account - show the order
and get the owner's go-ahead first.

## 7. Do it with the scripts

```
python features.py tracks.txt features.json      # free audio features (ReccoBeats)
python flow_order.py tracks.txt features.json ordered.txt
python flow_order.py tracks.txt features.json ordered.txt --flat   # focus / wind-down
```

`tracks.txt` is one `spotify:track:<id>` per line. `ordered.txt` pastes straight into a
playlist in the Spotify desktop app (see `spotify-library`). The script prints how many
neighbouring pairs have a smooth tempo step and a compatible key, before and after.
Songs without features are parked near the middle.
