/* Calibration tab state machine (G33 / G29 / paper-test).
   Included from ivibridge.c after ivi_settings.inc.

   Save rules: M500 only after "Calibration OK" (G33) or a complete
   "Bilinear Leveling Grid:" (G29), or on the paper-test Save path
   (M665 H + M500 + M211 S1). Never on Probing Failed, No convergence,
   warning:/? lines, timeout, or cancel.

   XYZ always chains into Leveling because G33's reset_bed_level wipes
   the bilinear mesh (and a following M500 would persist the NaN grid). */

enum {
    CAL_IDLE = 0,
    CAL_NEED_TEMP,
    CAL_COOL,
    CAL_PROMPT_BED,
    CAL_MOVE_INSTALL,
    CAL_PROMPT_ATTACH,
    CAL_M119,
    CAL_ATTACH_RETRY,
    CAL_HEAT,              /* 0.1.19 heated leveling: M140 S<t>, then poll until the bed is at temperature */
    CAL_RUN,
    CAL_SAVE,
    CAL_PROBE_M503,
    CAL_MOVE_REMOVE,
    CAL_PROMPT_REMOVE,
    CAL_PAPER_PREP,
    CAL_PAPER_JOG,
    CAL_PAPER_EXEC,
    CAL_DONE,
    CAL_FAIL
};

enum { CAL_K_NONE = 0, CAL_K_XYZ, CAL_K_LEVEL, CAL_K_PAPER, CAL_K_ALL };

#define CAL_GRID 7
#define CAL_TEMP_MAX 40.0
#define CAL_BED_MIN 40
#define CAL_BED_MAX 80

static struct {
    int st, kind;
    int want_level, want_paper;
    int running_g33;
    int m119_seen, m119_ok, m119_missing;
    int have_mesh, mesh_ok[CAL_GRID][CAL_GRID];
    float mesh[CAL_GRID][CAL_GRID];
    int H, R, L, S, ang[3], rod[3], endst[3];
    int abl, fade_h;
    long last_xyz, last_level, last_paper;
    long long started_ms, phase_ms, last_poll_ms, last_m114_ms;
    int progress, soft_off, confirmed;
    int paper_new_h;
    int bed_c;             /* heated leveling target °C (0 = the cold flow) */
    int bed_on;            /* this run turned the bed heater on (cancel / failure turns it off) */
    int cmd_sent;          /* waiting for current P_CAL command */
    char step[96], prompt[240], err[200], run_name[16];
} g_cal;

static int cal_g33_ms(void) {
    const char *e = getenv("IVIB_CAL_G33_MS");
    long v = e && *e ? atol(e) : 1200000L;
    if (v < 500) v = 500;
    if (v > 3600000) v = 3600000;
    return (int)v;
}
static int cal_g29_ms(void) {
    const char *e = getenv("IVIB_CAL_G29_MS");
    long v = e && *e ? atol(e) : 720000L;
    if (v < 500) v = 500;
    if (v > 3600000) v = 3600000;
    return (int)v;
}
static int cal_home_ms(void) {
    const char *e = getenv("IVIB_CAL_HOME_MS");
    long v = e && *e ? atol(e) : 120000L;
    if (v < 500) v = 500;
    if (v > 600000) v = 600000;
    return (int)v;
}
static int cal_heat_ms(void) {
    const char *e = getenv("IVIB_CAL_HEAT_MS");
    long v = e && *e ? atol(e) : 1200000L;     /* 20 min to reach the bed target */
    if (v < 500) v = 500;
    if (v > 3600000) v = 3600000;
    return (int)v;
}
static int cal_cmd_ms(void) {
    const char *e = getenv("IVIB_CAL_CMD_MS");
    long v = e && *e ? atol(e) : 30000L;
    if (v < 500) v = 500;
    if (v > 300000) v = 300000;
    return (int)v;
}

static int cal_busy(void) {
    return g_cal.st != CAL_IDLE && g_cal.st != CAL_DONE && g_cal.st != CAL_FAIL;
}

static const char *cal_phase_name(int st) {
    switch (st) {
    case CAL_IDLE: return "idle";
    case CAL_NEED_TEMP: return "need_temp";
    case CAL_COOL: return "cool";
    case CAL_PROMPT_BED: return "prompt_bed";
    case CAL_MOVE_INSTALL: return "move_install";
    case CAL_PROMPT_ATTACH: return "prompt_attach";
    case CAL_M119: return "m119";
    case CAL_ATTACH_RETRY: return "attach_retry";
    case CAL_HEAT: return "heat_bed";
    case CAL_RUN: return "run";
    case CAL_SAVE: return "save";
    case CAL_PROBE_M503: return "probe_m503";
    case CAL_MOVE_REMOVE: return "move_remove";
    case CAL_PROMPT_REMOVE: return "prompt_remove";
    case CAL_PAPER_PREP: return "paper_prep";
    case CAL_PAPER_JOG: return "paper_jog";
    case CAL_PAPER_EXEC: return "paper_save";
    case CAL_DONE: return "done";
    case CAL_FAIL: return "fail";
    default: return "idle";
    }
}

static void cal_settings_write(FILE *f) {
    if (g_cal.last_xyz) fprintf(f, "last_xyz=%ld\n", g_cal.last_xyz);
    if (g_cal.last_level) fprintf(f, "last_level=%ld\n", g_cal.last_level);
    if (g_cal.last_paper) fprintf(f, "last_paper=%ld\n", g_cal.last_paper);
}

static void cal_settings_read(const char *line) {
    if (!strncmp(line, "last_xyz=", 9)) g_cal.last_xyz = atol(line + 9);
    else if (!strncmp(line, "last_level=", 11)) g_cal.last_level = atol(line + 11);
    else if (!strncmp(line, "last_paper=", 11)) g_cal.last_paper = atol(line + 11);
}

static void cal_set_st(int st, const char *step, const char *prompt) {
    g_cal.st = st;
    g_cal.phase_ms = now_ms();
    g_cal.confirmed = 0;
    g_cal.cmd_sent = 0;
    snprintf(g_cal.step, sizeof g_cal.step, "%s", step ? step : "");
    snprintf(g_cal.prompt, sizeof g_cal.prompt, "%s", prompt ? prompt : "");
    logi_("cal: %s — %s", cal_phase_name(st), g_cal.step);
}

static void cal_fail(const char *why) {
    snprintf(g_cal.err, sizeof g_cal.err, "%s", why ? why : "calibration failed");
    g_cal.progress = 0;
    g_cal.prompt[0] = 0;
    /* Soft endstops must come back even on failure / cancel. */
    if (g_cal.soft_off && net_ready() && g_ser >= 0) {
        net_send("M211 S1", NW_OK, P_CAL, cal_cmd_ms(), NULL, NULL, NULL);
        g_cal.soft_off = 0;
        g_cal.cmd_sent = 1;
    } else if (g_cal.bed_on && net_ready() && g_ser >= 0) {
        /* heated leveling: cancel / failure turns the bed off (cal_tick retries if the link is busy) */
        net_send("M140 S0", NW_OK, P_CAL, cal_cmd_ms(), NULL, NULL, NULL);
        g_cal.bed_on = 0;
        g_cal.cmd_sent = 1;
    }
    cal_set_st(CAL_FAIL, "Failed", NULL);
    logf_("cal failed: %s", g_cal.err);
}

static void cal_succeed(void) {
    g_cal.bed_on = 0;                  /* heated leveling already sent M140 S0 after the save */
    g_cal.progress = 100;
    g_cal.prompt[0] = 0;
    cal_set_st(CAL_DONE, "Finished", NULL);
    logi_("cal: finished %s", g_cal.run_name);
}

static void cal_send(const char *cmd, int kind, const char *match, int timeout_ms) {
    if (!cmd || !*cmd) return;
    zoff_track_cmd(cmd);
    net_send(cmd, kind, P_CAL, timeout_ms, match, NULL, NULL);
    g_cal.cmd_sent = 1;
}

static void cal_send_ok(const char *cmd, int timeout_ms) {
    cal_send(cmd, NW_OK, NULL, timeout_ms);
}

/* Probe attach / removal needs a cool nozzle only. Stock checkTempForWizard checks the nozzle's actual
   temperature, not the bed, so a warm bed does not block the probe flows (needed for heated leveling). */
static int cal_temps_ok(void) {
    if (!S.have_t) return 0;
    return S.t_act <= CAL_TEMP_MAX;
}

static int cal_temps_fresh(void) {
    return S.have_t && S.t_ms && (now_ms() - S.t_ms) < 8000;
}

static const char *cal_cool_msg(void) {
    static char b[160];
    snprintf(b, sizeof b, "Let the nozzle cool to 40 °C or below before attaching the probe (nozzle %.0f °C).",
             S.have_t ? S.t_act : 0);
    return b;
}

static void cal_mark_last(int which) {
    long now = (long)time(NULL);
    if (which == CAL_K_XYZ) g_cal.last_xyz = now;
    else if (which == CAL_K_LEVEL) g_cal.last_level = now;
    else if (which == CAL_K_PAPER) g_cal.last_paper = now;
    settings_save();
}

static int cal_locked(char *err, size_t en) {
    if (job_active()) { snprintf(err, en, "a print is running; calibration is locked"); return 409; }
    if (AJ.active) { snprintf(err, en, "the touchscreen is printing; calibration is locked"); return 409; }
    if (S.working[0] && starts(S.working, "WORKING")) {
        snprintf(err, en, "printer reports %s; finish or stop that job first", S.working);
        return 409;
    }
    if (g_ser < 0) { snprintf(err, en, "printer link is down"); return 409; }
    if (R.st == R_PENDING) { snprintf(err, en, "a touchscreen request is already pending"); return 409; }
    return 0;
}

static int cal_start(const char *action, int bed_c, char *err, size_t en) {
    int rc = cal_locked(err, en);
    if (rc) return rc;
    if (cal_busy()) { snprintf(err, en, "calibration is already running"); return 409; }
    int kind = CAL_K_NONE;
    if (!action || !*action) { snprintf(err, en, "expected action xyz, level, paper, or all"); return 400; }
    if (!strcmp(action, "xyz")) kind = CAL_K_XYZ;
    else if (!strcmp(action, "level") || !strcmp(action, "leveling") || !strcmp(action, "g29")) kind = CAL_K_LEVEL;
    else if (!strcmp(action, "paper") || !strcmp(action, "zoffset") || !strcmp(action, "z-offset")) kind = CAL_K_PAPER;
    else if (!strcmp(action, "all")) kind = CAL_K_ALL;
    else { snprintf(err, en, "unknown action '%s' (use xyz, level, paper, or all)", action); return 400; }
    if (bed_c && kind != CAL_K_LEVEL) { snprintf(err, en, "a bed temperature is only used with action level"); return 400; }
    if (bed_c && bed_c < CAL_BED_MIN) bed_c = CAL_BED_MIN;
    if (bed_c > CAL_BED_MAX) bed_c = CAL_BED_MAX;

    memset(&g_cal.err, 0, sizeof g_cal.err);
    g_cal.kind = kind;
    g_cal.want_level = (kind == CAL_K_XYZ || kind == CAL_K_LEVEL || kind == CAL_K_ALL);
    g_cal.want_paper = (kind == CAL_K_PAPER || kind == CAL_K_ALL);
    g_cal.running_g33 = (kind == CAL_K_XYZ || kind == CAL_K_ALL);
    g_cal.started_ms = now_ms();
    g_cal.progress = 1;
    g_cal.soft_off = 0;
    g_cal.m119_seen = g_cal.m119_ok = g_cal.m119_missing = 0;
    g_cal.cmd_sent = 0;
    g_cal.confirmed = 0;
    g_cal.paper_new_h = INT_MIN;
    g_cal.bed_c = bed_c; g_cal.bed_on = 0;
    snprintf(g_cal.run_name, sizeof g_cal.run_name, "%s",
             kind == CAL_K_XYZ ? "xyz" : kind == CAL_K_LEVEL ? "level" : kind == CAL_K_PAPER ? "paper" : "all");

    if (kind == CAL_K_PAPER) {
        cal_set_st(CAL_PROMPT_BED, "Paper test",
                   "Confirm the build plate is installed and clear. The probe must be off for the paper test.");
        g_cal.progress = 8;
        return 0;
    }
    if (!cal_temps_fresh()) {
        cal_set_st(CAL_NEED_TEMP, "Checking temperatures", NULL);
        g_cal.progress = 2;
        return 0;
    }
    if (!cal_temps_ok()) {
        cal_set_st(CAL_COOL, "Waiting for cool-down", cal_cool_msg());
        g_cal.progress = 3;
        return 0;
    }
    cal_set_st(CAL_PROMPT_BED, "Build plate",
               "Confirm the build plate is installed and clear, then continue.");
    g_cal.progress = 6;
    return 0;
}

static int cal_confirm(char *err, size_t en) {
    if (!cal_busy()) { snprintf(err, en, "no calibration is waiting for a confirmation"); return 409; }
    if (g_cal.st != CAL_PROMPT_BED && g_cal.st != CAL_PROMPT_ATTACH &&
        g_cal.st != CAL_ATTACH_RETRY && g_cal.st != CAL_PROMPT_REMOVE) {
        snprintf(err, en, "nothing to confirm in this step");
        return 409;
    }
    g_cal.confirmed = 1;
    return 0;
}

static int iround_to(double v, int scale) {
    if (v >= 0) return (int)(v * scale + 0.5);
    return (int)(v * scale - 0.5);
}

static int cal_jog_ok(double dz) {
    int thou = iround_to(dz, 1000);
    const int steps[] = {5000, 1000, 100, 50, 10, -5000, -1000, -100, -50, -10};
    for (int i = 0; i < 10; i++) if (thou == steps[i]) return 1;
    return 0;
}

static int cal_jog(double dz, char *err, size_t en) {
    if (g_cal.st != CAL_PAPER_JOG) { snprintf(err, en, "jog is only available during the paper test"); return 409; }
    if (g_cal.cmd_sent || !net_ready()) { snprintf(err, en, "a move is already in progress"); return 409; }
    if (!cal_jog_ok(dz)) { snprintf(err, en, "jog step must be ±5, ±1, ±0.1, ±0.05, or ±0.01 mm"); return 400; }
    char cmd[48];
    snprintf(cmd, sizeof cmd, "G91\n"); /* sent as three commands sequentially via flag */
    /* Send G91, G1 Z{dz} F500, G90, M114 as a short burst: one at a time via cmd_sent chain.
       We stash the remaining moves in err-unused statics. */
    /* dz is kept in g_cal.step as jog:%.3f */
    /* Use step text to queue: "jog:<dz>" */
    snprintf(g_cal.step, sizeof g_cal.step, "jog:%.3f", dz);
    g_cal.confirmed = 2; /* 2 = start jog sequence */
    return 0;
}

static int cal_paper_save(char *err, size_t en) {
    if (g_cal.st != CAL_PAPER_JOG) { snprintf(err, en, "paper-test save is not available now"); return 409; }
    if (g_z_height_h == INT_MIN) { snprintf(err, en, "stored height is unknown; wait for M503, then retry"); return 409; }
    if (!S.have_pos) { snprintf(err, en, "current Z is unknown; jog or wait for M114, then retry"); return 409; }
    int zh = iround_to(S.z, 100);
    int nh = g_z_height_h - zh;
    if (nh < 15000 || nh > 30000) {
        snprintf(err, en, "refusing to save height %d.%02d mm (outside 150..300); check the current Z",
                 nh / 100, nh < 0 ? -nh % 100 : nh % 100);
        return 400;
    }
    g_cal.paper_new_h = nh;
    snprintf(g_cal.step, sizeof g_cal.step, "Saving H");
    g_cal.confirmed = 3; /* 3 = save */
    return 0;
}

static int cal_cancel(char *err, size_t en) {
    if (!cal_busy()) { snprintf(err, en, "no calibration is running"); return 409; }
    /* Mid-command: wait for the in-flight G-code, then fail without M500.
       Soft endstops are restored in cal_fail. */
    snprintf(g_cal.err, sizeof g_cal.err, "cancelled");
    if (g_cal.st == CAL_PAPER_JOG && g_cal.soft_off) {
        g_cal.confirmed = 4; /* 4 = cancel paper: M211 S1 then fail */
        snprintf(g_cal.step, sizeof g_cal.step, "Restoring endstops");
        return 0;
    }
    if (g_cal.cmd_sent) {
        g_cal.confirmed = 5; /* finish current cmd, then fail */
        return 0;
    }
    cal_fail("cancelled");
    return 0;
}

/* ---- serial parse (always, so the tab can show live M503 values) ---- */

static void cal_parse_m665(const char *l) {
    const char *p;
    if ((p = find_param(l, 'H'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.H = v; }
    if ((p = find_param(l, 'R'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.R = v; }
    if ((p = find_param(l, 'L'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.L = v; }
    if ((p = find_param(l, 'S'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.S = v; }
    if ((p = find_param(l, 'X'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.ang[0] = v; }
    if ((p = find_param(l, 'Y'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.ang[1] = v; }
    if ((p = find_param(l, 'Z'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.ang[2] = v; }
}

static void cal_parse_m666(const char *l) {
    const char *p;
    if ((p = find_param(l, 'X'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.endst[0] = v; }
    if ((p = find_param(l, 'Y'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.endst[1] = v; }
    if ((p = find_param(l, 'Z'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.endst[2] = v; }
}

static int cal_is_nan_tok(const char *p) {
    return !strncasecmp(p, "nan", 3) || !strncasecmp(p, "NAN", 3);
}

static void cal_parse_g29w(const char *l) {
    const char *pi = find_param(l, 'I'), *pj = find_param(l, 'J'), *pz = find_param(l, 'Z');
    if (!pi || !pj || !pz) return;
    int i = atoi(pi), j = atoi(pj);
    if (i < 0 || i >= CAL_GRID || j < 0 || j >= CAL_GRID) return;
    if (cal_is_nan_tok(pz)) { g_cal.mesh_ok[i][j] = 0; return; }
    g_cal.mesh[i][j] = strtof(pz, NULL);
    g_cal.mesh_ok[i][j] = 1;
    g_cal.have_mesh = 1;
}

static void cal_parse_m420(const char *l) {
    const char *p;
    if ((p = find_param(l, 'S'))) g_cal.abl = atoi(p) ? 1 : 0;
    if ((p = find_param(l, 'Z'))) { int v = parse_hund(p, NULL); if (v != INT_MIN) g_cal.fade_h = v; }
}

static void cal_on_line(const char *l) {
    if (!l || !*l) return;
    const char *s = l;
    if (!strncmp(s, "echo:", 5)) {
        s += 5;
        while (*s == ' ') s++;
    }
    if (starts(s, "M665") || starts(s, "M665 ")) cal_parse_m665(s);
    if (starts(s, "M666") || starts(s, "M666 ")) cal_parse_m666(s);
    if (starts(s, "M420") || starts(s, "M420 ")) cal_parse_m420(s);
    if (starts(s, "G29 W") || starts(s, "G29W")) cal_parse_g29w(s);
    if (istrstr(s, "Bed Leveling On")) g_cal.abl = 1;
    if (istrstr(s, "Bed Leveling Off")) g_cal.abl = 0;

    /* M119: accept open or TRIGGERED; reject a missing z_min or "no exist". */
    if (g_cal.st == CAL_M119 || (g_cal.cmd_sent && W.purpose == P_CAL && strstr(g_cal.step, "M119"))) {
        const char *z = strstr(l, "z_min:");
        if (z) {
            g_cal.m119_seen = 1;
            if (istrstr(z, "no exist") || istrstr(z, "noexist")) g_cal.m119_missing = 1;
            else g_cal.m119_ok = 1;
        }
    }

    /* Fail strings while a G33/G29 expect is in flight (before a success match). */
    if (W.purpose == P_CAL && W.kind == NW_EXPECT && !W.matched && !W.failed) {
        if (istrstr(l, "Probing Failed") || istrstr(l, "No convergence") ||
            starts(l, "warning:") || starts(l, "Error:") ||
            (l[0] == '?' && l[1] && l[1] != '\n')) {
            W.failed = 1;
            snprintf(W.fail, sizeof W.fail, "%.140s", l);
        }
    }
}

static void cal_hund_json(struct sb *s, const char *k, int h) {
    if (h == INT_MIN) sb_add(s, "\"%s\":null", k);
    else {
        char b[16];
        hund_fmt(h, b, sizeof b);
        sb_add(s, "\"%s\":%s", k, b);
    }
}

static void cal_json(struct sb *s) {
    long long t = now_ms();
    double el = 0;
    if (g_cal.started_ms && cal_busy()) el = (t - g_cal.started_ms) / 1000.0;
    else if (g_cal.started_ms && (g_cal.st == CAL_DONE || g_cal.st == CAL_FAIL))
        el = (g_cal.phase_ms - g_cal.started_ms) / 1000.0;
    if (el < 0) el = 0;

    /* Time-based progress while G33/G29 is running. */
    if (g_cal.st == CAL_RUN && g_cal.running_g33) {
        int denom = 900; /* ~15 min */
        int pct = 18 + (int)(el * 37.0 / denom);
        if (pct > 54) pct = 54;
        if (pct < 18) pct = 18;
        g_cal.progress = pct;
    } else if (g_cal.st == CAL_RUN && !g_cal.running_g33) {
        int base = (g_cal.kind == CAL_K_LEVEL) ? 20 : 62;
        int span = (g_cal.kind == CAL_K_LEVEL) ? 50 : 16;
        int denom = 300;
        int pct = base + (int)(el * span / denom);
        if (pct > base + span - 1) pct = base + span - 1;
        g_cal.progress = pct;
    }

    sb_add(s, "{\"busy\":%s,\"phase\":", cal_busy() ? "true" : "false");
    sb_str(s, cal_phase_name(g_cal.st));
    sb_add(s, ",\"run\":"); sb_str(s, g_cal.run_name[0] ? g_cal.run_name : "");
    sb_add(s, ",\"step\":"); sb_str(s, g_cal.step);
    sb_add(s, ",\"prompt\":");
    if (g_cal.prompt[0]) sb_str(s, g_cal.prompt); else sb_add(s, "null");
    sb_add(s, ",\"error\":");
    if (g_cal.err[0] && (g_cal.st == CAL_FAIL || g_cal.st == CAL_DONE)) sb_str(s, g_cal.err);
    else if (g_cal.err[0] && !strcmp(g_cal.err, "cancelled") && cal_busy()) sb_str(s, g_cal.err);
    else sb_add(s, "null");
    sb_add(s, ",\"progress\":%d,\"elapsed_s\":%.1f", g_cal.progress, el);
    /* 0.1.19 heated leveling: the run's bed target (null = cold flow) and the live bed temperature */
    if (g_cal.bed_c && (cal_busy() || g_cal.st == CAL_DONE || g_cal.st == CAL_FAIL)) sb_add(s, ",\"bed_target\":%d", g_cal.bed_c);
    else sb_add(s, ",\"bed_target\":null");
    if (S.have_t) sb_add(s, ",\"bed\":%.1f,\"nozzle\":%.1f", S.b_act, S.t_act); else sb_add(s, ",\"bed\":null,\"nozzle\":null");
    sb_add(s, ",\"xyz\":{");
    cal_hund_json(s, "H", g_cal.H != INT_MIN ? g_cal.H : g_z_height_h);
    sb_add(s, ","); cal_hund_json(s, "R", g_cal.R);
    sb_add(s, ","); cal_hund_json(s, "L", g_cal.L);
    sb_add(s, ","); cal_hund_json(s, "S", g_cal.S);
    sb_add(s, ",\"endstops\":{");
    cal_hund_json(s, "X", g_cal.endst[0]); sb_add(s, ",");
    cal_hund_json(s, "Y", g_cal.endst[1]); sb_add(s, ",");
    cal_hund_json(s, "Z", g_cal.endst[2]);
    sb_add(s, "},\"angles\":{");
    cal_hund_json(s, "X", g_cal.ang[0]); sb_add(s, ",");
    cal_hund_json(s, "Y", g_cal.ang[1]); sb_add(s, ",");
    cal_hund_json(s, "Z", g_cal.ang[2]);
    if (g_cal.last_xyz) sb_add(s, "},\"last_s\":%ld}", g_cal.last_xyz);
    else sb_add(s, "},\"last_s\":null}");

    sb_add(s, ",\"level\":{\"enabled\":%s,", g_cal.abl ? "true" : "false");
    cal_hund_json(s, "fade", g_cal.fade_h);
    sb_add(s, ",\"grid\":");
    if (!g_cal.have_mesh) sb_add(s, "null");
    else {
        sb_add(s, "[");
        for (int j = 0; j < CAL_GRID; j++) {
            if (j) sb_add(s, ",");
            sb_add(s, "[");
            for (int i = 0; i < CAL_GRID; i++) {
                if (i) sb_add(s, ",");
                if (!g_cal.mesh_ok[i][j]) sb_add(s, "null");
                else sb_add(s, "%.5f", (double)g_cal.mesh[i][j]);
            }
            sb_add(s, "]");
        }
        sb_add(s, "]");
    }
    if (g_cal.last_level) sb_add(s, ",\"last_s\":%ld}", g_cal.last_level);
    else sb_add(s, ",\"last_s\":null}");

    sb_add(s, ",\"paper\":{");
    if (S.have_pos) sb_add(s, "\"z\":%.3f,", S.z); else sb_add(s, "\"z\":null,");
    cal_hund_json(s, "H", g_z_height_h); sb_add(s, ",");
    /* offset / ref come from the 0.1.16 display math; duplicated here for the card. */
    {
        int off = zoff_offset_h(), ref = g_z_ref_h;
        cal_hund_json(s, "offset", off); sb_add(s, ",");
        cal_hund_json(s, "ref", ref);
    }
    if (g_cal.last_paper) sb_add(s, ",\"last_s\":%ld}}", g_cal.last_paper);
    else sb_add(s, ",\"last_s\":null}}");
}

static void cal_begin_probe_run(void) {
    g_cal.m119_seen = g_cal.m119_ok = g_cal.m119_missing = 0;
    if (g_cal.running_g33) {
        /* G33 P=4 default wipes the bilinear mesh. */
        g_cal.have_mesh = 0;
        memset(g_cal.mesh_ok, 0, sizeof g_cal.mesh_ok);
        cal_set_st(CAL_RUN, "XYZ calibration (G33) — about 15 minutes", NULL);
        g_cal.progress = (g_cal.kind == CAL_K_LEVEL) ? 20 : 18;
        cal_send("G33", NW_EXPECT, "Calibration OK", cal_g33_ms());
    } else {
        cal_set_st(CAL_RUN, "Auto-level (G29)", NULL);
        g_cal.progress = (g_cal.kind == CAL_K_LEVEL) ? 20 : 62;
        cal_send("G29", NW_EXPECT, "Bilinear Leveling Grid:", cal_g29_ms());
    }
}

static void cal_after_m503(void) {
    if (g_cal.running_g33) {
        cal_mark_last(CAL_K_XYZ);
        /* Always chain into leveling — the mesh was wiped. */
        g_cal.running_g33 = 0;
        cal_set_st(CAL_RUN, "Auto-level (G29) — leaving the probe on", NULL);
        g_cal.progress = 62;
        cal_send("G29", NW_EXPECT, "Bilinear Leveling Grid:", cal_g29_ms());
        return;
    }
    if (g_cal.want_level && g_cal.st == CAL_PROBE_M503)
        cal_mark_last(CAL_K_LEVEL);
    /* After leveling (or level-only), stow and maybe paper. */
    if (g_cal.kind == CAL_K_LEVEL && g_cal.bed_on) {
        /* heated leveling: the mesh is saved, turn the bed off before the probe comes off */
        cal_set_st(CAL_MOVE_REMOVE, "Turning the bed off (M140 S0)", NULL);
        g_cal.progress = 85;
        cal_send_ok("M140 S0", cal_cmd_ms());
        g_cal.bed_on = 0;
        g_cal.confirmed = 60;          /* 60 = M140 S0 in flight, 61 = send G0, 62 = G0 in flight */
        return;
    }
    if (g_cal.kind == CAL_K_LEVEL || g_cal.kind == CAL_K_XYZ || g_cal.kind == CAL_K_ALL) {
        cal_set_st(CAL_MOVE_REMOVE, "Moving up so you can remove the probe", NULL);
        g_cal.progress = 86;
        cal_send_ok("G0 X0 Y0 Z100 F1000", cal_cmd_ms());
        return;
    }
    cal_succeed();
}

static void cal_advance_from_confirm(void) {
    if (g_cal.st == CAL_PROMPT_BED && g_cal.confirmed) {
        if (g_cal.kind == CAL_K_PAPER) {
            cal_set_st(CAL_PAPER_PREP, "Homing and moving to the paper-test height", NULL);
            g_cal.progress = 20;
            g_cal.confirmed = 10; /* start paper prep sequence */
            return;
        }
        cal_set_st(CAL_MOVE_INSTALL, "Homing and moving up for the probe", NULL);
        g_cal.progress = 10;
        g_cal.confirmed = 11; /* start install moves */
        return;
    }
    if ((g_cal.st == CAL_PROMPT_ATTACH || g_cal.st == CAL_ATTACH_RETRY) && g_cal.confirmed) {
        g_cal.m119_seen = g_cal.m119_ok = g_cal.m119_missing = 0;
        cal_set_st(CAL_M119, "Checking that the probe is attached (M119)", NULL);
        g_cal.progress = 16;
        cal_send_ok("M119", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PROMPT_REMOVE && g_cal.confirmed) {
        if (g_cal.want_paper) {
            cal_set_st(CAL_PAPER_PREP, "Homing and moving to the paper-test height", NULL);
            g_cal.progress = 90;
            g_cal.confirmed = 10;
            return;
        }
        cal_succeed();
    }
}

static void cal_cmd_done(int timed_out, int failed, const char *fail) {
    g_cal.cmd_sent = 0;
    if (g_cal.confirmed == 5 || (g_cal.err[0] && !strcmp(g_cal.err, "cancelled") && g_cal.confirmed == 5)) {
        cal_fail("cancelled");
        return;
    }
    if (g_cal.st == CAL_FAIL) return;
    if (failed || timed_out) {
        if (timed_out) cal_fail("timed out waiting for the printer");
        else cal_fail(fail && fail[0] ? fail : "printer reported a failure");
        return;
    }
    switch (g_cal.st) {
    case CAL_NEED_TEMP:
        if (!cal_temps_ok()) {
            cal_set_st(CAL_COOL, "Waiting for cool-down", cal_cool_msg());
            g_cal.progress = 3;
        } else {
            cal_set_st(CAL_PROMPT_BED, "Build plate",
                       "Confirm the build plate is installed and clear, then continue.");
            g_cal.progress = 6;
        }
        return;
    case CAL_COOL:
        if (cal_temps_ok()) {
            cal_set_st(CAL_PROMPT_BED, "Build plate",
                       "Confirm the build plate is installed and clear, then continue.");
            g_cal.progress = 6;
        } else {
            snprintf(g_cal.prompt, sizeof g_cal.prompt, "%s", cal_cool_msg());
            g_cal.last_poll_ms = now_ms();
        }
        return;
    case CAL_MOVE_INSTALL:
        /* Sequence driven from cal_tick via confirmed=11,12,13 */
        if (g_cal.confirmed == 11) { g_cal.confirmed = 12; return; } /* G53 done → G28 */
        if (g_cal.confirmed == 12) { g_cal.confirmed = 13; return; } /* G28 done → G0 Z100 */
        cal_set_st(CAL_PROMPT_ATTACH, "Attach the probe",
                   "Clip the probe onto the toolhead, then continue. The bridge will check M119 (z_min).");
        g_cal.progress = 14;
        return;
    case CAL_M119:
        if (g_cal.m119_ok && !g_cal.m119_missing && g_cal.bed_c) {
            char st[96]; snprintf(st, sizeof st, "Heating the bed to %d °C", g_cal.bed_c);
            cal_set_st(CAL_HEAT, st, NULL);
            g_cal.progress = 17;
            g_cal.confirmed = 50;          /* 50 = send M140, 51 = wait loop */
        } else if (g_cal.m119_ok && !g_cal.m119_missing) {
            cal_begin_probe_run();
        } else {
            cal_set_st(CAL_ATTACH_RETRY, "Probe not detected",
                       "The probe was not seen (no z_min, or z_min: no exist). Attach it firmly and retry, or cancel.");
            g_cal.progress = 14;
        }
        return;
    case CAL_HEAT:
        if (g_cal.confirmed == 50) { g_cal.confirmed = 51; g_cal.bed_on = 1; g_cal.last_poll_ms = 0; return; }   /* M140 done */
        if (S.have_t && S.b_act >= g_cal.bed_c - 1.0) {
            logi_("cal: bed at %.1f °C (target %d), starting G29", S.b_act, g_cal.bed_c);
            cal_begin_probe_run();
            return;
        }
        if (now_ms() - g_cal.phase_ms > cal_heat_ms()) { cal_fail("the bed did not reach the leveling temperature"); return; }
        snprintf(g_cal.step, sizeof g_cal.step, "Heating the bed: %.0f / %d °C", S.have_t ? S.b_act : 0.0, g_cal.bed_c);
        return;
    case CAL_RUN:
        /* Success string was matched and the trailing ok arrived (G28 settle included). */
        cal_set_st(CAL_SAVE, "Saving settings (M500)", NULL);
        g_cal.progress = g_cal.running_g33 ? 56 : 82;
        cal_send_ok("M500", cal_cmd_ms());
        return;
    case CAL_SAVE:
        cal_set_st(CAL_PROBE_M503, "Refreshing settings (M503)", NULL);
        g_cal.progress = g_cal.running_g33 ? 58 : 84;
        cal_send_ok("M503", cal_cmd_ms());
        return;
    case CAL_PROBE_M503:
        cal_after_m503();
        return;
    case CAL_MOVE_REMOVE:
        if (g_cal.confirmed == 60) {
            g_cal.confirmed = 61;
            snprintf(g_cal.step, sizeof g_cal.step, "Moving up so you can remove the probe");
            g_cal.progress = 86;
            return;
        }
        if (g_cal.bed_c) {
            cal_set_st(CAL_PROMPT_REMOVE, "Remove the probe",
                       "Take the probe off the toolhead, then continue. The bed heater is off, but the bed is still hot; take care.");
        } else
        cal_set_st(CAL_PROMPT_REMOVE, "Remove the probe",
                   "Take the probe off the toolhead, then continue.");
        g_cal.progress = 88;
        return;
    case CAL_PAPER_PREP:
        if (g_cal.confirmed == 10) { g_cal.confirmed = 16; return; } /* M503 done */
        if (g_cal.confirmed == 16) { g_cal.confirmed = 20; return; } /* G28 done */
        if (g_cal.confirmed == 20) { g_cal.confirmed = 21; return; } /* Z50 done */
        if (g_cal.confirmed == 21) { g_cal.confirmed = 22; return; } /* Z40 done */
        /* M211 S0 done */
        g_cal.soft_off = 1;
        cal_set_st(CAL_PAPER_JOG, "Jog until the paper just drags, then save",
                   "Slide a sheet of paper under the nozzle. Use the jog buttons until it just drags, then Save. Cancel restores endstops without saving.");
        g_cal.progress = 92;
        /* Immediate M114 so the card shows Z. */
        if (net_ready()) cal_send_ok("M114", cal_cmd_ms());
        return;
    case CAL_PAPER_JOG:
        /* Jog sequence or trailing M114. */
        if (g_cal.confirmed == 2 || g_cal.confirmed == 30 || g_cal.confirmed == 31 || g_cal.confirmed == 32) {
            if (g_cal.confirmed == 2) { g_cal.confirmed = 30; return; }       /* G91 done */
            if (g_cal.confirmed == 30) { g_cal.confirmed = 31; return; }     /* G1 done */
            if (g_cal.confirmed == 31) { g_cal.confirmed = 32; return; }     /* G90 done */
            g_cal.confirmed = 0; /* M114 done */
            snprintf(g_cal.step, sizeof g_cal.step, "Jog until the paper just drags, then save");
            return;
        }
        if (g_cal.confirmed == 3) {
            /* first of save sequence (M665) done → M500 */
            g_cal.confirmed = 40;
            return;
        }
        if (g_cal.confirmed == 40) { g_cal.confirmed = 41; return; } /* M500 done → M211 S1 */
        if (g_cal.confirmed == 41) {
            g_cal.soft_off = 0;
            cal_mark_last(CAL_K_PAPER);
            /* Paper-test M665 is a new calibration: zoff_note_stored_h resets ref. */
            cal_succeed();
            return;
        }
        if (g_cal.confirmed == 4) {
            g_cal.soft_off = 0;
            cal_fail("cancelled");
            return;
        }
        /* stray M114 */
        return;
    case CAL_PAPER_EXEC:
        cal_succeed();
        return;
    default:
        return;
    }
}

static void cal_tick(void) {
    if (g_cal.st == CAL_DONE || g_cal.st == CAL_FAIL) {
        if (g_cal.st == CAL_FAIL && g_cal.soft_off && !g_cal.cmd_sent && net_ready() && g_ser >= 0) {
            cal_send_ok("M211 S1", cal_cmd_ms());
            g_cal.soft_off = 0;
        } else if (g_cal.st == CAL_FAIL && g_cal.bed_on && !g_cal.cmd_sent && net_ready() && g_ser >= 0) {
            cal_send_ok("M140 S0", cal_cmd_ms());
            g_cal.bed_on = 0;
        }
        return;
    }
    if (!cal_busy()) return;

    cal_advance_from_confirm();

    if (g_cal.cmd_sent || !net_ready() || g_ser < 0) return;

    /* Cool-down poll. */
    if (g_cal.st == CAL_COOL) {
        long long t = now_ms();
        if (cal_temps_ok()) {
            cal_set_st(CAL_PROMPT_BED, "Build plate",
                       "Confirm the build plate is installed and clear, then continue.");
            g_cal.progress = 6;
            return;
        }
        if (!g_cal.last_poll_ms || t - g_cal.last_poll_ms > 2500) {
            g_cal.last_poll_ms = t;
            snprintf(g_cal.prompt, sizeof g_cal.prompt, "%s", cal_cool_msg());
            cal_send_ok("M105", 8000);
        }
        return;
    }
    if (g_cal.st == CAL_NEED_TEMP) {
        cal_send_ok("M105", 8000);
        return;
    }

    /* Heated leveling: set the bed, then poll M105 (no blocking M190, so Cancel stays responsive) */
    if (g_cal.st == CAL_HEAT && g_cal.confirmed == 50) {
        char cmd[24]; snprintf(cmd, sizeof cmd, "M140 S%d", g_cal.bed_c);
        cal_send_ok(cmd, cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_HEAT && g_cal.confirmed == 51) {
        long long t = now_ms();
        if (!g_cal.last_poll_ms || t - g_cal.last_poll_ms > 2000) { g_cal.last_poll_ms = t; cal_send_ok("M105", 8000); }
        return;
    }

    if (g_cal.st == CAL_MOVE_REMOVE && g_cal.confirmed == 61) {
        cal_send_ok("G0 X0 Y0 Z100 F1000", cal_cmd_ms());
        g_cal.confirmed = 62;
        return;
    }

    /* Install move sequence: G53, G28, G0 X0 Y0 Z100 F1000 */
    if (g_cal.st == CAL_MOVE_INSTALL && g_cal.confirmed == 11) {
        cal_send_ok("G53", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_MOVE_INSTALL && g_cal.confirmed == 12) {
        cal_send_ok("G28", cal_home_ms());
        return;
    }
    if (g_cal.st == CAL_MOVE_INSTALL && g_cal.confirmed == 13) {
        cal_send_ok("G0 X0 Y0 Z100 F1000", cal_cmd_ms());
        g_cal.confirmed = 14;
        return;
    }

    /* Paper prep: G28, G1 X0 Y0 Z50 F1000, G1 Z40 F500, M211 S0 */
    if (g_cal.st == CAL_PAPER_PREP && g_cal.confirmed == 10) {
        cal_send_ok("M503", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_PREP && g_cal.confirmed == 16) {
        cal_send_ok("G28", cal_home_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_PREP && g_cal.confirmed == 20) {
        cal_send_ok("G1 X0 Y0 Z50 F1000", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_PREP && g_cal.confirmed == 21) {
        cal_send_ok("G1 X0 Y0 Z40 F500", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_PREP && g_cal.confirmed == 22) {
        cal_send_ok("M211 S0", cal_cmd_ms());
        g_cal.confirmed = 23;
        return;
    }

    /* Paper jog: G91, G1 Zdz F500, G90, M114. dz is in g_cal.step "jog:%.3f" */
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 2) {
        cal_send_ok("G91", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 30) {
        double dz = 0;
        const char *p = strstr(g_cal.step, "jog:");
        if (p) dz = atof(p + 4);
        char cmd[48];
        snprintf(cmd, sizeof cmd, "G1 Z%.3f F500", dz);
        cal_send_ok(cmd, cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 31) {
        cal_send_ok("G90", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 32) {
        cal_send_ok("M114", cal_cmd_ms());
        return;
    }

    /* Paper save: M665 H + M500 + M211 S1 */
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 3) {
        char hb[16], cmd[48];
        hund_fmt(g_cal.paper_new_h, hb, sizeof hb);
        snprintf(cmd, sizeof cmd, "M665 H%s", hb);
        g_cal.progress = 96;
        cal_set_st(CAL_PAPER_JOG, "Saving new height", NULL);
        g_cal.confirmed = 3;
        cal_send_ok(cmd, cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 40) {
        cal_send_ok("M500", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 41) {
        cal_send_ok("M211 S1", cal_cmd_ms());
        return;
    }
    if (g_cal.st == CAL_PAPER_JOG && g_cal.confirmed == 4) {
        cal_send_ok("M211 S1", cal_cmd_ms());
        return;
    }
}

static void api_ivi_cal_get(struct cli *c) {
    struct sb s = {0};
    cal_json(&s);
    jreply(c, 200, &s);
}

static void api_ivi_cal_post(struct cli *c, const char *body, const char *path) {
    char err[200] = {0}, act[32] = {0};
    const char *p = path ? path : "";
    if (!body) body = "";
    if (strstr(p, "/start") || (jget_str(body, "action", act, sizeof act) &&
                                strcmp(act, "confirm") && strcmp(act, "cancel") &&
                                strcmp(act, "jog") && strcmp(act, "save"))) {
        if (!act[0]) jget_str(body, "action", act, sizeof act);
        if (!act[0]) jget_str(body, "kind", act, sizeof act);
        char bv[16] = ""; int bed_c = 0;
        /* optional heated leveling: "bed":60 (clamped 40..80 in cal_start); true = 60; 0/false/null = cold flow */
        if (jget_str(body, "bed", bv, sizeof bv)) bed_c = !strcmp(bv, "true") ? 60 : (int)(atof(bv) + 0.5);
        if (bed_c < 0) bed_c = 0;
        int rc = cal_start(act, bed_c, err, sizeof err);
        if (rc) { jerr(c, rc, err); return; }
        struct sb s = {0}; sb_add(&s, "{\"ok\":true,\"cal\":"); cal_json(&s); sb_add(&s, "}"); jreply(c, 200, &s);
        return;
    }
    if (strstr(p, "/confirm") || !strcmp(act, "confirm") || jget_bool(body, "confirm")) {
        int rc = cal_confirm(err, sizeof err);
        if (rc) { jerr(c, rc, err); return; }
        struct sb s = {0}; sb_add(&s, "{\"ok\":true,\"cal\":"); cal_json(&s); sb_add(&s, "}"); jreply(c, 200, &s);
        return;
    }
    if (strstr(p, "/cancel") || !strcmp(act, "cancel") || jget_bool(body, "cancel")) {
        int rc = cal_cancel(err, sizeof err);
        if (rc) { jerr(c, rc, err); return; }
        struct sb s = {0}; sb_add(&s, "{\"ok\":true,\"cal\":"); cal_json(&s); sb_add(&s, "}"); jreply(c, 200, &s);
        return;
    }
    if (strstr(p, "/jog") || !strcmp(act, "jog")) {
        char db[32];
        double dz = 0;
        if (jget_str(body, "dz", db, sizeof db)) dz = atof(db);
        else if (jget_str(body, "z", db, sizeof db)) dz = atof(db);
        else {
            const char *q = strstr(body, "\"dz\"");
            if (q) { q = strchr(q, ':'); if (q) dz = atof(q + 1); }
        }
        int rc = cal_jog(dz, err, sizeof err);
        if (rc) { jerr(c, rc, err); return; }
        struct sb s = {0}; sb_add(&s, "{\"ok\":true,\"cal\":"); cal_json(&s); sb_add(&s, "}"); jreply(c, 200, &s);
        return;
    }
    if (strstr(p, "/save") || !strcmp(act, "save") || jget_bool(body, "save")) {
        int rc = cal_paper_save(err, sizeof err);
        if (rc) { jerr(c, rc, err); return; }
        struct sb s = {0}; sb_add(&s, "{\"ok\":true,\"cal\":"); cal_json(&s); sb_add(&s, "}"); jreply(c, 200, &s);
        return;
    }
    jerr(c, 400, "expected action start/confirm/cancel/jog/save");
}

static void cal_init(void) {
    memset(&g_cal, 0, sizeof g_cal);
    g_cal.H = g_cal.R = g_cal.L = g_cal.S = INT_MIN;
    g_cal.ang[0] = g_cal.ang[1] = g_cal.ang[2] = INT_MIN;
    g_cal.rod[0] = g_cal.rod[1] = g_cal.rod[2] = INT_MIN;
    g_cal.endst[0] = g_cal.endst[1] = g_cal.endst[2] = INT_MIN;
    g_cal.fade_h = 0;
}
