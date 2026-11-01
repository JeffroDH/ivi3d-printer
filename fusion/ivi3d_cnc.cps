/**
  IVI3D CNC post processor for Autodesk Fusion (CC BY-NC-SA 4.0, JeffroDH/ivi3d-printer).
  Emits the IVI 3licer CNC header + G-code: M3 S<percent> spindle on, M5 off, G0 Z safe heights.
  Firmware V1.3.2-alpha's M3 handler reads only S (0-100 %, clamped, ramped 10 %/300 ms) and ignores P,
  so IVI 3licer's "M3 P100" acts like a bare M3 (re-uses the last power). S is the default here;
  set "Spindle word" to P to copy IVI 3licer exactly. UNVERIFIED on hardware. See docs/laser_cnc_gcode.md.
  Origin: WCS X0 Y0 at the CENTRE of the stock, Z0 at the stock TOP (IVI cuts go to negative Z).
*/
description = "IVI3D CNC";
vendor = "IVI3D (community)";
vendorUrl = "https://github.com/JeffroDH/ivi3d-printer";
legal = "CC BY-NC-SA 4.0";
certificationLevel = 2;
minimumRevision = 45702;
longDescription = "CNC post for the IVI3D printer CNC head. Output matches IVI 3licer's header, M3 P<percent>/M5 and safe-Z moves. Unverified on hardware.";
extension = "cnc";
setCodePage("ascii");
capabilities = CAPABILITY_MILLING;
tolerance = spatial(0.01, MM);
minimumChordLength = spatial(0.25, MM);
minimumCircularRadius = spatial(0.01, MM);
maximumCircularRadius = spatial(1000, MM);
minimumCircularSweep = toRad(0.01);
maximumCircularSweep = toRad(180);
allowHelicalMoves = false;
allowedCircularPlanes = 0; // linearize all arcs (IVI files contain only G0/G1)

properties = {
  spindlePercent: {title: "Spindle power (%)", description: "Emitted as M3 S<percent> (firmware reads S as percent).", type: "integer", value: 100, scope: "post"},
  spindleWord:    {title: "Spindle word", description: "S (firmware-decoded, default) or P (IVI 3licer output; ignored by firmware).", type: "enum", values: ["S", "P"], value: "S", scope: "post"},
  safeZ:          {title: "Safe Z (mm)", description: "Clearance height at start/end (IVI 3licer: 10).", type: "number", value: 10, scope: "post"},
  retractZ:       {title: "Retract Z (mm)", description: "Height before spindle start (IVI 3licer: 5).", type: "number", value: 5, scope: "post"},
  jogSpeed:       {title: "Jog speed (mm/min)", description: "Header jog_speed and G0 time estimate.", type: "number", value: 3000, scope: "post"},
  maxPlungeFeed:  {title: "Max plunge feed (mm/min)", description: "Caps Z-down G1 feed (IVI 3licer: 300).", type: "number", value: 300, scope: "post"}
};

var WORK = 300, JOG = 3000, spindleOn = false;
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


function onOpen() {
  checkUnits();
  JOG = getProperty("jogSpeed");
  out("G90"); out("G21");
  move("G0", null, null, getProperty("safeZ"), 400);
}
function onSection() {
  if (currentSection.getType && currentSection.getType() != TYPE_MILLING) { error("IVI3D CNC post: only milling operations are supported."); }
  var p = currentSection.getInitialPosition ? currentSection.getInitialPosition() : null;
  if (p) { move("G0", null, null, getProperty("safeZ")); move("G0", p.x, p.y, null); }
  move("G0", null, null, getProperty("retractZ"));
  if (!spindleOn) {
    var pct = Math.max(1, Math.min(100, getProperty("spindlePercent")));
    out("M3 " + (getProperty("spindleWord") == "P" ? "P" : "S") + pct); spindleOn = true;
  }
}
function onRapid(x, y, z) { move("G0", x, y, z); }
function onLinear(x, y, z, feed) {
  var plunge = st.z !== null && z < st.z - 1e-6 && (st.x === null || Math.abs(x - st.x) < 1e-6) && (st.y === null || Math.abs(y - st.y) < 1e-6);
  if (plunge) { feed = Math.min(feed, getProperty("maxPlungeFeed")); }
  else if (feed > 0 && !st.workSet) { WORK = feed; st.workSet = true; }
  move("G1", x, y, z, feed);
}
function onDwell(seconds) { out("G4 P" + Math.round(seconds * 1000)); st.time += seconds; }
function onSectionEnd() {}
function onClose() {
  move("G0", null, null, getProperty("retractZ"));
  move("G0", null, null, getProperty("safeZ"));
  move("G0", 0, 0, null);
  out("M5"); spindleOn = false;
  flushAll(header("cnc", "line", getProperty("spindlePercent")));
}
