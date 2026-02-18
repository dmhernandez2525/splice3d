use <../../f1_1/cad/common.scad>;

// Tool holders for hex keys, spare blades, and PTFE offcuts.

module hex_key_holder() {
    difference() {
        cube([54, 24, 18], center = false);
        for (x = [8, 16, 24, 32, 40, 48]) {
            translate([x, 12, -0.1]) {
                cylinder(h = 16, d = 3.2, $fn = 20);
            }
        }
    }
}

module blade_magazine() {
    difference() {
        cube([42, 30, 10], center = false);
        for (x = [8, 18, 28]) {
            translate([x, 6, 2]) {
                cube([8, 18, 8.2], center = false);
            }
        }
    }

    // Snap tab for mounting onto enclosure wall.
    translate([16, 29, 4]) {
        cube([10, 3, 5], center = false);
    }
}

module ptfe_spool_clip() {
    difference() {
        rounded_block([36, 24, 14], radius = 1);
        translate([18, 12, 7]) {
            rotate([0, 90, 0]) {
                cylinder(h = 30, d = 10, center = true, $fn = 24);
            }
        }
    }

    translate([4, 22, 4]) {
        cube([10, 2, 5], center = false);
    }
}

module accessory_layout() {
    translate([8, 8, 0]) {
        hex_key_holder();
    }

    translate([72, 8, 0]) {
        blade_magazine();
    }

    translate([124, 8, 0]) {
        ptfe_spool_clip();
    }
}

accessory_layout();
