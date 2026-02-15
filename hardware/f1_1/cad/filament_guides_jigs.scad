use <common.scad>;

// Filament guides and alignment jigs for repeatable assembly.

module guide_block(length = 20, width = 14, height = 12) {
    difference() {
        rounded_block([length, width, height], radius = 1);
        translate([length * 0.5, width * 0.5, height * 0.5]) {
            filament_channel(length = length + 2, diameter = 2.1, axis = "x");
        }
    }

    translate([2, width * 0.5, height - 4]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }
}

module hotend_centering_jig() {
    difference() {
        rounded_block([32, 32, 10], radius = 1);
        translate([16, 16, -0.1]) {
            cylinder(h = 10.2, d = 6.2, center = false, $fn = 28);
        }
        translate([8, 8, -0.1]) {
            m3_hole(height = 10.2, diameter = 3.2);
        }
        translate([24, 8, -0.1]) {
            m3_hole(height = 10.2, diameter = 3.2);
        }
        translate([8, 24, -0.1]) {
            m3_hole(height = 10.2, diameter = 3.2);
        }
        translate([24, 24, -0.1]) {
            m3_hole(height = 10.2, diameter = 3.2);
        }
    }
}

module cutter_square_jig() {
    difference() {
        rounded_block([36, 22, 8], radius = 1);
        translate([18, 11, 4]) {
            filament_channel(length = 40, diameter = 2.0, axis = "x");
        }
        translate([10, 2, -0.1]) {
            cube([0.8, 18, 8.2], center = false);
        }
    }
}

module encoder_pressure_jig() {
    difference() {
        rounded_block([30, 20, 10], radius = 1);
        translate([8, 10, -0.1]) {
            m3_hole(height = 10.2, diameter = 3.2);
        }
        translate([22, 10, -0.1]) {
            m3_hole(height = 10.2, diameter = 3.2);
        }
        translate([15, 10, 2]) {
            cylinder(h = 8, d = 6, center = false, $fn = 24);
        }
    }
}

module build_plate_layout() {
    translate([5, 10, 0]) {
        guide_block();
    }
    translate([35, 10, 0]) {
        guide_block();
    }
    translate([65, 10, 0]) {
        guide_block();
    }
    translate([95, 10, 0]) {
        guide_block();
    }
    translate([125, 10, 0]) {
        guide_block();
    }

    translate([5, 42, 0]) {
        hotend_centering_jig();
    }
    translate([45, 44, 0]) {
        cutter_square_jig();
    }
    translate([88, 44, 0]) {
        encoder_pressure_jig();
    }
}

build_plate_layout();
