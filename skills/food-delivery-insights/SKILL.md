---
name: food-delivery-insights
description: Turn a food delivery app (Uber Eats) into data you own - every restaurant that delivers to you with rating, ETA, delivery fee and deal, every menu item with its price, a "best meals" report (deal-adjusted value, healthy, high-protein, vegan, fast), price tracking over time, and a summary of your own order history (what fees and tips really add). Read-only. Use for "what's good near me on Uber Eats", "find the best deals", "what should I order", "how much am I spending on delivery".
---

# Food delivery insights (Uber Eats)

The app shows you a few rows of restaurants and one menu at a time. Pulled out as data, the
same information answers better questions: *which meal is actually the best value once the
buy-one-get-one is counted? which "$0.49 delivery" places tack on big fees? what does my
usual order really cost?*

## Ground rules

- **Read only.** The agent never adds to a cart, orders, or touches payment or subscription
  sign-ups.
- It works in the browser where **you** are already signed in. No passwords, no tokens copied
  out.
- Saving the results is a file download, so the agent asks before each one.

## How it works

Everything runs inside your signed-in Uber Eats tab, through the same JSON calls the website
makes for itself (with the agent's browser JavaScript tool). That's much cleaner than scraping
the screen:

- **Menus:** `POST /_p/api/getStoreV1?localeCode=en-US` with `{"storeUuid": ...}` and a header
  `x-csrf-token: x`. The store UUID is hidden in plain sight: the id in `/store/<name>/<id>` is
  the UUID's 16 bytes in base64url. `capture.js` decodes it.
- **Your orders:** on the Orders page, `POST /_p/api/getPastOrdersV1?localeCode=en-US` with
  `{"lastWorkflowUUID": ""}` for the first page, then **the last order's uuid from the previous
  page**. The response also has a `nextCursor`. It looks like the pager, but sending it back
  just returns page one again.

`capture.js` collects every store on your feed, pulls each menu (spaced ~0.7 s apart; about
3 minutes for 140 stores), and saves one JSON file. `analyze.py` turns it into:

- **Best value meals, deal-adjusted:** an item in a "Buy 1, get 1" section counts at half price
  per meal.
- **Healthy, high-protein, vegan, fast-and-cheap** lists (keyword filters on the menu text).
- **Places by typical meal price**, and **fee traps** (delivery fee $5+).
- `stores-history.csv`: one row per restaurant per capture. Run it again next month and
  price creep and rotating deals show up.

## What it found in one real run (a US college-town suburb)

- ~140 stores delivered to one address: about 100 restaurants, the rest retail and grocery.
- Most restaurants had a $0.49 delivery fee; a handful charged $5-12 for the same distance.
- Median "real meal" on the menu: about $16.
- In a real order history, the final bill ran **roughly 1.3-1.5x the menu price** once service
  fees, tax and tip were added. That's the number to remember when a menu price looks fine.
- Buy-one-get-one sections changed the ranking more than anything else: a $15 entrée at BOGO
  beats most $9 "value" items.

## Browser-tool gotchas (cost real time)

- The JS tool returns only ~2 KB and **blocks results that contain URLs with query strings**.
  Return counts and picked fields; keep the bulk in `window.*`.
- A long loop keeps running after the tool's ~45 s timeout. Poll a counter.
- To get megabytes out, build a `Blob` and download it (with the owner's OK), then move the file.

## Limits

- "Meal", "healthy" and "high-protein" are keyword guesses, not nutrition data. Protein
  add-ons priced like a meal can slip in.
- Delivery-menu prices are often 10-20% above in-store; pickup is the cheap version.
- These are the website's internal calls. They can change without notice; the shapes above
  worked in September 2026.
