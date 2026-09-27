# Turning a messy Spotify library into 9 playlists that flow

**Skills:** [`spotify-library`](../skills/spotify-library/SKILL.md),
[`music-mood-grouping`](../skills/music-mood-grouping/SKILL.md),
[`keep-the-beat`](../skills/keep-the-beat/SKILL.md),
[`playlist-flow`](../skills/playlist-flow/SKILL.md)

## The problem

Years of saving songs: country, house, techno, party rap, rock, jazz, city pop, festival
sets. About 1,800 songs across dozens of playlists, one catch-all list over 600 songs
long. The goal wasn't just tidier playlists. The listener keeps a positive headspace on
purpose and wanted to know which songs carried a message that pulls the other way.

## 1. Get it all into files

The agent read the library from the web player the owner was already signed in to. No
API keys and no login tokens. It scrolled every virtualized list and collected rows,
then posted the export to a tiny receiver running on the same laptop, since tool output
can't carry a big JSON. The result: one dated snapshot of every song and playlist.

## 2. Judge the message, not just the sound

Every song got a one-line theme and a verdict (keep / review / tears down), from
knowledge of the song. **No lyrics were copied anywhere.** About 24 songs landed in "tears
down" and 41 in "review". For the ones with a great beat, the `keep-the-beat` skill looks
for an instrumental, a dub mix, the sampled original, or a sound-alike with a better
message before anything gets archived.

## 3. Sort by mood and activity

Spotify closed its own audio-features API to new apps, so the numbers came from
ReccoBeats, a free service. It had features for 1,304 of 1,655 tracks; genre filled
the gaps, marked as estimates. Each song got a mood corner (energy × brightness) and an
activity. A dry run proposed 8 playlists plus an Archive, then got renamed together:
Coffee & Country, Windows Down, No Days Off, Dancefloor Therapy, After Hours, Good Energy
Only, Flow State, Low Tide, and The Vault.

## 4. Build them in bulk

The web player can't paste songs in bulk, but the desktop app can. The agent put the
track links on the clipboard and pasted them into each new playlist. Two pastes
silently missed because the page wasn't loaded yet; checking every count caught them.

## 5. Make them flow

`flow_order.py` reorders each list like a DJ would: build energy to a peak about 70% of
the way in, keep tempo jumps small (half and double time count as matches), and keep
neighbouring songs in compatible keys (Camelot wheel). On one list, smooth tempo steps
went from **11% to 80%** of neighbouring pairs and compatible keys from **25% to 68%**.
Then Spotify's **Mix** transitions were switched on for every list.

## Lessons

- Verify every bulk action by count. "It said it worked" isn't the same as it working.
- Spotify's Smart Reorder wasn't in the Windows app, so ordering it ourselves was faster
  than hunting for it.
- The agent never removed a song. It flagged; the owner decided.
