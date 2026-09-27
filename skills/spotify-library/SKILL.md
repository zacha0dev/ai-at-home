---
name: spotify-library
description: Export a whole Spotify library and every playlist's tracks into plain files, keep a dated record, build new playlists in bulk, and review songs by their message. Use for "go through my Spotify", "what's in my playlists", "export my playlists", "clean up my library", "any negative songs in my playlists", or "make these into playlists".
---

# Spotify library

The point is to see what's actually in the library, keep a record of it, and help the
owner shape it. For example, toward music with a positive message. **Nothing is removed
without the owner's say.**

## Where records go

Keep them in the project (e.g. `records/spotify/`):
- `library.md` - everything in Your Library (playlists, artists, albums, podcasts)
- `playlists.md` - every track in Liked Songs and each owned playlist: artist, album, date added
- `snapshots/YYYY-MM-DD-export.json` - the raw export, so later runs can diff what changed
- `review-YYYY-MM-DD.md` - the message review: flagged songs, why, and the owner's decisions

## Reading the account

Spotify's Web API needs an app and OAuth. The approach here uses **the web player the
owner is already signed in to**, driven by a browser-automation tool.

- **Never sign in for the owner, and never capture or reuse the login token** from the
  page to call the API. Read what the page renders.
- **Don't interrupt playback.** People often have music on while you work. Navigating the
  web player doesn't stop it; clicking a row's play button does. Navigate by URL.
- **Lists are virtualized.** Only ~30 rows exist in the page at once. Scroll the list's
  real scroll container (the ancestor with `overflow-y: auto|scroll`) and collect rows
  keyed by `aria-rowindex`. The grid's `aria-rowcount` includes the header row.
- **Library:** grid `aria-label="Your Library"`; each row has an element with id
  `listrow-title-spotify:<type>:<id>`.
- **Open a playlist without clicking:** `history.pushState({}, '', '/playlist/<id>')`,
  then dispatch a `popstate` event. Some playlist names have trailing spaces; compare
  trimmed.
- **Row fields:** title `a[href*="/track/"]`, artists `a[href*="/artist/"]`, album
  `a[href*="/album/"]`; date added and duration from the `gridcell`s. A row's `innerText`
  runs the columns together, so don't use it.
- **Long loops:** browser-tool JavaScript calls time out (~45 s). Start the loop without
  awaiting it, keep progress in a `window` variable, and poll.
- **Getting big data out:** tool output truncates. Run a tiny local receiver (Python
  `http.server` on 127.0.0.1 that answers CORS and `Access-Control-Allow-Private-Network`)
  and `fetch` POST the JSON to it. Nothing leaves the machine. The browser may ask
  permission for the page to reach a local address; the owner allows it.

## Building playlists in bulk

- **The web player can't add songs in bulk.** Create and name the playlist there, then
  fill it in the **desktop app**:
  put newline-separated `spotify:track:<id>` lines on the clipboard, open the playlist
  with `spotify:playlist:<id>`, wait ~7 s, focus the window, paste (Ctrl+V), wait ~12 s
  for big lists.
- **Verify every count** afterwards. A paste into a page that wasn't loaded yet fails
  silently; re-run just that one.
- **Mix (transitions)** is a toggle button named `Mix` on the playlist page (UI
  Automation Invoke works). Smart Reorder was not in the Windows app when this was
  written; order it yourself with the `playlist-flow` skill.
- **Replace a playlist's order:** click the duration area of any visible song row, Ctrl+A,
  Delete, confirm only if the dialog names the right playlist, then paste the new order.
- Browser password managers pop "save contact info" prompts when you type playlist names.
  Close them; never save.

## Judging a song's message

Judge the song's **theme** from knowledge of the song. **Never paste lyrics** into
records (copyright); a title and a one-line theme in your own words.

- **Keep** - uplifting, motivating, love, gratitude, fun, instrumental with no real message.
- **Review** - heartbreak that can drag the mood; drinking-to-escape party songs.
- **Tears down** - self-hatred, hopelessness, put-downs, glorified self-destruction.

Mark confidence; say "unknown - listen" rather than guess. Present the flags; the owner
decides. For tear-down songs with a great beat, use the `keep-the-beat` skill.

## Cleaning up (only on the owner's go-ahead)

Confirm the exact list, one playlist at a time. Prefer moving songs to an **Archive**
playlist over deleting. Spotify-made lists (Daily Mix, Radio, Discover Weekly) can only
be followed or unfollowed, not edited.

## Handy platform facts

- Recommendations learn from behaviour: plays, skips, likes and saves. "Hide song",
  "Don't play this artist" and **Exclude from your Taste Profile** are the direct controls.
- **Account -> Privacy -> Download your data** emails a zip including extended streaming
  history (takes days). It's the only way to get play counts over time.

## Related skills

`music-mood-grouping` (sort by mood), `playlist-flow` (order by tempo and key),
`keep-the-beat` (keep the sound, lose the message), `speaker-checkup` (play it on the
house speakers).
