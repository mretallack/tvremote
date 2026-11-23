# Humax HDR-2000T — control from the network

Pause, play and other remote keys can be sent to the box over the LAN.
No custom firmware is needed. Nothing is installed on the box.

Verified working on 2026-11-22 against the box at `10.0.0.24`
(Humax HDR-2000T, Freeview, live TV). Pressing **PAUSE** from this
script froze the picture on screen.

Also verified 2026-11-23: **`./humax_remote.py one ok`** switched the box
to BBC One, channel 1. Digits need an `ok` after them.

## How it works

The box listens on **UDP port 22558**. That is the port the retired
"Humax TV Remote" phone app used. Send it a small binary packet and it
acts as if the matching button on the handset was pressed.

Each packet is:

```
"hmxra" 00 00 00 "rcu" 00 00 00 00 00   00   <2 hex key chars>   00000000f410783a01000000
```

The first part is a fixed header. `00` before the key may be a handset
code. The 2 characters are the key, written as ASCII hex (`"91"` for
pause). The 12-byte tail was never explained; the box accepts it as-is.
Discovery is not needed — the packet can be sent cold to the box's IP.

The protocol was found by **af123** and tested on the HDR-2000T by
**EEPhil** in the hummy.tv thread
[IP remote commands](https://hummy.tv/forum/threads/ip-remote-commands.7783/).

## Requirement

**Content Sharing must be on in the box settings.** With it off, the box
silently drops the packets. Path: Menu → Settings → System →
Content Sharing / DLNA.

## Use

```bash
./humax_remote.py pause
./humax_remote.py play
./humax_remote.py ok down down ok
./humax_remote.py channel 101         # tune to channel 101
./humax_remote.py bbc1                # named channels: bbc1 bbc2 itv ch4 ch5
./humax_remote.py --host 10.0.0.24 --list
./humax_remote.py pause --dry-run     # print the packet, send nothing
```

A digit alone changes channel on the HDR-2000T — `ok` is not needed
(tested 2026-11-23: `one` went straight to BBC One). The script still
sends `ok` after digits, which is harmless. `bbc1` is shorthand for
`channel 1`.

Python 3, standard library only.

## Keys

Playback

| Key | Name | Code |
|---|---|---|
| Play | `play` | 90 |
| Pause | `pause` | 91 |
| Stop | `stop` | 92 |
| Record | `record` | 93 |
| Forward | `forward` | 94 |
| Rewind | `rewind` | 95 |
| Skip back | `skip_back` | 96 |
| Skip forward | `skip_forward` | 97 |

Navigation

| Key | Name | Code |
|---|---|---|
| Up / Down / Left / Right | `up` `down` `left` `right` | 54 55 52 53 |
| OK | `ok` | 58 |
| Back | `back` | 56 |
| Exit | `exit` | 57 |
| Menu (Home) | `menu` | 32 |
| Guide | `guide` | 31 |
| List | `list` | 35 |
| Info | `i` | 30 |
| Media | `media` | 3d |
| Portal | `portal` | 3e |

Other

| Key | Name | Code |
|---|---|---|
| Channel up / down | `ch_up` `ch_down` | 50 51 |
| Volume up / down | `vol_up` `vol_down` | 70 71 |
| Mute | `mute` | 72 |
| Digits 0–9 | `zero` … `nine` | 10–19 |
| Colours | `red` `green` `yellow` `blue` | 20 21 22 23 |
| Radio / TV | `radio_tv` | 63 |
| Standby | `off` | 01 |

## What the box also exposes

Found with a port scan while working this out:

| Port | Service | Notes |
|---|---|---|
| 21 | FTP | Open by default. Banner `220 Welcome to connection.` |
| 23 | Telnet | Listener present but broken: replies `telnetd: applet not found` |

FTP gives read/write access to `/mnt/hd2/My Video`. It is the way people
pull recordings off a 2000T. Recordings are encrypted in the file, so FTP
copies do not play; the standard trick is to clear the `ENC` flag in the
`.hmt` sidecar and let DLNA re-index.

Port 21 was closed on a first scan and open minutes later — the box drops
the service in deep standby.

## Limits

- No custom firmware exists for the 2000T, and none is coming. The box is
  locked and the community gave up. hummy.tv:
  [can you run custom firmware on the 2000T](https://hummy.tv/forum/threads/can-you-run-custom-firmware-on-the-2000t.7417/).
- No HTTP API. Nothing answers on 80 or 443.
- SSDP/DLNA discovery got no reply on this box, even with Content Sharing
  on. Keys still worked.
- If keys ever stop landing, check Content Sharing first, then whether the
  box is awake.
