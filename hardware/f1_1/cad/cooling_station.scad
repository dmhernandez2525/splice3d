use <common.scad>;

// Cooling station with fan duct and integrated heat sink clamp.

module cooling_station() {
    difference() {
        rounded_block([88, 62, 50], radius = 1.5);

        // Filament path continuation.
        translate([44, 31, 25]) {
            filament_channel(length = 80, diameter = 2.05, axis = "x");
        }

        // Fan cavity for 4010 blower.
        translate([8, 10, 18]) {
            cube([24, 42, 30], center = false);
        }

        // Duct throat toward splice exit.
        translate([30, 22, 20]) {
            cube([30, 18, 12], center = false);
        }

        // Heat sink window to pull air across splice.
        translate([58, 18, 10]) {
            cube([22, 26, 24], center = false);
        }

        // Mounting slots.
        translate([18, 16, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([18, 46, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([62, 16, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([62, 46, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
    }

    // Fan screw bosses.
    for (x = [10, 30]) {
        for (y = [12, 50]) {
            translate([x, y, 15]) {
                difference() {
                    cylinder(h = 20, d = 7, center = false, $fn = 24);
                    m3_hole(height = 21, diameter = 3.2);
                }
            }
        }
    }

    // PTFE fittings.
    translate([6, 31, 25]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }
    translate([82, 31, 25]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }
}

cooling_station();
