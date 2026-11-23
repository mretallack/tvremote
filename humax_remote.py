#!/usr/bin/env python3
"""Send remote-control key codes to a Humax Freeview PVR over the LAN.

Protocol: UDP to port 22558. Each packet is

    "hmxra\\0\\0\\0rcu\\0\\0\\0\\0\\0" + "00" + <2 hex chars> + <12-byte tail>

The 12-byte tail 00000000f410783a01000000 was captured from the old
Humax remote app and is accepted by the HDR-2000T unchanged.

Verified: PAUSE on a Humax HDR-2000T, 2026-11-22. Content Sharing must be
on in the box settings.

Usage:
    ./humax_remote.py pause
    ./humax_remote.py play --host 10.0.0.24
    ./humax_remote.py ok exit up down
    ./humax_remote.py channel 101          # tune to channel 101
    ./humax_remote.py bbc1                 # tune to BBC One
    ./humax_remote.py --list
"""

import argparse
import socket
import sys

DEFAULT_HOST = "10.0.0.24"
PORT = 22558

HEADER = b"hmxra\x00\x00\x00rcu\x00\x00\x00\x00\x00"
TAIL = bytes.fromhex("00000000f410783a01000000")

# key name -> hex code. Base table from af123's packet capture, with the
# extra codes EEPhil tested on an HDR-2000T.
KEYS = {
    "off": "01",
    "zero": "10", "one": "11", "two": "12", "three": "13", "four": "14",
    "five": "15", "six": "16", "seven": "17", "eight": "18", "nine": "19",
    "red": "20", "green": "21", "yellow": "22", "blue": "23",
    "i": "30", "guide": "31", "menu": "32", "list": "35",
    "resolution": "37", "sub": "39", "plus": "3b",
    "media": "3d", "portal": "3e",
    "text": "80", "search": "47", "audio": "48",
    "ch_up": "50", "ch_down": "51", "left": "52", "right": "53",
    "up": "54", "down": "55", "back": "56", "exit": "57", "ok": "58",
    "play": "90", "pause": "91", "stop": "92", "record": "93",
    "forward": "94", "rewind": "95",
    "skip_back": "96", "skip_forward": "97",
    "vol_up": "70", "vol_down": "71", "mute": "72", "wide": "78",
    "radio_tv": "63",
}

ALIASES = {
    "skipback": "skip_back", "skipforward": "skip_forward",
    "ch+": "ch_up", "ch-": "ch_down", "vol+": "vol_up", "vol-": "vol_down",
    "ff": "forward", "rw": "rewind", "home": "menu", "ffwd": "forward",
}

DIGITS = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
          "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}

# A few named channels, so "bbc1" works instead of "channel 1".
CHANNELS = {
    "bbc1": 1, "bbcone": 1, "bbc2": 2, "itv1": 3, "itv": 3,
    "ch4": 4, "channel4": 4, "ch5": 5, "channel5": 5,
}


def resolve(name):
    name = ALIASES.get(name.lower(), name.lower())
    if name not in KEYS:
        raise SystemExit(
            f"unknown key: {name}\nrun with --list to see the names"
        )
    return KEYS[name]


def send(code, host=DEFAULT_HOST, port=PORT):
    """Send one key code. Returns the packet that was sent."""
    pkt = HEADER + b"00" + code.encode() + TAIL
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(pkt, (host, port))
    finally:
        sock.close()
    return pkt


def main(argv=None):
    ap = argparse.ArgumentParser(description="Humax IP remote")
    ap.add_argument("keys", nargs="*", help="key names, e.g. pause play")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--list", action="store_true", help="print key names")
    ap.add_argument("--dry-run", action="store_true", help="print packets only")
    args = ap.parse_args(argv)

    if args.list:
        names = sorted(set(KEYS) | set(ALIASES))
        print(" ".join(names))
        return 0

    if not args.keys:
        ap.print_help()
        return 2

    keys = list(args.keys)
    first = keys[0].lower()

    # "channel 101" / "bbc1" -> digits then OK
    if first == "channel" or first in CHANNELS:
        if first == "channel":
            if len(keys) < 2 or not keys[1].isdigit():
                raise SystemExit("usage: humax_remote.py channel <number>")
            number = keys[1]
            rest = keys[2:]
        else:
            number = str(CHANNELS[first])
            rest = keys[1:]
        keys = [DIGITS[d] for d in number] + ["ok"] + rest

    for name in keys:
        code = resolve(name)
        if args.dry_run:
            pkt = HEADER + b"00" + code.encode() + TAIL
        else:
            pkt = send(code, args.host, args.port)
        print(f"{name} {code} {pkt.hex()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
