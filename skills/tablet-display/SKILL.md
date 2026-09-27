---
name: tablet-display
description: Turn an old Windows tablet (Surface Pro or similar) into an always-on home display - get remote access to it with no keyboard, stop it sleeping, and launch a web page full screen on every sign-in. Use for "use my old tablet as a dashboard", "make this tablet a kitchen display", "I can't get into my tablet remotely", or "the tablet keeps going to sleep".
---

# Old tablet into an always-on display

Once the display is a web page, you never touch the tablet again to change what it shows.
Update the page and the tablet follows.

## 1. Get in with no keyboard: Remote Desktop, six taps

On the tablet: **Settings -> System -> Remote Desktop -> On -> Confirm.** Fully touch.
Then connect from your laptop with Remote Desktop Connection to the tablet's IP, and from
there it's a normal PC with your real keyboard and mouse.

- **Windows Home can't host Remote Desktop.** If the page is missing, fall back to
  Settings -> System -> Optional features -> OpenSSH Server.
- **The account needs a real password.** Remote Desktop never accepts a PIN. If the
  existing password is unknown, create a new local admin account in Settings (touch-only).

## 2. SSH with a key, so the agent can run things on it

Over the Remote Desktop session, run `ENABLE-SSH.cmd` as administrator (turns on the
OpenSSH server already built into Windows, starts it, opens port 22), then install your
laptop's public key. **Two silent failures cost the most time:**

- **Admin accounts read keys from `C:\ProgramData\ssh\administrators_authorized_keys`**,
  not `~/.ssh/authorized_keys`, and sshd ignores that file if its permissions are too loose
  (only Administrators and SYSTEM). No useful error either way.
- **"Running" is not "reachable."** The auto-created firewall rule may apply only to
  *Private* networks while your Wi-Fi is classified *Public*. Widen just that one rule:
  `Set-NetFirewallRule -Name OpenSSH-Server-In-TCP -Profile Any`. Leave the network
  category alone.

Checking whether it's up: **ping and ARP both lie** on Windows (ICMP is blocked by default;
a stale ARP entry reads like a dead host). Use a TCP probe:
`Test-NetConnection <ip> -Port 22` (or 445).

## 3. Stop it sleeping

Many tablets are **modern standby** machines (`powercfg /a` shows only "S0 Low Power
Idle"). On those, the screen turning off is itself a road into sleep, so fix both, on
AC power only:

```
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```

Battery settings stay as they were, so it still saves power when unplugged. Undo by
setting the AC values back (600 is a common default).

## 4. The display itself

`TABLET-MODE.cmd` asks for a URL and adds a startup shortcut that opens Edge full screen
in kiosk mode on every sign-in. `Alt+F4` exits; `TABLET-MODE-OFF.cmd` removes it and
changes nothing else. No kiosk accounts or registry edits, so it's always easy to undo.

Finish by hand (Settings, touch-friendly):
- auto-hide the taskbar
- auto sign-in (`netplwiz`) so a reboot lands on the display. Only do this if the tablet
  lives somewhere physically safe.

What to show: a calendar, a weather page, a home dashboard (e.g. one served from a
Raspberry Pi, see `pi-home-server`), or a photo slideshow.

## Getting scripts onto it

USB stick, a download from your own GitHub repo, or a temporary file share from the
laptop (`New-SmbShare ... -ReadAccess Everyone`, then remove it right after). Turn file
sharing back off when you're done.
