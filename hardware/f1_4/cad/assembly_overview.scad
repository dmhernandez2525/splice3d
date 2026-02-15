use <enclosure_bottom.scad>;
use <enclosure_top.scad>;
use <mounting_brackets.scad>;
use <filament_guides.scad>;
use <tool_accessory_mounts.scad>;
use <vent_ducts.scad>;
use <spool_holder.scad>;
use <cable_management.scad>;

// Phase F1.4 exploded visual overview.

module overview() {
    color([0.83, 0.86, 0.9]) {
        enclosure_bottom();
    }

    translate([0, 0, 44]) {
        color([0.75, 0.8, 0.85]) {
            enclosure_top();
        }
    }

    translate([14, 14, 6]) {
        color([0.86, 0.74, 0.6]) {
            mounting_brackets_layout();
        }
    }

    translate([14, 140, 6]) {
        color([0.7, 0.9, 0.7]) {
            filament_guides_layout();
        }
    }

    translate([100, 170, 6]) {
        color([0.92, 0.78, 0.62]) {
            accessory_layout();
        }
    }

    translate([220, 0, 0]) {
        color([0.7, 0.86, 0.95]) {
            vent_layout();
        }
    }

    translate([220, 130, 0]) {
        color([0.85, 0.85, 0.85]) {
            spool_holder_assembly();
        }
    }

    translate([0, 240, 0]) {
        color([0.8, 0.92, 0.72]) {
            cable_management_layout();
        }
    }
}

overview();
