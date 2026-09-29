"""analyze.py - turn an Uber Eats menu capture into a meal-value report + a tracking row per store.

    python analyze.py menus-2026-09-29.json.gz

Writes (same folder):
  report-<date>.md     meal-perspective read: cheapest real meals, deal-adjusted meals, healthy /
                       high-protein picks, fastest, fee traps - with simple filters applied
  stores-history.csv   one row per store per capture (append) - rating, ETA, fee, deal, meal
                       prices - so price and deal changes show up over time

Capture: the Uber Eats feed in the owner's signed-in browser (delivery), each store's menu via the
site's own getStoreV1 call from inside the page, saved as a download. See SKILL.md.
"""
import csv
import gzip
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else "menus-2026-09-29.json"
path = os.path.join(HERE, src)
data = json.load(gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") else open(path, encoding="utf-8"))
day = data["captured"][:10]

NOT_MEAL = re.compile(r"(?i)\b(drink|beverage|soda|coke|sprite|pepsi|tea|coffee|latte|juice|water|lemonade|"
                      r"smoothie|shake|dessert|cookie|brownie|cake|churro|ice cream|sweet|side|chips|fries|sauce|"
                      r"dressing|dip|extra|add[- ]on|kids?|napkin|utensil|cup of|bag|cutlery|topping|modifier)\b")
MEAL_WORD = re.compile(r"(?i)\b(bowl|plate|platter|combo|meal|entree|entrée|burrito|wrap|sandwich|sub|burger|"
                       r"pizza|pasta|ramen|pho|curry|tacos?|quesadilla|salad|poke|hibachi|teriyaki|gyro|"
                       r"chicken|steak|salmon|shrimp|rice|noodle|bento|roll)\b")
HEALTHY = re.compile(r"(?i)\b(bowl|salad|grilled|quinoa|poke|greens|veggie|vegetable|lean|brown rice|"
                     r"protein|power|fit|light|sashimi|pho|mediterranean)\b")
PROTEIN = re.compile(r"(?i)\b(high protein|protein|double (meat|chicken|steak)|grilled chicken|chicken breast|"
                     r"steak|salmon|tuna|shrimp|turkey|egg whites?)\b")
FRIED = re.compile(r"(?i)\b(fried|crispy|tempura|breaded|battered)\b")
VEG = re.compile(r"(?i)\b(vegan|vegetarian|plant[- ]based|tofu|impossible|beyond)\b")
PROMO_SEC = re.compile(r"(?i)^(buy 1, get 1|bogo|picked for you|order again|popular|featured|most ordered|deals?)")


def money(s, label):
    m = re.search(r"\$(\d+(?:\.\d\d)?) " + label, s or "")
    return float(m.group(1)) if m else None


def deal_of(card, name):
    parts = [p.strip() for p in (card or "").split("|")]
    if len(parts) > 1 and parts[0] == name and parts[1] and parts[1] != name and "Delivery Fee" not in parts[1]:
        return parts[1]
    return ""


def eta_min(e):
    m = re.match(r"(\d+)", e or "")
    return int(m.group(1)) if m else None


RETAIL = re.compile(r"(?i)grocery|retail|pharmacy|convenience|beauty|pet|electronics|alcohol|liquor|flowers|gift|home|office")
rows, meals = [], []
for s in data["stores"]:
    if RETAIL.search(", ".join((s.get("cuisines") or [])[:2])):
        continue
    fee = money(s.get("feedCard"), "Delivery Fee")
    deal = deal_of(s.get("feedCard"), s["name"])
    bogo_titles = {i["t"] for i in s["items"] if re.match(r"(?i)buy 1, get 1", i["sec"])}
    store_meals = []
    for i in s["items"]:
        text = "%s %s %s" % (i["sec"], i["t"], i["d"])
        if not (8 <= i["p"] <= 45):            # under $8 = single taco / side / add-on; over $45 = party tray
            continue
        if NOT_MEAL.search(i["t"] + " " + ("" if PROMO_SEC.match(i["sec"]) else i["sec"])):
            continue
        if not MEAL_WORD.search(text):
            continue
        m = {"store": s["name"], "item": i["t"], "price": i["p"], "sec": i["sec"], "desc": i["d"],
             "bogo": i["t"] in bogo_titles, "fee": fee, "eta": eta_min(s.get("eta")),
             "rating": s.get("rating"), "cuisine": ", ".join((s.get("cuisines") or [])[:3]),
             "healthy": bool(HEALTHY.search(text)) and not FRIED.search(text),
             "protein": bool(PROTEIN.search(text)), "veg": bool(VEG.search(text))}
        m["each"] = round(m["price"] / 2, 2) if m["bogo"] else m["price"]   # per meal if BOGO
        store_meals.append(m)
    meals += store_meals
    prices = sorted(m["price"] for m in store_meals)
    rows.append({"date": day, "store": s["name"], "slug": s["slug"], "cuisine": ", ".join((s.get("cuisines") or [])[:3]),
                 "price_bucket": s.get("priceBucket") or "", "rating": s.get("rating") or "",
                 "reviews": s.get("reviews") or "", "eta": s.get("eta") or "", "delivery_fee": fee if fee is not None else "",
                 "deal": deal, "menu_items": len(s["items"]), "meals": len(prices),
                 "meal_min": prices[0] if prices else "", "meal_median": round(statistics.median(prices), 2) if prices else "",
                 "open": s.get("isOpen"), "address": s.get("address") or ""})

hist = os.path.join(HERE, "stores-history.csv")
new = not os.path.exists(hist)
with open(hist, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    if new:
        w.writeheader()
    w.writerows(rows)


def good(m):                                   # the default filter: decent place, not a fee trap
    return (m["rating"] or 0) >= 4.5 and (m["fee"] is None or m["fee"] <= 2.49)


def table(ms, n=12):
    out = ["| Meal | Place | Price | Per meal | Fee | ETA | ★ |", "|---|---|---|---|---|---|---|"]
    seen = set()
    for m in ms:
        k = (m["store"], m["item"])
        if k in seen:
            continue
        seen.add(k)
        out.append("| %s | %s | $%.2f | %s | %s | %s | %s |" % (
            m["item"][:48], m["store"][:30], m["price"], ("**$%.2f** (BOGO)" % m["each"]) if m["bogo"] else "",
            ("$%.2f" % m["fee"]) if m["fee"] is not None else "?", ("%s min" % m["eta"]) if m["eta"] else "?", m["rating"] or ""))
        if len(out) - 2 >= n:
            break
    return "\n".join(out)


G = [m for m in meals if good(m)]
all_prices = [m["price"] for m in meals]
L = []
L.append("# Food delivery around you - meal value read (%s)\n" % day)
L.append("Captured %s: **%d stores, %d menu items, %d of them look like a full meal** ($8-45 at a restaurant, not a side / drink / "
         "dessert / add-on). Median meal price across everything: **$%.2f**. Prices are menu prices: Uber's service fee, "
         "tax and tip come on top (roughly +25-35%% on a single meal).\n" % (
             day, len(rows), sum(r["menu_items"] for r in rows), len(meals), statistics.median(all_prices)))
L.append("Default filter below: **rating 4.5+ and delivery fee $2.49 or less.** \"Per meal\" halves the price when the "
         "item is in a Buy 1, get 1 section (two meals for one price).\n")
L.append("## Best value meals, deal-adjusted\n" + table(sorted(G, key=lambda m: m["each"]), 15) + "\n")
L.append("## Buy-one-get-one: what two meals actually cost\n" + table(sorted([m for m in G if m["bogo"]], key=lambda m: m["each"]), 12) + "\n")
L.append("## Healthy picks (bowls, salads, grilled, poke; not fried), cheapest first\n" + table(sorted([m for m in G if m["healthy"]], key=lambda m: m["each"]), 15) + "\n")
L.append("## High-protein picks, cheapest first\n" + table(sorted([m for m in G if m["protein"] and not FRIED.search(m['item'] + ' ' + m['desc'])], key=lambda m: m["each"]), 12) + "\n")
L.append("## Vegan / vegetarian\n" + table(sorted([m for m in G if m["veg"]], key=lambda m: m["each"]), 10) + "\n")
L.append("## Fast (<= 15 min) and under $15 per meal\n" + table(sorted([m for m in G if m["eta"] and m["eta"] <= 15 and m["each"] <= 15], key=lambda m: (m["eta"], m["each"])), 12) + "\n")

L.append("## Places by typical meal price (median), 4.5+ rated\n\n| Place | Cuisine | Typical meal | Cheapest meal | Fee | ETA | Deal |\n|---|---|---|---|---|---|---|")
for r in sorted([r for r in rows if r["meal_median"] != "" and (r["rating"] or 0) >= 4.5], key=lambda r: r["meal_median"])[:30]:
    L.append("| %s | %s | $%.2f | $%.2f | %s | %s | %s |" % (r["store"][:30], r["cuisine"][:24], r["meal_median"], r["meal_min"],
             ("$%.2f" % r["delivery_fee"]) if r["delivery_fee"] != "" else "?", r["eta"], r["deal"]))
traps = [r for r in rows if r["delivery_fee"] != "" and r["delivery_fee"] >= 5]
L.append("\n## Fee traps (delivery fee $5+)\n\n" + ", ".join("%s ($%.2f)" % (r["store"], r["delivery_fee"]) for r in sorted(traps, key=lambda r: -r["delivery_fee"])) + "\n")
L.append("## How to use / refresh\n\n- Everything behind this is in `menus-%s.json` (full menus, prices, descriptions).\n"
         "- `stores-history.csv` gets one row per store per capture; compare captures to see price creep and which "
         "deals rotate.\n- Refresh: re-run the capture (README), then `python analyze.py menus-<date>.json`.\n" % day)
open(os.path.join(HERE, "report-%s.md" % day), "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("stores %d | meals %d | good %d | report-%s.md | history rows +%d" % (len(rows), len(meals), len(G), day, len(rows)))
