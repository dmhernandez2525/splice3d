use <cutting_station.scad>;
use <splice_chamber_station.scad>;
use <cooling_station.scad>;
use <encoder_station.scad>;
use <filament_guides_jigs.scad>;
use <modular_mounts.scad>;

// Compact assembly view for fit verification.

module assembly_compact() {
    modular_mount_rail();

    translate([8, 4, 10]) {
        cutting_station_enclosure();
    }

    translate([82, 6, 10]) {
        splice_chamber_station();
    }

    translate([150, 10, 10]) {
        cooling_station();
    }

    translate([200, 8, 10]) {
        encoder_station();
    }

    translate([32, 92, 0]) {
        build_plate_layout();
    }
}

assembly_compact();
