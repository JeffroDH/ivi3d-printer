/* Native touchscreen start/control via /tmp/ivibridge/print_request (and HTTP /api/ivi/r).
   Included from ivibridge.c after job_start. QML watchers in the app patch ack over loopback.
   The app's own slots (isPause, stopPrinting, setTargetTemperature, setBedTargetTemperature,
   setWorkSpeed, setFlowrate, zfinetunePlus, zfinetuneMinus) issue M2410 / M2411 S3 / M104 /
   M140 / M220 / M221 / M290 through the Sender, the same path as the screen buttons. The
   bridge does not inject those onto the serial link during a touchscreen job; a second
   writer would desync the app's stream.
   IVIB_NET_STREAM=1 restores the old network-stream job_start path (tests / debug only). */

#define REQ_START_MS 8000
#define REQ_CTL_MS   3000

enum { R_IDLE = 0, R_PENDING, R_ACKED };
enum { AWAIT_NONE = 0, AWAIT_UPLOAD, AWAIT_NOCONTENT, AWAIT_JSON };

static int g_net_stream;
static int g_assist_open;
static long long g_assist_until;

static struct {
    int st, id, ok, autostart, nozzle, bed, speed, flow, zoff, fan;
    char cmd[16], file[512], result[80];
    long long t0, deadline;
} R;

static void req_clear_file(void) {
    char p[576]; snprintf(p, sizeof p, "%s/print_request", ivib_dir());
    unlink(p);
}

static void req_reset_fields(void) {
    R.ok = 0; R.autostart = 0; R.result[0] = 0; R.file[0] = 0; R.cmd[0] = 0;
    R.nozzle = R.bed = R.speed = R.flow = R.zoff = R.fan = INT_MIN;
}

/* Hundredths of a millimetre: +/-1, +/-2, +/-5 for 0.01 / 0.02 / 0.05 mm. */
static void zoff_fmt(int h, char *b, size_t n) {
    snprintf(b, n, "%s0.0%d", h < 0 ? "-" : "", h < 0 ? -h : h);
}
/* Return 0 and set *h on a valid M290 Z step, 1 if M290 but not an allowed Z, -1 if not M290. */
static int parse_m290(const char *n, int *h) {
    if (!cmd_word(n, "M290")) return -1;
    const char *p = n + 4;
    while (*p == ' ') p++;
    if (*p != 'Z') return 1;
    p++;
    while (*p == ' ') p++;
    int sign = 1;
    if (*p == '+') p++;
    else if (*p == '-') { sign = -1; p++; }
    int v = 0;
    if (!strcmp(p, "0.01")) v = 1;
    else if (!strcmp(p, "0.02")) v = 2;
    else if (!strcmp(p, "0.05")) v = 5;
    else return 1;
    if (h) *h = sign * v;
    return 0;
}

static int req_write_file(void) {
    char p[576], tmp[600];
    snprintf(p, sizeof p, "%s/print_request", ivib_dir());
    snprintf(tmp, sizeof tmp, "%s/.print_request.tmp", ivib_dir());
    mkdir(ivib_dir(), 0755);
    FILE *f = fopen(tmp, "w"); if (!f) return -1;
    fprintf(f, "id=%d\ncmd=%s\n", R.id, R.cmd);
    if (R.file[0]) fprintf(f, "file=%s\n", R.file);
    if (!strcmp(R.cmd, "start")) fprintf(f, "autostart=%d\n", R.autostart);
    if (R.nozzle != INT_MIN) fprintf(f, "nozzle=%d\n", R.nozzle);
    if (R.bed != INT_MIN) fprintf(f, "bed=%d\n", R.bed);
    if (!strcmp(R.cmd, "speed") || !strcmp(R.cmd, "adjust")) {
        if (R.speed != INT_MIN) fprintf(f, "speed=%d\n", R.speed);
        if (R.speed != INT_MIN && !strcmp(R.cmd, "speed")) fprintf(f, "value=%d\n", R.speed);
    }
    if (!strcmp(R.cmd, "flow") || !strcmp(R.cmd, "adjust")) {
        if (R.flow != INT_MIN) fprintf(f, "flow=%d\n", R.flow);
        if (R.flow != INT_MIN && !strcmp(R.cmd, "flow")) fprintf(f, "value=%d\n", R.flow);
    }
    if (R.fan != INT_MIN) {                 /* 0.1.19: touchscreen Fan switch (on/off, like the stock Status page) */
        fprintf(f, "fan=%d\n", R.fan ? 1 : 0);
        if (!strcmp(R.cmd, "fan")) fprintf(f, "value=%d\n", R.fan ? 1 : 0);
    }
    if (R.zoff != INT_MIN) {
        char zb[16]; zoff_fmt(R.zoff, zb, sizeof zb);
        fprintf(f, "zoffset=%s\n", zb);
        if (!strcmp(R.cmd, "zoffset")) fprintf(f, "value=%s\n", zb);
    }
    if (fclose(f) || rename(tmp, p)) { unlink(tmp); return -1; }
    return 0;
}

static int printer_busy_for_start(char *err, size_t en) {
    if (job_active()) { snprintf(err, en, "a network job is already running"); return 409; }
    if (cal_busy()) { snprintf(err, en, "calibration is running"); return 409; }
    if (AJ.active) { snprintf(err, en, "the touchscreen is printing"); return 409; }
    if (S.working[0] && starts(S.working, "WORKING")) { snprintf(err, en, "printer reports %s; finish or stop that job first", S.working); return 409; }
    if (g_assist_open && now_ms() < g_assist_until) { snprintf(err, en, "a start is already open on the touchscreen"); return 409; }
    if (R.st == R_PENDING) { snprintf(err, en, "a touchscreen request is already pending"); return 409; }
    if (g_ser < 0) { snprintf(err, en, "printer link is down"); return 409; }
    return 0;
}

static int req_begin(const char *cmd, const char *file, int timeout_ms, char *err, size_t en) {
    if (R.st == R_PENDING) { snprintf(err, en, "a touchscreen request is already pending"); return 409; }
    if (!strcmp(cmd, "start")) {
        int rc = printer_busy_for_start(err, en); if (rc) return rc;
        if (!file || !file[0]) { snprintf(err, en, "no file"); return 400; }
        struct stat st; if (stat(file, &st) || !S_ISREG(st.st_mode)) { snprintf(err, en, "no such file"); return 404; }
    }
    R.id++; if (R.id <= 0) R.id = 1;
    req_reset_fields();
    snprintf(R.cmd, sizeof R.cmd, "%s", cmd);
    if (file) snprintf(R.file, sizeof R.file, "%s", file);
    R.st = R_PENDING;
    R.t0 = now_ms(); R.deadline = R.t0 + timeout_ms;
    if (req_write_file()) { snprintf(err, en, "could not write print_request"); R.st = R_IDLE; return 500; }
    logi_("request %d %s %s", R.id, cmd, R.file[0] ? R.file : "");
    return 0;
}

/* Fill adjust fields, then call req_begin and rewrite the file so fields are included. */
static int req_begin_adjust(const char *cmd, int nozzle, int bed, int speed, int flow, int zoff, int fan, int timeout_ms, char *err, size_t en) {
    int rc = req_begin(cmd, "", timeout_ms, err, en); if (rc) return rc;
    R.nozzle = nozzle; R.bed = bed; R.speed = speed; R.flow = flow; R.zoff = zoff; R.fan = fan;
    if (req_write_file()) { snprintf(err, en, "could not write print_request"); R.st = R_IDLE; return 500; }
    return 0;
}

static void req_complete_http(int ok, const char *result); /* defined after struct cli */

static const char *req_basename(const char *p) {
    const char *s = strrchr(p, '/'); return s ? s + 1 : p;
}

static void req_finish(int ok, const char *result) {
    if (R.st != R_PENDING) return;
    R.ok = ok;
    snprintf(R.result, sizeof R.result, "%s", result ? result : "");
    R.st = R_ACKED;
    req_clear_file();
    if (!strcmp(R.cmd, "start") && ok && (!strcmp(R.result, "opened") || !strcmp(R.result, "started"))) {
        g_assist_open = 1;
        g_assist_until = now_ms() + 300000;
        if (R.file[0]) snprintf(J.last_name, sizeof J.last_name, "%s", req_basename(R.file));
    }
    logi_("request %d ack ok=%d %s", R.id, ok, R.result);
    req_complete_http(ok, R.result);
}

static void req_tick(void) {
    long long t = now_ms();
    if (g_assist_open) {
        if (AJ.active) g_assist_open = 0;
        else if (t >= g_assist_until) { logf_("assist-mode start window expired"); g_assist_open = 0; }
    }
    if (R.st == R_PENDING && t >= R.deadline) {
        logf_("request %d timed out (%s)", R.id, R.cmd);
        /* a pre-0.1.19 touchscreen hook ignores cmd=fan */
        req_finish(0, !strcmp(R.cmd, "fan") ? "timeout (touchscreen fan control needs the 0.1.19 touchscreen app)" : "timeout");
    }
}

static void req_init(void) {
    memset(&R, 0, sizeof R);
    req_reset_fields();
    req_clear_file();
    { const char *e = getenv("IVIB_NET_STREAM"); g_net_stream = e && e[0] == '1' && !e[1]; }
}

static int native_start(const char *path, const char *name, char *err, size_t en) {
    if (g_net_stream) return job_start(path, name, err, en);
    int rc = req_begin("start", path, REQ_START_MS, err, en);
    if (!rc) {
        R.autostart = g_autostart ? 1 : 0;
        if (req_write_file()) { snprintf(err, en, "could not write print_request"); R.st = R_IDLE; return 500; }
        if (name && name[0]) snprintf(J.last_name, sizeof J.last_name, "%s", name);
    }
    return rc;
}

static int is_adjust_cmd(const char *n) {
    return cmd_word(n, "M104") || cmd_word(n, "M140") || cmd_word(n, "M220") || cmd_word(n, "M221") || cmd_word(n, "M290")
        || cmd_word(n, "M106") || cmd_word(n, "M107");
}

static int parse_sval(const char *n) {
    const char *p = strchr(n, 'S'); if (!p) return 0; return atoi(p + 1);
}
