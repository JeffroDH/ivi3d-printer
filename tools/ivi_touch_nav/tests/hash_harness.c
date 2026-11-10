/* Host-side parity harness: runs ivitap2.c's fb_hash() against a regular file posing as /dev/fb0. */
#include <stdarg.h>
#include <sys/ioctl.h>
#include <linux/fb.h>
#include <stdlib.h>
#include <string.h>
static int fake_ioctl(int fd, unsigned long req, ...);
#define ioctl fake_ioctl
#define main real_main
#include "../device/ivitap2.c"
#undef main
#undef ioctl
static int fake_ioctl(int fd, unsigned long req, ...) {
    va_list ap; va_start(ap, req); void *p = va_arg(ap, void *); va_end(ap); (void)fd;
    if (req == FBIOGET_VSCREENINFO) { struct fb_var_screeninfo *v = p; memset(v, 0, sizeof *v);
        v->xres = 800; v->yres = 480; v->bits_per_pixel = 32; v->yoffset = atoi(getenv("YOFF")); return 0; }
    if (req == FBIOGET_FSCREENINFO) { struct fb_fix_screeninfo *f = p; memset(f, 0, sizeof *f);
        f->line_length = 3200; return 0; }
    return -1;
}
int main(int argc, char **argv) {
    uint32_t h; if (argc != 6) return 2; fbdev = argv[1];
    if (fb_hash(atoi(argv[2]), atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), &h)) return 1;
    printf("%08x\n", h); return 0;
}
