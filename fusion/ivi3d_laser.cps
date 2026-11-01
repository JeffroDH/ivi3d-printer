/**
  IVI3D laser post processor for Autodesk Fusion (CC BY-NC-SA 4.0, JeffroDH/ivi3d-printer).
  Emits IVI 3licer 1.6.2 "line" (vector) laser G-code, modelled on its line-mode output:
    M106 P0          at start  (fan / air assist, NOT the laser)
    G0 F<jog> / G1 F<work>
    M3 S<power %>    laser on (first time; later a bare M3 reuses the last S)
    G1 ...           burn segment
    M5               laser off after each segment, before every G0
    M107 P0          at end (fan off)
  UNVERIFIED on hardware. Point mode (G4 P<dwell> L) is deliberately not emitted: IVI 3licer's
  point mode writes a bogus dwell (P896745231). See docs/laser_cnc_gcode.md.
  Origin: put the setup WCS at the CENTRE of the work area / stock (IVI jobs are centre-origin).
*/
description = "IVI3D Laser (line mode)";
vendor = "IVI3D (community)";
vendorUrl = "https://github.com/JeffroDH/ivi3d-printer";
legal = "CC BY-NC-SA 4.0";
certificationLevel = 2;
minimumRevision = 45702;
longDescription = "Laser post for the IVI3D printer laser head. Output matches IVI 3licer line mode: M3 S<power%> / M5 per segment, M106/M107 P0 fan. Unverified on hardware.";
extension = "nc";
setCodePage("ascii");
capabilities = CAPABILITY_JET;
tolerance = spatial(0.01, MM);
minimumChordLength = spatial(0.25, MM);
minimumCircularRadius = spatial(0.01, MM);
maximumCircularRadius = spatial(1000, MM);
minimumCircularSweep = toRad(0.01);
maximumCircularSweep = toRad(180);
allowHelicalMoves = false;
allowedCircularPlanes = 0; // no arcs: the IVI files only contain G0/G1, so arcs are linearized

properties = {
  powerPercent: {title: "Laser power (%)", description: "Written as M3 S<percent> (IVI 3licer convention, S = %).", type: "integer", value: 100, scope: "post"},
  airAssist:    {title: "Fan / air assist (M106 P0)", description: "Emit M106 P0 at start and M107 P0 at end, like IVI 3licer.", type: "boolean", value: true, scope: "post"},
  jogSpeed:     {title: "Jog speed (mm/min)", description: "G0 F value (IVI 3licer default 1500).", type: "number", value: 1500, scope: "post"},
  workSpeed:    {title: "Work speed (mm/min)", description: "Default G1 F if the operation has no cutting feed (IVI 3licer default 500).", type: "number", value: 500, scope: "post"}
};

var WORK = 500, JOG = 1500, POWER = 100, lastS = null;
// ---- shared IVI3D post core (pasted into both .cps files by build.py; edit here) ----
var xyzFormat = createFormat({decimals: 2, forceDecimal: true});
var fFormat = createFormat({decimals: 0});
var body = [];                       // buffered so the header can carry bounds/line counts
var st = {x: null, y: null, z: null, f: null, minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity,
          time: 0, on: false};

function out(s) { body.push(s); }
function fmtNum(v) { return xyzFormat.format(v); }

function trackXY(x, y, feed) {
  var px = st.x === null ? x : st.x, py = st.y === null ? y : st.y, pz = st.z === null ? 0 : st.z;
  var d = Math.sqrt((x - px) * (x - px) + (y - py) * (y - py));
  if (feed > 0) { st.time += d / feed * 60; }
  if (x < st.minX) { st.minX = x; } if (x > st.maxX) { st.maxX = x; }
  if (y < st.minY) { st.minY = y; } if (y > st.maxY) { st.maxY = y; }
}

function move(code, x, y, z, feed) {
  var w = [code];
  var nx0 = (x === undefined || x === null) ? st.x : x, ny0 = (y === undefined || y === null) ? st.y : y;
  var dxy = (nx0 !== null && (st.x === null || fmtNum(nx0) !== fmtNum(st.x))) ||
            (ny0 !== null && (st.y === null || fmtNum(ny0) !== fmtNum(st.y)));
  // IVI 3licer always writes X and Y together, so do the same
  if (dxy) { if (nx0 !== null) { w.push("X" + fmtNum(nx0)); } if (ny0 !== null) { w.push("Y" + fmtNum(ny0)); } }
  if (z !== undefined && z !== null && (st.z === null || fmtNum(z) !== fmtNum(st.z))) { w.push("Z" + fmtNum(z)); }
  if (w.length == 1) { return; }
  if (feed && fFormat.format(feed) !== st.f) { w.push("F" + fFormat.format(feed)); st.f = fFormat.format(feed); }
  if (code == "G1" && feed && st.firstCut === undefined) { st.firstCut = feed; }
  var nx = (x === undefined || x === null) ? st.x : x, ny = (y === undefined || y === null) ? st.y : y;
  if (dxy && nx !== null && ny !== null) { trackXY(nx, ny, code == "G0" ? JOG : (st.f ? Number(st.f) : WORK)); }
  if (z !== undefined && z !== null && st.z !== null && code == "G1") { st.time += Math.abs(z - st.z) / (feed || WORK) * 60; }
  st.x = nx; st.y = ny; if (z !== undefined && z !== null) { st.z = z; }
  out(w.join(" "));
}

function header(type, method, power) {
  var validBody = 0;
  for (var i = 0; i < body.length; ++i) { var t = body[i].replace(/^\s+|\s+$/g, ""); if (t && t.charAt(0) != ";") { validBody++; } }
  if (st.minX === Infinity) { st.minX = st.maxX = st.minY = st.maxY = 0; }
  var h = [";Header Start", ";header_type: " + type, ";renderMethod: " + method,
    ";file_total_lines: @T", ";file_valid_lines: " + validBody,
    ";estimated_time(s): " + st.time.toFixed(2),
    ";max_x(mm): " + st.maxX.toFixed(2), ";max_y(mm): " + st.maxY.toFixed(2), ";max_z(mm): 0",
    ";min_x(mm): " + st.minX.toFixed(2), ";min_y(mm): " + st.minY.toFixed(2), ";min_z(mm): 0",
    ";work_speed(mm/minute): " + Math.round(st.firstCut || WORK), ";jog_speed(mm/minute): " + Math.round(JOG),
    ";power(%): " + Math.round(power), ";Generated by Fusion ivi3d post", ";Header End", ""];
  var total = h.length + body.length;   // one line per writeln
  h[3] = ";file_total_lines: " + total;
  return h;
}

function flushAll(h) {
  for (var i = 0; i < h.length; ++i) { writeln(h[i]); }
  for (var j = 0; j < body.length; ++j) { writeln(body[j]); }
}

function checkUnits() {
  if (unit != MM) { error("IVI3D posts require millimetre output: set the setup/post units to mm."); }
}

function onCircular(clockwise, cx, cy, cz, x, y, z, feed) { linearize(tolerance); }
// ---- end shared core ----


function laserOn() {
  if (st.on) { return; }
  var p = Math.max(0, Math.min(100, POWER));
  if (lastS !== p) { out("M3 S" + p); lastS = p; } else { out("M3"); }
  st.on = true;
}
function laserOff() { if (st.on) { out("M5"); st.on = false; } }

function onOpen() {
  checkUnits();
  JOG = getProperty("jogSpeed"); WORK = getProperty("workSpeed"); POWER = getProperty("powerPercent");
  out("G90"); out("G21");
  if (getProperty("airAssist")) { out("M106 P0"); }
  out("G0 F" + Math.round(JOG));
  out("G1 F" + Math.round(WORK)); st.f = fFormat.format(WORK);
}
function onSection() {
  laserOff();
  if (currentSection.getType && currentSection.getType() != TYPE_JET) { error("IVI3D laser post: only laser (jet) operations are supported."); }
}
function onPower(power) { st.armed = !!power; if (!power) { laserOff(); } }
function onRapid(x, y, z) { laserOff(); move("G0", x, y, null); }
function onLinear(x, y, z, feed) {
  if (st.armed === false) { laserOff(); move("G0", x, y, null); return; }
  laserOn();
  move("G1", x, y, null, feed > 0 ? feed : WORK);
}
function onDwell(seconds) { out("G4 P" + Math.round(seconds * 1000)); st.time += seconds; }
function onSectionEnd() { laserOff(); }
function onClose() {
  laserOff();
  move("G0", 0, 0, null);
  if (getProperty("airAssist")) { out("M107 P0"); }
  flushAll(header("laser", "line", POWER));
}
