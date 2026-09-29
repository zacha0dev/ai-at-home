// capture.js - run inside your signed-in Uber Eats feed tab (your saved address, Delivery).
// Step 1 collects every store on the feed; step 2 pulls each menu through the site's own
// getStoreV1 call (same session, ~1.3 s per store, ~3 min for 139); step 3 saves one JSON
// download (the owner approves the download). Save it as menus-<date>.json (gzip -9 is fine),
// and run `python analyze.py menus-<date>.json.gz`.
//
// Browser-tool notes: returned strings are capped ~2 KB and anything carrying URLs with query
// strings is blocked, so return only counts; the loop outlives the 45 s eval timeout - poll
// `window.__all.length` until it equals `window.__stores.length`.

function uuid(id) {                       // store id in the URL is base64url of the UUID bytes
  let b = id.replace(/-/g, '+').replace(/_/g, '/'); while (b.length % 4) b += '=';
  const h = [...atob(b)].map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

// 1. stores on the feed (scroll to load them all)
for (let i = 0; i < 6; i++) { window.scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 1200)); }
const m = new Map();
document.querySelectorAll('a[href^="/store/"]').forEach(a => {
  const p = a.getAttribute('href').split('?')[0].split('/'); const id = p[3]; if (!id) return;
  let card = a.closest('div'); for (let k = 0; k < 4 && card && card.innerText.length < 40; k++) card = card.parentElement;
  const txt = (card ? card.innerText : a.innerText).replace(/\n+/g, ' | ');
  const prev = m.get(id); if (!prev || txt.length > prev.card.length) m.set(id, { slug: p[2], uuid: uuid(id), card: txt.slice(0, 220) });
});
window.__stores = [...m.values()];

// 2. menus
function items(d) {
  const out = [], seen = new Set();
  (function walk(o, sec) {
    if (!o || typeof o !== 'object') return;
    if (Array.isArray(o)) { o.forEach(x => walk(x, sec)); return; }
    let s = sec; if (o.standardItemsPayload && o.standardItemsPayload.title) s = o.standardItemsPayload.title.text || s;
    if (typeof o.title === 'string' && typeof o.price === 'number' && o.uuid) {
      if (!seen.has(o.uuid)) { seen.add(o.uuid); out.push({ sec: s || '', t: o.title, p: o.price / 100, d: (o.itemDescription || '').replace(/\s+/g, ' ').slice(0, 200) }); }
      return;
    }
    for (const k in o) { if (/image|url|tracking|analytics/i.test(k)) continue; walk(o[k], s); }
  })(d.catalogSectionsMap || {}, '');
  return out;
}
window.__all = [];
for (const s of window.__stores) {
  try {
    const r = await fetch('/_p/api/getStoreV1?localeCode=en-US', { method: 'POST', credentials: 'include',
      headers: { 'content-type': 'application/json', 'x-csrf-token': 'x' }, body: JSON.stringify({ storeUuid: s.uuid }) });
    const d = (await r.json()).data; if (!d || !d.title) continue;
    window.__all.push({ name: d.title, slug: s.slug, address: d.location && d.location.address, cuisines: d.cuisineList,
      priceBucket: d.priceBucket, rating: d.rating && d.rating.ratingValue, reviews: d.rating && d.rating.reviewCount,
      eta: d.etaRange && d.etaRange.text, serviceFee: d.fareInfo && d.fareInfo.serviceFee, isOpen: d.isOpen,
      feedCard: s.card, items: items(d) });
  } catch (e) { }
  await new Promise(r => setTimeout(r, 700));
}

// 3. save (download - ask first)
const day = new Date().toISOString().slice(0, 10);
const blob = new Blob([JSON.stringify({ captured: new Date().toISOString(), address: "saved address",
  diningMode: 'DELIVERY', feedStores: window.__stores.length, stores: window.__all })], { type: 'application/json' });
const l = document.createElement('a'); l.href = URL.createObjectURL(blob); l.download = `ubereats-menus-${day}.json`;
document.body.appendChild(l); l.click(); l.remove();
