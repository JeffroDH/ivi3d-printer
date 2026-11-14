/*
 * ivibridge - serial multiplexer + OctoPrint-compatible HTTP bridge for the IVI3D A33 board.
 *
 * Owns the real STM32 link (CH340 ttyUSB0), gives the stock touchscreen app a pty in its place
 * (the app's /dev/ttyUSB0 becomes a symlink to the pty slave), and lets the network side read
 * status and, when the app is idle, stream G-code and send start/pause/resume/stop.
 *
 * Rules (see DESIGN.md):
 *  - Pass-through: while the network side has nothing in flight, every byte from the STM32 goes to
 *    the app unchanged and every app line goes to the STM32 unchanged.
 *  - One owner at a time: the network side only transmits when the app has no command awaiting
 *    its 'ok'; app lines that arrive while a network command is in flight are queued.
 *  - Never two G-code streams: network jobs are refused while the app prints; while a network job
 *    runs, app lines other than read-only queries are held (the app is shown the stock
 *    "printing via IVI 3licer" lock page through a rewritten Working Status line).
 *  - Laser safety: jobs or commands containing M3/M4 with S>100 are refused.
 *  - Clean exit (SIGTERM/SIGINT) restores the original /dev/ttyUSB0 device node.
 *
 * Single-threaded poll() loop, static binary, no dependencies beyond libc.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <poll.h>
#include <dirent.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/statvfs.h>
#include <sys/sysmacros.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <limits.h>

#define VERSION "0.1.7-a33"
#define LINEMAX 1024
#define MAXCLI 8
#define APPQ 64
#define CONSOLE_N 200
#define RESEND_RING 256

/* ------------------------------------------------------------------ config */
static const char *g_serial = "/dev/ivi-stm32";   /* real link (node created by the start script) */
static const char *g_link = "/dev/ttyUSB0";       /* path the app opens; becomes a symlink to our pty */
static int g_port = 5001;
static const char *g_bind = "0.0.0.0";
static char g_apikey[128] = "";
static const char *g_updir = "/userdata/WifiFile";
static const char *g_logpath = NULL;
static int g_linenums = 1;          /* N<n> ... *<cs> on network streams */
static int g_restore = 1;           /* mknod the original node back on clean exit */
static int g_poll_s = 10;           /* idle M105 if no temperature report for this long (0 = never) */
static int g_stall_ms = 5000;       /* job line with no 'ok' for this long -> M105 stall probe */
static int g_resume_ms = 30000;     /* wait this long for "Resume complete" after M2411 S1 */
static int g_cancel_grace_ms = 1500;/* a cancel abandons an in-flight wait after this long */
static const char *g_www;            /* directory of the status page (index.html) */
static char g_wwwbuf[512];
#define QMAX 16
static char g_queue[QMAX][256];
static int g_qn;


/* ------------------------------------------------------------------ util */
static FILE *g_log, *g_plog;
static char g_p1root[256], g_jobs_persist[512], g_logs_persist[512], g_persist_logpath[576];
static int g_p1_ready;
static long long g_p1_last_check, g_log_max = 1048576;
static long long now_ms(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}
static const char *ivib_dir(void) {
    const char *d = getenv("IVIB_DIR");
    return (d && *d) ? d : "/tmp/ivibridge";
}

/* compact SHA-256, used to verify job-file copies to p1 */
static uint32_t rotr32(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
static void sha256_block(uint32_t h[8], const unsigned char blk[64]) {
    static const uint32_t K[64] = {
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    };
    uint32_t w[64], a, b, c, d, e, f, g, hv, t1, t2; int i;
    for (i = 0; i < 16; i++)
        w[i] = ((uint32_t)blk[i*4] << 24) | ((uint32_t)blk[i*4+1] << 16) | ((uint32_t)blk[i*4+2] << 8) | blk[i*4+3];
    for (i = 16; i < 64; i++) {
        uint32_t s0 = rotr32(w[i-15], 7) ^ rotr32(w[i-15], 18) ^ (w[i-15] >> 3);
        uint32_t s1 = rotr32(w[i-2], 17) ^ rotr32(w[i-2], 19) ^ (w[i-2] >> 10);
        w[i] = w[i-16] + s0 + w[i-7] + s1;
    }
    a = h[0]; b = h[1]; c = h[2]; d = h[3]; e = h[4]; f = h[5]; g = h[6]; hv = h[7];
    for (i = 0; i < 64; i++) {
        t1 = hv + (rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25)) + ((e & f) ^ ((~e) & g)) + K[i] + w[i];
        t2 = (rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
        hv = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
    }
    h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hv;
}
static int sha256_file(const char *path, char hex[65]) {
    FILE *f = fopen(path, "rb"); if (!f) return -1;
    uint32_t h[8] = { 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19 };
    unsigned char blk[64], buf[4096]; size_t n, used = 0; uint64_t total = 0;
    while ((n = fread(buf, 1, sizeof buf, f)) > 0) {
        size_t off = 0; total += n;
        while (off < n) {
            size_t take = 64 - used; if (take > n - off) take = n - off;
            memcpy(blk + used, buf + off, take); used += take; off += take;
            if (used == 64) { sha256_block(h, blk); used = 0; }
        }
    }
    fclose(f);
    blk[used++] = 0x80;
    if (used > 56) { while (used < 64) blk[used++] = 0; sha256_block(h, blk); used = 0; }
    while (used < 56) blk[used++] = 0;
    uint64_t bits = total * 8;
    for (int i = 7; i >= 0; i--) blk[used++] = (unsigned char)(bits >> (i * 8));
    sha256_block(h, blk);
    for (int i = 0; i < 8; i++) sprintf(hex + i * 8, "%08x", h[i]);
    hex[64] = 0; return 0;
}

static void rotate_log_file(const char *path, FILE **fp) {
    struct stat st;
    if (!path || !*path || !fp || stat(path, &st) || st.st_size < g_log_max) return;
    if (*fp && *fp != stderr) { fflush(*fp); fclose(*fp); *fp = NULL; }
    char old[640]; snprintf(old, sizeof old, "%s.1", path);
    unlink(old); rename(path, old);
    *fp = fopen(path, "a");
}
static void seed_persist_log(void) {
    if (!g_logpath || !g_persist_logpath[0]) return;
    struct stat st;
    if (stat(g_persist_logpath, &st) == 0 && st.st_size > 0) return;
    int in = open(g_logpath, O_RDONLY); if (in < 0) return;
    int out = open(g_persist_logpath, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (out < 0) { close(in); return; }
    char buf[4096]; ssize_t n; while ((n = read(in, buf, sizeof buf)) > 0) write(out, buf, (size_t)n);
    fsync(out); close(out); close(in);
}
static void refresh_p1(void);  /* defined after job_active so migrate can skip the live job */
static const char *updir_now(void);
static int find_job_file(const char *name, char *out, size_t on);

static void logf_x(int important, const char *fmt, ...) {
    char tb[32], msg[1024]; time_t t = time(NULL); struct tm tm; localtime_r(&t, &tm);
    strftime(tb, sizeof tb, "%Y-%m-%d %H:%M:%S", &tm);
    va_list ap; va_start(ap, fmt); vsnprintf(msg, sizeof msg, fmt, ap); va_end(ap);
    if (g_logpath && g_log && g_log != stderr) rotate_log_file(g_logpath, &g_log);
    if (g_log) {
        fprintf(g_log, "%s %s\n", tb, msg); fflush(g_log);
        if (important && g_log != stderr) fsync(fileno(g_log));
    }
    if (g_p1_ready && g_persist_logpath[0]) {
        if (!g_plog) g_plog = fopen(g_persist_logpath, "a");
        rotate_log_file(g_persist_logpath, &g_plog);
        if (g_plog) {
            fprintf(g_plog, "%s %s\n", tb, msg); fflush(g_plog);
            if (important) { fsync(fileno(g_plog)); sync(); }
        }
    }
}
#define logf_(...) logf_x(0, __VA_ARGS__)
#define logi_(...) logf_x(1, __VA_ARGS__)
static void rstrip(char *s) { size_t n = strlen(s); while (n && isspace((unsigned char)s[n-1])) s[--n] = 0; }
static int starts(const char *s, const char *p) { return strncmp(s, p, strlen(p)) == 0; }
static int istarts(const char *s, const char *p) { return strncasecmp(s, p, strlen(p)) == 0; }
static const char *istrstr(const char *h, const char *n) { return strcasestr(h, n); }
static void set_nonblock(int fd) { fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK); }

/* normalise one G-code line for decisions: strip comment, collapse spaces, upper-case */
static void norm_cmd(const char *in, char *out, size_t on) {
    size_t j = 0; int sp = 0;
    for (const char *p = in; *p && *p != ';' && j + 1 < on; p++) {
        unsigned char c = *p;
        if (c == '\r' || c == '\n') break;
        if (isspace(c)) { sp = 1; continue; }
        if (sp && j) out[j++] = ' ';
        sp = 0; out[j++] = toupper(c);
    }
    out[j] = 0;
}
static int cmd_is(const char *n, const char *code) { return strcmp(n, code) == 0; }
static int cmd_word(const char *n, const char *w) {      /* first word equals w */
    size_t l = strlen(w); return strncmp(n, w, l) == 0 && (n[l] == 0 || n[l] == ' ');
}
/* M3/M4 with S>100 (laser/spindle power) - refused everywhere */
static int laser_over(const char *n) {
    if (!(cmd_word(n, "M3") || cmd_word(n, "M4") || cmd_word(n, "M03") || cmd_word(n, "M04"))) return 0;
    const char *s = strstr(n, " S");
    if (!s) return 0;
    return atof(s + 2) > 100.0;
}

/* ------------------------------------------------------------------ console ring */
struct cline { long seq; char dir; char text[160]; };
static struct cline g_con[CONSOLE_N]; static long g_conseq;
static void con_add(char dir, const char *t) {
    struct cline *c = &g_con[(g_conseq + 1) % CONSOLE_N];
    c->seq = ++g_conseq; c->dir = dir; snprintf(c->text, sizeof c->text, "%s", t); rstrip(c->text);
}

/* ------------------------------------------------------------------ printer status */
static struct {
    double t_act, t_tgt, b_act, b_tgt; int have_t; long long t_ms;
    char working[32]; long long working_ms;
    int systat; double x, y, z; int have_pos;
    char fw[96];
    char head[64];                  /* last "info:Head ..." (reply to M2051); "none" after "No Print Head" */
} S = { .systat = -1 };

static void parse_status(const char *l) {
    const char *p;
    if ((p = strstr(l, "T:"))) {
        double a, t;
        if (sscanf(p + 2, "%lf /%lf", &a, &t) == 2 || sscanf(p + 2, "%lf/%lf", &a, &t) == 2) {
            S.t_act = a; S.t_tgt = t; S.have_t = 1; S.t_ms = now_ms();
        }
    }
    if ((p = strstr(l, "B:"))) {
        double a, t;
        if (sscanf(p + 2, "%lf /%lf", &a, &t) == 2 || sscanf(p + 2, "%lf/%lf", &a, &t) == 2) { S.b_act = a; S.b_tgt = t; }
    }
    if ((p = istrstr(l, "Working Status:"))) {
        p += 15; while (*p == ' ') p++;
        size_t k = 0; while (p[k] && !isspace((unsigned char)p[k]) && k < sizeof S.working - 1) k++;
        memcpy(S.working, p, k); S.working[k] = 0; S.working_ms = now_ms();
    }
    if ((p = istrstr(l, "job status:"))) S.systat = atoi(p + 11);
    if (l[0] == 'X' && l[1] == ':') {
        double x, y, z;
        if (sscanf(l, "X:%lf Y:%lf Z:%lf", &x, &y, &z) == 3) { S.x = x; S.y = y; S.z = z; S.have_pos = 1; }
    }
    if (istrstr(l, "firmware") && !S.fw[0]) snprintf(S.fw, sizeof S.fw, "%s", l);
    if ((p = istrstr(l, "info:Head"))) {
        p += 9; while (*p == ' ' || *p == ':') p++;
        snprintf(S.head, sizeof S.head, "%s", p);
    } else if (istrstr(l, "No Print Head")) snprintf(S.head, sizeof S.head, "none");
}
/* fan state, tracked from every M106/M107 written to the STM32 (app, page, job stream). The firmware never
   reports fan state, so this is the bridge's record of the last commands sent: P0/P1, 0..255, -1 = unknown */
static int g_fan[2] = { -1, -1 };
static void fan_track(const char *line) {
    char n[LINEMAX]; norm_cmd(line, n, sizeof n);
    char *st = strchr(n, '*'); if (st) *st = 0;                         /* job-line checksum */
    const char *c = n;
    if (c[0] == 'N' && isdigit((unsigned char)c[1])) { while (*c && *c != ' ') c++; while (*c == ' ') c++; }   /* line number */
    int on = cmd_word(c, "M106"), off = cmd_word(c, "M107");
    if (!on && !off) return;
    int pi = -1, sv = 255;
    for (const char *w = strchr(c, ' '); w; w = strchr(w, ' ')) {
        w++;
        if (*w == 'P') pi = atoi(w + 1);
        else if (*w == 'S') sv = (int)(atof(w + 1) + 0.5);
    }
    if (off) sv = 0;
    if (sv < 0) sv = 0;
    if (sv > 255) sv = 255;
    if (pi > 1) return;                                                   /* firmware ignores P > 1 */
    if (pi < 0) g_fan[0] = g_fan[1] = sv; else g_fan[pi] = sv;
}
static int fan_pct(int v) { return v < 0 ? -1 : (v * 100 + 127) / 255; }

/* M5 (laser off) is only sent when the firmware last reported a laser head; unknown / 3DP / none -> never */
static int head_is_laser(void) {
    if (!S.head[0] || !strcmp(S.head, "none")) return 0;
    char t[64]; size_t k = 0;                         /* head type = text before the first ',' */
    while (S.head[k] && S.head[k] != ',' && k < sizeof t - 1) { t[k] = S.head[k]; k++; }
    t[k] = 0;
    return istrstr(t, "laser") != NULL || istrstr(t, "LAS") != NULL;
}

/* ------------------------------------------------------------------ fds */
static int g_ser = -1, g_ptm = -1, g_pts_keep = -1, g_lfd = -1;
static char g_ptsname[64];
static struct stat g_orig; static int g_have_orig;     /* original /dev/ttyUSB0 node */
static long long g_ser_retry_ms;
static volatile sig_atomic_t g_quit;

struct lbuf { char b[LINEMAX + 4]; int n; };
static struct lbuf g_serbuf, g_appbuf;

/* ------------------------------------------------------------------ owner state */
enum { OWN_NONE, OWN_APP, OWN_NET };
static const char *own_name[] = { "none", "app", "net" };
static int g_owner = OWN_NONE;
static int g_app_pending;                 /* app lines sent, 'ok' not yet seen */
static long long g_last_app_tx, g_last_ser_rx, g_app_settle_until;
static char g_appq[APPQ][LINEMAX + 4]; static int g_appq_h, g_appq_n;
static long long g_net_settle_until;
static long g_app_dropped, g_app_dropped_total, g_stray_ok_dropped, g_app_lines, g_net_lines;
static int g_stray_budget; static long long g_stray_until;   /* late oks of an abandoned (cancelled) wait */

/* network command in flight */
enum { NW_NONE, NW_OK, NW_EXPECT };
static struct {
    int kind; char cmd[LINEMAX + 40]; char expect[3][40]; int nexp; int matched;
    long long deadline, settle_until; int purpose; int timed_out; int failed; char fail[160];
    char ack[40]; int acked; int ack_grace_ms;        /* EXPECT: early acknowledgement before the completion text */
    long line_n; long long stall_at; int probing; int line_acked; int line_is_m105; int lost;   /* job-line stall recovery */
    long long cancel_at;                               /* cancel requested while this was in flight */
    int quiet;                                         /* automatic page poll (M114): kept out of the console view */
} W;
static int g_next_quiet;                               /* set just before net_send for a quiet queued command */
enum { P_QUERY, P_JOBLINE, P_JOBCTL, P_START, P_POLL };

/* network console queue (validated commands from HTTP) */
static char g_netq[16][96]; static int g_netq_h, g_netq_n;
static unsigned char g_netq_quiet[16];          /* per slot: automatic page poll, hidden from the console */
static long long g_net_want_since;

/* ------------------------------------------------------------------ touchscreen (app) job, passive */
static struct {
    int active; long long started_ms, last_ms; long lines; double m73_pct; double m73_left_min; int end_seen;
} AJ;

/* ------------------------------------------------------------------ network job */
enum { J_IDLE, J_PREFLIGHT, J_M110, J_STARTING, J_PRINTING, J_PAUSING, J_PAUSED, J_RESUMING,
       J_FINISHING, J_CANCELLING, J_COOLDOWN, J_DONE, J_CANCELLED, J_ERROR };
static const char *jstate_name[] = { "Operational", "Starting", "Starting", "Starting", "Printing", "Pausing",
    "Paused", "Resuming", "Finishing", "Cancelling", "Cancelling", "Operational", "Cancelled", "Error" };
struct ring_e { long n; long off; };
static struct {
    int st; char name[256]; char path[512]; FILE *f; long long started_ms, ended_ms;
    long total_bytes, total_lines, sent_lines; long n; int want_pause, want_resume, want_cancel;
    struct ring_e ring[RESEND_RING]; long resend_n; int resends; int cool_i;
    long lost_retry_n; int stalls, lost_lines; long stall_line; int stall_tries;
    char err[200]; char last_name[256]; double m73_pct, m73_left_min; long long m73_ms;
} J;

static int job_active(void) { return J.st != J_IDLE && J.st != J_DONE && J.st != J_CANCELLED && J.st != J_ERROR; }

static void write_current_job(int on) {
    char p[512]; snprintf(p, sizeof p, "%s/current_job", ivib_dir());
    if (!on) { unlink(p); return; }
    FILE *f = fopen(p, "w"); if (!f) return;
    fprintf(f, "%s", J.path); fclose(f);
}
static int copy_verify_unlink(const char *src, const char *dst) {
    if (job_active() && !strcmp(src, J.path)) return -2;   /* keep the live job path valid */
    struct stat ss, ds;
    if (stat(src, &ss)) return -1;
    int in = open(src, O_RDONLY); if (in < 0) return -1;
    char tmp[1100]; snprintf(tmp, sizeof tmp, "%s.part", dst);
    int out = open(tmp, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out < 0) { close(in); return -1; }
    char buf[8192]; ssize_t n; int ok = 1;
    while ((n = read(in, buf, sizeof buf)) > 0) if (write(out, buf, (size_t)n) != n) { ok = 0; break; }
    if (n < 0) ok = 0;
    if (ok) fsync(out);
    close(out); close(in);
    if (!ok || stat(tmp, &ds) || ds.st_size != ss.st_size) { unlink(tmp); return -1; }
    char h1[65], h2[65];
    if (sha256_file(src, h1) || sha256_file(tmp, h2) || strcmp(h1, h2)) { unlink(tmp); return -1; }
    if (rename(tmp, dst)) { unlink(tmp); return -1; }
    unlink(src); return 0;
}
static void migrate_ram_jobs(void) {
    if (!g_p1_ready || !g_jobs_persist[0] || !g_updir) return;
    if (!strcmp(g_updir, g_jobs_persist)) return;
    DIR *d = opendir(g_updir); if (!d) return;
    struct dirent *e;
    while ((e = readdir(d))) {
        size_t l = strlen(e->d_name);
        if (e->d_name[0] == '.' || l < 7 || strcasecmp(e->d_name + l - 6, ".gcode")) continue;
        char src[1024], dst[1024];
        snprintf(src, sizeof src, "%s/%s", g_updir, e->d_name);
        snprintf(dst, sizeof dst, "%s/%s", g_jobs_persist, e->d_name);
        if (job_active() && !strcmp(src, J.path)) continue;
        int rc = copy_verify_unlink(src, dst);
        if (rc == 0) logi_("migrated %s to %s", e->d_name, g_jobs_persist);
        else if (rc == -1) logf_("migrate of %s failed", e->d_name);
    }
    closedir(d);
}
static void refresh_p1(void) {
    long long t = now_ms();
    if (g_p1_ready) { if (t - g_p1_last_check < 2000) return; }
    else if (g_p1_last_check && t - g_p1_last_check < 200) return;
    g_p1_last_check = t;
    char ready[512], root[256] = "";
    snprintf(ready, sizeof ready, "%s/p1.ready", ivib_dir());
    FILE *f = fopen(ready, "r");
    if (f) { if (fgets(root, sizeof root, f)) rstrip(root); fclose(f); }
    if (!root[0]) {
        const char *want = getenv("IVIB_P1"); if (!want || !*want) want = "/userdata/WifiFile";
        FILE *m = fopen("/proc/mounts", "r");
        if (m) {
            char line[512], dev[128], mp[256];
            while (fgets(line, sizeof line, m)) {
                if (sscanf(line, "%127s %255s", dev, mp) == 2 && !strcmp(mp, want)) { snprintf(root, sizeof root, "%s", want); break; }
            }
            fclose(m);
        }
    }
    if (!root[0]) return;
    if (!g_p1_ready) {
        snprintf(g_p1root, sizeof g_p1root, "%s", root);
        snprintf(g_jobs_persist, sizeof g_jobs_persist, "%s/ivibridge_jobs", root);
        snprintf(g_logs_persist, sizeof g_logs_persist, "%s/ivibridge_logs", root);
        mkdir(g_jobs_persist, 0755); mkdir(g_logs_persist, 0755);
        snprintf(g_persist_logpath, sizeof g_persist_logpath, "%s/ivibridge.log", g_logs_persist);
        seed_persist_log();
        if (!g_plog) g_plog = fopen(g_persist_logpath, "a");
        g_p1_ready = 1;
        logi_("p1 ready at %s; jobs persist under %s", root, g_jobs_persist);
        migrate_ram_jobs();
    } else migrate_ram_jobs();
}
static const char *updir_now(void) {
    refresh_p1();
    if (g_p1_ready && g_jobs_persist[0]) {
        struct stat st;
        if (stat(g_jobs_persist, &st) == 0 && S_ISDIR(st.st_mode)) return g_jobs_persist;
    }
    return g_updir;
}
static int find_job_file(const char *name, char *out, size_t on) {
    refresh_p1();
    if (g_p1_ready) {
        snprintf(out, on, "%s/%s", g_jobs_persist, name);
        if (!access(out, R_OK)) return 0;
    }
    snprintf(out, on, "%s/%s", g_updir, name);
    return access(out, R_OK) ? -1 : 0;
}


/* ------------------------------------------------------------------ io helpers */
static int write_all(int fd, const char *b, size_t n, int ms) {
    long long end = now_ms() + ms;
    while (n) {
        ssize_t w = write(fd, b, n);
        if (w > 0) { b += w; n -= w; continue; }
        if (w < 0 && errno != EAGAIN && errno != EINTR) return -1;
        if (now_ms() > end) return -1;
        struct pollfd p = { fd, POLLOUT, 0 }; poll(&p, 1, 20);
    }
    return 0;
}
static void to_app(const char *b, size_t n) {
    if (g_ptm < 0) return;
    if (write_all(g_ptm, b, n, 200) < 0) logf_("warn: app pty write dropped %zu bytes", n);
}
static void to_app_line(const char *l) { char b[LINEMAX + 4]; int k = snprintf(b, sizeof b, "%s\r\n", l); to_app(b, k); }
static int to_ser_line(const char *l) {
    if (g_ser < 0) return -1;
    char b[LINEMAX + 48]; int k = snprintf(b, sizeof b, "%s\n", l);
    if (write_all(g_ser, b, k, 1000) < 0) { logf_("serial write failed: %s", strerror(errno)); return -1; }
    fan_track(l);
    return 0;
}

#include "ivi_header.c"

/* ------------------------------------------------------------------ serial open / pty / link */
static int open_real_serial(void) {
    int fd = open(g_serial, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) return -1;
    struct termios t;
    if (tcgetattr(fd, &t) == 0) {
        cfmakeraw(&t);
        t.c_cflag &= ~(CSTOPB | PARENB | CRTSCTS | CSIZE);
        t.c_cflag |= CS8 | CREAD | CLOCAL;
        t.c_cc[VMIN] = 0; t.c_cc[VTIME] = 0;
        cfsetispeed(&t, B115200); cfsetospeed(&t, B115200);
        tcsetattr(fd, TCSANOW, &t);
    }
    ioctl(fd, TIOCEXCL);
    int bits = TIOCM_DTR | TIOCM_RTS; ioctl(fd, TIOCMBIS, &bits);   /* same as the app's setDTR/setRTS(true) */
    tcflush(fd, TCIOFLUSH);
    return fd;
}

static int make_pty(void) {
    int m = posix_openpt(O_RDWR | O_NOCTTY);
    if (m < 0 || grantpt(m) || unlockpt(m)) { logf_("pty: %s", strerror(errno)); return -1; }
    snprintf(g_ptsname, sizeof g_ptsname, "%s", ptsname(m));
    /* keep one slave fd open ourselves: the master then never sees EIO when the app closes/reopens */
    g_pts_keep = open(g_ptsname, O_RDWR | O_NOCTTY);
    if (g_pts_keep >= 0) {
        struct termios t;
        if (tcgetattr(g_pts_keep, &t) == 0) { cfmakeraw(&t); cfsetispeed(&t, B115200); cfsetospeed(&t, B115200); tcsetattr(g_pts_keep, TCSANOW, &t); }
    }
    set_nonblock(m);
    return m;
}

static int point_link(void) {
    char cur[256]; ssize_t k = readlink(g_link, cur, sizeof cur - 1);
    if (k > 0) { cur[k] = 0; if (strcmp(cur, g_ptsname) == 0) return 0; }
    struct stat st;
    if (lstat(g_link, &st) == 0 && S_ISCHR(st.st_mode) && !g_have_orig) { g_orig = st; g_have_orig = 1; }
    char tmp[300]; snprintf(tmp, sizeof tmp, "%s.ivibridge-new", g_link);
    unlink(tmp);
    if (symlink(g_ptsname, tmp) < 0 || rename(tmp, g_link) < 0) { logf_("link %s -> %s failed: %s", g_link, g_ptsname, strerror(errno)); unlink(tmp); return -1; }
    logf_("link %s -> %s", g_link, g_ptsname);
    return 0;
}

static void restore_link(void) {
    char cur[256]; ssize_t k = readlink(g_link, cur, sizeof cur - 1);
    if (k > 0) { cur[k] = 0; if (strcmp(cur, g_ptsname) == 0) unlink(g_link); }
    if (g_restore && g_have_orig) {
        struct stat st;
        if (lstat(g_link, &st) != 0) {
            if (mknod(g_link, S_IFCHR | (g_orig.st_mode & 07777), g_orig.st_rdev) == 0) {
                if (chown(g_link, g_orig.st_uid, g_orig.st_gid) != 0) { /* best effort */ }
                logf_("restored %s (char %u:%u)", g_link, major(g_orig.st_rdev), minor(g_orig.st_rdev));
            } else logf_("restore %s failed: %s", g_link, strerror(errno));
        }
    }
}

/* ------------------------------------------------------------------ arbitration */
static void appq_push(const char *raw) {
    if (g_appq_n >= APPQ) { logf_("warn: app queue full, dropping line"); g_app_dropped++; g_app_dropped_total++; return; }
    snprintf(g_appq[(g_appq_h + g_appq_n) % APPQ], LINEMAX + 4, "%s", raw); g_appq_n++;
}

/* job-control words the firmware answers with a status string (plain 'ok' not guaranteed) */
/* (hardware V1.3.2-alpha: S3/S4 answer "trigger stop/finish: ok" + "Finish stop" and no plain ok) */
static int nook_cmd(const char *n) { return cmd_is(n, "M2410") || cmd_word(n, "M2411"); }

static void app_forward(const char *raw) {
    char n[LINEMAX]; norm_cmd(raw, n, sizeof n);
    if (g_ser < 0 || write_all(g_ser, raw, strlen(raw), 1000) < 0) { logf_("serial write (app) failed"); return; }
    g_app_lines++; g_last_app_tx = now_ms(); g_owner = OWN_APP; fan_track(n);
    if (nook_cmd(n)) g_app_settle_until = now_ms() + 1500; else g_app_pending++;
    if (n[0]) con_add('a', n);
}

static void net_send(const char *line, int kind, int purpose, int timeout_ms, const char *e1, const char *e2, const char *e3) {
    memset(&W, 0, sizeof W);
    W.quiet = g_next_quiet; g_next_quiet = 0;
    W.kind = kind; W.purpose = purpose; snprintf(W.cmd, sizeof W.cmd, "%s", line);
    const char *es[3] = { e1, e2, e3 };
    for (int i = 0; i < 3; i++) if (es[i]) snprintf(W.expect[W.nexp++], 40, "%s", es[i]);
    W.deadline = now_ms() + timeout_ms;
    g_owner = OWN_NET;
    if (purpose != P_QUERY || g_netq_n == 0) g_net_want_since = 0;   /* queued console commands go as one burst */
    if (to_ser_line(line) < 0) { W.failed = 1; snprintf(W.fail, sizeof W.fail, "serial write failed"); }
    g_net_lines++; if (!W.quiet) con_add('>', line);
}

/* EXPECT with an early acknowledgement: 'ack' seen -> the completion text may take ack_grace_ms more */
static void net_expect(const char *line, int purpose, int timeout_ms, const char *done1, const char *done2, const char *ack, int ack_grace_ms) {
    net_send(line, NW_EXPECT, purpose, timeout_ms, done1, done2, NULL);
    if (ack) { snprintf(W.ack, sizeof W.ack, "%s", ack); W.ack_grace_ms = ack_grace_ms; }
}

/* fairness: once the network side has waited 250 ms it claims the next free turn; new app lines queue */
static int net_claim(void) { return g_net_want_since && now_ms() - g_net_want_since > 250; }

static int net_ready(void) {            /* may the network side transmit now? */
    if (g_ser < 0 || g_owner != OWN_NONE || W.kind != NW_NONE) return 0;
    if (now_ms() < g_net_settle_until) return 0;
    if (net_claim()) return 1;
    if (g_appq_n) return 0;
    if (now_ms() < g_net_settle_until) return 0;      /* late 'ok' of a job-control word */
    if (now_ms() - g_last_app_tx < 300) return 0;     /* let multi-line app sequences finish */
    return 1;
}

/* ------------------------------------------------------------------ network job */
static void job_end(int st, const char *why) {
    if (J.f) { fclose(J.f); J.f = NULL; }
    J.st = st; J.ended_ms = now_ms();
    if (why) snprintf(J.err, sizeof J.err, "%s", why);
    write_current_job(0);
    logi_("job %s: %s%s%s (%ld/%ld lines)", J.name, jstate_name[st], why ? " - " : "", why ? why : "", J.sent_lines, J.total_lines);
    migrate_ram_jobs();
    to_app_line("Working Status: IDLE");                 /* closes the touchscreen lock page */
    long d = g_app_dropped; if (d > 8) d = 8;            /* give back acks for held app commands */
    for (long i = 0; i < d; i++) to_app_line("ok");
    g_app_dropped = 0;
}

static int prescan(const char *path, long *bytes, long *lines, char *err, size_t en) {
    FILE *f = fopen(path, "r"); if (!f) { snprintf(err, en, "cannot open %s", path); return -1; }
    char l[LINEMAX + 2], n[LINEMAX]; long b = 0, c = 0, ln = 0;
    while (fgets(l, sizeof l, f)) {
        ln++; b += strlen(l); norm_cmd(l, n, sizeof n);
        if (!n[0]) continue;
        c++;
        if (laser_over(n)) { snprintf(err, en, "line %ld: laser/spindle power above S100 refused (%s)", ln, n); fclose(f); return -1; }
        if (cmd_word(n, "M2001") || cmd_word(n, "M2411") || cmd_word(n, "M2410") || cmd_word(n, "M997") || cmd_word(n, "M110")) {
            snprintf(err, en, "line %ld: job-control/firmware command not allowed inside a job (%s)", ln, n); fclose(f); return -1;
        }
    }
    fclose(f); *bytes = b; *lines = c; return 0;
}

static int job_start(const char *path, const char *name, char *err, size_t en) {
    if (job_active()) { snprintf(err, en, "a network job is already running"); return 409; }
    if (AJ.active) { snprintf(err, en, "the touchscreen is printing; network jobs are blocked until it finishes"); return 409; }
    if (g_ser < 0) { snprintf(err, en, "printer link is down"); return 409; }
    if (S.working[0] && starts(S.working, "WORKING")) { snprintf(err, en, "printer reports %s; finish or stop that job first", S.working); return 409; }
    long b, l; if (prescan(path, &b, &l, err, en) < 0) return 400;
    char keep[256]; snprintf(keep, sizeof keep, "%s", name);
    memset(&J, 0, sizeof J);
    snprintf(J.path, sizeof J.path, "%s", path); snprintf(J.name, sizeof J.name, "%s", keep);
    snprintf(J.last_name, sizeof J.last_name, "%s", keep);
    J.f = fopen(path, "r"); if (!J.f) { snprintf(err, en, "cannot open job"); return 500; }
    J.total_bytes = b; J.total_lines = l; J.st = J_PREFLIGHT; J.started_ms = now_ms(); J.resend_n = -1; J.lost_retry_n = -1; J.stall_line = -1; J.m73_pct = -1;
    write_current_job(1);
    logi_("job %s: queued (%ld lines, %ld bytes)", keep, l, b);
    return 0;
}

static unsigned cks(const char *s) { unsigned c = 0; while (*s) c ^= (unsigned char)*s++; return c & 0xff; }

/* next real command from the job file (comment/blank stripped); 0 at EOF */
static int job_next(char *out, size_t on, long *off) {
    char l[LINEMAX + 2];
    for (;;) {
        *off = ftell(J.f);
        if (!fgets(l, sizeof l, J.f)) return 0;
        char *c = strchr(l, ';'); if (c) *c = 0;
        rstrip(l); char *p = l; while (isspace((unsigned char)*p)) p++;
        if (!*p) continue;
        snprintf(out, on, "%s", p); return 1;
    }
}

/* how long a job line may go without 'ok' before the stall probe (ms). Blocking commands get the long
   timeout; G4 gets its dwell + the stall window. echo:busy extends either. */
static int line_stall_ms(const char *n) {
    static const char *longc[] = { "G28", "G29", "G30", "G33", "G34", "G35", "G76", "M0", "M1", "M109", "M190", "M191",
        "M116", "M226", "M303", "M400", "M600", "M701", "M702", "M48", "M999", NULL };
    for (int i = 0; longc[i]; i++) if (cmd_word(n, longc[i])) return 600000;
    if (cmd_word(n, "G4") || cmd_word(n, "G04")) {
        double ms = 0; const char *p;
        if ((p = strstr(n, " P"))) ms = atof(p + 2);
        if ((p = strstr(n, " S"))) ms += atof(p + 2) * 1000.0;
        if (ms > 590000) return 600000;
        return (int)ms + g_stall_ms;
    }
    return g_stall_ms;
}

static void job_send_line(void) {
    char cmd[LINEMAX], line[LINEMAX + 32], full[LINEMAX + 48]; long off;
    if (!job_next(cmd, sizeof cmd, &off)) { J.st = J_FINISHING; return; }
    char n[LINEMAX]; norm_cmd(cmd, n, sizeof n);
    if (cmd_word(n, "M73")) {
        const char *p = strstr(n, " P"); if (p) J.m73_pct = atof(p + 2);
        const char *r = strstr(n, " R"); if (r) { J.m73_left_min = atof(r + 2); J.m73_ms = now_ms(); }
    }
    if (g_linenums) {
        J.n++;
        J.ring[J.n % RESEND_RING].n = J.n; J.ring[J.n % RESEND_RING].off = off;
        snprintf(line, sizeof line, "N%ld %s", J.n, cmd);
        snprintf(full, sizeof full, "%s*%u", line, cks(line));
        net_send(full, NW_OK, P_JOBLINE, 600000, NULL, NULL, NULL);
    } else net_send(cmd, NW_OK, P_JOBLINE, 600000, NULL, NULL, NULL);
    W.line_n = g_linenums ? J.n : -1;
    W.line_is_m105 = cmd_word(n, "M105");
    /* the probe needs line numbers to be safe (a resend with the same N is deduplicated by the firmware) */
    if (g_linenums && g_stall_ms > 0) W.stall_at = now_ms() + line_stall_ms(n);
}

/* lines whose loss does not change the print */
static int noop_line(const char *cmd) {
    char n[LINEMAX]; norm_cmd(cmd, n, sizeof n);
    const char *nm = n; if (nm[0] == 'N') { while (*nm && *nm != ' ') nm++; while (*nm == ' ') nm++; }
    char b[LINEMAX]; snprintf(b, sizeof b, "%s", nm); char *st = strchr(b, '*'); if (st) *st = 0; rstrip(b);
    static const char *nop[] = { "M73", "M117", "M105", "M114", "M27", "G4", "G04", "M400", NULL };
    for (int i = 0; nop[i]; i++) if (cmd_word(b, nop[i])) return 1;
    return 0;
}

/* the in-flight network command completed (ok / expected text / timeout / failure) */
static void net_done(void) {
    int p = W.purpose, to = W.timed_out, failed = W.failed, matched = W.matched, acked = W.acked; char fail[160], cmd[LINEMAX + 40];
    long line_n = W.line_n; int lost = W.lost;
    snprintf(fail, sizeof fail, "%s", W.fail); snprintf(cmd, sizeof cmd, "%s", W.cmd);
    if (W.kind == NW_EXPECT) g_net_settle_until = now_ms() + 700;
    W.kind = NW_NONE; g_owner = OWN_NONE;
    if (!job_active() || p == P_QUERY || p == P_POLL) return;
    if (failed) { job_end(J_ERROR, fail); return; }
    if (p == P_JOBLINE) {                 /* line accounting is independent of pause state (firmware may pause mid-line) */
        if (to) { job_end(J_ERROR, "timed out waiting for 'ok'"); return; }
        if (J.resend_n >= 0) {
            long rn = J.resend_n; J.resend_n = -1;
            if (lost) J.lost_retry_n = line_n;           /* watch how the firmware takes the re-send */
            else if (J.lost_retry_n >= 0 && line_n == J.lost_retry_n) {
                J.lost_retry_n = -1;
                if (rn == line_n + 1) {           /* firmware already had this N: it took the number but never ok'd it */
                    if (noop_line(cmd)) logf_("job: N%ld was not executed by the printer (no-op line, ignored): %s", line_n, cmd);
                    else {
                        J.lost_lines++;
                        logf_("ERROR job: N%ld was accepted by number but never acknowledged; NOT re-sent (line-number dedup): %s", line_n, cmd);
                        snprintf(J.err, sizeof J.err, "line N%ld may not have executed (printer never acknowledged it): %.120s", line_n, cmd);
                    }
                }
            }
            if (++J.resends > 50) { job_end(J_ERROR, "too many resend requests"); return; }
            struct ring_e *e = &J.ring[rn % RESEND_RING];
            if (rn == J.n + 1) {              /* "resend the next line" == nothing to rewind */
                J.sent_lines++; return;
            }
            if (rn < 1 || rn > J.n || e->n != rn) { job_end(J_ERROR, "resend target outside window"); return; }
            fseek(J.f, e->off, SEEK_SET);
            J.sent_lines -= (J.n - rn); if (J.sent_lines < 0) J.sent_lines = 0;
            logf_("job: resend from N%ld", rn); J.n = rn - 1; return;
        }
        if (J.lost_retry_n >= 0 && line_n == J.lost_retry_n) J.lost_retry_n = -1;   /* the retry executed normally */
        J.sent_lines++; return;
    }
    switch (J.st) {
    case J_PREFLIGHT:
        if (S.working[0] && starts(S.working, "WORKING")) { job_end(J_ERROR, "printer is busy (Working Status reports a job)"); return; }
        if (S.systat == 5) { job_end(J_ERROR, "printer still holds a paused job (status 5); clear it first"); return; }
        J.st = g_linenums ? J_M110 : J_STARTING; return;
    case J_M110: J.st = J_STARTING; return;
    case J_STARTING:
        if (!matched || to) { job_end(J_ERROR, to ? "printer did not acknowledge M2411 S2" : "printer refused to start"); return; }
        J.st = J_PRINTING; to_app_line("Working Status: WORKING_PC");    /* stock lock page on the touchscreen */
        return;
    case J_PAUSING:
        if (matched) logf_("job: paused (Finish pause)");
        else if (acked) logf_("job: paused (trigger pause ack only, no \"Finish pause\")");
        else { logf_("job: printer did not confirm M2410; holding the stream as paused"); snprintf(J.err, sizeof J.err, "printer did not confirm pause"); }
        J.st = J_PAUSED; return;
    case J_RESUMING:
        if (matched) { logf_("job: resumed (Resume complete)"); J.st = J_PRINTING; return; }
        if (acked) {
            logf_("job: no \"Resume complete\" within %d ms after \"trigger resume\"; continuing (stall recovery armed)", g_resume_ms);
            J.st = J_PRINTING; return;
        }
        logf_("job: printer did not acknowledge M2411 S1; still paused");
        snprintf(J.err, sizeof J.err, "printer did not acknowledge resume; still paused");
        J.st = J_PAUSED; return;
    case J_FINISHING:
        if (!matched) logf_("job: M2411 S4 %s", acked ? "acknowledged without \"Finish stop\"" : "not acknowledged");
        job_end(J_DONE, NULL); return;
    case J_CANCELLING:
        if (!matched && !acked) logf_("job: M2411 S3 not acknowledged; cooling down anyway");
        J.st = J_COOLDOWN; J.cool_i = 0; return;
    case J_COOLDOWN: if (J.cool_i >= 4) job_end(J_CANCELLED, "cancelled"); return;
    }
}

static void job_tick(void) {
    if (!job_active() || !net_ready()) return;
    if (J.want_cancel && J.st != J_CANCELLING && J.st != J_COOLDOWN) {
        J.want_cancel = 0;
        if (J.st == J_PREFLIGHT || J.st == J_M110) { job_end(J_CANCELLED, "cancelled before start"); return; }
        J.st = J_CANCELLING;
        net_expect("M2411 S3", P_JOBCTL, 10000, "finish stop", "can't trigger stop", "trigger stop", 3000);
        return;
    }
    switch (J.st) {
    case J_PREFLIGHT: net_send("M2007", NW_OK, P_JOBCTL, 5000, NULL, NULL, NULL); return;
    case J_M110: net_send("M110 N0", NW_OK, P_JOBCTL, 5000, NULL, NULL, NULL); return;
    case J_STARTING: net_send("M2411 S2", NW_EXPECT, P_START, 30000, "trigger work: ok", NULL, NULL); return;
    case J_PRINTING:
        if (J.want_pause) {          /* complete on "Finish pause"; "trigger pause: ok" alone is accepted after 3 s */
            J.want_pause = 0; J.st = J_PAUSING; J.err[0] = 0;
            net_expect("M2410", P_JOBCTL, 10000, "finish pause", NULL, "trigger pause", 3000); return;
        }
        job_send_line(); return;
    case J_PAUSED:
        if (J.want_resume) {         /* never stream again before "Resume complete" (firmware drops lines until then) */
            J.want_resume = 0; J.st = J_RESUMING; J.err[0] = 0;
            net_expect("M2411 S1", P_JOBCTL, g_resume_ms, "resume complete", NULL, "trigger resume", g_resume_ms);
        }
        return;
    case J_FINISHING: net_expect("M2411 S4", P_JOBCTL, 10000, "finish stop", NULL, "trigger finish", 3000); return;
    case J_COOLDOWN: {
        static const char *c[] = { "M5", "M104 S0", "M140 S0", "M107" };
        if (J.cool_i == 0 && !head_is_laser()) J.cool_i = 1;       /* M5 only for a laser head */
        if (J.cool_i < 4) net_send(c[J.cool_i++], NW_OK, P_JOBCTL, 5000, NULL, NULL, NULL);
        return; }
    }
}

/* ------------------------------------------------------------------ STM32 -> routing */
static int is_term(const char *l) { return strcmp(l, "ok") == 0 || starts(l, "ok "); }
static int is_async(const char *l) {
    const char *s = l; while (*s == ' ') s++;
    return starts(s, "echo:busy") || istarts(s, "Working Status:") || istarts(s, "job status:") ||
           (starts(s, "T:") && !starts(l, "ok")) || strstr(s, "Count A:") != NULL || (s[0] == 'X' && s[1] == ':') ||
           istarts(s, "CMD buffer:") || istarts(s, "Homed:");
}
static int is_halt(const char *l) { return istrstr(l, "printer halted") || istrstr(l, "kill() called"); }

static void ser_line(char *raw, int rawlen) {
    char l[LINEMAX + 4]; snprintf(l, sizeof l, "%.*s", rawlen, raw); rstrip(l);
    char *lp = l; while (*lp == '\r') lp++;
    g_last_ser_rx = now_ms();
    parse_status(lp);
    int term = is_term(lp);
    int ws = istarts(lp, "Working Status:");
    if (is_halt(lp)) {                                     /* always reaches the app (stock halt dialog) */
        to_app(raw, rawlen);
        if (job_active()) job_end(J_ERROR, lp);
        if (g_owner == OWN_NET) { W.kind = NW_NONE; g_owner = OWN_NONE; }
        con_add('<', lp); return;
    }
    /* firmware-side pause of our job (touchscreen/firmware trigger) */
    if (job_active() && J.st == J_PRINTING && istrstr(lp, "trigger pause") && !(g_owner == OWN_NET && J.st == J_PAUSING)) {
        if (!(g_owner == OWN_NET && W.purpose == P_JOBCTL)) { J.st = J_PAUSED; logf_("job paused by the printer: %s", lp); }
    }
    if (g_owner == OWN_NET) {
        if (ws && job_active()) to_app_line("Working Status: WORKING_PC");
        else if (is_async(lp)) to_app(raw, rawlen);          /* reports the app normally sees */
        if (lp[0] && !is_async(lp) && !W.quiet) con_add('<', lp);
        if (strstr(lp, "echo:busy")) {
            W.deadline = now_ms() + (W.purpose == P_JOBLINE ? 600000 : 30000);
            if (W.stall_at && W.stall_at < now_ms() + 2 * g_stall_ms) W.stall_at = now_ms() + 2 * g_stall_ms;
        }
        if (W.purpose == P_JOBLINE && (istarts(lp, "Resend:") || istarts(lp, "rs "))) {
            const char *p = lp + (lp[0] == 'r' || lp[0] == 'R' ? (lp[1] == 's' || lp[1] == 'S' ? (lp[2] == ' ' ? 3 : 7) : 7) : 7);
            while (*p == ' ' || *p == 'N' || *p == ':') p++;
            J.resend_n = atol(p);
        }
        if (W.purpose == P_START && (istrstr(lp, "Can't start work") || istrstr(lp, "start work failed"))) {
            W.failed = 1; snprintf(W.fail, sizeof W.fail, "printer refused to start: %s", lp);
        }
        if (W.kind == NW_EXPECT) {
            for (int i = 0; i < W.nexp; i++) if (!W.matched && istrstr(lp, W.expect[i])) { W.matched = 1; W.settle_until = now_ms() + 300; }
            if (!W.matched && W.ack[0] && !W.acked && istrstr(lp, W.ack)) {
                W.acked = 1; long long g = now_ms() + W.ack_grace_ms; if (g < W.deadline) W.deadline = g;
            }
            if (W.failed) net_done();
            /* a plain 'ok' during EXPECT is consumed here and never reaches the app */
        } else if (W.kind == NW_OK && W.failed) {
            net_done();
        } else if (W.kind == NW_OK && term) {
            if (!W.probing) net_done();
            else {
                /* stall probe outstanding: the firmware answers in order, so a plain ok is the line's (late) ok and
                   "ok T:" is the probe's reply. Probe reply without the line's ok = the line was dropped. */
                int probe_reply = strstr(lp, "T:") != NULL;
                if (W.line_is_m105 && !W.line_acked) probe_reply = 0;
                if (!probe_reply) { W.line_acked = 1; logf_("job: late ok for N%ld (no loss)", W.line_n); }
                else {
                    if (!W.line_acked && J.resend_n < 0) {
                        logf_("job: N%ld got no ok (probe answered first); re-sending it with the same line number", W.line_n);
                        J.resend_n = W.line_n; W.lost = 1;
                    }
                    net_done();
                }
            }
        }
        return;
    }
    /* settle window after a network job-control word: swallow its late plain 'ok' */
    if (term && g_owner == OWN_NONE && W.kind == NW_NONE && now_ms() < g_net_settle_until) { g_stray_ok_dropped++; con_add('<', "(stray ok after network job-control word dropped)"); return; }
    if (term && g_owner == OWN_NONE && W.kind == NW_NONE && g_stray_budget > 0 && now_ms() < g_stray_until) {
        g_stray_budget--; g_stray_ok_dropped++; con_add('<', "(late ok of an abandoned network wait dropped)"); return;
    }
    /* app owns the link, or nobody: pass-through */
    if (ws && job_active()) to_app_line("Working Status: WORKING_PC");
    else to_app(raw, rawlen);
    if (lp[0] && !is_async(lp)) con_add('<', lp);
    if (term && g_owner == OWN_APP) {
        if (g_app_pending > 0) g_app_pending--;
        if (g_app_pending == 0 && now_ms() >= g_app_settle_until) g_owner = OWN_NONE;
    }
}

/* ------------------------------------------------------------------ app -> routing */
static int allowed_during_net_job(const char *n) {
    static const char *ok[] = { "M105", "M114", "M2007", "M2005", "M115", "M119", "M2051", "M503", "M2155", "M220", "M27", NULL };
    for (int i = 0; ok[i]; i++) if (cmd_word(n, ok[i])) {
        if (cmd_word(n, "M220") && strchr(n, 'S')) return 0;    /* query only */
        return 1;
    }
    return 0;
}

static void app_line(char *raw) {
    char n[LINEMAX]; norm_cmd(raw, n, sizeof n);
    if (cmd_is(n, "M2411 S2") && !job_active()) {
        memset(&AJ, 0, sizeof AJ); AJ.active = 1; AJ.started_ms = now_ms(); AJ.m73_pct = -1; logf_("touchscreen job started");
    }
    if (AJ.active) {
        AJ.last_ms = now_ms();
        if (n[0]) AJ.lines++;
        if (cmd_word(n, "M73")) { const char *p = strstr(n, " P"); if (p) AJ.m73_pct = atof(p + 2); const char *r = strstr(n, " R"); if (r) AJ.m73_left_min = atof(r + 2); }
        if (cmd_is(n, "M2411 S3") || cmd_is(n, "M2411 S4") || cmd_is(n, "M108")) AJ.end_seen = 1;
    }
    if (job_active()) {
        if (cmd_is(n, "M108") || cmd_is(n, "M2001 S1")) {
            /* "Disconnect IVI 3licer" on the lock page: stop our job the graceful way */
            if (!J.want_cancel && J.st != J_CANCELLING && J.st != J_COOLDOWN) { logf_("touchscreen asked to stop the network job (%s)", n); J.want_cancel = 1; }
            to_app_line("ok"); con_add('a', n); return;
        }
        if (allowed_during_net_job(n)) { if (g_owner == OWN_NET || g_appq_n || net_claim()) appq_push(raw); else app_forward(raw); return; }
        if (n[0]) { g_app_dropped++; g_app_dropped_total++; logf_("held app command during network job: %s", n); con_add('x', n); }
        return;
    }
    if (g_owner == OWN_NET || g_appq_n || net_claim()) { appq_push(raw); return; }
    app_forward(raw);
}

/* ------------------------------------------------------------------ periodic */
static void tick(void) {
    long long t = now_ms();
    /* cancel is never blocked behind an in-flight wait: give the reply a moment, then abandon it */
    if (W.kind != NW_NONE && job_active() && J.want_cancel && J.st != J_CANCELLING && J.st != J_COOLDOWN) {
        if (!W.cancel_at) W.cancel_at = t + g_cancel_grace_ms;
        else if (t >= W.cancel_at) {
            logf_("cancel: abandoning the wait for a reply to %s", W.cmd);
            g_stray_budget = (W.kind == NW_OK ? 1 : 0) + (W.probing ? 1 : 0); g_stray_until = t + 15000;
            W.kind = NW_NONE; g_owner = OWN_NONE; g_net_settle_until = 0;
        }
    }
    if (W.kind == NW_OK && W.purpose == P_JOBLINE && W.stall_at && !W.probing && t >= W.stall_at && g_ser >= 0) {
        if (J.stall_line == W.line_n) J.stall_tries++; else { J.stall_line = W.line_n; J.stall_tries = 1; }
        if (J.stall_tries > 3) { W.failed = 1; snprintf(W.fail, sizeof W.fail, "N%ld stalled 3 times; giving up", W.line_n); net_done(); }
        else {
            W.probing = 1; J.stalls++;
            logf_("job: no ok for N%ld within its stall window; probing with M105", W.line_n);
            to_ser_line("M105"); con_add('>', "M105 (stall probe)");
        }
    }
    if (W.kind != NW_NONE) {
        if (W.kind == NW_EXPECT && W.matched && t >= W.settle_until) net_done();
        else if (t > W.deadline) { W.timed_out = 1; logf_("timeout waiting for reply to %s", W.cmd); net_done(); }
    }
    if (g_owner == OWN_APP) {
        if (g_app_pending == 0 && t >= g_app_settle_until) g_owner = OWN_NONE;
        else if (t - g_last_ser_rx > 5000 && t - g_last_app_tx > 5000 && !AJ.active) {
            logf_("app ownership resync (pending %d, link quiet 5 s)", g_app_pending); g_app_pending = 0; g_owner = OWN_NONE;
        }
    }
    {   int want = (g_netq_n && !AJ.active) || (job_active() && (J.st != J_PAUSED || J.want_cancel || J.want_resume));
        if (!want) g_net_want_since = 0; else if (!g_net_want_since) g_net_want_since = t; }
    /* queued app lines get their turn (one at a time while sharing) */
    while (!net_claim() && g_owner != OWN_NET && W.kind == NW_NONE && g_appq_n && g_ser >= 0) {
        if (g_owner == OWN_APP && g_app_pending) break;
        char line[LINEMAX + 4]; snprintf(line, sizeof line, "%s", g_appq[g_appq_h]); g_appq_h = (g_appq_h + 1) % APPQ; g_appq_n--;
        char n[LINEMAX]; norm_cmd(line, n, sizeof n);
        if (job_active() && !allowed_during_net_job(n)) { g_app_dropped++; g_app_dropped_total++; continue; }
        app_forward(line);
    }
    /* touchscreen job end: an end word then quiet, or firmware idle + quiet */
    if (AJ.active) {
        int idle = S.working[0] && !starts(S.working, "WORKING") && S.working_ms > AJ.started_ms + 3000;
        if ((AJ.end_seen && t - AJ.last_ms > 3000) || (idle && t - AJ.last_ms > 15000)) { AJ.active = 0; logf_("touchscreen job ended (%ld lines)", AJ.lines); }
    }
    job_tick();
    if (g_netq_n && net_ready() && !AJ.active && (!job_active() || J.st == J_PRINTING || J.st == J_PAUSED)) {
        char c[96]; snprintf(c, sizeof c, "%s", g_netq[g_netq_h]);
        int qq = g_netq_quiet[g_netq_h]; g_netq_quiet[g_netq_h] = 0; g_netq_h = (g_netq_h + 1) % 16; g_netq_n--;
        g_next_quiet = qq;
        if (nook_cmd(c)) net_send(c, NW_EXPECT, P_QUERY, 5000, "trigger", NULL, NULL);
        else net_send(c, NW_OK, P_QUERY, 10000, NULL, NULL, NULL);
    }
    /* idle temperature poll, only if the firmware's own reports stopped */
    if (g_poll_s > 0 && !job_active() && !AJ.active && net_ready() && t - g_last_app_tx > 2000 &&
        t - S.t_ms > g_poll_s * 1000LL && t - g_last_ser_rx > 1000) {
        S.t_ms = t;
        net_send("M105", NW_OK, P_POLL, 5000, NULL, NULL, NULL);
    }
}

/* ------------------------------------------------------------------ HTTP */
struct cli {
    int fd; char hdr[16384]; int hn; int hdone; long clen, got; char *body; int up_fd; char up_tmp[600];
    char method[8], path[512], query[512], ctype[256], key[160]; long long t0; int lan;
};
static struct cli C[MAXCLI];

static void cli_close(struct cli *c) {
    if (c->fd >= 0) close(c->fd);
    if (c->up_fd >= 0) { close(c->up_fd); unlink(c->up_tmp); }
    free(c->body); memset(c, 0, sizeof *c); c->fd = -1; c->up_fd = -1;
}

struct sb { char *b; size_t n, cap; };
static void sb_add(struct sb *s, const char *fmt, ...) {
    va_list ap; va_start(ap, fmt); char tmp[4096]; int k = vsnprintf(tmp, sizeof tmp, fmt, ap); va_end(ap);
    if (k < 0) return;
    if ((size_t)k >= sizeof tmp) k = sizeof tmp - 1;
    if (s->n + k + 1 > s->cap) { s->cap = (s->n + k + 1) * 2; s->b = realloc(s->b, s->cap); }
    memcpy(s->b + s->n, tmp, k); s->n += k; s->b[s->n] = 0;
}
static void sb_str(struct sb *s, const char *v) {
    sb_add(s, "\"");
    for (const unsigned char *p = (const unsigned char *)v; *p; p++) {
        if (*p == '"' || *p == '\\') sb_add(s, "\\%c", *p);
        else if (*p < 0x20) sb_add(s, "\\u%04x", *p);
        else sb_add(s, "%c", *p);
    }
    sb_add(s, "\"");
}
static void reply(struct cli *c, int code, const char *ctype, const char *body, size_t n) {
    const char *msg = code == 200 ? "OK" : code == 201 ? "Created" : code == 204 ? "No Content" : code == 400 ? "Bad Request" :
        code == 403 ? "Forbidden" : code == 404 ? "Not Found" : code == 409 ? "Conflict" : code == 413 ? "Payload Too Large" : "Error";
    char h[512]; int k = snprintf(h, sizeof h, "HTTP/1.1 %d %s\r\nServer: ivibridge/%s\r\nContent-Type: %s\r\nContent-Length: %zu\r\n"
        "Cache-Control: no-store\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Headers: X-Api-Key, Content-Type\r\nConnection: close\r\n\r\n",
        code, msg, VERSION, ctype, n);
    if (write_all(c->fd, h, k, 5000) < 0) return;
    if (n) write_all(c->fd, body, n, 5000);
}
static void jreply(struct cli *c, int code, struct sb *s) { reply(c, code, "application/json", s->b ? s->b : "{}", s->b ? s->n : 2); free(s->b); }
static void jerr(struct cli *c, int code, const char *msg) { struct sb s = {0}; sb_add(&s, "{\"error\":"); sb_str(&s, msg); sb_add(&s, "}"); jreply(c, code, &s); }

/* tiny JSON getters for the flat objects OctoPrint clients send */
static int jget_str(const char *j, const char *k, char *out, size_t on) {
    char pat[64]; snprintf(pat, sizeof pat, "\"%s\"", k);
    const char *p = j ? strstr(j, pat) : NULL; if (!p) return 0;
    p = strchr(p + strlen(pat), ':'); if (!p) return 0; p++;
    while (isspace((unsigned char)*p)) p++;
    if (*p == '"') { p++; size_t i = 0; while (*p && *p != '"' && i + 1 < on) { if (*p == '\\' && p[1]) p++; out[i++] = *p++; } out[i] = 0; return 1; }
    size_t i = 0; while (*p && *p != ',' && *p != '}' && *p != ']' && !isspace((unsigned char)*p) && i + 1 < on) out[i++] = *p++;
    out[i] = 0; return i > 0;
}
static int jget_bool(const char *j, const char *k) { char v[16]; return jget_str(j, k, v, sizeof v) && (!strcmp(v, "true") || !strcmp(v, "1")); }

/* console allowlist, same limits as ivi_bridge.py check_command (no M3/M4 at all) */
static int check_command(const char *in, char *out, size_t on, char *err, size_t en) {
    char n[160]; norm_cmd(in, n, sizeof n);
    if (!n[0]) { snprintf(err, en, "empty command"); return -1; }
    if (laser_over(n)) { snprintf(err, en, "laser/spindle power above S100 refused"); return -1; }
    static const char *exact[] = { "M503", "M115", "M119", "M105", "M2007", "M2410", "M2411 S1", "M2411 S3", "M107", "M114",
        "M82", "M83", "G90", "G91", "G28", "G28 X", "G28 Y", "G28 Z", "G28 X Y", "G28 X Y Z", "M220", "M106", NULL };
    for (int i = 0; exact[i]; i++) if (!strcmp(n, exact[i])) { snprintf(out, on, "%s", n); return 0; }
    /* fans: M106 [P0|P1] [S0..255], M107 [P0|P1] */
    if (cmd_word(n, "M106") || cmd_word(n, "M107")) {
        int is106 = n[3] == '6', seenp = 0, seens = 0; char tmp[160]; snprintf(tmp, sizeof tmp, "%s", n + 4);
        char *sv, *w;
        for (w = strtok_r(tmp, " ", &sv); w; w = strtok_r(NULL, " ", &sv)) {
            char *e; long v = strtol(w + 1, &e, 10);
            if (*e || e == w + 1) { snprintf(err, en, "bad fan word %s", w); return -1; }
            if (w[0] == 'P' && !seenp++) { if (v < 0 || v > 1) { snprintf(err, en, "fan index %s outside P0..P1", w); return -1; } }
            else if (w[0] == 'S' && is106 && !seens++) { if (v < 0 || v > 255) { snprintf(err, en, "M106 %s outside 0..255", w); return -1; } }
            else { snprintf(err, en, "bad fan word %s", w); return -1; }
        }
        snprintf(out, on, "%s", n); return 0;
    }
    struct { const char *code; int lo, hi; } lim[] = { {"M104", 0, 300}, {"M140", 0, 120}, {"M220", 10, 300}, {"M221", 10, 200}, {"M106", 0, 255} };
    for (size_t i = 0; i < sizeof lim / sizeof lim[0]; i++) {
        size_t l = strlen(lim[i].code);
        if (!strncmp(n, lim[i].code, l) && n[l] == ' ' && n[l+1] == 'S') {
            char *e; long v = strtol(n + l + 2, &e, 10);
            if (*e || e == n + l + 2) break;
            if (v < lim[i].lo || v > lim[i].hi) { snprintf(err, en, "%s S%ld outside %d..%d", lim[i].code, v, lim[i].lo, lim[i].hi); return -1; }
            snprintf(out, on, "%s", n); return 0;
        }
    }
    if (cmd_word(n, "G1")) {
        double cap[128] = {0}; cap['X'] = 150; cap['Y'] = 150; cap['Z'] = 300; cap['E'] = 150; cap['F'] = 6000;
        int seen[128] = {0}; char tmp[160]; snprintf(tmp, sizeof tmp, "%s", n + 2);
        char *sv, *w = strtok_r(tmp, " ", &sv); if (!w) { snprintf(err, en, "G1 needs an axis"); return -1; }
        for (; w; w = strtok_r(NULL, " ", &sv)) {
            unsigned char k = w[0]; char *e; double v = strtod(w + 1, &e);
            if (k >= 128 || !cap[k] || *e || e == w + 1 || seen[k]++) { snprintf(err, en, "bad G1 word %s", w); return -1; }
            if (v > cap[k] || v < -cap[k] || (k == 'F' && v <= 0)) { snprintf(err, en, "%s exceeds limit", w); return -1; }
        }
        snprintf(out, on, "%s", n); return 0;
    }
    snprintf(err, en, "command not allowed: %s", n); return -1;
}

static int is_lan(const struct sockaddr_in *a) {
    if (a->sin_family != AF_INET) return 0;
    unsigned ip = ntohl(a->sin_addr.s_addr);
    return (ip >> 24) == 10 || (ip >> 16) == 0xC0A8 || (ip >> 20) == 0xAC1;
}
static int authed(struct cli *c) {
    if (!g_apikey[0]) return 0;
    if (c->lan) return 1;   /* home-network client (RFC1918 only; loopback and Tailscale 100.x still need the key) */
    if (!strcmp(c->key, g_apikey)) return 1;
    char q[200]; snprintf(q, sizeof q, "apikey=%s", g_apikey);
    const char *f = strstr(c->query, q);
    return f && (f == c->query || f[-1] == '&') && (f[strlen(q)] == 0 || f[strlen(q)] == '&');
}

static const char *state_text(char *buf, size_t n) {
    if (g_ser < 0) return "Offline";
    if (job_active()) return jstate_name[J.st];
    if (AJ.active) return "Printing";
    if (S.working[0] && starts(S.working, "WORKING")) return (S.systat == 5 || S.systat == 4) ? "Paused" : "Printing";
    if (J.st == J_ERROR && J.err[0] && now_ms() - J.ended_ms < 60000) { snprintf(buf, n, "Error: %s", J.err); return buf; }
    return "Operational";
}

static void api_printer(struct cli *c) {
    struct sb s = {0}; char sbuf[256]; const char *st = state_text(sbuf, sizeof sbuf);
    int printing = !strcmp(st, "Printing") || !strcmp(st, "Starting") || !strcmp(st, "Finishing") || !strcmp(st, "Resuming");
    int paused = !strcmp(st, "Paused") || !strcmp(st, "Pausing");
    sb_add(&s, "{\"state\":{\"text\":"); sb_str(&s, st);
    sb_add(&s, ",\"flags\":{\"operational\":%s,\"printing\":%s,\"paused\":%s,\"pausing\":%s,\"cancelling\":%s,\"ready\":%s,\"error\":%s,\"closedOrError\":%s}},",
        g_ser >= 0 ? "true" : "false", printing ? "true" : "false", paused ? "true" : "false", !strcmp(st, "Pausing") ? "true" : "false",
        !strcmp(st, "Cancelling") ? "true" : "false",
        (!job_active() && !AJ.active && g_ser >= 0 && !printing && !paused) ? "true" : "false", starts(st, "Error") ? "true" : "false",
        (g_ser < 0 || starts(st, "Error")) ? "true" : "false");
    if (S.have_t) sb_add(&s, "\"temperature\":{\"tool0\":{\"actual\":%.1f,\"target\":%.1f,\"offset\":0},\"bed\":{\"actual\":%.1f,\"target\":%.1f,\"offset\":0}},",
        S.t_act, S.t_tgt, S.b_act, S.b_tgt);
    else sb_add(&s, "\"temperature\":{},");
    if (S.have_pos) sb_add(&s, "\"position\":{\"x\":%.2f,\"y\":%.2f,\"z\":%.2f},", S.x, S.y, S.z); else sb_add(&s, "\"position\":null,");
    sb_add(&s, "\"ivi\":{\"bridge\":\"a33\",\"link\":%s,\"owner\":\"%s\",\"touchscreen_job\":%s,\"working\":",
        g_ser >= 0 ? "true" : "false", own_name[g_owner], AJ.active ? "true" : "false");
    sb_str(&s, S.working);
    sb_add(&s, ",\"head\":"); sb_str(&s, S.head);
    sb_add(&s, ",\"systat\":%d", S.systat);
    int f0 = fan_pct(g_fan[0]), f1 = fan_pct(g_fan[1]), fm = f0 > f1 ? f0 : f1;
    if (fm < 0) sb_add(&s, ",\"fan\":null,\"fans\":[null,null]");
    else {
        sb_add(&s, ",\"fan\":%d,\"fans\":[", fm);
        if (f0 < 0) sb_add(&s, "null,"); else sb_add(&s, "%d,", f0);
        if (f1 < 0) sb_add(&s, "null]"); else sb_add(&s, "%d]", f1);
    }
    sb_add(&s, ",\"report_age_s\":%.1f}}", S.t_ms ? (now_ms() - S.t_ms) / 1000.0 : -1.0);
    jreply(c, 200, &s);
}

static void api_job(struct cli *c) {
    struct sb s = {0}; char sbuf[256]; const char *st = state_text(sbuf, sizeof sbuf);
    long long t = now_ms();
    if (job_active() || ((J.st == J_DONE || J.st == J_CANCELLED || J.st == J_ERROR) && !AJ.active)) {
        double comp = J.total_lines ? 100.0 * J.sent_lines / J.total_lines : 0;
        double el = J.started_ms ? ((job_active() ? t : J.ended_ms) - J.started_ms) / 1000.0 : 0;
        double left = -1;
        if (J.m73_ms && job_active()) { left = J.m73_left_min * 60.0 - (t - J.m73_ms) / 1000.0; if (left < 0) left = 0; }
        else if (J.sent_lines > 0 && job_active()) left = el * (J.total_lines - J.sent_lines) / J.sent_lines;
        sb_add(&s, "{\"job\":{\"file\":{\"name\":"); sb_str(&s, J.name);
        sb_add(&s, ",\"origin\":\"local\",\"size\":%ld}},\"progress\":{\"completion\":%.2f,\"printTime\":%.0f,", J.total_bytes, comp, el);
        if (left >= 0) sb_add(&s, "\"printTimeLeft\":%.0f,", left); else sb_add(&s, "\"printTimeLeft\":null,");
        sb_add(&s, "\"filepos\":%ld},\"state\":", J.sent_lines);
        if (job_active()) sb_str(&s, jstate_name[J.st]);
        else if (J.st == J_ERROR) { char e[260]; snprintf(e, sizeof e, "Error: %s", J.err); sb_str(&s, e); }
        else sb_str(&s, st);
        sb_add(&s, ",\"ivi\":{\"source\":\"network stream (a33)\",\"job_state\":\"%s\",\"sent\":%ld,\"total\":%ld,\"resends\":%d,\"stalls\":%d,\"lost_lines\":%d", jstate_name[J.st], J.sent_lines, J.total_lines, J.resends, J.stalls, J.lost_lines);
        if (J.err[0]) { sb_add(&s, ",\"message\":"); sb_str(&s, J.err); }
        sb_add(&s, "}}");
    } else if (AJ.active) {
        double el = (t - AJ.started_ms) / 1000.0;
        sb_add(&s, "{\"job\":{\"file\":{\"name\":null,\"origin\":\"printer\"}},\"progress\":{\"completion\":");
        if (AJ.m73_pct >= 0) sb_add(&s, "%.1f", AJ.m73_pct); else sb_add(&s, "null");
        sb_add(&s, ",\"printTime\":%.0f,\"printTimeLeft\":", el);
        if (AJ.m73_left_min > 0) sb_add(&s, "%.0f", AJ.m73_left_min * 60); else sb_add(&s, "null");
        sb_add(&s, ",\"filepos\":%ld},\"state\":\"Printing\",\"ivi\":{\"source\":\"touchscreen\",\"lines_sent\":%ld}}", AJ.lines, AJ.lines);
    } else {
        sb_add(&s, "{\"job\":{\"file\":{\"name\":"); if (J.last_name[0]) sb_str(&s, J.last_name); else sb_add(&s, "null");
        sb_add(&s, ",\"origin\":\"local\"}},\"progress\":{\"completion\":null,\"printTime\":null,\"printTimeLeft\":null,\"filepos\":null},\"state\":");
        sb_str(&s, st); sb_add(&s, "}");
    }
    jreply(c, 200, &s);
}

static int safe_name(const char *in, char *out, size_t on) {
    const char *b = strrchr(in, '/'); b = b ? b + 1 : in;
    size_t j = 0;
    for (const char *p = b; *p && j + 1 < on; p++) {
        unsigned char ch = *p;
        out[j++] = (isalnum(ch) || ch == '.' || ch == '-' || ch == '_' || ch == ' ' || ch == '(' || ch == ')') ? ch : '_';
    }
    out[j] = 0;
    size_t l = strlen(out);
    if (!l || out[0] == '.' || l < 7 || strcasecmp(out + l - 6, ".gcode")) return -1;
    return 0;
}


static int queue_has(const char *name) {
    for (int i = 0; i < g_qn; i++) if (!strcmp(g_queue[i], name)) return 1;
    return 0;
}
static int queue_add(const char *name, char *err, size_t en) {
    if (queue_has(name)) { snprintf(err, en, "already queued"); return -1; }
    if (g_qn >= QMAX) { snprintf(err, en, "queue is full"); return -1; }
    snprintf(g_queue[g_qn++], sizeof g_queue[0], "%s", name);
    return 0;
}
static int queue_del(const char *name) {
    int w = 0;
    for (int i = 0; i < g_qn; i++) if (strcmp(g_queue[i], name)) snprintf(g_queue[w++], sizeof g_queue[0], "%s", g_queue[i]);
    int n = g_qn - w; g_qn = w; return n;
}
static void sb_queue(struct sb *s) {
    sb_add(s, ",\"queue\":[");
    for (int i = 0; i < g_qn; i++) { if (i) sb_add(s, ","); sb_str(s, g_queue[i]); }
    sb_add(s, "]");
}

static int qget(const char *q, const char *k, char *out, size_t on) {
    if (!q || !k) return 0;
    size_t kl = strlen(k);
    for (const char *p = q; *p; ) {
        if (!strncmp(p, k, kl) && p[kl] == '=') {
            p += kl + 1; size_t i = 0;
            while (*p && *p != '&' && i + 1 < on) {
                if (p[0] == '%' && isxdigit((unsigned char)p[1]) && isxdigit((unsigned char)p[2])) {
                    char h[3] = { p[1], p[2], 0 }; out[i++] = (char)strtol(h, NULL, 16); p += 3;
                } else if (*p == '+') { out[i++] = ' '; p++; }
                else out[i++] = *p++;
            }
            out[i] = 0; return 1;
        }
        const char *amp = strchr(p, '&'); if (!amp) break; p = amp + 1;
    }
    return 0;
}

static int parse_est_duration(const char *s, long *out) {
    long t = 0; const char *p = s; int any = 0;
    while (*p) {
        while (*p && !isdigit((unsigned char)*p)) p++;
        if (!*p) break;
        char *e; long v = strtol(p, &e, 10); if (e == p) break; p = e;
        while (*p == ' ') p++;
        if (*p == 'h' || *p == 'H') { t += v * 3600; p++; }
        else if (*p == 'm' || *p == 'M') { t += v * 60; p++; }
        else if (*p == 's' || *p == 'S') { t += v; p++; }
        else t += v;
        any = 1;
    }
    if (any) *out = t;
    return any ? 0 : -1;
}

typedef struct {
    int have_time, have_mm, have_g, have_thumb;
    long time_s;
    double filament_mm, filament_g;
} file_meta;

static void scan_meta_line(const char *line, file_meta *m) {
    const char *s = line;
    while (*s == ';' || isspace((unsigned char)*s)) s++;
    if (!strncasecmp(s, "estimated_time(s):", 18)) {
        if (!m->have_time) { m->time_s = atol(s + 18); m->have_time = 1; }
        return;
    }
    if (!strncasecmp(s, "estimated printing time (normal mode)", 37) || !strncasecmp(s, "model printing time", 19)) {
        const char *eq = strchr(s, '=');
        if (eq && !m->have_time && parse_est_duration(eq + 1, &m->time_s) == 0) m->have_time = 1;
        return;
    }
    if (!strncasecmp(s, "filament_used(m):", 17)) {
        if (!m->have_mm) { m->filament_mm = atof(s + 17) * 1000.0; m->have_mm = 1; }
        return;
    }
    if (!strncasecmp(s, "filament_weight(g):", 19)) {
        if (!m->have_g) { m->filament_g = atof(s + 19); m->have_g = 1; }
        return;
    }
    if (strcasestr(s, "total filament used [g]") || strcasestr(s, "filament used [g]")) {
        const char *eq = strchr(s, '='); if (eq && !m->have_g) { m->filament_g = atof(eq + 1); m->have_g = 1; }
        return;
    }
    if (strcasestr(s, "filament used [mm]")) {
        const char *eq = strchr(s, '='); if (eq && !m->have_mm) { m->filament_mm = atof(eq + 1); m->have_mm = 1; }
        return;
    }
    if (strcasestr(s, "thumbnail") && strcasestr(s, "begin")) m->have_thumb = 1;
}

static void scan_meta_buf(char *b, file_meta *m, int skip_partial) {
    char *p = b;
    if (skip_partial) { char *n = strchr(p, '\n'); if (n) p = n + 1; }
    while (p && *p) {
        char *nl = strchr(p, '\n'); if (nl) *nl = 0;
        if (p[0] == ';') scan_meta_line(p, m);
        if (nl) *nl = '\n';
        p = nl ? nl + 1 : NULL;
    }
}

static void file_meta_from(const char *path, file_meta *m) {
    memset(m, 0, sizeof *m);
    int fd = open(path, O_RDONLY); if (fd < 0) return;
    struct stat st; if (fstat(fd, &st) || st.st_size <= 0) { close(fd); return; }
    const size_t HEAD = 262144, TAIL = 32768;
    size_t n1 = (size_t)st.st_size < HEAD ? (size_t)st.st_size : HEAD;
    char *b = malloc(n1 + 1);
    if (b) {
        ssize_t r = read(fd, b, n1); if (r < 0) r = 0; b[r] = 0;
        scan_meta_buf(b, m, 0); free(b);
    }
    if ((size_t)st.st_size > HEAD + TAIL) {
        if (lseek(fd, st.st_size - (off_t)TAIL, SEEK_SET) >= 0) {
            b = malloc(TAIL + 1);
            if (b) {
                ssize_t r = read(fd, b, TAIL); if (r < 0) r = 0; b[r] = 0;
                scan_meta_buf(b, m, 1); free(b);
            }
        }
    }
    close(fd);
}

static int b64val(unsigned char c) {
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}
static int b64dec(const char *in, size_t inlen, unsigned char *out, size_t on, size_t *wn) {
    size_t w = 0; unsigned acc = 0; int n = 0;
    for (size_t i = 0; i < inlen; i++) {
        unsigned char c = (unsigned char)in[i];
        if (c == '=' || isspace(c) || c == ';') continue;
        int v = b64val(c); if (v < 0) continue;
        acc = (acc << 6) | (unsigned)v; if (++n < 4) continue;
        if (w + 3 > on) return -1;
        out[w++] = (unsigned char)((acc >> 16) & 0xff);
        out[w++] = (unsigned char)((acc >> 8) & 0xff);
        out[w++] = (unsigned char)(acc & 0xff);
        acc = 0; n = 0;
    }
    if (n == 2) { if (w + 1 > on) return -1; out[w++] = (unsigned char)((acc >> 4) & 0xff); }
    else if (n == 3) {
        if (w + 2 > on) return -1;
        acc <<= 6;
        out[w++] = (unsigned char)((acc >> 16) & 0xff);
        out[w++] = (unsigned char)((acc >> 8) & 0xff);
    }
    *wn = w; return 0;
}

static int extract_thumb(const char *path, unsigned char **out, size_t *on, char *mime, size_t mn) {
    int fd = open(path, O_RDONLY); if (fd < 0) return -1;
    struct stat st; if (fstat(fd, &st) || st.st_size <= 0) { close(fd); return -1; }
    size_t cap = (size_t)st.st_size > 524288 ? 524288 : (size_t)st.st_size;
    char *b = malloc(cap + 1); if (!b) { close(fd); return -1; }
    ssize_t r = read(fd, b, cap); close(fd); if (r < 0) { free(b); return -1; }
    b[r] = 0;
    int best_area = -1, best_kind = 0;
    char *best_s = NULL, *best_e = NULL;
    char *p = b;
    while (p && *p) {
        char *nl = strchr(p, '\n');
        size_t llen = nl ? (size_t)(nl - p) : strlen(p);
        char save = p[llen]; p[llen] = 0;
        int is_begin = strcasestr(p, "thumbnail") && strcasestr(p, "begin");
        int kind = 0, w = 0, h = 0;
        if (is_begin) {
            kind = (strcasestr(p, "JPG") || strcasestr(p, "JPEG")) ? 2 : (strcasestr(p, "QOI") ? 0 : 1);
            const char *x = strcasestr(p, "begin"); if (x) x += 5;
            while (x && *x && !isdigit((unsigned char)*x)) x++;
            if (x) { w = atoi(x); while (*x && *x != 'x' && *x != 'X') x++; if (*x) { x++; h = atoi(x); } }
        }
        p[llen] = save;
        if (!is_begin || !kind) { p = nl ? nl + 1 : NULL; continue; }
        char *start = nl ? nl + 1 : NULL, *endline = NULL, *e = start;
        while (e && *e) {
            char *n2 = strchr(e, '\n');
            size_t el = n2 ? (size_t)(n2 - e) : strlen(e);
            char s2 = e[el]; e[el] = 0;
            int is_end = strcasestr(e, "thumbnail") && strcasestr(e, "end");
            e[el] = s2;
            if (is_end) { endline = e; break; }
            e = n2 ? n2 + 1 : NULL;
        }
        if (start && endline) {
            int area = w * h;
            if (area >= best_area) { best_area = area; best_kind = kind; best_s = start; best_e = endline; }
            p = strchr(endline, '\n'); p = p ? p + 1 : NULL;
        } else p = nl ? nl + 1 : NULL;
    }
    if (!best_s || !best_e) { free(b); return -1; }
    size_t rawn = (size_t)(best_e - best_s);
    char *raw = malloc(rawn + 1); if (!raw) { free(b); return -1; }
    size_t k = 0;
    for (const char *s = best_s; s < best_e; s++) {
        unsigned char ch = (unsigned char)*s;
        if (ch == ';' || isspace(ch)) continue;
        raw[k++] = *s;
    }
    raw[k] = 0;
    unsigned char *img = malloc(k + 4); size_t wn = 0;
    if (!img || b64dec(raw, k, img, k + 4, &wn) || wn == 0) { free(raw); free(img); free(b); return -1; }
    free(raw); free(b);
    snprintf(mime, mn, "%s", best_kind == 2 ? "image/jpeg" : "image/png");
    *out = img; *on = wn; return 0;
}

static void resolve_www(const char *argv0) {
    if (g_www && g_www[0]) return;
    const char *e = getenv("IVIB_WWW");
    if (e && *e) { g_www = e; return; }
    char dir[512]; snprintf(dir, sizeof dir, "%s", argv0 && argv0[0] ? argv0 : ".");
    char *sl = strrchr(dir, '/'); if (sl) *sl = 0; else snprintf(dir, sizeof dir, ".");
    snprintf(g_wwwbuf, sizeof g_wwwbuf, "%s/www", dir);
    char idx[576]; snprintf(idx, sizeof idx, "%s/index.html", g_wwwbuf);
    if (!access(idx, R_OK)) { g_www = g_wwwbuf; return; }
    if (!access("/userapp/ivibridge/www/index.html", R_OK)) g_www = "/userapp/ivibridge/www";
}

static int path_under_www(const char *rel, char *out, size_t on) {
    if (!g_www || !g_www[0] || !rel) return -1;
    if (rel[0] == '/') rel++;
    if (!rel[0] || !strcmp(rel, "index.html")) rel = "index.html";
    if (strchr(rel, '/') || strstr(rel, "..")) return -1;
    snprintf(out, on, "%s/%s", g_www, rel);
    return 0;
}

static void serve_www(struct cli *c, const char *rel) {
    char path[600];
    if (path_under_www(rel, path, sizeof path)) { jerr(c, 404, "no status page (www/index.html not found)"); return; }
    int fd = open(path, O_RDONLY); struct stat st;
    if (fd < 0 || fstat(fd, &st) || !S_ISREG(st.st_mode)) {
        if (fd >= 0) close(fd);
        jerr(c, 404, "no status page (www/index.html not found)"); return;
    }
    if (st.st_size > 2 * 1024 * 1024) { close(fd); jerr(c, 413, "file too large"); return; }
    size_t n = (size_t)st.st_size; char *b = malloc(n ? n : 1);
    if (!b) { close(fd); jerr(c, 500, "out of memory"); return; }
    size_t off = 0;
    while (off < n) { ssize_t r = read(fd, b + off, n - off); if (r <= 0) break; off += (size_t)r; }
    close(fd);
    const char *ct = "application/octet-stream";
    size_t pl = strlen(path);
    if (pl >= 5 && !strcasecmp(path + pl - 5, ".html")) ct = "text/html; charset=utf-8";
    else if (pl >= 4 && !strcasecmp(path + pl - 4, ".htm")) ct = "text/html; charset=utf-8";
    else if (pl >= 3 && !strcasecmp(path + pl - 3, ".js")) ct = "text/javascript";
    else if (pl >= 4 && !strcasecmp(path + pl - 4, ".css")) ct = "text/css";
    else if (pl >= 4 && !strcasecmp(path + pl - 4, ".png")) ct = "image/png";
    else if (pl >= 4 && !strcasecmp(path + pl - 4, ".jpg")) ct = "image/jpeg";
    else if (pl >= 5 && !strcasecmp(path + pl - 5, ".jpeg")) ct = "image/jpeg";
    reply(c, 200, ct, b, off); free(b);
}

static int delete_job(const char *name, char *err, size_t en) {
    char path[1024];
    if (find_job_file(name, path, sizeof path)) { snprintf(err, en, "no such file"); return 404; }
    if (job_active() && !strcmp(path, J.path)) { snprintf(err, en, "that file is printing"); return 409; }
    if (unlink(path)) { snprintf(err, en, "could not delete"); return 500; }
    queue_del(name);
    return 0;
}

static int print_named(const char *name, char *err, size_t en) {
    char path[1024];
    if (find_job_file(name, path, sizeof path)) { snprintf(err, en, "no such file"); return 404; }
    return job_start(path, name, err, en);
}

static void api_thumb(struct cli *c, const char *name) {
    char safe[256], path[1024];
    if (safe_name(name, safe, sizeof safe) < 0) { jerr(c, 400, "bad file name"); return; }
    if (find_job_file(safe, path, sizeof path)) { jerr(c, 404, "no such file"); return; }
    unsigned char *img = NULL; size_t n = 0; char mime[32];
    if (extract_thumb(path, &img, &n, mime, sizeof mime)) { jerr(c, 404, "no thumbnail"); return; }
    reply(c, 200, mime, (char *)img, n); free(img);
}

static void api_files_dir(struct sb *s, const char *dir, int *first, char seen[][256], int *nseen, int maxseen) {
    DIR *d = opendir(dir); if (!d) return;
    struct dirent *e;
    while ((e = readdir(d))) {
        size_t l = strlen(e->d_name);
        if (e->d_name[0] == '.' || l < 7 || strcasecmp(e->d_name + l - 6, ".gcode")) continue;
        int dup = 0; for (int i = 0; i < *nseen; i++) if (!strcmp(seen[i], e->d_name)) { dup = 1; break; }
        if (dup) continue;
        char p[1024]; snprintf(p, sizeof p, "%s/%s", dir, e->d_name); struct stat st; if (stat(p, &st)) continue;
        sb_add(s, "%s{\"name\":", *first ? "" : ","); sb_str(s, e->d_name);
        sb_add(s, ",\"origin\":\"local\",\"type\":\"machinecode\",\"size\":%lld,\"date\":%lld,\"mtime\":%lld",
            (long long)st.st_size, (long long)st.st_mtime, (long long)st.st_mtime);
        file_meta meta; file_meta_from(p, &meta);
        if (meta.have_time) sb_add(s, ",\"time_s\":%ld", meta.time_s); else sb_add(s, ",\"time_s\":null");
        if (meta.have_mm) sb_add(s, ",\"filament_mm\":%.2f", meta.filament_mm); else sb_add(s, ",\"filament_mm\":null");
        if (meta.have_g) sb_add(s, ",\"filament_g\":%.2f", meta.filament_g); else sb_add(s, ",\"filament_g\":null");
        sb_add(s, ",\"thumbnail\":%s}", meta.have_thumb ? "true" : "false");
        *first = 0;
        if (*nseen < maxseen) snprintf(seen[(*nseen)++], 256, "%s", e->d_name);
    }
    closedir(d);
}
static void api_files(struct cli *c) {
    struct sb s = {0}; sb_add(&s, "{\"files\":[");
    int first = 1; char seen[64][256]; int nseen = 0;
    refresh_p1();
    if (g_p1_ready) api_files_dir(&s, g_jobs_persist, &first, seen, &nseen, 64);
    api_files_dir(&s, g_updir, &first, seen, &nseen, 64);
    const char *frd = updir_now();
    struct statvfs v; long long fr = statvfs(frd, &v) == 0 ? (long long)v.f_bavail * v.f_frsize : 0;
    sb_add(&s, "],\"free\":%lld", fr); sb_queue(&s); sb_add(&s, "}"); jreply(c, 200, &s);
}

/* multipart: pull the file part and the 'print' field out of the spooled body */
static void finish_upload(struct cli *c) {
    close(c->up_fd); c->up_fd = -1;
    int fd = open(c->up_tmp, O_RDONLY); struct stat st;
    if (fd < 0 || fstat(fd, &st) || st.st_size == 0) { if (fd >= 0) close(fd); unlink(c->up_tmp); jerr(c, 400, "empty upload"); return; }
    char *m = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0); close(fd);
    if (m == MAP_FAILED) { unlink(c->up_tmp); jerr(c, 500, "mmap failed"); return; }
    char bnd[200] = "--"; const char *bp = strstr(c->ctype, "boundary=");
    if (!bp) { munmap(m, st.st_size); unlink(c->up_tmp); jerr(c, 400, "not multipart"); return; }
    bp += 9; if (*bp == '"') bp++;
    size_t bl = 2; while (*bp && *bp != '"' && *bp != ';' && bl < sizeof bnd - 1) bnd[bl++] = *bp++;
    bnd[bl] = 0;
    char fname[256] = "", printv[16] = ""; const char *fdata = NULL; size_t flen = 0;
    const char *end = m + st.st_size, *p = memmem(m, st.st_size, bnd, bl);
    while (p) {
        const char *h = p + bl; if (h + 2 > end || (h[0] == '-' && h[1] == '-')) break;
        const char *he = memmem(h, end - h, "\r\n\r\n", 4); if (!he) break;
        const char *data = he + 4;
        const char *nx = memmem(data, end - data, bnd, bl); if (!nx) break;
        size_t dl = nx - data; if (dl >= 2 && data[dl-2] == '\r' && data[dl-1] == '\n') dl -= 2;
        char hdr[1024]; size_t hl = he - h < 1023 ? (size_t)(he - h) : 1023; memcpy(hdr, h, hl); hdr[hl] = 0;
        char *fn = strcasestr(hdr, "filename=\""), *nm = strcasestr(hdr, "name=\"print\"");
        if (fn) { fn += 10; char *q = strchr(fn, '"'); if (q) { *q = 0; snprintf(fname, sizeof fname, "%s", fn); } fdata = data; flen = dl; }
        else if (nm) { size_t k = dl < 15 ? dl : 15; memcpy(printv, data, k); printv[k] = 0; rstrip(printv); }
        p = nx;
    }
    char safe[256];
    if (!fdata || safe_name(fname, safe, sizeof safe) < 0) { munmap(m, st.st_size); unlink(c->up_tmp); jerr(c, 400, "no .gcode file in upload"); return; }
    off_t foff = (off_t)(fdata - m), flen_o = (off_t)flen;
    munmap(m, st.st_size);
    const char *udir = updir_now();
    char dst[1024], tmp2[1100]; snprintf(dst, sizeof dst, "%s/%s", udir, safe); snprintf(tmp2, sizeof tmp2, "%s/.%s.part", udir, safe);
    if (job_active() && !strcmp(dst, J.path)) { unlink(c->up_tmp); jerr(c, 409, "that file is printing"); return; }
    int in = open(c->up_tmp, O_RDONLY);
    int added = (in >= 0) ? ivi_prepare_gcode(in, foff, flen_o, tmp2, IVI_NOZZLE_DEF, NULL) : -1;
    if (added < 0) {
        logf_("G-code preparation skipped for %s", safe);
        int out = open(tmp2, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        int ok = in >= 0 && out >= 0 && ivi_copy_range(in, foff, flen_o, out) == 0;
        if (out >= 0) { fsync(out); close(out); }
        added = 0;
        if (!ok) { if (in >= 0) close(in); unlink(c->up_tmp); unlink(tmp2); jerr(c, 500, "could not store file"); return; }
    }
    if (in >= 0) close(in);
    unlink(c->up_tmp);
    if (rename(tmp2, dst)) { unlink(tmp2); jerr(c, 500, "could not store file"); return; }
    struct stat st2; size_t outlen = (size_t)flen_o;
    if (stat(dst, &st2) == 0) outlen = (size_t)st2.st_size;
    if (added) logi_("added IVI header to %s", safe);
    logi_("upload stored %s (%zu bytes)", dst, outlen);
    int start = !strcasecmp(printv, "true");
    if (start) {
        char err[256]; int rc = job_start(dst, safe, err, sizeof err);
        if (rc) { jerr(c, rc, err); return; }
    } else snprintf(J.last_name, sizeof J.last_name, "%s", safe);
    struct sb s = {0}; sb_add(&s, "{\"done\":true,\"files\":{\"local\":{\"name\":"); sb_str(&s, safe);
    sb_add(&s, ",\"origin\":\"local\"}},\"effectivePrint\":%s,\"effectiveSelect\":true}", start ? "true" : "false");
    jreply(c, 201, &s);
}

static void api_console(struct cli *c) {
    long since = 0; const char *q = strstr(c->query, "since="); if (q) since = atol(q + 6);
    struct sb s = {0}; sb_add(&s, "{\"lines\":["); int first = 1;
    long lo = g_conseq - CONSOLE_N + 1; if (lo < 1) lo = 1;
    for (long i = (since + 1 > lo ? since + 1 : lo); i <= g_conseq; i++) {
        struct cline *e = &g_con[i % CONSOLE_N]; if (e->seq != i) continue;
        sb_add(&s, "%s{\"seq\":%ld,\"dir\":\"%c\",\"text\":", first ? "" : ",", e->seq, e->dir); sb_str(&s, e->text); sb_add(&s, "}"); first = 0;
    }
    sb_add(&s, "],\"seq\":%ld}", g_conseq); jreply(c, 200, &s);
}

static void api_link(struct cli *c) {
    struct sb s = {0};
    sb_add(&s, "{\"version\":\"%s\",\"serial\":", VERSION); sb_str(&s, g_serial);
    sb_add(&s, ",\"serial_open\":%s,\"pty\":", g_ser >= 0 ? "true" : "false"); sb_str(&s, g_ptsname);
    sb_add(&s, ",\"link\":"); sb_str(&s, g_link);
    sb_add(&s, ",\"owner\":\"%s\",\"app_pending\":%d,\"app_queue\":%d,\"app_lines\":%ld,\"net_lines\":%ld,\"app_held_total\":%ld,"
        "\"stray_ok_dropped\":%ld,\"line_numbers\":%s,\"firmware\":", own_name[g_owner], g_app_pending, g_appq_n, g_app_lines, g_net_lines,
        g_app_dropped_total, g_stray_ok_dropped, g_linenums ? "true" : "false");
    sb_str(&s, S.fw); sb_add(&s, "}");
    jreply(c, 200, &s);
}

static void handle(struct cli *c) {
    const char *p = c->path; int get = !strcmp(c->method, "GET"), post = !strcmp(c->method, "POST");
    if (!strcmp(c->method, "OPTIONS")) { reply(c, 204, "text/plain", "", 0); return; }
    if (get && (!strcmp(p, "/") || !strcmp(p, "/index.html"))) { serve_www(c, "index.html"); return; }
    if (g_apikey[0] && !authed(c)) { jerr(c, 403, "Invalid API key"); return; }
    if (get) {
        if (!strcmp(p, "/api/version")) { struct sb s = {0}; sb_add(&s, "{\"api\":\"0.1\",\"server\":\"1.9.0\",\"text\":\"OctoPrint (ivi-bridge %s)\"}", VERSION); jreply(c, 200, &s); return; }
        if (!strcmp(p, "/api/server")) { struct sb s = {0}; sb_add(&s, "{\"version\":\"1.9.0\",\"safemode\":null}"); jreply(c, 200, &s); return; }
        if (!strcmp(p, "/api/printer")) { api_printer(c); return; }
        if (!strcmp(p, "/api/job")) { api_job(c); return; }
        if (!strcmp(p, "/api/ivi/files/thumb")) {
            char name[256]; if (!qget(c->query, "name", name, sizeof name)) { jerr(c, 400, "name required"); return; }
            api_thumb(c, name); return;
        }
        if (!strcmp(p, "/api/ivi/files") || !strcmp(p, "/api/ivi/queue")) { api_files(c); return; }
        if (starts(p, "/api/files/local/") && strlen(p) > 17) {
            const char *rest = p + 17; const char *slash = strrchr(rest, '/');
            if (slash && !strcmp(slash, "/thumbnail")) {
                char tmp[256]; size_t n = (size_t)(slash - rest); if (n >= sizeof tmp) n = sizeof tmp - 1;
                memcpy(tmp, rest, n); tmp[n] = 0; api_thumb(c, tmp); return;
            }
        }
        if (starts(p, "/api/files")) { api_files(c); return; }
        if (!strcmp(p, "/api/ivi/console")) { api_console(c); return; }
        if (!strcmp(p, "/api/ivi/link")) { api_link(c); return; }
        jerr(c, 404, "not found"); return;
    }
    if (!strcmp(c->method, "DELETE") && starts(p, "/api/files/local/")) {
        char safe[256], err[256];
        if (safe_name(p + 17, safe, sizeof safe) < 0) { jerr(c, 400, "bad file name"); return; }
        int rc = delete_job(safe, err, sizeof err); if (rc) { jerr(c, rc, err); return; }
        struct sb s = {0}; sb_add(&s, "{\"message\":\"deleted\"}"); jreply(c, 200, &s); return;
    }
    if (!post) { jerr(c, 404, "not found"); return; }
    if (!g_apikey[0]) { jerr(c, 403, "no API key configured: controls are disabled"); return; }
    if (!strcmp(p, "/api/files/local") || !strcmp(p, "/api/files/sdcard")) { finish_upload(c); return; }
    const char *body = c->body ? c->body : "{}";
    if (starts(p, "/api/files/local/")) {           /* OctoPrint select (+print) of a stored file */
        char cmd[32] = "", safe[256], err[256];
        jget_str(body, "command", cmd, sizeof cmd);
        if (strcmp(cmd, "select") || safe_name(p + 17, safe, sizeof safe) < 0) { jerr(c, 400, "unsupported"); return; }
        char path[1024]; if (find_job_file(safe, path, sizeof path)) { jerr(c, 404, "no such file"); return; }
        if (jget_bool(body, "print")) { int rc = job_start(path, safe, err, sizeof err); if (rc) { jerr(c, rc, err); return; } }
        else snprintf(J.last_name, sizeof J.last_name, "%s", safe);
        reply(c, 204, "text/plain", "", 0); return;
    }
    if (!strcmp(p, "/api/ivi/files") || !strcmp(p, "/api/ivi/queue")) {
        char act[32] = "", name[256] = "", safe[256], err[256];
        jget_str(body, "action", act, sizeof act); jget_str(body, "name", name, sizeof name);
        if (!act[0]) { jerr(c, 400, "action required"); return; }
        if (!strcmp(act, "clear")) { g_qn = 0; struct sb s = {0}; sb_add(&s, "{\"message\":\"queue cleared\"}"); jreply(c, 200, &s); return; }
        if (!strcmp(act, "start_next")) {
            if (!g_qn) { jerr(c, 409, "queue is empty"); return; }
            snprintf(safe, sizeof safe, "%s", g_queue[0]);
            memmove(g_queue[0], g_queue[1], (size_t)(g_qn - 1) * sizeof g_queue[0]); g_qn--;
            int rc = print_named(safe, err, sizeof err);
            if (rc) {
                if (g_qn < QMAX) {
                    memmove(g_queue[1], g_queue[0], (size_t)g_qn * sizeof g_queue[0]);
                    snprintf(g_queue[0], sizeof g_queue[0], "%s", safe); g_qn++;
                }
                jerr(c, rc, err); return;
            }
            struct sb s = {0}; sb_add(&s, "{\"message\":\"started %s\"}", safe);
            jreply(c, 200, &s); return;
        }
        if (safe_name(name, safe, sizeof safe) < 0) { jerr(c, 400, "bad file name"); return; }
        if (!strcmp(act, "print") || !strcmp(act, "select")) {
            int rc = print_named(safe, err, sizeof err); if (rc) { jerr(c, rc, err); return; }
            struct sb s = {0}; sb_add(&s, "{\"message\":\"printing\"}"); jreply(c, 200, &s); return;
        }
        if (!strcmp(act, "delete")) {
            int rc = delete_job(safe, err, sizeof err); if (rc) { jerr(c, rc, err); return; }
            struct sb s = {0}; sb_add(&s, "{\"message\":\"deleted\"}"); jreply(c, 200, &s); return;
        }
        if (!strcmp(act, "queue") || !strcmp(act, "add")) {
            char path[1024]; if (find_job_file(safe, path, sizeof path)) { jerr(c, 404, "no such file"); return; }
            if (queue_add(safe, err, sizeof err)) { jerr(c, 409, err); return; }
            struct sb s = {0}; sb_add(&s, "{\"message\":\"queued\"}"); jreply(c, 200, &s); return;
        }
        if (!strcmp(act, "unqueue") || !strcmp(act, "remove")) {
            if (!queue_del(safe)) { jerr(c, 404, "not in queue"); return; }
            struct sb s = {0}; sb_add(&s, "{\"message\":\"removed\"}"); jreply(c, 200, &s); return;
        }
        jerr(c, 400, "unsupported action"); return;
    }
    if (!strcmp(p, "/api/ivi/clear")) {   /* Orca plugin "clear": drop a stale PC job state (M2411 S3), as ivi_bridge.py */
        if (job_active()) { jerr(c, 409, "a job is running; use Cancel"); return; }
        if (AJ.active || (S.working[0] && starts(S.working, "WORKING_SCREEN"))) { jerr(c, 409, "the touchscreen is printing; stop it on the printer"); return; }
        if (g_netq_n + 2 > 16) { jerr(c, 409, "command queue full"); return; }
        snprintf(g_netq[(g_netq_h + g_netq_n) % 16], 96, "M2411 S3"); g_netq_n++;
        snprintf(g_netq[(g_netq_h + g_netq_n) % 16], 96, "M2007"); g_netq_n++;
        struct sb s = {0}; sb_add(&s, "{\"message\":\"sent M2411 S3; printer reported %s before the clear\"}", S.working[0] ? S.working : "unknown");
        jreply(c, 200, &s); return;
    }
    if (!strcmp(p, "/api/job")) {
        char cmd[32] = "", act[32] = "toggle"; jget_str(body, "command", cmd, sizeof cmd); jget_str(body, "action", act, sizeof act);
        if (AJ.active && !job_active()) { jerr(c, 409, "the touchscreen owns this job; pause or stop it on the printer"); return; }
        if (!strcmp(cmd, "start")) {
            char path[1024], err[256], nm[256];
            if (!J.last_name[0]) { jerr(c, 409, "no file selected"); return; }
            snprintf(nm, sizeof nm, "%s", J.last_name); if (find_job_file(nm, path, sizeof path)) { jerr(c, 404, "no such file"); return; }
            int rc = job_start(path, nm, err, sizeof err); if (rc) { jerr(c, rc, err); return; }
            reply(c, 204, "text/plain", "", 0); return;
        }
        if (!job_active()) { jerr(c, 409, "no active job"); return; }
        if (!strcmp(cmd, "pause")) {
            int pause = !strcmp(act, "pause") || (!strcmp(act, "toggle") && J.st == J_PRINTING);
            if (pause && J.st == J_PRINTING) J.want_pause = 1;
            else if (!pause && J.st == J_PAUSED) J.want_resume = 1;
        } else if (!strcmp(cmd, "cancel")) J.want_cancel = 1;
        else { jerr(c, 400, "unsupported command"); return; }
        struct sb s = {0}; sb_add(&s, "{\"state\":\"%s\"}", jstate_name[J.st]); jreply(c, 200, &s); return;
    }
    if (starts(p, "/api/printer/")) {
        char list[8][96]; int nl = 0; char v[64], err[200];
        if (!strcmp(p, "/api/printer/command")) {
            char one[96]; if (jget_str(body, "command", one, sizeof one)) snprintf(list[nl++], 96, "%s", one);
            const char *a = strstr(body, "\"commands\"");
            if (a && (a = strchr(a, '['))) {
                a++;
                while (nl < 8) {
                    const char *q1 = strchr(a, '"'), *e = strchr(a, ']');
                    if (!q1 || (e && e < q1)) break;
                    const char *q2 = strchr(q1 + 1, '"'); if (!q2) break;
                    snprintf(list[nl++], 96, "%.*s", (int)(q2 - q1 - 1), q1 + 1); a = q2 + 1;
                }
            }
        } else if (!strcmp(p, "/api/printer/bed") && jget_str(body, "target", v, sizeof v)) snprintf(list[nl++], 96, "M140 S%d", (int)(atof(v) + 0.5));
        else if (!strcmp(p, "/api/printer/tool") && jget_str(body, "tool0", v, sizeof v)) snprintf(list[nl++], 96, "M104 S%d", (int)(atof(v) + 0.5));
        else if (!strcmp(p, "/api/printer/tool") && jget_str(body, "factor", v, sizeof v)) snprintf(list[nl++], 96, "M221 S%d", atoi(v));
        else if (!strcmp(p, "/api/printer/printhead") && jget_str(body, "factor", v, sizeof v)) snprintf(list[nl++], 96, "M220 S%d", atoi(v));
        if (!nl) { jerr(c, 400, "no command"); return; }
        if (AJ.active) { jerr(c, 409, "the touchscreen is printing; controls are read-only"); return; }
        for (int i = 0; i < nl; i++) {
            char out[96];
            if (check_command(list[i], out, sizeof out, err, sizeof err)) { jerr(c, 400, err); return; }
            if (job_active() && !(cmd_word(out, "M104") || cmd_word(out, "M140") || cmd_word(out, "M220") || cmd_word(out, "M221") ||
                                  cmd_word(out, "M106") || cmd_word(out, "M107") || cmd_word(out, "M105") || cmd_word(out, "M114"))) {
                jerr(c, 409, "only temperature/fan/speed/flow commands while a job runs"); return;
            }
            snprintf(list[i], 96, "%s", out);
        }
        if (g_netq_n + nl > 16) { jerr(c, 409, "command queue full"); return; }
        /* "quiet":true marks automatic position polls (M114 only) so they stay out of the console view */
        int quiet = jget_bool(body, "quiet");
        for (int i = 0; i < nl; i++) {
            int slot = (g_netq_h + g_netq_n) % 16;
            snprintf(g_netq[slot], 96, "%s", list[i]); g_netq_quiet[slot] = quiet && cmd_is(list[i], "M114"); g_netq_n++;
        }
        reply(c, 204, "text/plain", "", 0); return;
    }
    jerr(c, 404, "not found");
}

static void parse_headers(struct cli *c) {
    char *e = strstr(c->hdr, "\r\n\r\n"); *e = 0;
    char *line = c->hdr, *nl = strstr(line, "\r\n"); if (nl) *nl = 0;
    char url[1024] = ""; sscanf(line, "%7s %1023s", c->method, url);
    char *q = strchr(url, '?'); if (q) { *q = 0; snprintf(c->query, sizeof c->query, "%s", q + 1); }
    snprintf(c->path, sizeof c->path, "%s", url);
    for (char *h = nl ? nl + 2 : NULL; h && *h; ) {
        char *n2 = strstr(h, "\r\n"); if (n2) *n2 = 0;
        if (istarts(h, "Content-Length:")) c->clen = atol(h + 15);
        else if (istarts(h, "Content-Type:")) { char *v = h + 13; while (*v == ' ') v++; snprintf(c->ctype, sizeof c->ctype, "%s", v); }
        else if (istarts(h, "X-Api-Key:")) { char *v = h + 10; while (*v == ' ') v++; snprintf(c->key, sizeof c->key, "%s", v); rstrip(c->key); }
        else if (istarts(h, "Authorization: Bearer ")) { snprintf(c->key, sizeof c->key, "%s", h + 22); rstrip(c->key); }
        h = n2 ? n2 + 2 : NULL;
    }
}

static int is_upload(struct cli *c) { return !strcmp(c->method, "POST") && (!strcmp(c->path, "/api/files/local") || !strcmp(c->path, "/api/files/sdcard")); }

static void cli_read(struct cli *c) {
    char buf[16384];
    ssize_t r = read(c->fd, buf, sizeof buf);
    if (r <= 0) { if (r < 0 && (errno == EAGAIN || errno == EINTR)) return; cli_close(c); return; }
    char *data = buf; size_t n = (size_t)r;
    if (!c->hdone) {
        size_t prev = c->hn;
        size_t k = n; if (c->hn + k > sizeof c->hdr - 1) k = sizeof c->hdr - 1 - c->hn;
        memcpy(c->hdr + c->hn, buf, k); c->hn += k; c->hdr[c->hn] = 0;
        char *e = strstr(c->hdr, "\r\n\r\n");
        if (!e) { if (c->hn >= (int)sizeof c->hdr - 1) { jerr(c, 413, "headers too large"); cli_close(c); } return; }
        size_t hl = e + 4 - c->hdr;              /* body starts at buf[hl - prev]; take it from buf, not the */
        size_t off = hl - prev, extra = n - off;  /* (possibly truncated) header copy */
        parse_headers(c); c->hdone = 1;
        if (is_upload(c)) {
            if (!g_apikey[0]) { jerr(c, 403, "no API key configured: controls are disabled"); cli_close(c); return; }
            if (!authed(c)) { jerr(c, 403, "Invalid API key"); cli_close(c); return; }
            if (c->clen <= 0 || c->clen > 512L * 1024 * 1024) { jerr(c, 413, "bad size"); cli_close(c); return; }
            snprintf(c->up_tmp, sizeof c->up_tmp, "%s/.ivibridge_upload_%d.tmp", updir_now(), c->fd);
            c->up_fd = open(c->up_tmp, O_WRONLY | O_CREAT | O_TRUNC, 0600);
            if (c->up_fd < 0) { jerr(c, 500, "cannot spool upload"); cli_close(c); return; }
        } else if (c->clen > 65536) { jerr(c, 413, "body too large"); cli_close(c); return; }
        else if (c->clen > 0) c->body = calloc(1, c->clen + 1);
        data = buf + off; n = extra;
    }
    if ((long)n > c->clen - c->got) n = c->clen - c->got;
    if (n) {
        if (c->up_fd >= 0) { if (write_all(c->up_fd, data, n, 10000) < 0) { jerr(c, 500, "write failed"); cli_close(c); return; } }
        else if (c->body) memcpy(c->body + c->got, data, n);
        c->got += n;
    }
    if (c->got >= c->clen) { handle(c); cli_close(c); }
}

/* ------------------------------------------------------------------ main */
static void on_sig(int s) { (void)s; g_quit = 1; }

static void usage(void) {
    fprintf(stderr, "ivibridge %s\n  -s real_serial (%s)  -L app_link (%s)  -p port (%d)  -b bind (%s)\n"
        "  -k apikey | -K keyfile   -u upload_dir (%s)  -l logfile  -c (no line numbers)\n"
        "  -n (do not recreate the original device node on exit)  -P idle_poll_s (%d)\n"
        "  -w www_dir             status page directory (or IVIB_WWW / <bindir>/www)\n"
        "  -W line_stall_ms (%d, 0 = no stall probe)  -R resume_complete_wait_ms (%d)\n"
        "  --add-header IN OUT [--nozzle 0.3] [--date YYYY-MM-DD HH:MM:SS]\n", VERSION, g_serial, g_link, g_port, g_bind, g_updir, g_poll_s,
        g_stall_ms, g_resume_ms);
}

int main(int argc, char **argv) {
    int o; g_log = stderr;
    if (argc >= 2 && !strcmp(argv[1], "--add-header")) return ivi_add_header_main(argc, argv);
    { const char *lm = getenv("IVIB_LOG_MAX"); if (lm && *lm) { long long v = atoll(lm); if (v >= 256) g_log_max = v; } }
    while ((o = getopt(argc, argv, "s:L:p:b:k:K:u:l:cnP:W:R:w:hV")) != -1) switch (o) {
        case 's': g_serial = optarg; break;
        case 'L': g_link = optarg; break;
        case 'p': g_port = atoi(optarg); break;
        case 'b': g_bind = optarg; break;
        case 'k': snprintf(g_apikey, sizeof g_apikey, "%s", optarg); break;
        case 'K': { FILE *f = fopen(optarg, "r"); if (f) { if (fgets(g_apikey, sizeof g_apikey, f)) rstrip(g_apikey); fclose(f); } break; }
        case 'u': g_updir = optarg; break;
        case 'l': g_logpath = optarg; break;
        case 'c': g_linenums = 0; break;
        case 'n': g_restore = 0; break;
        case 'P': g_poll_s = atoi(optarg); break;
        case 'w': g_www = optarg; break;
        case 'W': g_stall_ms = atoi(optarg); break;
        case 'R': g_resume_ms = atoi(optarg); if (g_resume_ms < 1000) g_resume_ms = 1000; break;
        case 'V': printf("ivibridge %s\n", VERSION); return 0;
        default: usage(); return 2;
    }
    if (g_logpath) { FILE *f = fopen(g_logpath, "a"); if (f) g_log = f; }
    resolve_www(argv[0]);
    for (int i = 0; i < MAXCLI; i++) { C[i].fd = -1; C[i].up_fd = -1; }
    signal(SIGPIPE, SIG_IGN); signal(SIGTERM, on_sig); signal(SIGINT, on_sig); if (signal(SIGHUP, SIG_IGN) != SIG_IGN) signal(SIGHUP, on_sig);   /* keep nohup's ignore */
    logi_("ivibridge %s starting: serial %s, app link %s, http %s:%d, api key %s", VERSION, g_serial, g_link, g_bind, g_port,
          g_apikey[0] ? "set" : "NOT set (read-only)");

    g_ser = open_real_serial();
    if (g_ser < 0) { logi_("cannot open %s: %s", g_serial, strerror(errno)); return 1; }
    g_ptm = make_pty(); if (g_ptm < 0) return 1;
    if (point_link() < 0) { restore_link(); return 1; }

    g_lfd = socket(AF_INET, SOCK_STREAM, 0); int one = 1; setsockopt(g_lfd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    struct sockaddr_in a = { .sin_family = AF_INET, .sin_port = htons(g_port) }; inet_pton(AF_INET, g_bind, &a.sin_addr);
    if (bind(g_lfd, (void *)&a, sizeof a) || listen(g_lfd, 8)) { logi_("http bind %s:%d: %s (continuing without HTTP)", g_bind, g_port, strerror(errno)); close(g_lfd); g_lfd = -1; }
    else set_nonblock(g_lfd);
    g_last_ser_rx = g_last_app_tx = now_ms() - 10000;
    long long last_link_check = now_ms();

    while (!g_quit) {
        struct pollfd pf[3 + MAXCLI]; int np = 0, iser = -1, iptm, ilfd = -1, ic[MAXCLI];
        if (g_ser >= 0) { iser = np; pf[np++] = (struct pollfd){ g_ser, POLLIN, 0 }; }
        iptm = np; pf[np++] = (struct pollfd){ g_ptm, POLLIN, 0 };
        if (g_lfd >= 0) { ilfd = np; pf[np++] = (struct pollfd){ g_lfd, POLLIN, 0 }; }
        for (int i = 0; i < MAXCLI; i++) { ic[i] = -1; if (C[i].fd >= 0) { ic[i] = np; pf[np++] = (struct pollfd){ C[i].fd, POLLIN, 0 }; } }
        int r = poll(pf, np, 20);
        if (r < 0 && errno != EINTR) break;
        if (iser >= 0 && (pf[iser].revents & (POLLIN | POLLERR | POLLHUP))) {
            char b[4096]; ssize_t k = read(g_ser, b, sizeof b);
            if (k > 0) {
                for (ssize_t i = 0; i < k; i++) {
                    struct lbuf *L = &g_serbuf; L->b[L->n++] = b[i];
                    if (b[i] == '\n' || L->n >= LINEMAX) { ser_line(L->b, L->n); L->n = 0; }
                }
            } else if (k == 0 || (errno != EAGAIN && errno != EINTR)) {
                logi_("serial link lost (%s); retrying", k == 0 ? "EOF" : strerror(errno));
                close(g_ser); g_ser = -1; g_ser_retry_ms = now_ms() + 1000;
                if (job_active()) job_end(J_ERROR, "printer link lost");
                W.kind = NW_NONE; g_owner = OWN_NONE; g_app_pending = 0;
            }
        }
        if (pf[iptm].revents & POLLIN) {
            char b[4096]; ssize_t k = read(g_ptm, b, sizeof b);
            for (ssize_t i = 0; i < k; i++) {
                struct lbuf *L = &g_appbuf; L->b[L->n++] = b[i];
                if (b[i] == '\n' || L->n >= LINEMAX) { L->b[L->n] = 0; if (g_ser >= 0) app_line(L->b); else g_app_dropped++; L->n = 0; }
            }
        }
        if (ilfd >= 0 && (pf[ilfd].revents & POLLIN)) {
            struct sockaddr_in pa; socklen_t pl = sizeof pa; memset(&pa, 0, sizeof pa);
            int fd = accept(g_lfd, (struct sockaddr *)&pa, &pl);
            if (fd >= 0) {
                int slot = -1; for (int i = 0; i < MAXCLI; i++) if (C[i].fd < 0) { slot = i; break; }
                if (slot < 0) close(fd);
                else { memset(&C[slot], 0, sizeof C[slot]); C[slot].fd = fd; C[slot].up_fd = -1; C[slot].t0 = now_ms(); C[slot].lan = is_lan(&pa); set_nonblock(fd); }
            }
        }
        for (int i = 0; i < MAXCLI; i++) if (ic[i] >= 0 && C[i].fd >= 0 && (pf[ic[i]].revents & (POLLIN | POLLHUP | POLLERR))) cli_read(&C[i]);
        for (int i = 0; i < MAXCLI; i++) if (C[i].fd >= 0 && !C[i].hdone && now_ms() - C[i].t0 > 15000) cli_close(&C[i]);
        if (g_ser < 0 && now_ms() >= g_ser_retry_ms) {
            g_ser = open_real_serial(); g_ser_retry_ms = now_ms() + 1000;
            if (g_ser >= 0) { logi_("serial link back"); g_last_ser_rx = now_ms(); }
        }
        if (now_ms() - last_link_check > 2000) { last_link_check = now_ms(); point_link(); refresh_p1();
            if (g_pts_keep >= 0) ioctl(g_pts_keep, TIOCNXCL); }   /* the app's TIOCEXCL must not outlive it (we hold the slave open) */   /* mdev may recreate the node */
        if (g_ser >= 0) tick();
    }
    logi_("shutting down");
    if (g_ser >= 0) ioctl(g_ser, TIOCNXCL);   /* hand the port back without our exclusive flag */
    if (job_active()) {
        /* fail safe: never leave the printer mid-job with nobody feeding it */
        logi_("exiting with a network job active (%s): stopping it", jstate_name[J.st]);
        static const char *stop[] = { "M2411 S3\n", "M5\n", "M104 S0\n", "M140 S0\n", "M107\n" };
        int laser = head_is_laser();
        if (g_ser >= 0) for (int i = 0; i < 5; i++) {
            if (i == 1 && !laser) continue;                      /* M5 only for a laser head */
            write_all(g_ser, stop[i], strlen(stop[i]), 500); fan_track(stop[i]); usleep(150000);
        }
        to_app_line("Working Status: IDLE");
    }
    restore_link();
    return 0;
}
