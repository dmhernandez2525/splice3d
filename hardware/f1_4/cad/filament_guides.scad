use <../../f1_1/cad/common.scad>;

// Guide tubes and entry/exit fittings with smooth internal channels.

module guide_fitting_block(length = 28, width = 16, height = 14) {
    difference() {
        rounded_block([length, width, height], radius = 1);

        translate([length * 0.5, width * 0.5, height * 0.5]) {
            filament_channel(length = length + 4, diameter = 2.1, axis = "x");
        }

        translate([4, width * 0.5, height * 0.5]) {
            rotate([0, 90, 0]) {
                cylinder(h = length - 8, d = 4.8, center = true, $fn = 28);
            }
        }
    }

    translate([2, width * 0.5, height - 5]) {
        rotate([0, 90, 0]) {
            pc4_m6_fitting_port();
        }
    }
}

module curved_transition_guide() {
    difference() {
        rounded_block([38, 24, 16], radius = 1);

        // Smooth bend path through guide.
        hull() {
            translate([8, 12, 8]) {
                rotate([0, 90, 0]) {
                    cylinder(h = 3, d = 2.2, center = true, $fn = 28);
                }
            }
            translate([30, 16, 10]) {
                rotate([15, 90, 0]) {
                    cylinder(h = 3, d = 2.2, center = true, $fn = 28);
                }
            }
        }
    }
}

module filament_guides_layout() {
    for (x = [6, 40, 74, 108, 142]) {
        translate([x, 8, 0]) {
            guide_fitting_block();
        }
    }

    translate([10, 36, 0]) {
        curved_transition_guide();
    }
    translate([56, 36, 0]) {
        curved_transition_guide();
    }
    translate([102, 36, 0]) {
        curved_transition_guide();
    }
}

filament_guides_layout();
