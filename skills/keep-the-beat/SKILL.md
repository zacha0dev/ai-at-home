---
name: keep-the-beat
description: Judge a song's message (uplifting / neutral / tears down) without reproducing lyrics, and when the message is bad but the beat is good, find a way to keep the beat - instrumental, dub or club mix, the sampled original, or a sound-alike with a better message. Use for "is this song negative", "I like the beat but not the words", or tear-down songs flagged in a library review.
---


# Keep the beat, lose the message

Some people keep a positive, motivating mindset on purpose. Some songs you can't
stand lyrically anymore, but the production works in the right context. This skill separates
the two.

## 1. Judge the message (responsibly)

- **Never paste lyrics** into records or chat (copyright). A few words, quoted, at most.
- Sources for what a song is about: Genius song descriptions and annotations (the API
  gives these, not lyrics), Spotify's *About the Song* cards (Premium beta), artist
  interviews, Wikipedia song articles, and plain knowledge of the song.
- Record: a **one-line theme in your own words** + a verdict:
  - **Uplifting** - motivating, grateful, loving, fun.
  - **Neutral** - no real message, or instrumental. Most house and techno.
  - **Tears down** - hopelessness, self-harm, self-loathing, drugs as identity,
    put-downs of women or of yourself, violence, spite as the point.
- Mark confidence; say "unknown - listen" rather than guess.

Why it matters: prosocial lyrics raise empathy and mood
(Greitemeyer 2009); violent lyrics raise hostile thoughts even in humorous songs
(Anderson 2003); choosing sad music tends to deepen low mood (Garrido & Schubert 2015);
motivating lyrics can prompt positive self-talk in exercise.

## 2. If the message tears down but the beat is good, in this order

1. **Instrumental or dub version.** Search Spotify for `"<title> instrumental"`,
   `dub`, `club mix`, `extended`. Dubs keep the groove with only vocal fragments; common
   for house/EDM, patchier for country and metalcore.
2. **The sampled original** - Spotify's **SongDNA** (Premium, Mar 2026) shows samples,
   covers and credits.
3. **A sound-alike with a better message** - same BPM band, key (Camelot neighbour) and
   energy. Find candidates with Tunebat's advanced search (key + BPM) or ReccoBeats
   features, then check the new song's message.
4. **Context-only keep** - if nothing replaces it and you still want it, keep it only in
   a list where words don't land (a loud party mix), and note it. Passive listening
   still has an effect, so this is the last option.
5. Otherwise **remove** (move to an *Archive* playlist rather than delete).

Note: the **explicit-content toggle** and "clean" edits only remove swear words. They do
not change what a song is about.

## 3. Teach the algorithm

For songs you drop, suggest **Exclude from your Taste Profile** (per track, since Oct
2025) so they stop shaping recommendations and Wrapped, and **Hide** for songs inside
Spotify-made or other people's playlists.

## 4. Output

Add the verdict and the chosen action to the review file
(e.g. `review-YYYY-MM-DD.md`, "Decision" column), e.g.
`Tears down | swap -> dub mix | ` or `Tears down | archive | exclude from taste profile`.
Changes in Spotify happen only after the owner confirms the list.
