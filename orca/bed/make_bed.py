#!/usr/bin/env python3
"""IVI3D bed texture for OrcaSlicer. Units = mm, origin = bed centre, +Y = rear.
Plate outline: rounded triangle = equilateral triangle (inradius RT) offset by RC, so the plate's
inradius RT+RC = 115 mm clears the 105 mm printable circle with ~10 mm margin (proportions traced from
ivi3d.com product image bk11, which is a perspective view - scale is estimated, not measured).
Holes: hex grid, PITCH mm, 18 mm in from the plate edge, as in the photo. Run: python3 make_bed.py"""
import math, os
import cairosvg
D = os.path.dirname(os.path.abspath(__file__))
RT, RC, PRINT_R, PITCH, HOLE_D, HALF = 45.0, 70.0, 105.0, 8.0, 1.6, 170.0
dirs = [math.radians(a) for a in (90, 210, 330)]          # vertex directions: apex at rear
V = [(2*RT*math.cos(a), 2*RT*math.sin(a)) for a in dirs]   # triangle vertices (circumradius 2*RT)
def outline():
    pts = []
    for i, a in enumerate(dirs):
        for k in range(31):                                 # arc of 120 deg around each vertex
            t = a - math.radians(60) + math.radians(120) * k / 30
            pts.append((V[i][0] + RC*math.cos(t), V[i][1] + RC*math.sin(t)))
    return pts
def in_tri(x, y, inr):                                      # point inside triangle of inradius inr
    return all(-(x*math.cos(a) + y*math.sin(a)) <= inr for a in dirs)
def dist_tri(x, y):                                         # distance from triangle (0 inside)
    if in_tri(x, y, RT): return 0.0
    d = min(math.hypot(x-vx, y-vy) for vx, vy in V)
    for i in range(3):
        (ax, ay), (bx, by) = V[i], V[(i+1) % 3]
        t = max(0, min(1, ((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2)))
        d = min(d, math.hypot(x-ax-t*(bx-ax), y-ay-t*(by-ay)))
    return d
holes = []
rows = int(HALF/(PITCH*0.866)) + 1
for j in range(-rows, rows+1):
    y = j * PITCH * math.sqrt(3)/2
    for i in range(-30, 31):
        x = (i + (0.5 if j % 2 else 0)) * PITCH
        if dist_tri(x, y) <= RC - 18: holes.append((x, y))
S = lambda p: f"{p[0]+HALF:.2f},{HALF-p[1]:.2f}"
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 {2*HALF:g} {2*HALF:g}">',
       f'<path d="M{" L".join(S(p) for p in outline())} Z" fill="#e9eaec" stroke="#9a9ea4" stroke-width="1.2"/>']
svg += [f'<circle cx="{x+HALF:.2f}" cy="{HALF-y:.2f}" r="{HOLE_D/2}" fill="#8c9096"/>' for x, y in holes]
svg += [f'<circle cx="{HALF}" cy="{HALF}" r="{PRINT_R}" fill="none" stroke="#3aa0d8" stroke-width="0.8" stroke-dasharray="4 3" opacity="0.8"/>',
        '</svg>']
full = "\n".join(svg) + "\n"
open(os.path.join(D, "ivi3d_plate_full.svg"), "w").write(full)          # whole plate, for reference
# Orca stretches the texture over the bounding box of printable_area (210 x 210 mm), so the texture
# itself is cropped to +/-105 mm; the plate corners fall outside the printable box.
tex = full.replace(f'viewBox="0 0 {2*HALF:g} {2*HALF:g}"', f'viewBox="{HALF-PRINT_R:g} {HALF-PRINT_R:g} {2*PRINT_R:g} {2*PRINT_R:g}"')
tex = tex.replace(f'r="{PRINT_R}" fill="none"', f'r="{PRINT_R-0.6}" fill="none"')
open(os.path.join(D, "ivi3d_bed.svg"), "w").write(tex)
cairosvg.svg2png(url=os.path.join(D, "ivi3d_bed.svg"), write_to=os.path.join(D, "ivi3d_bed.png"),
                 output_width=1024, output_height=1024)
print(len(holes), "holes")
