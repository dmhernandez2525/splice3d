use <../../f1_1/cad/common.scad>;

// Bottom shell with cable channels, captive nuts, and snap tabs.

module enclosure_bottom() {
    difference() {
        rounded_block([218, 218, 42], radius = 2);

        // Inner cavity.
        translate([10, 10, 4]) {
            cube([198, 198, 34], center = false);
        }

        // Cable channels along left and right walls.
        translate([12, 24, 6]) {
            cube([14, 170, 10], center = false);
        }
        translate([192, 24, 6]) {
            cube([14, 170, 10], center = false);
        }

        // Captive nut slots for M3 hex nuts.
        for (x = [28, 190]) {
            for (y = [28, 190]) {
                translate([x, y, 4]) {
                    cylinder(h = 4, d = 6.2, $fn = 6);
                }
            }
        }

        // Board and bracket mounting holes.
        for (x = [60, 95, 130, 165]) {
            translate([x, 32, -0.1]) {
                m3_hole(height = 10);
            }
            translate([x, 186, -0.1]) {
                m3_hole(height = 10);
            }
        }
    }

    // Snap-fit tabs for top enclosure mating.
    for (x = [36, 90, 144, 182]) {
        translate([x, 0, 30]) {
            cube([10, 3, 8], center = false);
        }
        translate([x, 215, 30]) {
            cube([10, 3, 8], center = false);
        }
    }
}

enclosure_bottom();
