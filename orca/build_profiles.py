#!/usr/bin/env python3
"""Generate OrcaSlicer user presets (machine / filament / process) + an .orca_printer bundle for the IVI3D delta.
Values come from IVI 3licer 1.6.2 (resources/CuraEngine/Config/ivi3d.def.json + the user's active_final.def.json)
and the printer's M503 dump; see README.md for sourced vs assumed. Run: python3 build_profiles.py"""
import json, math, os, zipfile

D = os.path.dirname(os.path.abspath(__file__))
PRINTER = "IVI3D 0.3 nozzle"
FILAMENT = "IVI3D PLA"
PROCESS = "IVI3D 0.15mm Standard"
RADIUS = 105.0          # Cura "elliptic" 210 x 210, centre is zero
HEIGHT = 220            # machine_height (delta height H233.22 in M503)
VERSION = "2.3.0.0"

def circle(r, n=72):
    return [f"{r * math.cos(2 * math.pi * i / n):.3f}x{r * math.sin(2 * math.pi * i / n):.3f}" for i in range(n)]

START = """; IVI3D start (matches IVI 3licer 1.6.2 machine_start_gcode; G53/M82 as sent before FDM jobs)
G53 ; machine coordinate system
M82 ; absolute extrusion
M104 S[nozzle_temperature_initial_layer]
M140 S[bed_temperature_initial_layer_single]
G28 ; home (delta homes to the top)
G90 ; absolute positioning
G1 Y-100.0 Z15.0 F2000
M109 S[nozzle_temperature_initial_layer] ; wait for hotend
M190 S[bed_temperature_initial_layer_single] ; wait for bed
G92 E0
G1 Z0.8 F500.0
G1 X8.66 Y-98.94 E8.0 F500.0 ; intro line
G1 X17.25 Y-97.81 E15 F500.0 ; intro line
G92 E0
; IVI3D start end"""

END = """; IVI3D end (IVI 3licer 1.6.2 machine_end_gcode + fan off)
M104 S0 ; extruder heater off
M140 S0 ; bed heater off
M107 ; part fan off (added; not in IVI 3licer)
G90 ; absolute positioning
G92 E1
G1 E-1 F300 ; relieve pressure
M203 Z500
M82 ; absolute extrusion mode
; IVI3D end end"""

machine = {
    "type": "machine", "name": PRINTER, "from": "User", "inherits": "", "version": VERSION,
    "printer_settings_id": PRINTER, "printer_technology": "FFF", "printer_model": "IVI3D", "printer_variant": "0.3",
    "gcode_flavor": "marlin", "printable_area": circle(RADIUS), "printable_height": str(HEIGHT),
    "bed_exclude_area": [], "nozzle_diameter": ["0.3"], "nozzle_type": "brass", "extruder_offset": ["0x0"],
    "max_layer_height": ["0.24"], "min_layer_height": ["0.05"],
    "use_relative_e_distances": "0", "use_firmware_retraction": "0",
    "retraction_length": ["6.5"], "retraction_speed": ["25"], "deretraction_speed": ["25"],
    "retract_when_changing_layer": ["0"], "z_hop": ["0"], "retraction_minimum_travel": ["1.5"], "wipe": ["0"],
    "machine_max_speed_x": ["500"], "machine_max_speed_y": ["500"], "machine_max_speed_z": ["500"], "machine_max_speed_e": ["100"],
    "machine_max_acceleration_x": ["1000"], "machine_max_acceleration_y": ["1000"], "machine_max_acceleration_z": ["1000"],
    "machine_max_acceleration_e": ["1000"], "machine_max_acceleration_extruding": ["1000"],
    "machine_max_acceleration_retracting": ["1000"], "machine_max_acceleration_travel": ["1000"],
    "machine_max_jerk_x": ["15"], "machine_max_jerk_y": ["15"], "machine_max_jerk_z": ["10"], "machine_max_jerk_e": ["5"],
    "emit_machine_limits_to_gcode": "0",
    "machine_start_gcode": START, "machine_end_gcode": END,
    "before_layer_change_gcode": "", "layer_change_gcode": "", "change_filament_gcode": "",
    "thumbnails": "", "host_type": "octoprint", "print_host": "127.0.0.1:5000",
    "printhost_apikey": "PASTE-API-KEY-FROM-IVI-BRIDGE-INSTALLER", "print_host_webui": "http://127.0.0.1:5000/",
    "default_filament_profile": [FILAMENT], "default_print_profile": PROCESS,
    "machine_pause_gcode": "M2410", "auxiliary_fan": "0", "silent_mode": "0",
}

filament = {
    "type": "filament", "name": FILAMENT, "from": "User", "inherits": "", "version": VERSION,
    "filament_settings_id": [FILAMENT], "compatible_printers": [PRINTER],
    "filament_type": ["PLA"], "filament_diameter": ["1.75"], "filament_flow_ratio": ["1"], "filament_density": ["1.24"],
    "nozzle_temperature": ["210"], "nozzle_temperature_initial_layer": ["215"],
    "nozzle_temperature_range_low": ["190"], "nozzle_temperature_range_high": ["230"],
    "hot_plate_temp": ["60"], "hot_plate_temp_initial_layer": ["60"],
    "cool_plate_temp": ["60"], "cool_plate_temp_initial_layer": ["60"],
    "textured_plate_temp": ["60"], "textured_plate_temp_initial_layer": ["60"],
    "eng_plate_temp": ["60"], "eng_plate_temp_initial_layer": ["60"],
    "fan_min_speed": ["100"], "fan_max_speed": ["100"], "close_fan_the_first_x_layers": ["1"],
    "filament_max_volumetric_speed": ["8"], "slow_down_layer_time": ["8"],
}

process = {
    "type": "process", "name": PROCESS, "from": "User", "inherits": "", "version": VERSION,
    "print_settings_id": PROCESS, "compatible_printers": [PRINTER],
    "layer_height": "0.15", "initial_layer_print_height": "0.3",
    "line_width": "0.3", "outer_wall_line_width": "0.28", "inner_wall_line_width": "0.28",
    "top_surface_line_width": "0.28", "internal_solid_infill_line_width": "0.28", "sparse_infill_line_width": "0.28",
    "support_line_width": "0.28", "initial_layer_line_width": "0.3",
    "wall_loops": "3", "top_shell_layers": "6", "top_shell_thickness": "0.9", "bottom_shell_layers": "4",
    "bottom_shell_thickness": "0.6", "sparse_infill_density": "15%", "sparse_infill_pattern": "grid",
    "outer_wall_speed": "45", "inner_wall_speed": "50", "sparse_infill_speed": "60", "internal_solid_infill_speed": "60",
    "top_surface_speed": "30", "travel_speed": "80", "initial_layer_speed": "18", "initial_layer_infill_speed": "18",
    "initial_layer_travel_speed": "30", "skirt_speed": "18", "gap_infill_speed": "30", "support_speed": "40",
    "bridge_speed": "25",
    "default_acceleration": "500", "outer_wall_acceleration": "500", "inner_wall_acceleration": "500",
    "top_surface_acceleration": "500", "sparse_infill_acceleration": "500", "initial_layer_acceleration": "500",
    "travel_acceleration": "500", "default_jerk": "15", "outer_wall_jerk": "15", "inner_wall_jerk": "15",
    "top_surface_jerk": "15", "infill_jerk": "15", "initial_layer_jerk": "15", "travel_jerk": "15",
    "skirt_loops": "1", "skirt_distance": "3", "brim_type": "no_brim", "brim_width": "8",
    "enable_support": "0", "support_type": "normal(auto)", "support_threshold_angle": "50",
    "support_base_pattern": "rectilinear", "support_object_xy_distance": "0.35",
    "seam_position": "aligned", "gcode_label_objects": "0", "exclude_object": "0",
    "post_process": [],
}

# IVI 3licer 1.6.2 built-in quality defs for the 0.3 nozzle (resources/CuraEngine/Config/test/quality.(0.3).*.def.json).
# Shell layer counts are derived like Cura does from thickness/layer (the files' default *_layers/wall_line_count are
# stale defaults; the active Standard config showed 3 walls / 6 top / 4 bottom computed from thickness).
def variant(name, layer, top_thick, top, bottom, walls, infill, outer, inner, fill, topbot, travel):
    p = dict(process, name=name, print_settings_id=name, layer_height=str(layer),
             wall_loops=str(walls), top_shell_layers=str(top), top_shell_thickness=str(top_thick),
             bottom_shell_layers=str(bottom), sparse_infill_density=f"{infill}%",
             outer_wall_speed=str(outer), inner_wall_speed=str(inner), sparse_infill_speed=str(fill),
             internal_solid_infill_speed=str(fill), top_surface_speed=str(topbot), travel_speed=str(travel))
    return p

# fast_print(0.3): layer 0.2, top 0.9 / bottom 0.6 mm, wall 0.8 mm, 15 %, wall_0 50, wall_x 60, infill 80, topbottom 40, travel 100
fast = variant("IVI3D 0.20mm Fast", 0.2, 0.9, 5, 3, 3, 15, 50, 60, 80, 40, 100)
# high_quality(0.3): layer 0.1, top 1.2 / bottom 0.6 mm, wall 0.8 mm, 20 %, wall_0 30, wall_x 45, infill 50, topbottom 30, travel 60
hq = variant("IVI3D 0.10mm High Quality", 0.1, 1.2, 12, 6, 3, 20, 30, 45, 50, 30, 60)
PROCESSES = [process, fast, hq]

# Extra filaments. Baseline = Anycubic's own OrcaSlicer vendor profiles (OrcaSlicer resources/profiles/Anycubic/filament,
# "Anycubic <X> @Anycubic Kobra S1 0.4 nozzle" / "TPU 95A @Kobra S1 Max 0.4"). Max volumetric speed scaled for the
# 0.3 nozzle at ~0.55x (nozzle area ratio (0.3/0.4)^2 = 0.56) and capped at the PLA value (8). See README for sources.
def fil(name, ftype, density, t, t0, lo, hi, bed, fmin, fmax, nofan, vol, layer_time, retract=None, rspeed=None, extra=None):
    f = dict(filament, name=name, filament_settings_id=[name], filament_type=[ftype], filament_density=[str(density)],
             nozzle_temperature=[str(t)], nozzle_temperature_initial_layer=[str(t0)],
             nozzle_temperature_range_low=[str(lo)], nozzle_temperature_range_high=[str(hi)],
             fan_min_speed=[str(fmin)], fan_max_speed=[str(fmax)], close_fan_the_first_x_layers=[str(nofan)],
             filament_max_volumetric_speed=[str(vol)], slow_down_layer_time=[str(layer_time)])
    for k in ("hot_plate_temp", "cool_plate_temp", "textured_plate_temp", "eng_plate_temp"):
        f[k] = [str(bed)]; f[k + "_initial_layer"] = [str(bed)]
    if retract is not None: f["filament_retraction_length"] = [str(retract)]
    if rspeed is not None: f["filament_retraction_speed"] = [str(rspeed)]; f["filament_deretraction_speed"] = [str(rspeed)]
    f.update(extra or {})
    return f

EXTRA_FILAMENTS = [
    # Anycubic ABS: 250/250 C, bed 90, fan 10-80 (off 5 layers), 15 mm3/s @0.4
    fil("IVI3D ABS", "ABS", 1.04, 250, 250, 240, 280, 90, 10, 80, 5, 8, 30),
    # Anycubic ASA: 260/260 C, bed 100, fan 10-60 (off 5 layers), 12 mm3/s @0.4
    fil("IVI3D ASA", "ASA", 1.07, 260, 260, 240, 280, 100, 10, 60, 5, 7, 35),
    # Anycubic PETG: 250/250 C, bed 70, fan 30-90 (off 3), retract 1.5 mm @0.4 direct drive (machine 6.5 kept: Bowden)
    fil("IVI3D PETG", "PETG", 1.27, 240, 245, 220, 260, 70, 30, 90, 3, 7, 30),
    # Tangled TUFF Pro PCTG baseline: nozzle 250-280, bed 70-90, fan <=25 %, 30-60 mm/s
    fil("IVI3D PCTG (Tangled TUFF)", "PCTG", 1.27, 260, 260, 250, 280, 80, 10, 25, 3, 6, 20),
    # Anycubic TPU 95A: 205 / 215 first layer, bed 35, fan 100, retract 1 mm @30, 3.2 mm3/s @0.4
    fil("IVI3D TPU 95A", "FLEX", 1.21, 215, 220, 190, 240, 35, 100, 100, 1, 1.5, 10, retract=1.0, rspeed=20),
    # EXPERIMENTAL: Stratasys SR-30 soluble support (alkaline-soluble, NOT PVA). Printed alone on a single nozzle.
    fil("IVI3D SR-30 Soluble (EXPERIMENTAL)", "PVA", 1.2, 255, 260, 245, 265, 100, 0, 20, 3, 4, 20,
        extra={"filament_soluble": ["1"], "filament_is_support": ["1"],
               "filament_notes": ["EXPERIMENTAL. Stratasys SR-30 (alkaline-soluble terpolymer, NOT PVA). Dissolve in "
                                  "heated NaOH bath ~70 C. Pairs with ABS/ASA; single nozzle = whole-part tests only. "
                                  "Dry before use; enclosure recommended."]}),
]
FILAMENTS = [filament] + EXTRA_FILAMENTS

def write(sub, obj):
    os.makedirs(os.path.join(D, sub), exist_ok=True)
    p = os.path.join(D, sub, obj["name"] + ".json")
    with open(p, "w") as f: json.dump(obj, f, indent=4); f.write("\n")
    return p

if __name__ == "__main__":
    mpath = write("machine", machine); fpaths = [write("filament", f) for f in FILAMENTS]
    ppaths = [write("process", p) for p in PROCESSES]; paths = [mpath] + fpaths + ppaths
    bundle = os.path.join(D, "IVI3D.orca_printer")
    structure = {"bundle_id": "ivi3d_" + VERSION, "bundle_type": "printer config bundle", "version": VERSION,
                 "printer_preset_name": PRINTER,
                 "printer_config": [f"printer/{PRINTER}.json"], "filament_config": [f"filament/{f['name']}.json" for f in FILAMENTS],
                 "process_config": [f"process/{p['name']}.json" for p in PROCESSES]}
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("bundle_structure.json", json.dumps(structure, indent=4))
        z.write(mpath, f"printer/{PRINTER}.json")
        for f, path in zip(FILAMENTS, fpaths): z.write(path, f"filament/{f['name']}.json")
        for p, path in zip(PROCESSES, ppaths): z.write(path, f"process/{p['name']}.json")
    print("\n".join(paths + [bundle]))
