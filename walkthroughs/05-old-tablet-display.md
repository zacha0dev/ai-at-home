# An old Surface tablet became an always-on display

**Skill:** [`tablet-display`](../skills/tablet-display/SKILL.md)

## The problem

A Surface tablet with **no keyboard**, sitting unused. The goal: a counter-top display
that never sleeps and shows a web page, managed from the laptop so nobody has to poke
at it again.

## The wall

File sharing was on, but file sharing isn't remote control. Both machines were in a
plain home workgroup, so the laptop's account meant nothing to the tablet and every
remote command got "Access is denied". Scripts that assumed a keyboard were useless on a
touch-only device.

## What got through

1. **Remote Desktop: six taps in Settings.** No typing. From then on the tablet had the
   laptop's real keyboard and mouse.
2. A new local admin account with a known password (Remote Desktop won't take a PIN).
3. Over that session, one pasted command turned on the SSH server built into Windows and
   installed the laptop's key.
4. **The fix everything hinged on:** SSH reported "Running" and still refused
   connections. The firewall rule applied only to *Private* networks, and the home Wi-Fi
   was classified *Public*. Widening that single rule opened it.

## The sleep problem

The tablet kept dropping the session. It turned out to be a *modern standby* machine,
set to sleep and dim after 10 minutes on AC. On these, a dark screen leads into sleep, so
both timeouts went to "never" on AC power only. Battery behaviour stayed as it was.

## Lessons

- Ping and ARP both reported the tablet as dead while it was online. A TCP probe on a
  real port is the only honest "is it up?".
- Admin accounts on Windows read SSH keys from a different file than normal users, and
  silently ignore it if its permissions are loose.
