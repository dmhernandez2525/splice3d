use <common.scad>;

// Encoder wheel mount with spring loaded idler arm.

module encoder_station() {
    difference() {
        rounded_block([84, 66, 52], radius = 1.5);

        // Filament path through encoder nip point.
        translate([42, 33, 28]) {
            filament_channel(length = 72, diameter = 2.05, axis = "x");
        }

        // Encoder wheel cavity.
        translate([26, 18, 18]) {
            cube([20, 30, 26], center = false);
        }

        // Idler arm cavity.
        translate([50, 16, 16]) {
            cube([20, 34, 30], center = false);
        }

        // Spring seat pocket.
        translate([62, 28, 12]) {
            cylinder(h = 16, d = 8, center = false, $fn = 24);
        }

        // Mounting slots.
        translate([16, 16, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([16, 50, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([56, 16, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
        translate([56, 50, -0.1]) {
            slot_hole(length = 12, width = 3.5, height = 8);
        }
    }

    // Encoder axle bosses.
    translate([34, 14, 30]) {
        rotate([90, 0, 0]) {
            cylinder(h = 38, d = 6, center = false, $fn = 24);
        }
    }

    translate([54, 14, 30]) {
        rotate([90, 0, 0]) {
            cylinder(h = 38, d = 6, center = false, $fn = 24);
        }
    }

    // PTFE fitting ports.
    translate([6, 33, 28]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }

    translate([78, 33, 28]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }
}

module encoder_idler_arm() {
    difference() {
        rounded_block([42, 14, 10], radius = 1);
        translate([6, 7, -0.1]) {
            m3_hole(height = 11, diameter = 3.2);
        }
        translate([32, 7, -0.1]) {
            m3_hole(height = 11, diameter = 3.2);
        }
    }
}

encoder_station();
