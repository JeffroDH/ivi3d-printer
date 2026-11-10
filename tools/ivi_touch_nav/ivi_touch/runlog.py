"""Per-run log: log.txt (human), steps.jsonl (machine), one PNG per observed frame."""
import json, os, time


class RunLog:
    def __init__(self, root, name="run", save_png=True, echo=print):
        self.dir = os.path.join(root, time.strftime("%Y%m%d_%H%M%S_") + name)
        os.makedirs(self.dir, exist_ok=True)
        self.n, self.save_png, self.echo = 0, save_png, echo
        self._txt = open(os.path.join(self.dir, "log.txt"), "a")
        self._js = open(os.path.join(self.dir, "steps.jsonl"), "a")

    def event(self, kind, msg, frame=None, **data):
        self.n += 1
        png = None
        if frame is not None and self.save_png:
            png = "%03d_%s.png" % (self.n, kind)
            frame.to_png(os.path.join(self.dir, png))
        line = "%s #%03d %-8s %s%s" % (time.strftime("%H:%M:%S"), self.n, kind, msg, ("  [%s]" % png) if png else "")
        self._txt.write(line + "\n"); self._txt.flush()
        rec = dict(n=self.n, t=time.time(), kind=kind, msg=msg, png=png); rec.update(data)
        self._js.write(json.dumps(rec, default=str) + "\n"); self._js.flush()
        if self.echo:
            self.echo(line)

    def close(self):
        self._txt.close(); self._js.close()
