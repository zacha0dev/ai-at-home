"""flow_order.py - order a playlist by energy arc, tempo steps and Camelot-compatible keys.

    python flow_order.py tracks.txt features.json ordered.txt          # arc: build, peak ~70%, cool down
    python flow_order.py tracks.txt features.json ordered.txt --flat   # flat energy (focus, wind-down)

tracks.txt     one spotify:track:<id> per line (duplicates are dropped)
features.json  {track_id: {"energy", "valence", "tempo", "key", "mode", ...}} - see features.py
ordered.txt    the new order, ready to paste into a playlist in the Spotify desktop app

Greedy walk: each next song is the one closest to the target energy for its position,
with the smallest tempo jump and the most compatible key. Not optimal, but it sounds
right and runs instantly. Songs without features are parked just before the middle.
"""
import argparse
import json

# Spotify pitch class + mode -> Camelot number (letter B = major, A = minor)
MAJ = {0: 8, 1: 3, 2: 10, 3: 5, 4: 12, 5: 7, 6: 2, 7: 9, 8: 4, 9: 11, 10: 6, 11: 1}
MIN = {0: 5, 1: 12, 2: 7, 3: 2, 4: 9, 5: 4, 6: 11, 7: 6, 8: 1, 9: 8, 10: 3, 11: 10}


def camelot(f):
    if f.get("key") is None or f["key"] < 0:
        return None
    return (MAJ if f.get("mode") == 1 else MIN)[f["key"]], "B" if f.get("mode") == 1 else "A"


def key_cost(a, b):
    if not a or not b:
        return 1.0
    (n1, l1), (n2, l2) = a, b
    d = min((n1 - n2) % 12, (n2 - n1) % 12)
    if d == 0:
        return 0.0 if l1 == l2 else 0.3      # same key / relative major-minor
    if d == 1:
        return 0.3 if l1 == l2 else 0.6      # neighbour / diagonal
    if d == 2 and l1 == l2:
        return 0.8                            # energy lift or drop
    return 1.5 + 0.2 * d


def tempo_cost(t1, t2):
    if not t1 or not t2:
        return 1.0
    r = min(abs(t2 / t1 - 1), abs(2 * t2 / t1 - 1), abs(t2 / (2 * t1) - 1))   # half/double time counts
    return 0 if r <= 0.04 else (0.5 if r <= 0.08 else 1.5 + 5 * (r - 0.08))


def order(ids, F, arc=True):
    have = [i for i in ids if F.get(i)]
    missing = [i for i in ids if not F.get(i)]
    n = len(have)
    if n == 0:
        return ids
    es = sorted(F[i]["energy"] for i in have)
    lo, hi = es[int(0.15 * (n - 1))], es[int(0.9 * (n - 1))]

    def target(k):
        x = k / max(1, n - 1)
        if not arc:
            return (lo + hi) / 2
        return lo + (hi - lo) * (x / 0.7 if x <= 0.7 else (1 - x) / 0.3 * 0.8 + 0.2)

    # opener: a bright song near the starting energy
    start = min(have, key=lambda i: abs(F[i]["energy"] - target(0)) - 0.5 * F[i].get("valence", 0.5))
    seq, left = [start], set(have) - {start}
    while left:
        cur, tg = F[seq[-1]], target(len(seq))
        nxt = min(left, key=lambda i: 3.0 * abs(F[i]["energy"] - tg)
                  + tempo_cost(cur.get("tempo"), F[i].get("tempo"))
                  + key_cost(camelot(cur), camelot(F[i])))
        seq.append(nxt)
        left.discard(nxt)
    mid = int(len(seq) * 0.45)
    return seq[:mid] + missing + seq[mid:]


def smooth(seq, F):
    pairs = t = k = 0
    for a, b in zip(seq, seq[1:]):
        if F.get(a) and F.get(b):
            pairs += 1
            t += tempo_cost(F[a].get("tempo"), F[b].get("tempo")) <= 0.5
            k += key_cost(camelot(F[a]), camelot(F[b])) <= 0.6
    return pairs, t, k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tracks")
    ap.add_argument("features")
    ap.add_argument("out")
    ap.add_argument("--flat", action="store_true", help="keep energy level instead of an arc")
    a = ap.parse_args()
    F = json.load(open(a.features, encoding="utf-8"))
    uris = [l.strip() for l in open(a.tracks, encoding="utf-8") if l.strip()]
    ids = list(dict.fromkeys(u.split(":")[-1] for u in uris))
    new = order(ids, F, arc=not a.flat)
    open(a.out, "w", encoding="utf-8").write("\n".join("spotify:track:" + i for i in new) + "\n")
    p0, t0, k0 = smooth(ids, F)
    p1, t1, k1 = smooth(new, F)
    print("%d songs (%d duplicates dropped, %d without features)" % (len(ids), len(uris) - len(ids),
          sum(1 for i in ids if not F.get(i))))
    print("smooth tempo steps: %d%% -> %d%%   compatible keys: %d%% -> %d%%" % (
        100 * t0 // max(1, p0), 100 * t1 // max(1, p1), 100 * k0 // max(1, p0), 100 * k1 // max(1, p1)))


if __name__ == "__main__":
    main()
