/* ivitap2 - guarded synthetic tap / slow drag for the IVI3D touchscreen (gt9xx, Type-A MT).
 * Extends ivitap (ivi_virtual_touch) with:
 *   -G x,y,w,h,HASH  guard: right before injecting, hash the rectangle of the *visible* fb0 page
 *                    (FNV-1a 32 over the raw row bytes) and refuse (exit 4) unless it equals HASH.
 *                    The Mac computes HASH from the screenshot it just classified, so the tap only
 *                    happens if nothing changed under the finger since that screenshot (TOCTOU guard).
 *   -H x,y,w,h       print the hash of that rectangle and exit (diagnostics / calibration).
 *   -S x2,y2,ms      instead of a tap, drag from (X,Y) to (x2,y2) over ms milliseconds, hold still
 *                    150 ms, then release (slow drag => no ListView flick momentum).
 * Safety identical to ivitap: device name must contain "gt9xx" and X/Y max must be 800/480.
 * Build (box): zig cc -target arm-linux-musleabi -mcpu=cortex_a7 -static -Os -s -o ivitap2 ivitap2.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <linux/fb.h>

static const char *dev = "/dev/input/event3", *fbdev = "/dev/fb0", *want = "gt9xx";

static void ev(struct input_event *e, int t, int c, int v) { memset(e, 0, sizeof *e); e->type = t; e->code = c; e->value = v; }

static int fb_hash(int x, int y, int w, int h, uint32_t *out) {
    int fd = open(fbdev, O_RDONLY);
    if (fd < 0) { perror(fbdev); return -1; }
    struct fb_var_screeninfo v; struct fb_fix_screeninfo f;
    if (ioctl(fd, FBIOGET_VSCREENINFO, &v) < 0 || ioctl(fd, FBIOGET_FSCREENINFO, &f) < 0) { perror("fb ioctl"); close(fd); return -1; }
    int bpp = v.bits_per_pixel / 8;
    if (bpp != 4 || x < 0 || y < 0 || w <= 0 || h <= 0 || x + w > (int)v.xres || y + h > (int)v.yres) {
        fprintf(stderr, "fb: bad rect or bpp=%d (xres %u yres %u)\n", bpp * 8, v.xres, v.yres); close(fd); return -1;
    }
    uint32_t hsh = 2166136261u; unsigned char row[800 * 4];
    if (w * bpp > (int)sizeof row) { close(fd); return -1; }
    for (int r = 0; r < h; r++) {
        off_t off = (off_t)(v.yoffset + y + r) * f.line_length + (off_t)(v.xoffset + x) * bpp;
        if (pread(fd, row, w * bpp, off) != w * bpp) { perror("pread fb"); close(fd); return -1; }
        for (int i = 0; i < w * bpp; i++) { hsh ^= row[i]; hsh *= 16777619u; }
    }
    close(fd); *out = hsh; return 0;
}

static int parse4(const char *s, int *a, int *b, int *c, int *d) { return sscanf(s, "%d,%d,%d,%d", a, b, c, d) == 4; }

int main(int argc, char **argv) {
    int hold_ms = 100, dry = 0, opt, gx, gy, gw, gh, have_guard = 0, drag = 0, x2 = 0, y2 = 0, drag_ms = 600;
    unsigned long ghash = 0;
    while ((opt = getopt(argc, argv, "d:t:w:nG:H:S:")) != -1) {
        switch (opt) {
        case 'd': dev = optarg; break;
        case 't': hold_ms = atoi(optarg); break;
        case 'w': want = optarg; break;
        case 'n': dry = 1; break;
        case 'G': if (sscanf(optarg, "%d,%d,%d,%d,%lx", &gx, &gy, &gw, &gh, &ghash) != 5) goto usage; have_guard = 1; break;
        case 'H': { int a, b, c, d; uint32_t hv; if (!parse4(optarg, &a, &b, &c, &d)) goto usage;
                    if (fb_hash(a, b, c, d, &hv)) return 1; printf("%08x\n", hv); return 0; }
        case 'S': if (sscanf(optarg, "%d,%d,%d", &x2, &y2, &drag_ms) != 3) goto usage; drag = 1; break;
        default: goto usage;
        }
    }
    if (argc - optind != 2) {
usage:
        fprintf(stderr, "usage: ivitap2 [-d dev] [-t hold_ms] [-n] [-G x,y,w,h,hash] [-S x2,y2,ms] X Y | ivitap2 -H x,y,w,h\n");
        return 2;
    }
    int x = atoi(argv[optind]), y = atoi(argv[optind + 1]);
    if (x < 0 || x > 799 || y < 0 || y > 479 || x2 < 0 || x2 > 799 || y2 < 0 || y2 > 479 ||
        hold_ms < 20 || hold_ms > 600 || drag_ms < 100 || drag_ms > 3000) {
        fprintf(stderr, "refusing: coordinates/time out of range\n"); return 2;
    }
    if (dry) { printf("dry-run: %s %d,%d%s\n", drag ? "drag" : "tap", x, y, have_guard ? " (guarded)" : ""); return 0; }
    int fd = open(dev, O_RDWR);
    if (fd < 0) { perror(dev); return 1; }
    char name[128] = {0}; struct input_absinfo ax, ay;
    if (ioctl(fd, EVIOCGNAME(sizeof name - 1), name) < 0 || ioctl(fd, EVIOCGABS(ABS_MT_POSITION_X), &ax) < 0 ||
        ioctl(fd, EVIOCGABS(ABS_MT_POSITION_Y), &ay) < 0) { perror("ioctl input"); return 1; }
    if (!strstr(name, want) || ax.maximum != 800 || ay.maximum != 480) {
        fprintf(stderr, "refusing: %s is \"%s\" X..%d Y..%d, not the 800x480 gt9xx panel\n", dev, name, ax.maximum, ay.maximum); return 3;
    }
    if (have_guard) {
        uint32_t now;
        if (fb_hash(gx, gy, gw, gh, &now)) return 1;
        if (now != (uint32_t)ghash) { fprintf(stderr, "GUARD_MISMATCH %08x != %08lx (screen changed) - not tapping\n", now, ghash); return 4; }
    }
    struct input_event f[7], up[4];
    ev(&up[0], EV_ABS, ABS_MT_TOUCH_MAJOR, 0); ev(&up[1], EV_ABS, ABS_MT_WIDTH_MAJOR, 0);
    ev(&up[2], EV_SYN, SYN_MT_REPORT, 0); ev(&up[3], EV_SYN, SYN_REPORT, 0);
    int steps = drag ? drag_ms / 20 : 1;
    for (int i = 0; i <= (drag ? steps : 0); i++) {
        int cx = drag ? x + (x2 - x) * i / steps : x, cy = drag ? y + (y2 - y) * i / steps : y;
        ev(&f[0], EV_ABS, ABS_MT_POSITION_X, cx); ev(&f[1], EV_ABS, ABS_MT_POSITION_Y, cy);
        ev(&f[2], EV_ABS, ABS_MT_TOUCH_MAJOR, 20); ev(&f[3], EV_ABS, ABS_MT_WIDTH_MAJOR, 20);
        ev(&f[4], EV_ABS, ABS_MT_TRACKING_ID, 0); ev(&f[5], EV_SYN, SYN_MT_REPORT, 0); ev(&f[6], EV_SYN, SYN_REPORT, 0);
        if (write(fd, f, sizeof f) != (ssize_t)sizeof f) { perror("write"); return 1; }
        usleep(drag ? 20000 : hold_ms * 1000);
    }
    if (drag) { usleep(150000); } /* hold still: zero release velocity */
    if (write(fd, up, sizeof up) != (ssize_t)sizeof up) { perror("write up"); return 1; }
    close(fd);
    printf("OK %s %d,%d\n", drag ? "drag" : "tap", x, y);
    return 0;
}
