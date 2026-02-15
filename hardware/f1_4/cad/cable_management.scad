use <../../f1_1/cad/common.scad>;

// Clip-on cable channels with integrated strain relief blocks.

module cable_channel(length = 80) {
    difference() {
        cube([length, 14, 10], center = false);
        translate([2, 2, 2]) {
            cube([length - 4, 10, 8.2], center = false);
        }
    }

    // Snap clip feet.
    translate([8, 14, 2]) {
        cube([8, 2, 6], center = false);
    }
    translate([length - 16, 14, 2]) {
        cube([8, 2, 6], center = false);
    }
}

module strain_relief_block() {
    difference() {
        rounded_block([26, 18, 14], radius = 1);
        translate([13, 9, 7]) {
            rotate([0, 90, 0]) {
                cylinder(h = 20, d = 6, center = true, $fn = 24);
            }
        }
        translate([13, 9, -0.1]) {
            m3_hole(height = 14.2);
        }
    }
}

module cable_management_layout() {
    translate([8, 8, 0]) {
        cable_channel(length = 60);
    }
    translate([80, 8, 0]) {
        cable_channel(length = 80);
    }
    translate([168, 8, 0]) {
        cable_channel(length = 28);
    }

    translate([20, 36, 0]) {
        strain_relief_block();
    }
    translate([60, 36, 0]) {
        strain_relief_block();
    }
    translate([100, 36, 0]) {
        strain_relief_block();
    }
    translate([140, 36, 0]) {
        strain_relief_block();
    }
}

cable_management_layout();
