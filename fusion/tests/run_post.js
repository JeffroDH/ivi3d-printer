// Minimal mock of the Fusion post API: runs a .cps against a synthetic toolpath, prints G-code.
// Usage: node run_post.js ../ivi3d_laser.cps laser|cnc
const fs = require("fs"), vm = require("vm");
const [, , cps, kind] = process.argv;
const lines = [];
const ctx = {
  MM: 0, IN: 1, unit: 0, CAPABILITY_JET: 4, CAPABILITY_MILLING: 1, TYPE_JET: 2, TYPE_MILLING: 0,
  spatial: v => v, toRad: d => d * Math.PI / 180, setCodePage() {}, writeln: s => lines.push(s),
  error: m => { throw new Error(m); }, warning() {}, Math,
  createFormat: o => ({ format: v => o.forceDecimal ? Number(v).toFixed(o.decimals) : String(Math.round(v)) }),
  linearize() {}, tolerance: 0.01,
  currentSection: { getType: () => kind === "laser" ? 2 : 0, getInitialPosition: () => ({ x: -20, y: -15, z: 5 }) },
};
ctx.getProperty = k => ctx.properties[k].value;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(cps, "utf8"), ctx);
const sq = [[-20, -15], [20, -15], [20, 15], [-20, 15], [-20, -15]];
ctx.onOpen(); ctx.onSection();
if (kind === "laser") {
  for (const pass of [0, 1]) {
    ctx.onPower(false); ctx.onRapid(sq[0][0] + pass, sq[0][1] + pass, 0);
    ctx.onPower(true);
    for (const [x, y] of sq.slice(1)) ctx.onLinear(x + pass, y + pass, 0, 600);
  }
  ctx.onPower(false);
} else {
  for (const z of [-0.4, -0.8]) {
    ctx.onRapid(-20, -15, 5); ctx.onLinear(-20, -15, z, 1000);
    for (const [x, y] of sq.slice(1)) ctx.onLinear(x, y, z, 300);
    ctx.onRapid(-20, -15, 5);
  }
}
ctx.onSectionEnd(); ctx.onClose();
process.stdout.write(lines.join("\n") + "\n");
