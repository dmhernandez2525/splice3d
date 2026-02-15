use <cutting_station.scad>;
use <splice_chamber_station.scad>;
use <cooling_station.scad>;
use <encoder_station.scad>;
use <filament_guides_jigs.scad>;
use <modular_mounts.scad>;

// Exploded assembly with numbered callouts.

module callout(number_text, position) {
    translate(position) {
        color([0.1, 0.1, 0.1]) {
            linear_extrude(height = 1.2) {
                text(number_text, size = 8, halign = "center", valign = "center");
            }
        }
    }
}

module assembly_exploded() {
    color([0.8, 0.8, 0.85]) {
        modular_mount_rail();
    }
    callout("1", [16, 86, 2]);

    translate([8, 4, 28]) {
        color([0.9, 0.72, 0.52]) {
            cutting_station_enclosure();
        }
    }
    callout("2", [55, 82, 30]);

    translate([82, 6, 40]) {
        color([0.92, 0.58, 0.42]) {
            splice_chamber_station();
        }
    }
    callout("3", [125, 84, 44]);

    translate([150, 10, 52]) {
        color([0.56, 0.76, 0.9]) {
            cooling_station();
        }
    }
    callout("4", [190, 80, 56]);

    translate([200, 8, 64]) {
        color([0.58, 0.88, 0.62]) {
            encoder_station();
        }
    }
    callout("5", [236, 80, 68]);

    translate([32, 92, 24]) {
        color([0.84, 0.84, 0.84]) {
            build_plate_layout();
        }
    }
    callout("6", [106, 154, 26]);
}

assembly_exploded();
