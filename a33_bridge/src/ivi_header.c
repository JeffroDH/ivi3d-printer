/* IVI 3licer ';Header Start' block, ported from bridge/ivi_bridge.py
 * (scan_gcode / build_ivi_header / has_ivi_header / prepare_gcode).
 * Streamed in two passes; no full-file buffer. No command stripping (DEFAULT_STRIP is empty).
 */
#ifndef IVI_HEADER_C
#define IVI_HEADER_C

#define IVI_LOOK 4096
#define IVI_HEAD_MAX 100
#define IVI_HEAD_ARENA (64 * 1024)
#define IVI_LINEMAX 8192
#define IVI_NOZZLE_DEF 0.3

struct ivi_st {
    long lines, valid;
    int nhead;
    const char *head[IVI_HEAD_MAX];
    char arena[IVI_HEAD_ARENA];
    size_t arena_used;
    off_t head_bytes;
    int has_time, time_s, has_m73, m73_s;
    char filament_type[128];
    char nozzle_temperature[64];
    char hot_plate_temp[64];
    char bed_temperature[64];
    char sparse_infill_speed[64];
    char max_z_height[64];
    char nozzle_diameter[64];
    char filament_used_mm[256];
    char filament_used_g[256];
    char total_filament_used_g[256];
    int got_filament_type, got_nozzle_temperature, got_hot_plate_temp, got_bed_temperature;
    int got_sparse_infill_speed, got_max_z_height, got_nozzle_diameter;
    int got_filament_used_mm, got_filament_used_g, got_total_filament_used_g;
    double mn[3], mx[3], pos[3], e;
    int has_mn[3], has_mx[3], rel, rel_e;
};

static int ivi_has_header_fd(int fd, off_t off, off_t len) {
    unsigned char b[IVI_LOOK];
    size_t n = (len > IVI_LOOK) ? IVI_LOOK : (size_t)((len < 0) ? 0 : len);
    if (!n) return 0;
    if (lseek(fd, off, SEEK_SET) != off) return -1;
    ssize_t r = read(fd, b, n);
    if (r <= 0) return 0;
    return memmem(b, (size_t)r, ";Header Start", 13) != NULL;
}

/* Python 3 int(round(x)) for non-negative durations; half away from zero is not used (banker's). */
static int ivi_round_int(double x) {
    int neg = 0;
    if (x < 0) { neg = 1; x = -x; }
    long i = (long)x;
    double frac = x - (double)i;
    long r;
    if (frac > 0.5) r = i + 1;
    else if (frac < 0.5) r = i;
    else r = (i & 1) ? i + 1 : i;
    return (int)(neg ? -r : r);
}

/* '5h 58m 3s' / '1d 2h 3m' -> seconds, or -1 if none (Python parse_duration). */
static int ivi_parse_duration(const char *s) {
    double tot = 0; int hit = 0;
    const char *p = s;
    while (*p) {
        if (!((*p >= '0' && *p <= '9') || *p == '.')) { p++; continue; }
        /* try to match (\d+(?:\.\d+)?)\s*([dhms]) at this position */
        if (!(*p >= '0' && *p <= '9')) { p++; continue; }
        const char *start = p;
        while (*p >= '0' && *p <= '9') p++;
        if (*p == '.') {
            const char *d = p + 1;
            if (*d >= '0' && *d <= '9') {
                p++;
                while (*p >= '0' && *p <= '9') p++;
            }
        }
        const char *u = p;
        while (*u == ' ' || *u == '\t') u++;
        if (*u == 'd' || *u == 'h' || *u == 'm' || *u == 's') {
            char tmp[64]; size_t n = (size_t)(p - start);
            if (n >= sizeof tmp) n = sizeof tmp - 1;
            memcpy(tmp, start, n); tmp[n] = 0;
            double v = strtod(tmp, NULL);
            tot += v * (*u == 'd' ? 86400.0 : *u == 'h' ? 3600.0 : *u == 'm' ? 60.0 : 1.0);
            hit = 1;
            p = u + 1;
        } else {
            /* not a match; advance one character from start so we don't loop */
            p = start + 1;
        }
    }
    return hit ? ivi_round_int(tot) : -1;
}

static void ivi_first(const char *v, char *out, size_t n) {
    if (!v) { if (n) out[0] = 0; return; }
    const char *c = strchr(v, ',');
    const char *sc = strchr(v, ';');
    const char *end = v + strlen(v);
    if (c && c < end) end = c;
    if (sc && sc < end) end = sc;
    while (v < end && isspace((unsigned char)*v)) v++;
    while (end > v && isspace((unsigned char)end[-1])) end--;
    size_t l = (size_t)(end - v);
    if (l >= n) l = n ? n - 1 : 0;
    if (n) { memcpy(out, v, l); out[l] = 0; }
}

/* _num: int if integral, else float. Returns 0 if unparseable (None). */
static int ivi_num(const char *v, int *is_int, long *iv, double *fv) {
    char tmp[128];
    ivi_first(v, tmp, sizeof tmp);
    if (!tmp[0]) return 0;
    char *end = NULL;
    errno = 0;
    double f = strtod(tmp, &end);
    if (end == tmp) return 0;
    while (*end && isspace((unsigned char)*end)) end++;
    if (*end) return 0;
    if (f == (double)(long)f && f >= (double)LONG_MIN && f <= (double)LONG_MAX) {
        *is_int = 1; *iv = (long)f; return 1;
    }
    *is_int = 0; *fv = f; return 1;
}

/* Python 3 "%g" % float (default precision 6). */
static void ivi_py_g(char *dst, size_t n, double v) {
    if (!n) return;
    if (v != v) { snprintf(dst, n, "nan"); return; }
    char buf[96];
    snprintf(buf, sizeof buf, "%.6g", v);
    /* Some libcs emit 3-digit exponents (e+006); Python uses at least 2, no extra leading zeros beyond 2. */
    char *e = strchr(buf, 'e');
    if (!e) e = strchr(buf, 'E');
    if (e && (e[1] == '+' || e[1] == '-')) {
        char sign = e[1];
        char *d = e + 2;
        while (*d == '0' && d[1]) d++;
        /* ensure at least 2 digits if the value is a single digit? Python 3 %g: '1e-05', '1e+06', '1e+10' */
        char num[16];
        snprintf(num, sizeof num, "%s", d);
        if (strlen(num) < 2) {
            char z[16];
            snprintf(z, sizeof z, "0%s", num);
            snprintf(e, (size_t)(buf + sizeof buf - e), "e%c%s", sign, z);
        } else {
            snprintf(e, (size_t)(buf + sizeof buf - e), "e%c%s", sign, num);
        }
    }
    snprintf(dst, n, "%s", buf);
}

static void ivi_fmt(char *dst, size_t n, int is_int, long iv, double fv) {
    if (is_int) snprintf(dst, n, "%ld", iv);
    else ivi_py_g(dst, n, fv);
}

static int ivi_is_generated(const char *line) {
    if (*line != ';') return 0;
    const char *p = line + 1;
    while (*p == ' ' || *p == '\t') p++;
    return strncasecmp(p, "generated", 9) == 0;
}

static int ivi_is_comment(const char *line) { return line[0] == ';'; }

/* ^;\s*KEY\s*[=:]\s*(.*)$  on a stripped line. */
static int ivi_set_match(const char *line, const char *key, char *val, size_t vn) {
    if (*line != ';') return 0;
    const char *p = line + 1;
    while (*p == ' ' || *p == '\t') p++;
    size_t kl = strlen(key);
    if (strncmp(p, key, kl) != 0) return 0;
    p += kl;
    while (*p == ' ' || *p == '\t') p++;
    if (*p != '=' && *p != ':') return 0;
    p++;
    while (*p == ' ' || *p == '\t') p++;
    /* rest of line, then strip trailing */
    size_t l = strlen(p);
    while (l && isspace((unsigned char)p[l - 1])) l--;
    if (l >= vn) l = vn ? vn - 1 : 0;
    if (vn) { memcpy(val, p, l); val[l] = 0; }
    return 1;
}

static int ivi_m73(const char *s, int *out) {
    /* ^M73\s+P0\s+R(\d+)  case-insensitive */
    const char *p = s;
    if (strncasecmp(p, "M73", 3) != 0) return 0;
    p += 3;
    if (!isspace((unsigned char)*p)) return 0;
    while (isspace((unsigned char)*p)) p++;
    if (strncasecmp(p, "P0", 2) != 0) return 0;
    p += 2;
    if (*p >= '0' && *p <= '9') return 0; /* P0 must not be a prefix of P01 etc? P0 then \s+ */
    if (!isspace((unsigned char)*p)) return 0;
    while (isspace((unsigned char)*p)) p++;
    if (*p != 'R' && *p != 'r') return 0;
    p++;
    if (!(*p >= '0' && *p <= '9')) return 0;
    long v = 0;
    while (*p >= '0' && *p <= '9') { v = v * 10 + (*p - '0'); p++; }
    *out = (int)v * 60;
    return 1;
}

/* [XYZEF](-?\d*\.?\d+) starting at s; returns next search point or NULL. */
static const char *ivi_ax(const char *s, char *axis, double *val) {
    for (; *s; s++) {
        char k = *s;
        if (k != 'X' && k != 'Y' && k != 'Z' && k != 'E' && k != 'F') continue;
        const char *p = s + 1;
        const char *num = p;
        if (*p == '-') p++;
        int idig = 0;
        while (*p >= '0' && *p <= '9') { p++; idig = 1; }
        if (*p == '.') {
            const char *ad = p + 1;
            if (*ad >= '0' && *ad <= '9') {
                p++;
                while (*p >= '0' && *p <= '9') p++;
            } else if (!idig) {
                continue;
            } else {
                /* match only the integer part, leave the dot */
                p = num;
                if (*p == '-') p++;
                while (*p >= '0' && *p <= '9') p++;
            }
        } else if (!idig) {
            continue;
        }
        char tmp[64];
        size_t l = (size_t)(p - num);
        if (!l) continue;
        if (l >= sizeof tmp) l = sizeof tmp - 1;
        memcpy(tmp, num, l); tmp[l] = 0;
        *axis = k;
        *val = strtod(tmp, NULL);
        return p;
    }
    return NULL;
}

static int ivi_is_g0g1(const char *c) {
    return !strncmp(c, "G0 ", 3) || !strncmp(c, "G1 ", 3) || !strcmp(c, "G0") || !strcmp(c, "G1")
        || !strncmp(c, "G0X", 3) || !strncmp(c, "G0Y", 3) || !strncmp(c, "G0Z", 3)
        || !strncmp(c, "G1X", 3) || !strncmp(c, "G1Y", 3) || !strncmp(c, "G1Z", 3) || !strncmp(c, "G1E", 3);
}

static int ivi_store(char *dst, size_t n, int *got, const char *v) {
    if (*got) return 0;
    snprintf(dst, n, "%s", v);
    *got = 1;
    return 1;
}

static int ivi_take_set(struct ivi_st *st, const char *line) {
    char v[256];
    if (ivi_set_match(line, "filament_type", v, sizeof v))
        return ivi_store(st->filament_type, sizeof st->filament_type, &st->got_filament_type, v);
    if (ivi_set_match(line, "nozzle_temperature", v, sizeof v))
        return ivi_store(st->nozzle_temperature, sizeof st->nozzle_temperature, &st->got_nozzle_temperature, v);
    if (ivi_set_match(line, "hot_plate_temp", v, sizeof v))
        return ivi_store(st->hot_plate_temp, sizeof st->hot_plate_temp, &st->got_hot_plate_temp, v);
    if (ivi_set_match(line, "bed_temperature", v, sizeof v))
        return ivi_store(st->bed_temperature, sizeof st->bed_temperature, &st->got_bed_temperature, v);
    if (ivi_set_match(line, "sparse_infill_speed", v, sizeof v))
        return ivi_store(st->sparse_infill_speed, sizeof st->sparse_infill_speed, &st->got_sparse_infill_speed, v);
    if (ivi_set_match(line, "max_z_height", v, sizeof v))
        return ivi_store(st->max_z_height, sizeof st->max_z_height, &st->got_max_z_height, v);
    if (ivi_set_match(line, "nozzle_diameter", v, sizeof v))
        return ivi_store(st->nozzle_diameter, sizeof st->nozzle_diameter, &st->got_nozzle_diameter, v);
    if (ivi_set_match(line, "filament used [mm]", v, sizeof v))
        return ivi_store(st->filament_used_mm, sizeof st->filament_used_mm, &st->got_filament_used_mm, v);
    if (ivi_set_match(line, "filament used [g]", v, sizeof v))
        return ivi_store(st->filament_used_g, sizeof st->filament_used_g, &st->got_filament_used_g, v);
    if (ivi_set_match(line, "total filament used [g]", v, sizeof v))
        return ivi_store(st->total_filament_used_g, sizeof st->total_filament_used_g, &st->got_total_filament_used_g, v);
    return 0;
}

/* Byte-at-a-time line reads are too slow for large files. Use a buffered reader. */
struct ivi_rdr {
    int fd;
    off_t pos, end;
    char buf[65536];
    size_t bn, bi;
    int eof, err;
};

static int ivi_rdr_fill(struct ivi_rdr *r) {
    if (r->eof || r->err) return -1;
    if (r->pos >= r->end) { r->eof = 1; return -1; }
    size_t want = sizeof r->buf;
    if ((off_t)want > r->end - r->pos) want = (size_t)(r->end - r->pos);
    if (lseek(r->fd, r->pos, SEEK_SET) != r->pos) { r->err = 1; return -1; }
    ssize_t n = read(r->fd, r->buf, want);
    if (n < 0) { r->err = 1; return -1; }
    if (n == 0) { r->eof = 1; return -1; }
    r->pos += n;
    r->bn = (size_t)n;
    r->bi = 0;
    return 0;
}

static int ivi_rdr_line(struct ivi_rdr *r, char *raw, size_t rawcap, size_t *raw_n) {
    if (r->err) return -1;
    size_t n = 0;
    int saw_nl = 0;
    for (;;) {
        if (r->bi >= r->bn) {
            if (ivi_rdr_fill(r) < 0) break;
        }
        char ch = r->buf[r->bi++];
        if (n + 1 < rawcap) raw[n++] = ch;
        else {
            /* overflow: keep consuming until newline, don't store */
        }
        if (ch == '\n') { saw_nl = 1; break; }
    }
    if (r->err) return -1;
    if (n == 0 && (r->eof || r->pos >= r->end) && r->bi >= r->bn) return 0;
    raw[n < rawcap ? n : rawcap - 1] = 0;
    *raw_n = n < rawcap ? n : rawcap - 1;
    (void)saw_nl;
    return 1;
}

static void ivi_strip_copy(const char *raw, size_t raw_n, char *line, size_t lcap) {
    /* equivalent of raw.strip() for matching; raw may include \r\n */
    size_t a = 0, b = raw_n;
    while (a < b && isspace((unsigned char)raw[a])) a++;
    while (b > a && isspace((unsigned char)raw[b - 1])) b--;
    size_t l = b - a;
    if (l >= lcap) l = lcap - 1;
    memcpy(line, raw + a, l);
    line[l] = 0;
}

static void ivi_rstrip_nl(const char *raw, size_t raw_n, char *out, size_t ocap) {
    /* raw.rstrip("\r\n") */
    size_t b = raw_n;
    while (b && (raw[b - 1] == '\n' || raw[b - 1] == '\r')) b--;
    if (b >= ocap) b = ocap - 1;
    memcpy(out, raw, b);
    out[b] = 0;
}

static int ivi_scan(struct ivi_rdr *r, struct ivi_st *st) {
    memset(st, 0, sizeof *st);
    st->time_s = -1;
    st->m73_s = -1;
    int head_done = 0, keep_head = 1;
    char raw[IVI_LINEMAX], line[IVI_LINEMAX];
    size_t raw_n;
    int rc;
    while ((rc = ivi_rdr_line(r, raw, sizeof raw, &raw_n)) > 0) {
        st->lines++;
        ivi_strip_copy(raw, raw_n, line, sizeof line);
        if (!head_done) {
            if (ivi_is_comment(line) && !ivi_is_generated(line) && st->nhead < IVI_HEAD_MAX) {
                char stored[IVI_LINEMAX];
                ivi_rstrip_nl(raw, raw_n, stored, sizeof stored);
                size_t sl = strlen(stored) + 1;
                if (st->arena_used + sl <= sizeof st->arena && st->nhead < IVI_HEAD_MAX) {
                    char *p = st->arena + st->arena_used;
                    memcpy(p, stored, sl);
                    st->arena_used += sl;
                    st->head[st->nhead++] = p;
                    st->head_bytes += (off_t)raw_n;
                    /* If the stored line was truncated vs raw_n, head_bytes still uses raw_n (file bytes). */
                } else {
                    /* arena full: still count as a head line for skip, even if text is dropped (rare). */
                    st->head[st->nhead++] = "";
                    st->head_bytes += (off_t)raw_n;
                }
                continue;
            }
            head_done = 1;
            if (!ivi_is_generated(line)) {
                st->nhead = 0;
                st->head_bytes = 0;
                st->arena_used = 0;
                keep_head = 0;
            }
            (void)keep_head;
        }
        if (!line[0]) continue;
        if (line[0] == ';') {
            /* time */
            {
                const char *p = line + 1;
                while (*p == ' ' || *p == '\t') p++;
                const char *pref = "estimated printing time (normal mode)";
                size_t pl = strlen(pref);
                if (!strncmp(p, pref, pl)) {
                    p += pl;
                    while (*p == ' ' || *p == '\t') p++;
                    if (*p == '=') {
                        p++;
                        while (*p == ' ' || *p == '\t') p++;
                        int t = ivi_parse_duration(p);
                        if (t >= 0) { st->has_time = 1; st->time_s = t; }
                    }
                    continue;
                }
            }
            ivi_take_set(st, line);
            continue;
        }
        st->valid++;
        /* c = line.split(";", 1)[0].upper() */
        char c[IVI_LINEMAX];
        const char *semi = strchr(line, ';');
        size_t cl = semi ? (size_t)(semi - line) : strlen(line);
        if (cl >= sizeof c) cl = sizeof c - 1;
        memcpy(c, line, cl); c[cl] = 0;
        for (char *q = c; *q; q++) *q = (char)toupper((unsigned char)*q);
        if (ivi_is_g0g1(c)) {
            double newp[3] = { st->pos[0], st->pos[1], st->pos[2] };
            int ext = 0;
            const char *s = c + 2;
            char ax; double v;
            while ((s = ivi_ax(s, &ax, &v)) != NULL) {
                if (ax == 'E') {
                    ext = st->rel_e ? (v > 0) : (v > st->e);
                    st->e = st->rel_e ? (st->e + v) : v;
                } else if (ax != 'F') {
                    int i = (ax == 'X') ? 0 : (ax == 'Y') ? 1 : 2;
                    newp[i] = st->rel ? (st->pos[i] + v) : v;
                }
            }
            if (ext) {
                double *ps[2] = { st->pos, newp };
                for (int k = 0; k < 2; k++) {
                    for (int i = 0; i < 3; i++) {
                        if (!st->has_mn[i] || ps[k][i] < st->mn[i]) { st->mn[i] = ps[k][i]; st->has_mn[i] = 1; }
                        if (!st->has_mx[i] || ps[k][i] > st->mx[i]) { st->mx[i] = ps[k][i]; st->has_mx[i] = 1; }
                    }
                }
            }
            st->pos[0] = newp[0]; st->pos[1] = newp[1]; st->pos[2] = newp[2];
        } else if (!strncmp(c, "G91", 3)) {
            st->rel = st->rel_e = 1;
        } else if (!strncmp(c, "G90", 3)) {
            st->rel = st->rel_e = 0;
        } else if (!strncmp(c, "M83", 3)) {
            st->rel_e = 1;
        } else if (!strncmp(c, "M82", 3)) {
            st->rel_e = 0;
        } else if (!strncmp(c, "G92", 3)) {
            const char *s = c + 3;
            char ax; double v;
            while ((s = ivi_ax(s, &ax, &v)) != NULL) {
                if (ax == 'E') st->e = v;
                else if (ax == 'X' || ax == 'Y' || ax == 'Z')
                    st->pos[ax == 'X' ? 0 : ax == 'Y' ? 1 : 2] = v;
            }
        } else if (!st->has_m73) {
            int m;
            if (ivi_m73(c, &m)) { st->has_m73 = 1; st->m73_s = m; }
        }
    }
    return r->err ? -1 : 0;
}

static int ivi_sum_csv(const char *s, double *out) {
    double tot = 0;
    const char *p = s;
    while (*p) {
        const char *comma = strchr(p, ',');
        size_t n = comma ? (size_t)(comma - p) : strlen(p);
        char tmp[256];
        if (n >= sizeof tmp) n = sizeof tmp - 1;
        memcpy(tmp, p, n); tmp[n] = 0;
        char *t = tmp;
        while (*t && isspace((unsigned char)*t)) t++;
        char *e = t + strlen(t);
        while (e > t && isspace((unsigned char)e[-1])) *--e = 0;
        if (*t) {
            char *end = NULL;
            errno = 0;
            double v = strtod(t, &end);
            if (end == t) return -1;
            while (*end && isspace((unsigned char)*end)) end++;
            if (*end) return -1;
            tot += v;
        }
        p = comma ? comma + 1 : p + strlen(p);
    }
    *out = tot;
    return 0;
}

static int ivi_write_all(int fd, const char *b, size_t n) {
    while (n) {
        ssize_t w = write(fd, b, n);
        if (w > 0) { b += w; n -= (size_t)w; continue; }
        if (w < 0 && errno != EINTR) return -1;
    }
    return 0;
}

static int ivi_put(int fd, const char *s) { return ivi_write_all(fd, s, strlen(s)); }
static int ivi_putln(int fd, const char *s) {
    if (ivi_put(fd, s)) return -1;
    return ivi_write_all(fd, "\n", 1);
}

static int ivi_build_header(int fd, const struct ivi_st *st, double nozzle, const char *date) {
    char line[512], fb[64], nzbuf[64];
    int is_int; long iv; double fv;
    double nz = nozzle;
    if (st->got_nozzle_diameter) {
        if (ivi_num(st->nozzle_diameter, &is_int, &iv, &fv)) {
            if (is_int) nz = (double)iv; else nz = fv;
            ivi_fmt(nzbuf, sizeof nzbuf, is_int, iv, fv);
        } else {
            snprintf(nzbuf, sizeof nzbuf, "None"); /* _num failed; _fmt(None) */
        }
    } else {
        /* default nozzle is a float argument */
        ivi_py_g(nzbuf, sizeof nzbuf, nz);
    }

    int t = st->has_time ? st->time_s : (st->has_m73 ? st->m73_s : 0);
    const char *bed = st->got_hot_plate_temp ? st->hot_plate_temp
                    : (st->got_bed_temperature ? st->bed_temperature : "0");

    int spd_int = 1; long spd_i = 0; double spd_f = 0;
    if (st->got_sparse_infill_speed) {
        if (!ivi_num(st->sparse_infill_speed, &spd_int, &spd_i, &spd_f)) { spd_int = 1; spd_i = 0; }
    }
    /* `_num(...) or 0` */
    if (spd_int && spd_i == 0 && !st->got_sparse_infill_speed) { spd_int = 1; spd_i = 0; }
    else if (!spd_int && spd_f == 0.0) { spd_int = 1; spd_i = 0; }
    else if (spd_int && spd_i == 0) { /* keep 0 */ }

    double mn[3], mx[3];
    for (int i = 0; i < 3; i++) {
        mn[i] = st->has_mn[i] ? st->mn[i] : 0.0;
        mx[i] = st->has_mx[i] ? st->mx[i] : 0.0;
    }
    if (!st->has_mx[2] && st->got_max_z_height) {
        int zi; long ziv; double zfv;
        if (ivi_num(st->max_z_height, &zi, &ziv, &zfv)) mx[2] = zi ? (double)ziv : zfv;
        else mx[2] = 0.0;
    }

    if (ivi_putln(fd, ";Header Start")) return -1;
    if (ivi_putln(fd, "")) return -1;
    for (int i = 0; i < st->nhead; i++) if (ivi_putln(fd, st->head[i] ? st->head[i] : "")) return -1;
    if (ivi_putln(fd, "")) return -1;
    snprintf(line, sizeof line, ";header_type: 3dp,%smm", nzbuf);
    if (ivi_putln(fd, line)) return -1;
    snprintf(line, sizeof line, ";file_total_lines: %ld", st->lines + 20);
    if (ivi_putln(fd, line)) return -1;
    snprintf(line, sizeof line, ";file_valid_lines: %ld", st->valid);
    if (ivi_putln(fd, line)) return -1;
    snprintf(line, sizeof line, ";estimated_time(s): %d", t);
    if (ivi_putln(fd, line)) return -1;

    if (st->got_filament_used_mm) {
        double mm;
        if (ivi_sum_csv(st->filament_used_mm, &mm) < 0) return -1;
        snprintf(line, sizeof line, ";filament_used(m): %.2f", mm / 1000.0);
        if (ivi_putln(fd, line)) return -1;
    }
    const char *g = st->got_filament_used_g ? st->filament_used_g
                  : (st->got_total_filament_used_g ? st->total_filament_used_g : NULL);
    if (g) {
        double grams;
        if (ivi_sum_csv(g, &grams) < 0) return -1;
        snprintf(line, sizeof line, ";filament_weight(g): %.2f", grams);
        if (ivi_putln(fd, line)) return -1;
    }

    char mat[128];
    if (st->got_filament_type) ivi_first(st->filament_type, mat, sizeof mat);
    else mat[0] = 0;
    if (!mat[0]) snprintf(mat, sizeof mat, "PLA");
    snprintf(line, sizeof line, ";material_type: %s", mat);
    if (ivi_putln(fd, line)) return -1;

    /* nozzle temp */
    {
        int ok = ivi_num(st->got_nozzle_temperature ? st->nozzle_temperature : "0", &is_int, &iv, &fv);
        if (!ok || (is_int && iv == 0 && !fv) ) {
            /* `_num(...) or 0` — 0 is used if None or 0 */
        }
        if (!ok) { is_int = 1; iv = 0; }
        else if (is_int && iv == 0) { /* 0 is falsy, still 0 */ }
        else if (!is_int && fv == 0.0) { is_int = 1; iv = 0; }
        ivi_fmt(fb, sizeof fb, is_int, iv, fv);
        if (!ok) snprintf(fb, sizeof fb, "0");
        snprintf(line, sizeof line, ";nozzle_temperature(\xC2\xB0""C): %s", fb);
        if (ivi_putln(fd, line)) return -1;
    }
    {
        int ok = ivi_num(bed, &is_int, &iv, &fv);
        if (!ok) { is_int = 1; iv = 0; }
        else if (!is_int && fv == 0.0) { is_int = 1; iv = 0; }
        ivi_fmt(fb, sizeof fb, is_int, iv, fv);
        if (!ok) snprintf(fb, sizeof fb, "0");
        snprintf(line, sizeof line, ";build_plate_temperature(\xC2\xB0""C): %s", fb);
        if (ivi_putln(fd, line)) return -1;
    }
    /* work_speed: _fmt(spd * 60) */
    {
        if (spd_int) {
            snprintf(fb, sizeof fb, "%ld", spd_i * 60);
        } else {
            ivi_py_g(fb, sizeof fb, spd_f * 60.0);
        }
        /* `_num(...) or 0` already applied */
        snprintf(line, sizeof line, ";work_speed(mm/minute): %s", fb);
        if (ivi_putln(fd, line)) return -1;
    }
    static const char *axes = "xyz";
    for (int k = 0; k < 2; k++) {
        const double *arr = (k == 0) ? mx : mn;
        const char *name = (k == 0) ? "max" : "min";
        for (int i = 0; i < 3; i++) {
            snprintf(line, sizeof line, ";%s_%c(mm): %.2f", name, axes[i], arr[i]);
            if (ivi_putln(fd, line)) return -1;
        }
    }
    if (ivi_putln(fd, "")) return -1;
    if (ivi_putln(fd, ";Header End")) return -1;
    if (ivi_putln(fd, "")) return -1;
    if (ivi_putln(fd, ";G-code for 3dp engraving")) return -1;
    if (ivi_putln(fd, ";Generated by IVI 3licer")) return -1;
    char dbuf[64];
    const char *d = date;
    if (!d || !d[0]) {
        time_t now = time(NULL);
        struct tm tm;
        localtime_r(&now, &tm);
        strftime(dbuf, sizeof dbuf, "%Y-%m-%d %H:%M:%S", &tm);
        d = dbuf;
    }
    snprintf(line, sizeof line, ";%s", d);
    if (ivi_putln(fd, line)) return -1;
    if (ivi_putln(fd, "")) return -1;
    /* Python join ends with the last empty strings producing a trailing extra \n already
     * from [date, "", ""] -> date\n\n  (no third newline). putln("") after date writes date's
     * newline (from previous putln of date) plus another blank line's newline — that's date\n \n,
     * which is correct. We must NOT add a further blank. */
    return 0;
}

static int ivi_copy_range(int in, off_t off, off_t len, int out) {
    char buf[65536];
    if (lseek(in, off, SEEK_SET) != off) return -1;
    while (len > 0) {
        size_t n = (len > (off_t)sizeof buf) ? sizeof buf : (size_t)len;
        ssize_t r = read(in, buf, n);
        if (r < 0) return -1;
        if (r == 0) break;
        if (ivi_write_all(out, buf, (size_t)r)) return -1;
        len -= r;
    }
    return 0;
}

/* Prepare G-code from src[off, off+len) into dst path.
 * Returns 1 if a header was added, 0 if copied as-is (already had a header), -1 on error.
 * On error dest may be partial; caller should unlink. date may be NULL (local now). */
static int ivi_prepare_gcode(int srcfd, off_t off, off_t len, const char *dst, double nozzle, const char *date) {
    int has = ivi_has_header_fd(srcfd, off, len);
    if (has < 0) return -1;
    int out = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out < 0) return -1;
    if (has) {
        int rc = ivi_copy_range(srcfd, off, len, out);
        fsync(out); close(out);
        return rc ? -1 : 0;
    }
    struct ivi_st *st = calloc(1, sizeof *st);
    if (!st) { close(out); return -1; }
    struct ivi_rdr r = {0};
    r.fd = srcfd; r.pos = off; r.end = off + len;
    if (ivi_scan(&r, st)) { free(st); close(out); return -1; }
    if (ivi_build_header(out, st, nozzle, date)) { free(st); close(out); return -1; }
    off_t body = off + st->head_bytes;
    off_t rest = (off + len) - body;
    if (rest < 0) rest = 0;
    free(st);
    if (ivi_copy_range(srcfd, body, rest, out)) { close(out); return -1; }
    fsync(out); close(out);
    return 1;
}

static int ivi_prepare_path(const char *src, const char *dst, double nozzle, const char *date) {
    int fd = open(src, O_RDONLY);
    if (fd < 0) return -1;
    struct stat st;
    if (fstat(fd, &st)) { close(fd); return -1; }
    int rc = ivi_prepare_gcode(fd, 0, st.st_size, dst, nozzle, date);
    close(fd);
    return rc;
}

/* CLI: ivibridge --add-header IN OUT [--nozzle 0.3] [--date "YYYY-MM-DD HH:MM:SS"]
 * Exit 0 on success (prints "added" or "exists" on stderr). */
static int ivi_add_header_main(int argc, char **argv) {
    const char *src = NULL, *dst = NULL, *date = NULL;
    double nozzle = IVI_NOZZLE_DEF;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--nozzle") && i + 1 < argc) { nozzle = strtod(argv[++i], NULL); continue; }
        if (!strcmp(argv[i], "--date") && i + 1 < argc) { date = argv[++i]; continue; }
        if (!src) { src = argv[i]; continue; }
        if (!dst) { dst = argv[i]; continue; }
        fprintf(stderr, "usage: ivibridge --add-header IN OUT [--nozzle 0.3] [--date YYYY-MM-DD HH:MM:SS]\n");
        return 2;
    }
    if (!src || !dst) {
        fprintf(stderr, "usage: ivibridge --add-header IN OUT [--nozzle 0.3] [--date YYYY-MM-DD HH:MM:SS]\n");
        return 2;
    }
    int rc = ivi_prepare_path(src, dst, nozzle, date);
    if (rc < 0) { fprintf(stderr, "add-header failed: %s\n", strerror(errno)); return 1; }
    fprintf(stderr, "%s\n", rc ? "added" : "exists");
    return 0;
}

#endif
