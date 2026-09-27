# The robot vacuum joined the AI, then got lost

**Skill:** [`robot-vacuum-home-assistant`](../skills/robot-vacuum-home-assistant/SKILL.md)

## The goal

A Dreame D20 Plus that cleans a whole downstairs, controlled only from a phone app. The
goal: let the AI agent on the laptop start it, check it and fold it into routines.

## "It's on the network" / "I can't see it"

The owner knew it was online. Two network scans and an mDNS listen found every speaker, both
TVs, the Pi and the phone, but no vacuum. (One bonus: the listen turned up the house
**thermostat**, advertising itself over HomeKit and unpaired. That's the path to controlling the
AC.) The fix: a watch sweeping the network every 10 seconds while the owner restarted the
robot. It appeared within a minute: `dreame_vacuum_r2564z`.

Every local port was closed, so it was cloud-only. Research turned up the right Home
Assistant integration and one catch: only its **beta** supported Dreamehome accounts.

## Setting it up

Home Assistant went onto the Raspberry Pi in Docker, plus the beta integration. The owner
created the HA login and typed the Dreamehome password (the agent handled the town
for the location, switched the server country from EU to US, and clicked through the rest).
The access token went from HA's Copy button straight into a private file, and never
appeared on screen or in chat.

Result: 126 entities. Docked, 100% battery, 15 cleans since April, last one in July, wheels
at 51%.

## The first test

`start`: cleaning in 8 seconds. `dock` a minute later: "returning"... then an **error: drop**,
cleared in 26 seconds, then paused. A second `dock`: "returning" for minutes.

The live map explained it: a fresh partial map, no dock on it. The robot had lost track of
where it was. The agent paused it so it would stay put, told it to speak ("I'm here"), and
read the map: stuck among a cluster of small obstacles, which is usually chair and table legs.

## Lessons

- The "drop" error on a flat floor, after three idle months, pointed at **dirty cliff sensors**.
  Clean the robot before the first remote run.
- Errors clear themselves. Read their reason from history.
- A paused robot that talks is easy to find. A lost robot being driven blind is not.
