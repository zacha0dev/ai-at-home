# The thermostat's pairing code kept changing

## The ask

"Can you get to my AC?" The owner had tried to connect the thermostat to other tools before
and it never worked.

## Why the obvious route was closed

It's an ecobee. Home Assistant offered an "ecobee" integration, but that one needs a
developer API key, and ecobee stopped handing those out. Dead end.

The same thermostat also speaks **HomeKit**, and Home Assistant can pair with HomeKit devices
directly on the home network. No ecobee account, no key, no cloud. Home Assistant had already
discovered it and was waiting for a pairing code.

## The code that didn't work

The owner sent a photo of the thermostat's HomeKit screen with the 8-digit code. The pairing
failed: `authentication_error`.

The reason: **the code changes every time that screen is opened.** The photo showed a code
from an earlier visit to the screen. With the screen open and a fresh code typed in straight
away, it paired on the first try. That was the whole problem.

## What it can do now

From the laptop, in the background: read the temperature, humidity and whether it's cooling;
set the target; switch cool / heat / off. A test change from 74 to 73 had it cooling within
about 20 seconds.

## The schedule

The owner wanted 74 during the day, 69-70 at night, and a vacation mode. The thermostat's
own schedule can't be edited over HomeKit, so Home Assistant became the schedule: a morning
automation, a night automation, and a vacation toggle the other two respect.

The open question was whether the thermostat's built-in schedule would fight back. It
didn't. A set-point from Home Assistant becomes a **hold**, and at the first night change the
thermostat took the new target and held it.

## Lessons

- When a pairing code is shown on a device's screen, use it live, not from a photo.
- Check for a local protocol (HomeKit, Matter) before chasing a vendor's cloud API.
- Put the schedule where you can edit it from the agent, and mention it when someone asks
  for a one-off change: the next scheduled change will overwrite it.
