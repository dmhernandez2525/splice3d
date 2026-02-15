use <../../f1_1/cad/common.scad>;

// Cooling and heater exhaust ducting with optional HEPA frame mount.

hepa_enabled = true;

module fan_to_splice_duct() {
    difference() {
        hull() {
            translate([10, 20, 0]) {
                cube([36, 36, 20], center = false);
            }
            translate([120, 36, 0]) {
                cube([52, 20, 20], center = false);
            }
        }

        hull() {
            translate([16, 26, 4]) {
                cube([24, 24, 14], center = false);
            }
            translate([128, 40, 4]) {
                cube([36, 12, 14], center = false);
            }
        }
    }
}

module heater_exhaust_duct() {
    difference() {
        hull() {
            translate([12, 74, 0]) {
                cube([38, 30, 24], center = false);
            }
            translate([124, 88, 0]) {
                cube([48, 20, 24], center = false);
            }
        }

        hull() {
            translate([18, 80, 5]) {
                cube([26, 18, 14], center = false);
            }
            translate([130, 92, 5]) {
                cube([34, 12, 14], center = false);
            }
        }
    }
}

module hepa_frame() {
    difference() {
        cube([54, 54, 6], center = false);
        translate([5, 5, -0.1]) {
            cube([44, 44, 6.2], center = false);
        }

        for (x = [7, 47]) {
            for (y = [7, 47]) {
                translate([x, y, -0.1]) {
                    m3_hole(height = 6.2);
                }
            }
        }
    }
}

module vent_layout() {
    fan_to_splice_duct();
    heater_exhaust_duct();

    if (hepa_enabled) {
        translate([120, 10, 0]) {
            hepa_frame();
        }
    }
}

vent_layout();
