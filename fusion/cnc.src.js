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
//@@COMMON@@

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
