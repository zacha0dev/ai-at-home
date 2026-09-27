"""routine.py - one-word speaker routines: music on a speaker group at a set volume.

    python routine.py work       # background music, low enough for video calls
    python routine.py leisure    # a bit louder
    python routine.py list

Each routine moves Spotify to the target (only if it isn't already there), starts the
station (only if it isn't already playing), then sets every speaker's volume.
Edit ROUTINES to match your house: the target is a speaker or group name exactly as the
Google Home app shows it, and the station is any playlist or radio saved in Your Library.
"""
import os
import subprocess
import sys

ROUTINES = {
    # name: (speaker or group, playlist/station in Your Library, volume 0-1)
    "work": ("WHOLE HOUSE", "My Favorite Radio", 0.33),
    "leisure": ("WHOLE HOUSE", "My Favorite Radio", 0.37),
}
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "list"
    if name not in ROUTINES:
        for k, (t, s, v) in ROUTINES.items():
            print("%-8s %s on %s at %d%%" % (k, s, t, v * 100))
        return
    target, station, vol = ROUTINES[name]
    subprocess.run(["powershell", "-NoProfile", "-File", os.path.join(HERE, "spotify_to.ps1"), target, station], check=False)
    subprocess.run([sys.executable, os.path.join(HERE, "speakers.py"), "--volume", str(vol)], check=False)


if __name__ == "__main__":
    main()
