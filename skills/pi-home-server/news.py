"""
news.py - a 24/7 news collector for a Raspberry Pi (or any always-on box).

Standard library only: no pip install, no API key, no account. Public RSS feeds.
Run it every 30 minutes from cron and it keeps a rolling 14-day store of headlines,
sorted into lanes, lightly ranked by keywords you choose.

The point is FETCHING, not NOTIFYING. It quietly keeps itself current; you (or your AI
agent) ask it what happened when you want to know. Nothing pings you.

Run:  python3 news.py              # fetch once, update store.json
      python3 news.py --top 5      # also print the top items
      python3 news.py --lane ai    # top items for one lane
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(ROOT, "store.json")
UA = "Mozilla/5.0 (compatible; news-desk/1.0)"
KEEP_DAYS = 14
TIMEOUT = 20

FEEDS = {
    # lane: [(source name, public RSS/Atom URL)] - edit freely
    "ai": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("HN 200+", "https://hnrss.org/frontpage?points=200"),
    ],
    "world": [
        ("BBC world", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("NPR", "https://feeds.npr.org/1001/rss.xml"),
    ],
    "economy": [
        ("Fed press", "https://www.federalreserve.gov/feeds/press_monetary.xml"),
        ("WSJ markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
    ],
    "science": [
        ("NASA", "https://www.nasa.gov/news-release/feed/"),
        ("Science Daily", "https://www.sciencedaily.com/rss/top.xml"),
    ],
}

# Words that make an item matter MORE to you. Keep it small and readable -
# a ranking nobody can explain is a ranking nobody trusts. Edit to taste.
WEIGHTS = {
    "federal reserve": 5, "interest rate": 5, "inflation": 4, "recession": 4,
    "anthropic": 4, "claude": 4, "openai": 3, "llm": 2, "agent": 2,
    "raspberry pi": 3, "open source": 2, "security": 2, "breach": 3,
    "storm": 3, "hurricane": 4, "earthquake": 4, "election": 3,
}


def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = (s.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
          .replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", s).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def parse(raw):
    """Handle RSS and Atom without a dependency."""
    root = ET.fromstring(raw)
    out = []
    for it in root.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        g = {}
        for ch in it:
            g.setdefault(ch.tag.split("}")[-1], ch)
        title = clean(g["title"].text if "title" in g else "")
        if not title:
            continue
        link = ""
        if "link" in g:
            link = g["link"].get("href") or clean(g["link"].text) or ""
        when = ""
        for k in ("pubDate", "published", "updated", "date"):
            if k in g and g[k].text:
                when = g[k].text.strip()
                break
        summary = ""
        for k in ("description", "summary", "content"):
            if k in g and g[k].text:
                summary = clean(g[k].text)[:400]
                break
        out.append(dict(title=title, link=link, when=when, summary=summary))
    return out


def score(item):
    hay = (item["title"] + " " + item["summary"]).lower()
    return sum(w for k, w in WEIGHTS.items() if k in hay)


def load():
    if not os.path.exists(STORE):
        return {"items": {}, "runs": []}
    try:
        return json.load(open(STORE, encoding="utf-8"))
    except Exception:
        return {"items": {}, "runs": []}


def save(db):
    tmp = STORE + ".tmp"
    json.dump(db, open(tmp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    os.replace(tmp, STORE)       # atomic; a half-written store is worse than a stale one


def run():
    db = load()
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.isoformat(timespec="seconds")
    added, errors = 0, []

    for lane, feeds in FEEDS.items():
        for name, url in feeds:
            try:
                items = parse(fetch(url))
            except Exception as e:
                errors.append(f"{lane}/{name}: {type(e).__name__}")
                continue
            for it in items:
                key = hashlib.sha1((it["link"] or it["title"]).encode()).hexdigest()[:16]
                if key in db["items"]:
                    continue
                db["items"][key] = dict(
                    lane=lane, source=name, title=it["title"], link=it["link"],
                    summary=it["summary"], when=it["when"], seen=stamp,
                    score=score(it))
                added += 1

    cutoff = (now - dt.timedelta(days=KEEP_DAYS)).isoformat(timespec="seconds")
    before = len(db["items"])
    db["items"] = {k: v for k, v in db["items"].items() if v.get("seen", "") >= cutoff}
    dropped = before - len(db["items"])

    db["runs"] = (db.get("runs", []) + [dict(at=stamp, added=added, dropped=dropped,
                                             total=len(db["items"]), errors=errors)])[-200:]
    save(db)
    return added, dropped, len(db["items"]), errors


def top(db, lane=None, n=5, hours=24):
    cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)).isoformat(timespec="seconds")
    rows = [v for v in db["items"].values()
            if v.get("seen", "") >= cut and (lane is None or v["lane"] == lane)]
    rows.sort(key=lambda r: (-r["score"], r.get("seen", "")))
    return rows[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0, help="also print the top N items")
    ap.add_argument("--lane", choices=list(FEEDS), help="limit --top to one lane")
    ap.add_argument("--hours", type=int, default=24)
    a = ap.parse_args()

    added, dropped, total, errors = run()
    print(f"news-desk: +{added} new, -{dropped} aged out, {total} held"
          + (f" | {len(errors)} feed error(s): {'; '.join(errors)}" if errors else ""))

    if a.top:
        db = load()
        for r in top(db, a.lane, a.top, a.hours):
            print(f"  [{r['lane']:7}] {r['score']:>2}  {r['title'][:95]}")


if __name__ == "__main__":
    main()
