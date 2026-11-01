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
//@@COMMON@@

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
