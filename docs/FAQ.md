# Frequently Asked Questions

> Common questions about Splice3D.

## General

### What is Splice3D?

Splice3D is an open-source system that pre-joins multiple colors of filament into a single spool. This lets you print multi-color objects on any single-extruder 3D printer without tool changers or AMS systems.

### How is this different from Mosaic Palette?

| Feature | Mosaic Palette | Splice3D |
|---------|---------------|----------|
| Price | $600-900 | ~$200 DIY |
| Method | Real-time splicing | Pre-spliced spool |
| Colors | Up to 8 | 2 (V1), 7+ planned |
| Complexity | Integrated system | Separate prep step |
| Open Source | No | Yes |

### What printers does it work with?

Any FDM printer with a standard 1.75mm filament path. The splicer is independent of your printer - you just load the pre-spliced spool like normal filament.

### What slicers are supported?

Currently: **OrcaSlicer** (including BambuStudio profiles)

The parser looks for standard `T0`, `T1` tool change commands and `M600` color change commands.

---

## Hardware

### What parts do I need?

See [BOM.md](BOM.md) for the full list. Key components:
- BTT SKR Mini E3 v2 board
- 3x NEMA17 motors (from Ender 3)
- Hotend assembly (weld chamber)
- SG90 servo (cutter)
- ~$170-250 total

### Can I use a different controller board?

Yes, but you'll need to update pin mappings in `config.h`. Any 32-bit board with 4 stepper outputs should work.

### What filaments work?

**V1 Tested:**
- PLA ✓
- PLA+ ✓
- Matte PLA ✓

**Should work (needs testing):**
- PETG
- ABS/ASA

**Not recommended:**
- TPU (flexible = feeding issues)
- Wood-fill (may clog)

### How long does splicing take?

~45 seconds per splice. A print with 100 color changes takes about 75 minutes to prepare.

For the Starry Night Vase (4000+ changes): ~50 hours of splice prep time.

---

## Software

### How do I process G-code?

```bash
cd postprocessor
python splice3d_postprocessor.py your_model.gcode --colors white black
```

This creates:
- `your_model_splice_recipe.json` - Send to machine
- `your_model_modified.gcode` - Print with spliced spool

### Why is my recipe empty?

Your G-code doesn't contain tool changes. Check:
1. OrcaSlicer configured for 2+ extruders
2. Different colors assigned to model parts
3. Tool change commands present (`T0`, `T1`, or `M600`)

### Can I test without hardware?

Yes! Use the simulator:

```bash
cd cli
python simulator.py ../samples/test_multicolor_splice_recipe.json
```

---

## Troubleshooting

### Colors are in wrong positions

**Cause:** Filament feed calibration is off.

**Fix:** Recalibrate steps/mm:
1. Mark filament 100mm from extruder
2. Feed 100mm
3. Measure actual distance
4. Calculate: `new_steps = current_steps × (100 / actual)`

### Splices are weak (break easily)

**Causes:**
- Temperature too low
- Hold time too short
- Moisture in filament

**Fixes:**
- Increase splice temp +10°C
- Increase hold time +1s
- Dry filament before use

### Splices are too fat (jam in Bowden)

**Causes:**
- Temperature too high
- PTFE tube worn
- Over-compression

**Fixes:**
- Decrease temp -10°C
- Replace 2mm ID PTFE tube
- Reduce compression distance

---

## Future Plans

### Will there be more colors?

Yes! V2-V3 will add a selector mechanism for 4-7+ colors.

### Will there be Wi-Fi?

Planned for V3+. Will use ESP32 for wireless control and web interface.

### Can I contribute?

Absolutely! See [CONTRIBUTING.md](../CONTRIBUTING.md). Areas where help is welcome:
- Hardware testing
- CAD for printable parts
- Documentation
- Slicer plugins
