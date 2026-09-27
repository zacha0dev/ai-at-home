"""features.py - fetch free audio features (energy, valence, tempo, key...) for Spotify tracks.

    python features.py tracks.txt features.json

Spotify closed its own audio-features API to new apps in Nov 2024. ReccoBeats
(https://reccobeats.com) is a free, keyless service that takes Spotify track IDs and
returns the same kind of numbers. Expect some tracks to come back empty.

Runs in small batches and honours 429 Retry-After. Re-running skips tracks already in
the output file, so an interrupted run just continues.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.reccobeats.com/v1/audio-features?ids="
BATCH = 40


def fetch(ids):
    req = urllib.request.Request(API + ",".join(ids), headers={"Accept": "application/json",
                                                              "User-Agent": "ai-at-home/features"})
    while True:
        try:
            data = json.load(urllib.request.urlopen(req, timeout=30))
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "5")) + 1)
                continue
            raise
    items = data.get("content", data) if isinstance(data, dict) else data
    out = {}
    for it in items or []:
        sid = (it.get("href") or "").rstrip("/").split("/")[-1]   # href is the open.spotify.com track link
        if sid:
            out[sid] = it
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    ids = list(dict.fromkeys(l.strip().split(":")[-1] for l in open(src, encoding="utf-8") if l.strip()))
    F = json.load(open(dst, encoding="utf-8")) if os.path.exists(dst) else {}
    todo = [i for i in ids if i not in F]
    for k in range(0, len(todo), BATCH):
        F.update(fetch(todo[k:k + BATCH]))
        json.dump(F, open(dst, "w", encoding="utf-8"))
        time.sleep(1)
    print("%d of %d tracks have features" % (sum(1 for i in ids if i in F), len(ids)))


if __name__ == "__main__":
    main()
