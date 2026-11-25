/* Persistent auto-start (default off) and Z-offset tracking.
   Included from ivibridge.c after ivi_request.inc.

   Stock calibration writes delta height via M665 H, then M500. Live Adjust
   uses M290 babysteps only. new_H = stored_H - babystep_total, because
   M290 Z+ raises the nozzle and a smaller H persists that after the next home.
   Mid-print M665 is not applied (kinematic recalc). Save queues until idle,
   then M665 H + M500, and a cancelling M290 so leftover babysteps do not stack. */

static const char *settings_path(void) {
    const char *e = getenv("IVIB_SETTINGS");
    if (e && *e) return e;
    if (!access("/userapp/ivibridge", W_OK)) return "/userapp/ivibridge/settings";
    static char p[576];
    snprintf(p, sizeof p, "%s/settings", ivib_dir());
    return p;
}

/* millimetres in hundredths (0.01 mm). INT_MIN = unknown. */
static int g_z_height_h = INT_MIN;   /* last M665 H (stock stored calibration) */
static int g_z_probe_h = INT_MIN;    /* last M851 Z (probe offset; not the paper-test save) */
static int g_z_baby_h;               /* accumulated M290 this print */
static int g_z_ref_h = INT_MIN;      /* display zero: offset = ref - effective H */
static int g_z_own_h = INT_MIN;      /* H we are applying; do not treat as a new calibration */
static int g_z_pending;
static int g_z_pending_h;
static int g_z_pending_baby;
static long long g_z_m503_at;
static char g_z_last[80];
static int g_z_skip_baby;

static void hund_fmt(int h, char *b, size_t n);
static int parse_hund(const char *p, const char **end);

static int settings_save(void) {
    const char *path = settings_path();
    char tmp[600];
    snprintf(tmp, sizeof tmp, "%s.tmp", path);
    FILE *f = fopen(tmp, "w");
    if (!f) { logf_("settings: cannot write %s", path); return -1; }
    fprintf(f, "autostart=%d\n", g_autostart ? 1 : 0);
    if (g_z_ref_h != INT_MIN) {
        char rh[16]; hund_fmt(g_z_ref_h, rh, sizeof rh);
        fprintf(f, "ref_h=%s\n", rh);
    }
    cal_settings_write(f);
    if (fclose(f) || rename(tmp, path)) { unlink(tmp); logf_("settings: cannot replace %s", path); return -1; }
    return 0;
}

static void settings_load(void) {
    g_autostart = 0;
    g_z_ref_h = INT_MIN;
    FILE *f = fopen(settings_path(), "r");
    if (!f) {
        logi_("settings: autostart=0 (no file yet)");
        return;
    }
    char line[128];
    while (fgets(line, sizeof line, f)) {
        rstrip(line);
        if (!strncmp(line, "autostart=", 10))
            g_autostart = (line[10] == '1');
        else if (!strncmp(line, "ref_h=", 6)) {
            int v = parse_hund(line + 6, NULL);
            if (v != INT_MIN) g_z_ref_h = v;
        }
        else cal_settings_read(line);
    }
    fclose(f);
    if (g_z_ref_h == INT_MIN)
        logi_("settings: autostart=%d ref unset (%s)", g_autostart, settings_path());
    else
        logi_("settings: autostart=%d ref=%d.%02d (%s)", g_autostart, g_z_ref_h / 100,
              g_z_ref_h < 0 ? -g_z_ref_h % 100 : g_z_ref_h % 100, settings_path());
}


static int parse_hund(const char *p, const char **end) {
    int sign = 1;
    if (*p == '+') p++;
    else if (*p == '-') { sign = -1; p++; }
    if (!isdigit((unsigned char)*p) && *p != '.') return INT_MIN;
    int ip = 0, frac = 0, nd = 0;
    while (isdigit((unsigned char)*p)) { ip = ip * 10 + (*p - '0'); p++; }
    if (*p == '.') {
        p++;
        while (isdigit((unsigned char)*p) && nd < 3) {
            frac = frac * 10 + (*p - '0');
            nd++; p++;
        }
        while (isdigit((unsigned char)*p)) p++; /* ignore extra digits */
    }
    if (nd == 0) frac = 0;
    else if (nd == 1) frac *= 10;
    else if (nd == 3) { frac = (frac + 5) / 10; } /* round tenths of a hundredth */
    if (end) *end = p;
    return sign * (ip * 100 + frac);
}

static void hund_fmt(int h, char *b, size_t n) {
    int neg = h < 0, v = neg ? -h : h;
    snprintf(b, n, "%s%d.%02d", neg ? "-" : "", v / 100, v % 100);
}

/* Find first '<letter><number>' in a Marlin settings line. */
static const char *find_param(const char *s, char key) {
    for (; *s; s++) {
        if (*s == key && (s[1] == '-' || s[1] == '+' || s[1] == '.' || isdigit((unsigned char)s[1])))
            return s + 1;
    }
    return NULL;
}


/* Update stored H. A change that is not our own queued save is treated as
   a stock paper-test calibration: the display reference is reset so the
   shown offset returns to 0.00. Our own save leaves the reference alone
   so the displayed offset is unchanged. */
static void zoff_note_stored_h(int v) {
    if (v == INT_MIN) return;
    if (g_z_own_h != INT_MIN && v == g_z_own_h) {
        g_z_height_h = v;
        g_z_own_h = INT_MIN;
        return;
    }
    int first = (g_z_ref_h == INT_MIN);
    int calib = (g_z_height_h != INT_MIN && v != g_z_height_h);
    g_z_height_h = v;
    if (first || calib) {
        g_z_ref_h = v;
        settings_save();
        logi_("zoffset reference %s to %d.%02d", first ? "set" : "reset after calibration",
              v / 100, v < 0 ? -v % 100 : v % 100);
    }
}

static int zoff_effective_h(void);
static int zoff_offset_h(void) {
    int eff = zoff_effective_h();
    if (eff == INT_MIN || g_z_ref_h == INT_MIN) return INT_MIN;
    return g_z_ref_h - eff;
}

static int zoff_set_zero(char *err, size_t en) {
    int eff = zoff_effective_h();
    if (eff == INT_MIN) {
        snprintf(err, en, "stored height is unknown; wait for an M503 report, then retry");
        return 409;
    }
    g_z_ref_h = eff;
    if (settings_save()) {
        snprintf(err, en, "could not persist the new zero");
        return 500;
    }
    snprintf(err, en, "current offset is now 0.00");
    logi_("zoffset reference set to current effective %d.%02d", eff / 100,
          eff < 0 ? -eff % 100 : eff % 100);
    return 0;
}

static void zoff_parse_fw(const char *l) {
    const char *p;
    if ((p = strstr(l, "M665"))) {
        const char *h = find_param(p, 'H');
        if (h) {
            int v = parse_hund(h, NULL);
            if (v != INT_MIN) zoff_note_stored_h(v);
        }
    }
    if ((p = strstr(l, "M851"))) {
        const char *z = find_param(p, 'Z');
        if (z) {
            int v = parse_hund(z, NULL);
            if (v != INT_MIN) g_z_probe_h = v;
        }
    }
}

static void zoff_track_cmd(const char *n) {
    char buf[LINEMAX];
    snprintf(buf, sizeof buf, "%s", n ? n : "");
    char *st = strchr(buf, '*'); if (st) *st = 0;
    const char *c = buf;
    if (c[0] == 'N' && isdigit((unsigned char)c[1])) {
        while (*c && *c != ' ') c++;
        while (*c == ' ') c++;
    }
    int h = 0, rc = parse_m290(c, &h);
    if (rc == 0) {
        /* Ignore the one-shot idle neutralize we queued after a save. */
        if (g_z_skip_baby && h == g_z_skip_baby) g_z_skip_baby = 0;
        else g_z_baby_h += h;
    }
    if (cmd_word(c, "M665")) {
        const char *hh = find_param(c, 'H');
        if (hh) {
            int v = parse_hund(hh, NULL);
            if (v != INT_MIN) zoff_note_stored_h(v);
        }
    }
    /* Home clears firmware babysteps. */
    if (cmd_word(c, "G28")) g_z_baby_h = 0;
    /* A new screen/network start-work also begins a fresh print adjustment. */
    if (cmd_is(c, "M2411 S2")) g_z_baby_h = 0;
}

static int zoff_effective_h(void) {
    if (g_z_height_h == INT_MIN) return INT_MIN;
    return g_z_height_h - g_z_baby_h;
}

static int zoff_idle(void) {
    if (job_active() || AJ.active || cal_busy() || R.st == R_PENDING || g_ser < 0) return 0;
    if (S.working[0] && starts(S.working, "WORKING")) return 0;
    return 1;
}

static int zoff_queue(const char *cmd) {
    if (g_netq_n >= 16) return -1;
    int slot = (g_netq_h + g_netq_n) % 16;
    snprintf(g_netq[slot], 96, "%s", cmd);
    g_netq_quiet[slot] = 1;
    g_netq_n++;
    return 0;
}

static void zoff_json(struct sb *s) {
    char hb[16], pb[16], bb[16], eb[16];
    sb_add(s, "{\"height\":");
    if (g_z_height_h == INT_MIN) sb_add(s, "null");
    else { hund_fmt(g_z_height_h, hb, sizeof hb); sb_add(s, "%s", hb); }
    sb_add(s, ",\"probe\":");
    if (g_z_probe_h == INT_MIN) sb_add(s, "null");
    else { hund_fmt(g_z_probe_h, pb, sizeof pb); sb_add(s, "%s", pb); }
    hund_fmt(g_z_baby_h, bb, sizeof bb);
    sb_add(s, ",\"babystep\":%s", bb);
    int eff = zoff_effective_h();
    sb_add(s, ",\"effective_height\":");
    if (eff == INT_MIN) sb_add(s, "null");
    else { hund_fmt(eff, eb, sizeof eb); sb_add(s, "%s", eb); }
    sb_add(s, ",\"reference\":");
    if (g_z_ref_h == INT_MIN) sb_add(s, "null");
    else { char rb[16]; hund_fmt(g_z_ref_h, rb, sizeof rb); sb_add(s, "%s", rb); }
    int off = zoff_offset_h();
    sb_add(s, ",\"offset\":");
    if (off == INT_MIN) sb_add(s, "null");
    else { char ob[16]; hund_fmt(off, ob, sizeof ob); sb_add(s, "%s", ob); }
    sb_add(s, ",\"pending_save\":%s", g_z_pending ? "true" : "false");
    if (g_z_pending) {
        char ph[16]; hund_fmt(g_z_pending_h, ph, sizeof ph);
        sb_add(s, ",\"pending_height\":%s", ph);
    } else sb_add(s, ",\"pending_height\":null");
    sb_add(s, ",\"idle\":%s", zoff_idle() ? "true" : "false");
    sb_add(s, ",\"last_save\":");
    if (g_z_last[0]) sb_str(s, g_z_last);
    else sb_add(s, "null");
    sb_add(s, "}");
}

static int zoff_queue_save(char *err, size_t en) {
    if (g_z_height_h == INT_MIN) {
        snprintf(err, en, "stored height is unknown; wait for an M503 report, then retry");
        return 409;
    }
    if (!g_z_baby_h && !g_z_pending) {
        snprintf(err, en, "no this-print adjustment to save");
        return 409;
    }
    int nh = g_z_pending ? g_z_pending_h : (g_z_height_h - g_z_baby_h);
    /* Delta height is around 233 mm on this machine; reject wild values. */
    if (nh < 15000 || nh > 30000) {
        snprintf(err, en, "refusing to save height %d.%02d mm (outside 150..300)", nh / 100, nh < 0 ? -nh % 100 : nh % 100);
        return 400;
    }
    g_z_pending_h = nh;
    g_z_pending_baby = g_z_baby_h;
    g_z_pending = 1;
    if (zoff_idle())
        snprintf(err, en, "queued; will apply M665 H + M500 now that the printer is idle");
    else
        snprintf(err, en, "queued; will apply M665 H + M500 when the print ends (M665 is not sent mid-print)");
    logi_("zoffset save queued: H %d.%02d (baby %d) %s", nh / 100, nh % 100, g_z_pending_baby, zoff_idle() ? "idle" : "wait");
    return 0;
}

static void zoff_want_probe(void) {
    long long t = now_ms();
    if (g_z_height_h != INT_MIN) return;
    if (!zoff_idle() || !net_ready() || g_netq_n >= 14) return;
    if (g_z_m503_at && t - g_z_m503_at < 15000) return;
    if (zoff_queue("M503") == 0) g_z_m503_at = t;
}

static void zoff_tick(void) {
    if (!g_z_pending || !zoff_idle() || !net_ready() || g_netq_n + 3 > 16) return;
    char cmd[48], hb[16];
    hund_fmt(g_z_pending_h, hb, sizeof hb);
    snprintf(cmd, sizeof cmd, "M665 H%s", hb);
    if (zoff_queue(cmd) || zoff_queue("M500")) {
        logf_("zoffset save: command queue full");
        return;
    }
    /* After the job, cancel leftover firmware babysteps so they do not stack
       on the new H if the next print does not home. This is a small M290,
       only once the printer is idle — never mid-print. */
    if (g_z_pending_baby) {
        char zb[16], m290[40];
        hund_fmt(-g_z_pending_baby, zb, sizeof zb);
        snprintf(m290, sizeof m290, "M290 Z%s", zb);
        zoff_queue(m290);
        g_z_skip_baby = -g_z_pending_baby;
    }
    snprintf(g_z_last, sizeof g_z_last, "saved H%s (neutralize baby %d)", hb, g_z_pending_baby);
    logi_("zoffset apply: %s then M500%s", cmd, g_z_pending_baby ? " and cancelling M290" : "");
    g_z_own_h = g_z_pending_h;   /* keep displayed offset; do not reset reference */
    g_z_height_h = g_z_pending_h;
    g_z_baby_h = 0;
    g_z_pending = 0;
    g_z_pending_baby = 0;
}
