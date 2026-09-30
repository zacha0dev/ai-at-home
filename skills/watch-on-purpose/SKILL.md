---
name: watch-on-purpose
description: Trade the endless scroll (YouTube, TikTok, Reels) for shows and films you actually pick and finish. The agent reads your streaming history (Hulu, Netflix, Max, Disney+... in a signed-in browser), builds a "personality pack" of your taste that it keeps learning, curates a finite watchlist, adds it to My List / My Stuff, and runs a little ritual around watching. Use for "what should I watch", "get me off YouTube", "build my watchlist", "I keep doom-scrolling", or "learn what I like".
---

# Watch on purpose

Short-form feeds are built to never end. A good show or film **ends**, which is the whole
point. This skill makes the agent your picky friend who knows your taste: it studies what you
already watch, keeps a living **personality pack** about you, and hands you a short list of
things worth finishing, so you open the app already knowing what you're there for.

## Ground rules

- Works in the browser where you're already signed in. Never signs in, never changes plans,
  add-ons or payment, never cancels.
- Adding titles to My List / My Stuff is fine (easy to undo). Anything account-level waits for
  you to say so.
- Your pack lives in a private file. Keep it out of anything public.

## 1. Read the room (15 minutes, once)

From the streaming site's home and list pages (`get_page_text` after scrolling to load rows):

- **Continue Watching**: what you actually return to.
- **My List / My Stuff**: what past-you meant to watch (and what you finished).
- **"Because you watched ..." rows**: the service's own guess at your taste. Useful and free.
- **Progress bars**: films abandoned at 40% say as much as favorites.

## 2. Build the personality pack

Fill `personality-pack.md` (template in this folder). It's a character sheet, not a profile:

| Stat | What it captures |
|---|---|
| **Home genre** | the lane you always drift back to (adult animation, anime, crime docs...) |
| **Comfort vs. challenge** | rewatch-cozy vs. "make me think"; most people want both, on different nights |
| **Attention budget** | 22-minute episodes, 45-minute dramas, or a 2.5-hour film tonight? |
| **Finish rate** | complete series you finished vs. abandoned; the most honest stat there is |
| **Hard no's** | genres, gore level, "no laugh tracks" |
| **Wildcards** | the one-offs that surprised you; they point to what to try next |

Add 3-5 quick questions if history is thin ("comfort show or something new tonight?").

## 3. Curate a bucket, not a feed

A **bucket** is 12-20 titles you've committed to, grouped so every mood has an answer:

- **Things with an ending**: limited series, finished shows, films. Prefer these.
- **Comfort picks**: rewatchable, low-stakes, and capped at a set number of episodes.
- **Stretch picks**: one or two slightly outside the home genre, chosen from the wildcards.
- **Finish what you started**: anything with a progress bar goes near the top.

Check each title is included in the plan. Search results say "ADD-ON" when it's an extra
subscription; skip those. Add the bucket to **My List / My Stuff**, then reload and confirm.
The checkmark right after clicking can be a hover state, not a save.

## 4. The ritual (this is what beats the scroll)

1. **Pick before you open the app**, from the bucket, not the home screen rows.
2. **Say the count out loud**: "two episodes" or "this film". Turn **autoplay off** in the
   app's settings.
3. **Log it when you finish**: title, one line, 1-5 stars. The agent updates the pack.
4. Keep YouTube for *search* (a specific how-to), never the home feed.

## 5. The pack keeps learning

Every finished title updates the pack: star ratings shift the genre weights, abandoned titles
lower them, and the "finish rate" stat keeps you honest. Once a month, ask the agent for a
**taste report**: what's trending up, what you've outgrown, and three new picks from the
wildcards.

## Streaming-site notes (Hulu, September 2026)

- `/search?q=...` in the URL doesn't run a search. Click the search box and type.
- Search results open on the **thumbnail**; the first click sometimes doesn't take.
- The details window's **+** sits next to the play button and turns into a ✓.
