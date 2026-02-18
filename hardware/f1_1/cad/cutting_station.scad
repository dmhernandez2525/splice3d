use <common.scad>;

// SG90 cutter enclosure with blade guide and aligned filament channel.

module cutting_station_enclosure() {
    difference() {
        rounded_block([120, 72, 45], radius = 1.5);

        // Servo body pocket (SG90 nominal 23x12.2x24mm with clearance).
        translate([16, 24, 10]) {
            cube([26, 16, 28], center = false);
        }

        // Servo cable slot.
        translate([8, 31, 6]) {
            cube([12, 8, 8], center = false);
        }

        // Blade travel slot.
        translate([58, 33.5, 6]) {
            cube([20, 5, 28], center = false);
        }

        // Main filament channel through cutter body.
        translate([72, 36, 22]) {
            filament_channel(length = 84, diameter = 2.1, axis = "x");
        }

        // Mounting slots for modular rail.
        translate([28, 20, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([28, 52, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([86, 20, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([86, 52, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
    }

    // PTFE input fitting boss.
    translate([20, 36, 18]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }

    // PTFE output fitting boss.
    translate([104, 36, 18]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }
}

module blade_alignment_insert() {
    difference() {
        cube([26, 14, 8], center = false);
        translate([4, 7, 4]) {
            rotate([0, 90, 0]) {
                filament_channel(length = 24, diameter = 2.0, axis = "x");
            }
        }
        translate([10, 1, -0.1]) {
            cube([0.9, 12, 8.2], center = false);
        }
    }
}

cutting_station_enclosure();
