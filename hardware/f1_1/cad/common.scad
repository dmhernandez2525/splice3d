// Shared constants and primitives for F1.1 mechanical design.

filament_diameter = 1.75;
ptfe_inner_diameter = 2.0;
mount_hole_diameter = 3.2;
mount_slot_width = 3.5;
mount_slot_length = 10.0;

module rounded_block(size_vec, radius = 2) {
    x = size_vec[0];
    y = size_vec[1];
    z = size_vec[2];

    minkowski() {
        cube([x - (2 * radius), y - (2 * radius), z - (2 * radius)], center = false);
        sphere(r = radius, $fn = 24);
    }
}

module m3_hole(height = 12, diameter = mount_hole_diameter) {
    cylinder(h = height, d = diameter, center = false, $fn = 32);
}

module slot_hole(length = mount_slot_length, width = mount_slot_width, height = 8) {
    hull() {
        translate([0, 0, 0]) {
            cylinder(h = height, d = width, center = false, $fn = 24);
        }
        translate([length, 0, 0]) {
            cylinder(h = height, d = width, center = false, $fn = 24);
        }
    }
}

module filament_channel(length = 30, diameter = ptfe_inner_diameter, axis = "x") {
    if (axis == "x") {
        rotate([0, 90, 0]) {
            cylinder(h = length, d = diameter, center = true, $fn = 36);
        }
    } else if (axis == "y") {
        rotate([90, 0, 0]) {
            cylinder(h = length, d = diameter, center = true, $fn = 36);
        }
    } else {
        cylinder(h = length, d = diameter, center = true, $fn = 36);
    }
}

module pc4_m6_fitting_port() {
    difference() {
        cylinder(h = 8, d = 8, center = false, $fn = 24);
        translate([0, 0, -0.5]) {
            cylinder(h = 9, d = 4.6, center = false, $fn = 24);
        }
    }
}

module modular_rail(width = 80, depth = 12, length = 210) {
    difference() {
        cube([length, width, depth], center = false);

        for (slot_x = [15 : 20 : length - 15]) {
            translate([slot_x, width * 0.5, 0]) {
                slot_hole(length = mount_slot_length, width = mount_slot_width, height = depth + 1);
            }
        }
    }
}
