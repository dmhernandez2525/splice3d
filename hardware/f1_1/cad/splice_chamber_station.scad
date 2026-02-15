use <common.scad>;

// Heated splice chamber station around repurposed hotend core.

module splice_chamber_station() {
    difference() {
        rounded_block([98, 70, 48], radius = 1.5);

        // Heater block pocket (16x16x12mm) with service clearance.
        translate([40, 27, 16]) {
            cube([24, 16, 16], center = false);
        }

        // PTFE constrained channel through hot zone.
        translate([49, 35, 24]) {
            filament_channel(length = 86, diameter = 2.05, axis = "x");
        }

        // Thermistor service bore.
        translate([58, 16, 24]) {
            rotate([90, 0, 0]) {
                cylinder(h = 14, d = 3.2, center = false, $fn = 24);
            }
        }

        // Heater cartridge bore.
        translate([44, 35, 20]) {
            rotate([0, 90, 0]) {
                cylinder(h = 26, d = 6.2, center = false, $fn = 28);
            }
        }

        // Rail slots for maintenance removal.
        translate([20, 18, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([20, 52, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([72, 18, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([72, 52, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
    }

    // Entry and exit guide bosses.
    translate([8, 35, 24]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }

    translate([90, 35, 24]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }

    // Clamp ears for hotend retention screws.
    translate([34, 6, 14]) {
        cube([8, 10, 20], center = false);
    }
    translate([56, 6, 14]) {
        cube([8, 10, 20], center = false);
    }
}

splice_chamber_station();
