"""routine.py - Zach's speaker routines: music on the whole house at a set volume.

    python routine.py leisure     # your station on the whole house at 37%
    python routine.py work        # same station at 33% - low enough for video calls
    python routine.py list

Each routine: start the station if it isn't playing, (re)connect Spotify to the target,
shuffle and jump to a random spot so it isn't the same start every time, set every
speaker's volume, then check the speakers really report Spotify - if not, reconnect once. Add a routine by adding a
line to ROUTINES.
"""
import os
import subprocess
import sys

ROUTINES = {
    # name: (target speaker/group, station in Your Library, volume)
    "leisure": ("WHOLE HOUSE", "My Favorite Radio", 0.37),
    "work": ("WHOLE HOUSE", "My Favorite Radio", 0.33),
}
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "list"
    if name not in ROUTINES:
        for k, (t, s, v) in ROUTINES.items():
            print("%-8s %s on %s at %d%%" % (k, s, t, v * 100))
        return
    target, station, vol = ROUTINES[name]
    ps = ["powershell", "-NoProfile", "-File", os.path.join(HERE, "spotify_to.ps1"), target, station, "-Shuffle"]
    subprocess.run(ps, check=False)
    for attempt in (1, 2):
        out = subprocess.run([sys.executable, os.path.join(HERE, "speakers.py"), "--volume", str(vol)],
                             capture_output=True, text=True).stdout
        print(out)
        if "app=Spotify" in out:
            return
        if attempt == 1:
            print("speakers idle - reconnecting once")
            subprocess.run(ps[:-1], check=False)   # re-pick the device without skipping again
    print("speakers still idle - check the group leader (speakers.py FROZEN?)")


if __name__ == "__main__":
    main()
