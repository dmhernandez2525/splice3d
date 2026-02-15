# F1.4 Printed Parts CAD

This directory contains OpenSCAD source for the full printed-parts package.

## Parts

1. `enclosure_bottom.scad`
2. `enclosure_top.scad`
3. `mounting_brackets.scad`
4. `filament_guides.scad`
5. `tool_accessory_mounts.scad`
6. `vent_ducts.scad`
7. `spool_holder.scad`
8. `cable_management.scad`
9. `assembly_overview.scad`

## Validation

```bash
python3 scripts/hardware/validate_f1_4.py
python3 -m unittest postprocessor.tests.test_printed_parts_validation -v
```

## Notes

1. All functional parts stay within `220x220mm` print envelope.
2. Snap-fit joints are used on enclosure and accessory interfaces.
3. Critical channels and clips are modeled for support-free printing in their recommended orientation.
