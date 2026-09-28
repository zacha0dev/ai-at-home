"""thermostat.py - read and set a thermostat through Home Assistant from your laptop.

    python thermostat.py                 # mode, inside temp, target, humidity, running?
    python thermostat.py 72              # set the target temperature
    python thermostat.py cool            # cool | heat | off | auto (= heat_cool)
    python thermostat.py vacation on|off # toggle input_boolean.vacation_mode (see automations.yaml)
    python thermostat.py clear-hold      # press the thermostat's clear-hold button, if it has one

Config (environment variables, with defaults):
  HA_URL      http://homeassistant.local:8123
  HA_TOKEN    path to a file holding a long-lived access token (~/.config/home-assistant/token)
  HA_CLIMATE  the thermostat entity id (climate.home)
Stdlib only.
"""
import json
import os
import sys
import time
import urllib.request

BASE = os.environ.get("HA_URL", "http://homeassistant.local:8123").rstrip("/") + "/api"
TOKEN = open(os.path.expanduser(os.environ.get("HA_TOKEN", "~/.config/home-assistant/token"))).read().strip()
CLIMATE = os.environ.get("HA_CLIMATE", "climate.home")
NAME = CLIMATE.split(".", 1)[1]
MODES = {"cool": "cool", "heat": "heat", "off": "off", "auto": "heat_cool"}


def api(path, data=None):
    req = urllib.request.Request(BASE + path, method="POST" if data is not None else "GET",
                                 data=None if data is None else json.dumps(data).encode(),
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def call(domain, service, **data):
    return api("/services/%s/%s" % (domain, service), data)


def status():
    s = api("/states/" + CLIMATE)
    a = s["attributes"]
    print("mode %s | now %s | target %s | humidity %s | %s | fan %s" % (
        s["state"], a.get("current_temperature"), a.get("temperature"),
        a.get("current_humidity"), a.get("hvac_action", "?"), a.get("fan_mode", "?")))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg.replace(".", "", 1).isdigit():
        call("climate", "set_temperature", entity_id=CLIMATE, temperature=float(arg))
    elif arg in MODES:
        call("climate", "set_hvac_mode", entity_id=CLIMATE, hvac_mode=MODES[arg])
    elif arg == "vacation":
        if len(sys.argv) > 2:
            call("input_boolean", "turn_" + sys.argv[2], entity_id="input_boolean.vacation_mode")
        print("vacation mode:", api("/states/input_boolean.vacation_mode")["state"])
    elif arg == "clear-hold":
        call("button", "press", entity_id="button.%s_clear_hold" % NAME)
    elif arg:
        sys.exit(__doc__)
    if arg:
        time.sleep(3)
    status()


if __name__ == "__main__":
    main()
