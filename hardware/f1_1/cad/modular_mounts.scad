use <common.scad>;

// Modular station mounting rail with removable station interface pads.

module station_mount_pad(width = 50, depth = 40, height = 8) {
    difference() {
        cube([width, depth, height], center = false);

        translate([10, 10, -0.1]) {
            m3_hole(height = height + 0.2);
        }
        translate([40, 10, -0.1]) {
            m3_hole(height = height + 0.2);
        }
        translate([10, 30, -0.1]) {
            m3_hole(height = height + 0.2);
        }
        translate([40, 30, -0.1]) {
            m3_hole(height = height + 0.2);
        }

        translate([17, 20, -0.1]) {
            slot_hole(length = 16, width = 3.5, height = height + 0.2);
        }
    }
}

module modular_mount_rail() {
    union() {
        modular_rail(width = 80, depth = 10, length = 210);

        for (offset = [0 : 40 : 160]) {
            translate([offset + 8, 20, 10]) {
                station_mount_pad();
            }
        }
    }
}

modular_mount_rail();
