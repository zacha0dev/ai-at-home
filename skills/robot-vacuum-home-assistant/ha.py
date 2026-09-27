"""ha.py - drive a Dreame robot vacuum (or anything else) through Home Assistant from your laptop.

    python ha.py status                 # vacuum state, battery, errors, consumables
    python ha.py start                  # clean everything
    python ha.py rooms 1 3              # clean rooms by id (see `status` for names)
    python ha.py pause | stop | dock | locate
    python ha.py call <domain> <service> '<json data>'   # anything else in HA

Config (environment variables, with defaults):
  HA_URL     http://homeassistant.local:8123
  HA_TOKEN   path to a file holding a long-lived access token (~/.config/home-assistant/token)
  HA_VACUUM  the vacuum entity id (vacuum.robot) - see Settings -> Entities in HA
Revoke the token any time in HA -> your profile -> Security. Stdlib only.
"""
import json
import os
import sys
import urllib.request

BASE = os.environ.get("HA_URL", "http://homeassistant.local:8123").rstrip("/") + "/api"
TOKEN = open(os.path.expanduser(os.environ.get("HA_TOKEN", "~/.config/home-assistant/token"))).read().strip()
VAC = os.environ.get("HA_VACUUM", "vacuum.robot")
PREFIX = VAC.split(".", 1)[1]


def api(path, data=None):
    req = urllib.request.Request(BASE + path, method="POST" if data is not None else "GET",
                                 data=None if data is None else json.dumps(data).encode(),
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def state(eid):
    return api("/states/" + eid)


def status():
    v = state(VAC)
    s = {e["entity_id"]: e["state"] for e in api("/states") if PREFIX in e["entity_id"]}
    g = lambda k: s.get("sensor.%s_%s" % (PREFIX, k), "?")
    print("vacuum: %s | status %s | battery %s%% | error %s" % (v["state"], g("status"), g("battery_level"), g("error")))
    print("parts left: main brush %s%%, side brush %s%%, filter %s%%, wheels %s%%" % (
        g("main_brush_left"), g("side_brush_left"), g("filter_left"), g("wheel_dirty_left")))
    print("cleans: %s, last %s" % (g("cleaning_count"), g("cleaning_history")[:10]))
    rooms = next(iter((v["attributes"].get("rooms") or {}).values()), [])
    print("rooms: " + ", ".join("%s=%s" % (r["id"], r["name"]) for r in rooms))


def call(domain, service, data):
    api("/services/%s/%s" % (domain, service), data)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        return status()
    if cmd == "start":
        call("vacuum", "start", {"entity_id": VAC})
    elif cmd in ("pause", "stop", "locate"):
        call("vacuum", cmd, {"entity_id": VAC})
    elif cmd == "dock":
        call("vacuum", "return_to_base", {"entity_id": VAC})
    elif cmd == "rooms":
        call("dreame_vacuum", "vacuum_clean_segment", {"entity_id": VAC, "segments": [int(x) for x in sys.argv[2:]]})
    elif cmd == "call":
        call(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]) if len(sys.argv) > 4 else {})
    else:
        sys.exit(__doc__)
    print("sent: " + cmd)


if __name__ == "__main__":
    main()
