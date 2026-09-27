"""speakers.py - check up on the Google Home speakers and set volume.

    python speakers.py                 # status of every speaker and group
    python speakers.py --volume 0.35   # set every speaker and group, then show status

Needs `pip install pychromecast`. LAN only, no
Google account. A device that is on Wi-Fi but will not connect on port 8009 has a frozen
cast service - that is the "Spotify gets stuck" failure (see SKILL.md).
"""
import argparse
import socket
import time

import pychromecast


def port_open(host, port=8009):
    try:
        socket.create_connection((host, port), timeout=3).close()
        return True
    except OSError:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume", type=float)
    a = ap.parse_args()
    ccs, browser = pychromecast.get_chromecasts(timeout=12)
    ok = []
    for cc in sorted(ccs, key=lambda c: c.cast_info.friendly_name):
        info = cc.cast_info
        try:
            cc.wait(timeout=10)
            if a.volume is not None:
                cc.set_volume(a.volume)
            ok.append(cc)
        except Exception:
            print("%-14s %-15s %s:%s  FROZEN - on the network but not taking casts%s" % (
                info.friendly_name, info.model_name, info.host, info.port,
                "" if port_open(info.host) else " (cast port closed; restart the device)"))
    time.sleep(2)
    for cc in ok:
        st, m = cc.status, cc.media_controller.status
        print("%-14s %-15s %s  app=%-10s vol=%.0f%%%s  %s" % (
            cc.cast_info.friendly_name, cc.cast_info.model_name, cc.cast_info.host,
            st.display_name, st.volume_level * 100, " muted" if st.volume_muted else "", (m.title or "")[:40]))
    browser.stop_discovery()


if __name__ == "__main__":
    main()
