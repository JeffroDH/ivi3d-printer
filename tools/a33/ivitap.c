/* ivitap - inject one synthetic tap into the IVI3D touchscreen evdev node.
 * Mirrors the gt9xx_ts driver's own Type-A multitouch frames (goodix_ts_work_func):
 *   down: ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TOUCH_MAJOR, ABS_MT_WIDTH_MAJOR,
 *         ABS_MT_TRACKING_ID, SYN_MT_REPORT, SYN_REPORT
 *   up:   ABS_MT_TOUCH_MAJOR=0, ABS_MT_WIDTH_MAJOR=0, SYN_MT_REPORT, SYN_REPORT
 * Writing to an evdev node makes the kernel inject the events into that device (evdev_write ->
 * input_inject_event), so every reader of the node (the Qt app) sees them.
 * Safety: refuses to write unless the device name contains the expected string (default "gt9xx")
 * and ABS_MT_POSITION_X/Y maxima are 800/480 (override with -f). -n = dry run (print hex, no write).
 * Build (box): zig cc -target arm-linux-musleabihf -mcpu=cortex_a7 -static -Os -o ivitap ivitap.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

static int mk(struct input_event *e, int type, int code, int value) {
    memset(e, 0, sizeof *e); e->type = type; e->code = code; e->value = value; return 1;
}
static void dump(const char *tag, struct input_event *ev, int n) {
    for (int i = 0; i < n; i++) {
        const unsigned char *p = (const unsigned char *)&ev[i];
        printf("%s type=%u code=0x%02x value=%d :", tag, ev[i].type, ev[i].code, ev[i].value);
        for (unsigned j = 0; j < sizeof ev[i]; j++) printf(" %02x", p[j]);
        printf("\n");
    }
}
int main(int argc, char **argv) {
    const char *dev = "/dev/input/event3", *want = "gt9xx";
    int hold_ms = 100, dry = 0, force = 0, opt;
    while ((opt = getopt(argc, argv, "d:t:w:nf")) != -1) {
        switch (opt) {
        case 'd': dev = optarg; break;
        case 't': hold_ms = atoi(optarg); break;
        case 'w': want = optarg; break;
        case 'n': dry = 1; break;
        case 'f': force = 1; break;
        default: goto usage;
        }
    }
    if (argc - optind != 2) {
usage:
        fprintf(stderr, "usage: ivitap [-d /dev/input/eventN] [-t hold_ms] [-w name_substr] [-n dry] [-f] X Y\n");
        return 2;
    }
    int x = atoi(argv[optind]), y = atoi(argv[optind + 1]);
    if (x < 0 || x > 799 || y < 0 || y > 479 || hold_ms < 20 || hold_ms > 600) {
        fprintf(stderr, "refusing: x 0..799, y 0..479, hold 20..600 ms (long holds trigger pressAndHold)\n");
        return 2;
    }
    struct input_event down[7], up[4];
    int n = 0;
    n += mk(&down[n], EV_ABS, ABS_MT_POSITION_X, x);
    n += mk(&down[n], EV_ABS, ABS_MT_POSITION_Y, y);
    n += mk(&down[n], EV_ABS, ABS_MT_TOUCH_MAJOR, 20);
    n += mk(&down[n], EV_ABS, ABS_MT_WIDTH_MAJOR, 20);
    n += mk(&down[n], EV_ABS, ABS_MT_TRACKING_ID, 0);
    n += mk(&down[n], EV_SYN, SYN_MT_REPORT, 0);
    n += mk(&down[n], EV_SYN, SYN_REPORT, 0);
    n = 0;
    n += mk(&up[n], EV_ABS, ABS_MT_TOUCH_MAJOR, 0);
    n += mk(&up[n], EV_ABS, ABS_MT_WIDTH_MAJOR, 0);
    n += mk(&up[n], EV_SYN, SYN_MT_REPORT, 0);
    n += mk(&up[n], EV_SYN, SYN_REPORT, 0);
    if (dry) { printf("sizeof(struct input_event)=%u\n", (unsigned)sizeof(struct input_event));
               dump("down", down, 7); dump("up", up, 4); return 0; }

    int fd = open(dev, O_RDWR);
    if (fd < 0) { perror(dev); return 1; }
    char name[128] = {0};
    if (ioctl(fd, EVIOCGNAME(sizeof name - 1), name) < 0) { perror("EVIOCGNAME"); return 1; }
    struct input_absinfo ax, ay;
    if (ioctl(fd, EVIOCGABS(ABS_MT_POSITION_X), &ax) < 0 || ioctl(fd, EVIOCGABS(ABS_MT_POSITION_Y), &ay) < 0) {
        perror("EVIOCGABS"); return 1;
    }
    fprintf(stderr, "device %s name=\"%s\" X %d..%d Y %d..%d\n", dev, name, ax.minimum, ax.maximum, ay.minimum, ay.maximum);
    if (!force && (strstr(name, want) == NULL || ax.maximum != 800 || ay.maximum != 480)) {
        fprintf(stderr, "refusing: device does not look like the 800x480 gt9xx touch panel (use -f to override)\n");
        return 3;
    }
    if (write(fd, down, sizeof down) != (ssize_t)sizeof down) { perror("write down"); return 1; }
    usleep(hold_ms * 1000);
    if (write(fd, up, sizeof up) != (ssize_t)sizeof up) { perror("write up"); return 1; }
    close(fd);
    fprintf(stderr, "tapped %d,%d (hold %d ms)\n", x, y, hold_ms);
    return 0;
}
