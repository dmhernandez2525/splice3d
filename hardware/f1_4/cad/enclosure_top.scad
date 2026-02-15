use <../../f1_1/cad/common.scad>;

// Top shell with ventilation, labels, and optional HEPA frame pocket.

module enclosure_top() {
    difference() {
        rounded_block([218, 218, 38], radius = 2);

        // Inner clearance.
        translate([8, 8, 2]) {
            cube([202, 202, 34], center = false);
        }

        // Vent slots across splice and electronics zones.
        for (x = [26 : 16 : 186]) {
            translate([x, 36, -0.1]) {
                cube([8, 130, 4], center = false);
            }
        }

        // Service label recesses.
        translate([20, 178, -0.1]) {
            cube([72, 24, 1.4], center = false);
        }
        translate([126, 178, -0.1]) {
            cube([72, 24, 1.4], center = false);
        }

        // Optional HEPA mount opening.
        translate([154, 22, -0.1]) {
            cube([44, 44, 3.5], center = false);
        }
    }

    // Snap-fit pockets for bottom tabs.
    for (x = [36, 90, 144, 182]) {
        translate([x + 1, 0, 24]) {
            cube([8, 3, 8], center = false);
        }
        translate([x + 1, 215, 24]) {
            cube([8, 3, 8], center = false);
        }
    }
}

enclosure_top();
