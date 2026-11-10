// ============================================================================
// DEBUGUART 3-pin pogo holder — A33_407MB_200916
// Simple one-piece handheld / arm-mount block. Through-bores for R75 sleeves.
//
// PHOTO ESTIMATES (ruler image; approximate — NOT surveyed):
//   Pad order L→R, silkscreen upright: GND, DEBUGUART_RX, DEBUGUART_TX
//   Along-edge center spacings from image ≈ 1.9 mm then 2.8 mm
//     (raw image-plane ~1.93 / ~2.79; rounded — unequal adjacent pitches
//      are suspicious; may be center-pick / perspective error, or real
//      non-grid test points. Do not treat as precise.)
//   Image also showed slight pad-row tilt vs the ruler; that is NOT treated
//     as real PCB skew. Primary models use a STRAIGHT row parallel to the
//     board-edge reference (constant Y).
//   Pad copper Ø ≈ 0.9 mm in image → treat ~1.0 ± 0.2 mm.
//   Edge inset (image-plane) ≈ 5 mm (foreshortened; real likely ~4–7 mm).
//
// FRONT PHOTOS: board on chassis standoffs, densely populated (STM32F407,
// blue Allwinner A33 module, AP6236, JSTs, microSD, micro-USB near edge).
// No underside/component clamp. This is a contact block only.
//
// Socket retention: through-bore; rely on press-fit and/or adhesive at the
// BACK (non-contact) face. No internal shoulder claimed. No metal set
// screws between sockets (short risk).
//
// Export:
//   openscad -D 'part="holder_photo"'   -o stl/holder_photo.stl uart_pogo_holder.scad
//   openscad -D 'part="holder_2_0"'     -o stl/holder_2_0.stl uart_pogo_holder.scad
//   openscad -D 'part="holder_2_5"'     -o stl/holder_2_5.stl uart_pogo_holder.scad
//   openscad -D 'part="bore_coupon"'    -o stl/bore_coupon.stl uart_pogo_holder.scad
//   openscad -D 'part="assembled"' --imgsize=1400,1000 -o renders/assembled.png ...
// ============================================================================

/* [Part] */
part = "assembled"; // [holder_photo, holder_2_0, holder_2_5, bore_coupon, assembled, exploded]

/* [Independent bore coordinates — photo variant]
   Origin: GND bore center in XY.
   +X = along board edge toward RX/TX (photo left→right).
   +Y = toward board interior (away from board edge).
   +Z = out of board (holder sits above pads; tips exit z=0 face).
   All Y equal (straight row). Edit these if calipers disagree.
*/
photo_x = [0.0, 1.9, 4.7];  // ~1.9 then ~2.8 along-edge estimates
photo_y = [0.0, 0.0, 0.0];  // no image-tilt skew baked in

/* [Equal-pitch variants] */
pitch_2_0 = 2.0;
pitch_2_5 = 2.5;

/* [Socket bore] */
// Printed through-bore for R75-class sleeve. Confirm with bore_coupon.
r75_hole = 1.40; // [1.20:0.05:1.70]
// Vendor sleeve OD ~1.32 (reference only)
r75_od_ref = 1.32;

/* [Body] */
body_h = 12.0;          // along pin axis (thickness of block)
wall_xy = 2.2;          // plastic around outermost bores
body_y_front = 3.5;     // material toward board edge from pad row (Y-)
body_y_back  = 5.5;     // material toward interior / fingers (Y+)
// Rear mount tab (M3), clear of bores and wire exits
mount_tab = true;
mount_hole = 3.4;       // M3 clearance
mount_spacing = 16.0;
mount_tab_t = 4.0;
mount_setback = 7.5;    // tab center behind pad row (+Y)

/* [Coupon] */
coupon_holes = [1.30, 1.40, 1.50, 1.60];

/* [Print] */
$fn = 48;
eps = 0.05;

labels = ["GND", "RX", "TX"];

// ---------------------------------------------------------------------------
function equal_xs(pitch) = [0, pitch, 2*pitch];
function equal_ys(pitch) = [0, 0, 0];

module round_box(x, y, z, r=1.0) {
    hull() for (ix=[r, x-r]) for (iy=[r, y-r])
        translate([ix, iy, 0]) cylinder(r=r, h=z);
}

module holder(xs, ys, tag="") {
    // Body extents from bore coordinates
    xmin = min(xs) - wall_xy;
    xmax = max(xs) + wall_xy;
    ymin = min(ys) - body_y_front;
    ymax = max(ys) + body_y_back;
    len = xmax - xmin;
    wid = ymax - ymin;

    difference() {
        union() {
            translate([xmin, ymin, 0])
                round_box(len, wid, body_h, 1.2);
            if (mount_tab) {
                // Rear tab: overlaps body in Y and Z so union is clean
                mid_x = (min(xs) + max(xs)) / 2;
                tab_w = mount_spacing + 10;
                translate([mid_x - tab_w/2, ymax - 2.0, 0])
                    cube([tab_w, mount_setback + 4.0, body_h]);
            }
        }
        // Through-bores (normal to board / tip face z=0). Full height.
        for (i = [0:2]) {
            translate([xs[i], ys[i], -eps])
                cylinder(d=r75_hole, h=body_h + 2*eps);
        }
        // Mount holes — only through the rear tab, never through probe zone
        if (mount_tab) {
            mid_x = (min(xs) + max(xs)) / 2;
            for (s = [-1, 1]) {
                translate([mid_x + s*mount_spacing/2,
                           ymax + mount_setback - 2.0,
                           -eps])
                    cylinder(d=mount_hole, h=body_h + 2*eps);
            }
        }
        // Mark GND/RX/TX with sharpie after print (L→R). No engraved marks
        // (keeps the mesh manifold).
    }
}

module bore_coupon() {
    holes = coupon_holes;
    spacing = 9;
    plate_w = spacing * len(holes) + 8;
    plate_d = 14;
    plate_h = 10;
    difference() {
        translate([-plate_w/2, -plate_d/2, 0])
            round_box(plate_w, plate_d, plate_h, 1.0);
        for (i = [0:len(holes)-1]) {
            x = -((len(holes)-1)/2)*spacing + i*spacing;
            translate([x, 0, -eps])
                cylinder(d=holes[i], h=plate_h + 2*eps);
            // L→R holes = 1.30, 1.40, 1.50, 1.60 mm. Mark with sharpie if needed.
        }
    }
}

// ---------------------------------------------------------------------------
// Previews
// ---------------------------------------------------------------------------
module assembled_preview() {
    // Photo-estimate holder over a ghost PCB edge
    color([0.35, 0.48, 0.72])
        holder(photo_x, photo_y);
    // Sleeve / probe ghosts (through-bores)
    for (i = [0:2]) {
        col = i==0 ? [0.85,0.25,0.25] : (i==1 ? [0.9,0.75,0.15] : [0.3,0.7,0.4]);
        color(col)
            translate([photo_x[i], photo_y[i], -2.5])
                cylinder(d=0.9, h=body_h + 4);
    }
    // PCB ghost — edge at y = -body_y_front - small margin visually
    color([0.15, 0.45, 0.25, 0.35])
        translate([-8, -body_y_front - 0.8, -1.6])
            cube([20, 22, 1.6]);
    // Pad ghosts on PCB
    for (i = [0:2]) {
        color([0.85, 0.65, 0.2])
            translate([photo_x[i], photo_y[i], -1.6])
                cylinder(d=1.0, h=0.12);
    }
}

module exploded_preview() {
    color([0.35, 0.48, 0.72])
        translate([-18, 0, 0]) holder(photo_x, photo_y);
    color([0.45, 0.55, 0.65])
        translate([8, 0, 0]) holder(equal_xs(pitch_2_0), equal_ys(pitch_2_0));
    color([0.55, 0.45, 0.65])
        translate([28, 0, 0]) holder(equal_xs(pitch_2_5), equal_ys(pitch_2_5));
    color([0.75, 0.65, 0.45])
        translate([-5, 28, 0]) bore_coupon();
    color("black")
        translate([-18, -12, 0]) linear_extrude(0.2)
            text("photo ~1.9/2.8", size=2.2, halign="center");
    color("black")
        translate([8, -12, 0]) linear_extrude(0.2)
            text("2.0 eq", size=2.2, halign="center");
    color("black")
        translate([28, -12, 0]) linear_extrude(0.2)
            text("2.5 eq", size=2.2, halign="center");
    color("black")
        translate([-5, 18, 0]) linear_extrude(0.2)
            text("bore coupon", size=2.2, halign="center");
}

// ---------------------------------------------------------------------------
if      (part == "holder_photo") holder(photo_x, photo_y);
else if (part == "holder_2_0")  holder(equal_xs(pitch_2_0), equal_ys(pitch_2_0));
else if (part == "holder_2_5")  holder(equal_xs(pitch_2_5), equal_ys(pitch_2_5));
else if (part == "bore_coupon") bore_coupon();
else if (part == "assembled")   assembled_preview();
else if (part == "exploded")    exploded_preview();
else holder(photo_x, photo_y);
