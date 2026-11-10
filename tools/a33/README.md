# A33 framebuffer and tap helpers

These are the small helpers from the touchscreen analysis. The navigator in [../ivi_touch_nav/](../ivi_touch_nav/README.md) uses `ivitap2` instead of these; keep these for a manual tap or a one-off screenshot.

The rootfs dynamic linker is `/lib/ld-linux.so.3` (ARM EABI5 soft-float). A hard-float binary will not run.

## `ivitap.c`

One synthetic tap into the gt9xx evdev node. Refuses to write unless the device name contains `gt9xx` and the axis maxima are 800×480.

```
zig cc -target arm-linux-musleabi -mcpu=cortex_a7 -static -Os -s -o ivitap ivitap.c
```

The prebuilt `ivitap2` used by the navigator is built the same way from `../ivi_touch_nav/device/ivitap2.c` (it adds the framebuffer hash guard and the slow drag).

## `ivitap.sh`

BusyBox-only tap. No binary upload. It writes 16-byte `input_event` records with `dd bs=16`.

```
sh ivitap.sh X Y [/dev/input/event3] [hold_us]
```

`X` is 0..799 and `Y` is 0..479. Confirm the node with `cat /proc/bus/input/devices` before passing a device other than the default.

## `fb2png.py`

Turns a raw `/dev/fb0` dump into a PNG. Needs Pillow.

```
dd if=/dev/fb0 of=/tmp/fb.raw bs=1536000 count=1
python3 fb2png.py /tmp/fb.raw out.png 800 480 3200 0
```

Arguments after the output path are width, height, stride, and y offset. The visible page's y offset is the `pan` sysfs value (`0` or `480`).
