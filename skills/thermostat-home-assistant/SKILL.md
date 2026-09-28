---
name: thermostat-home-assistant
description: Control a smart thermostat (ecobee, or any HomeKit-capable thermostat) from your AI agent through Home Assistant - locally, with no thermostat cloud account or developer key. Pair it over HomeKit, read temperature / humidity / whether it's running, set the target and mode, run a daily schedule and a vacation mode as Home Assistant automations. Use for "set the AC to 72", "is the AC running", "make it cooler at night", "vacation mode", or "connect my thermostat to Home Assistant".
---

# Thermostat through Home Assistant (HomeKit, local)

## Why HomeKit, not the thermostat's cloud

ecobee stopped issuing developer API keys, so the `ecobee` cloud integration card that Home
Assistant shows is a dead end for new setups. Most ecobee models (and many others) speak
**HomeKit**, and Home Assistant's **HomeKit Controller** integration pairs with them directly
on your network: no account, no key, no cloud in the loop. Ignore the cloud card.

You need Home Assistant running (the `robot-vacuum-home-assistant` skill covers a Raspberry Pi
setup) and a long-lived access token in a private file.

## Pair it (the one gotcha that costs an evening)

1. On the thermostat: **Main Menu -> Settings -> HomeKit**. It shows an 8-digit code and a QR.
2. **The code changes every time that screen opens.** A photo taken earlier, or a code from
   a previous visit to the screen, fails with `authentication_error`. Open the screen, then
   type the code that's on it *right now*.
3. In Home Assistant the thermostat is usually already discovered ("Home (Thermostat)").
   Add it and enter the code as `XXX-XX-XXX`.
4. HomeKit allows **one** controller. If it's already in Apple Home, remove it there (or reset
   HomeKit pairing on the thermostat) first. To get it back into Apple Home later, expose it
   through Home Assistant's own HomeKit Bridge.

You get a `climate.<name>` entity (modes off / heat / cool / heat_cool, target temperature,
fan on / auto), temperature and humidity sensors, a **clear hold** button, and a select for
the thermostat's own comfort settings (home / sleep / away).

## Drive it

```
python thermostat.py                 # mode, inside temp, target, humidity, running or idle
python thermostat.py 72              # set the target (your HA units)
python thermostat.py cool            # cool | heat | off | auto (= heat_cool)
python thermostat.py vacation on     # hold the vacation temperature, pause the schedule
python thermostat.py clear-hold      # hand control back to the thermostat's own schedule
```

Config via environment variables: `HA_URL`, `HA_TOKEN` (path to the token file),
`HA_CLIMATE` (e.g. `climate.home`). Stdlib only.

Changing the temperature is a change in someone's house: the agent does it when asked.
Reading it is always fine.

## Schedules: let Home Assistant own them

- Setting a temperature from Home Assistant creates a **hold** on the thermostat, which
  overrides the thermostat's built-in schedule until cleared. Tested overnight: the HA
  set-point held, and the thermostat's schedule did not fight it.
- The thermostat's *own* schedule (times and temperatures) can't be edited over HomeKit.
  You can only switch its comfort setting (home / sleep / away).
- So the clean design is: **Home Assistant is the schedule.** Two time-triggered automations
  (day and night set-points) plus an `input_boolean` for vacation mode, which the day/night
  automations check before running. `automations.yaml` in this folder is a working example.
- Remember the schedule when someone asks for a one-off change: "set it to 67" at night
  lasts until the next morning automation fires. Say so.

## Ideas that build on it

Pre-cool before you get home (needs the HA phone app for home/away), a humidity alert, a
"leaving" routine that raises the AC and starts the robot vacuum.
