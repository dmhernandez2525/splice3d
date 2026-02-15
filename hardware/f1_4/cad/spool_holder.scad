use <../../f1_1/cad/common.scad>;

// Spool holder for standard 1kg spools (200mm OD, 55mm hub).

module spool_side_stand() {
    difference() {
        rounded_block([90, 20, 90], radius = 2);

        // Axle slot for 8mm rod, supports 55mm hub width stack.
        translate([45, 10, 62]) {
            rotate([90, 0, 0]) {
                cylinder(h = 22, d = 8.3, center = true, $fn = 28);
            }
        }

        // Weight reduction pocket.
        translate([24, 4, 18]) {
            cube([42, 14, 50], center = false);
        }

        // Base mounting holes.
        translate([20, 10, -0.1]) {
            m3_hole(height = 8);
        }
        translate([70, 10, -0.1]) {
            m3_hole(height = 8);
        }
    }
}

module spool_base() {
    difference() {
        cube([210, 120, 8], center = false);

        for (x = [20, 50, 80, 130, 160, 190]) {
            translate([x, 20, -0.1]) {
                m3_hole(height = 9);
            }
            translate([x, 100, -0.1]) {
                m3_hole(height = 9);
            }
        }
    }
}

module spool_holder_assembly() {
    spool_base();

    translate([18, 50, 8]) {
        spool_side_stand();
    }

    translate([102, 50, 8]) {
        spool_side_stand();
    }

    // Cross brace and rod support for 55mm hub clearance.
    translate([52, 56, 58]) {
        cube([50, 8, 8], center = false);
    }
}

spool_holder_assembly();
