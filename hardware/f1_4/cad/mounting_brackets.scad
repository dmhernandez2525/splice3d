use <../../f1_1/cad/common.scad>;

// Internal mounts for SKR board, steppers, and power supply.

module skr_mount() {
    difference() {
        cube([100, 70, 6], center = false);
        for (x = [12, 88]) {
            for (y = [12, 58]) {
                translate([x, y, -0.1]) {
                    m3_hole(height = 7);
                }
            }
        }
    }

    for (x = [12, 88]) {
        for (y = [12, 58]) {
            translate([x, y, 6]) {
                cylinder(h = 8, d = 8, $fn = 24);
            }
        }
    }
}

module nema17_mount() {
    difference() {
        cube([52, 52, 6], center = false);

        translate([26, 26, -0.1]) {
            cylinder(h = 7, d = 24, $fn = 36);
        }

        for (x = [10.5, 41.5]) {
            for (y = [10.5, 41.5]) {
                translate([x, y, -0.1]) {
                    m3_hole(height = 7);
                }
            }
        }
    }
}

module psu_mount() {
    difference() {
        cube([112, 50, 8], center = false);

        for (x = [12, 56, 100]) {
            translate([x, 25, -0.1]) {
                m3_hole(height = 9);
            }
        }

        translate([20, 10, 2]) {
            cube([72, 30, 7], center = false);
        }
    }
}

module mounting_brackets_layout() {
    translate([6, 6, 0]) {
        skr_mount();
    }

    translate([118, 6, 0]) {
        nema17_mount();
    }

    translate([118, 66, 0]) {
        nema17_mount();
    }

    translate([6, 84, 0]) {
        psu_mount();
    }
}

mounting_brackets_layout();
