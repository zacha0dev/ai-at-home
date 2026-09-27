---
name: tv-from-laptop
description: Diagnose and control an Android TV / Google TV (TCL, Sony, Hisense, Chromecast with Google TV...) from a laptop on the same Wi-Fi using ADB - find why it's slow or "loading funny", reboot it, clear a crash-looping app, set the volume, send remote-control keys. Use for "my TV is acting weird", "the TV is slow", "the TV has no sound", or "turn the TV off from the laptop".
---

# TV from the laptop (Android / Google TV)

## Setup (once)

1. On the TV: **Settings -> System -> About -> tap "Build" 7 times** to unlock developer
   options, then **Developer options -> USB debugging -> On** (network debugging on some
   models).
2. On the laptop: get Google's **platform-tools** (`adb`). The portable zip is enough,
   no installer.
3. `adb connect <tv-ip>:5555`, then accept the "Allow USB debugging?" prompt **on the TV**
   with the remote. Tick "Always allow from this computer".

Find the TV's IP in its network settings or your router's device list.

## Diagnose "it's loading funny"

Run these and read them together. One number alone misleads.

```
adb -s <tv>:5555 shell uptime                                   # days since last reboot
adb -s <tv>:5555 shell cat /proc/meminfo | head -5               # memory
adb -s <tv>:5555 shell "cat /proc/swaps"                         # swap use
adb -s <tv>:5555 shell "ps -A | grep -c ' Z '"                   # zombie processes
adb -s <tv>:5555 shell "dumpsys activity | grep -i anr | head"   # app-not-responding events
adb -s <tv>:5555 shell "logcat -b crash -d | tail -40"           # recent crashes
adb -s <tv>:5555 shell "dumpsys package <pkg> | grep lastUpdateTime"   # what updated when
```

A real case: 86 days of uptime, **1,100 zombie processes**, swap 73% used, the remote
service freezing every ~3.5 minutes, and Google Assistant crash-looping. The trigger was a
launcher update the Play Store pushed two days earlier, exactly when "it started acting
funny". High load average on these chips is mostly stuck kernel threads and a red
herring on its own.

## Fix, in order: stop at the first one that works

1. **Reboot.** `adb reboot`, or unplug for 30 s. In the real case this took zombies
   1,100 -> 0 and swap 78% -> 4%, back on the home screen in 38 seconds.
2. **If it comes back within a day**, clear the misbehaving app's data. This is non-destructive;
   you just sign back in:
   `adb -s <tv>:5555 shell pm clear <package>` (e.g. `com.google.android.katniss` is
   Google Assistant).
3. **If it still recurs**, the latest update is the cause: Settings -> Apps -> that app ->
   Uninstall updates, or wait for the next update.

## Volume and sound

```
adb -s <tv>:5555 shell cmd media_session volume --stream 3 --set 50   # music stream
adb -s <tv>:5555 shell "dumpsys audio | grep -A6 STREAM_MUSIC"        # read it back
```

Many TVs use **0-100** for this stream (many phones use 0-15). If sound seems broken,
**read the level first**: one TV was found at 1 while casting, which is silent, not quiet.

## Remote-control keys

```
adb -s <tv>:5555 shell input keyevent KEYCODE_HOME
adb -s <tv>:5555 shell input keyevent KEYCODE_SLEEP     # standby (off)
adb -s <tv>:5555 shell input keyevent KEYCODE_WAKEUP    # only if the network is still up
```

**Off works, on usually doesn't.** Many TVs shut their whole network down in standby, so
nothing on the Wi-Fi can reach them again, and Wake-on-LAN is often ignored. Ways to turn
it *on* remotely: a Nest speaker ("Hey Google, turn on the TV", if linked in Google Home),
HDMI-CEC from a device on the HDMI chain, or an IR bridge.

## Safety

- ADB on port 5555 is a door into the TV for anything on your network that the TV has
  trusted. **Turn USB debugging off when you're done**, or at least check the trusted
  computers list.
- Don't install or sideload apps over ADB unless you meant to. Check the installed list
  with `adb shell pm list packages -3` instead.
