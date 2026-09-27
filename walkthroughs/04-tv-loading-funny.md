# The TV was "loading funny"

**Skill:** [`tv-from-laptop`](../skills/tv-from-laptop/SKILL.md)

## The problem

A Google TV (TCL) had gotten sluggish: menus lagged, the remote felt delayed, apps hung.
Nothing had obviously changed.

## What the agent found, from the laptop

With developer mode and network debugging on, the laptop could read the TV like any
Android device:

| Reading | Value |
|---|---|
| Days since last reboot | **86** |
| Zombie processes | **1,099**, every one a leftover crash handler |
| Swap in use | 73% of 2 GB RAM |
| App-not-responding events | one every **~3.5 minutes**, all the remote/search service |
| Crashes | Google Assistant dying over and over |

And the timing: the Play Store had auto-updated the Google TV home screen and screensaver
two days earlier, which was exactly when it "started acting funny". The update landed on a
box that already had three months of built-up junk.

## The fix

One `adb reboot`. Zombies 1,100 -> 0, swap 78% -> 4%, back on the home screen in 38
seconds. The written plan had two more steps (clear Assistant's data, then roll back the
update) that were never needed.

## Two bonus findings

- **The volume was at 1** while casting. Not broken, just silent. Read the level before
  assuming anything else is wrong.
- **The laptop can turn the TV off, but not on.** In standby this model shuts its whole
  network down, and Wake-on-LAN was ignored. A Nest speaker linked in Google Home ("Hey
  Google, turn on the TV") is the remote "on" button.
