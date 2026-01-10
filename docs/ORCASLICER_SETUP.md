# OrcaSlicer Configuration for Splice3D

> Configure OrcaSlicer to generate multi-color G-code for Splice3D processing.

## Overview

To generate G-code that Splice3D can process, we configure OrcaSlicer to treat your single-extruder Centauri Carbon as a **virtual multi-extruder printer**.

This produces G-code with:
- `T0`, `T1` tool change commands
- Prime tower for color transitions
- Proper purge volumes

The Splice3D post-processor then:
1. Extracts segment lengths from tool changes
2. Generates the splice recipe
3. Strips tool changes from G-code

## Method 1: Virtual Extruder Profile (Recommended)

### Step 1: Create New Printer Profile

1. Open OrcaSlicer
2. Go to **Printer Settings** → **Add Printer**
3. Select **Centauri Carbon** as base
4. Name it: `Centauri Carbon - Splice3D`

### Step 2: Configure Multiple Extruders

In Printer Settings:

```
General:
  Extruders: 2  (or more for additional colors)

Extruder 1 (T0):
  Nozzle diameter: 0.4
  Min layer height: 0.1
  Max layer height: 0.3
  Retraction length: 0.8
  
Extruder 2 (T1):
  [Same as Extruder 1 - they're virtual]
```

### Step 3: Configure Tool Change G-code

In **Printer Settings** → **Custom G-code** → **Tool change G-code**:

```gcode
; SPLICE3D: Tool change T[next_extruder]
T[next_extruder]
```

This inserts clean tool change markers that our post-processor can detect.

### Step 4: Configure Prime Tower

In **Print Settings** → **Multiple Extruders**:

```
Enable prime tower: ✓
Prime tower width: 60mm
Prime tower brim width: 3mm
Prime tower position: Auto (or manual X/Y)
```

The prime tower is essential - it provides the purge zone where colors transition.

### Step 5: Set Purge Volumes

In **Filament Settings** → **Purge volumes**:

```
Matrix (mm³):
        To T0   To T1
From T0:  0      100
From T1:  100    0
```

Adjust based on actual testing. 100mm³ ≈ 40mm of filament.

## Method 2: M600 Color Change (Simpler)

For quick testing without full multi-extruder setup:

### In Slicer:
1. Use single extruder config
2. Add color change via **Edit** → **Add color change** at layer heights

### Post-process:
The post-processor detects `M600` commands as tool changes:

```python
# In gcode_parser.py
elif line.startswith('M600'):
    # Treat M600 as tool change
    tool_index = (tool_index + 1) % 2
```

## Exporting G-code

### Export Workflow:

1. Slice your model normally
2. Save G-code as `my_print.gcode`
3. Run post-processor:

```bash
cd postprocessor
python3 splice3d_postprocessor.py ../my_print.gcode --colors white black
```

4. Outputs:
   - `my_print_splice_recipe.json` → Send to Splice3D machine
   - `my_print_modified.gcode` → Print with spliced filament

## Recommended Print Settings

For best results with spliced filament:

```
Layer height: 0.2mm  (standard)
First layer: 0.25mm

Speeds:
  First layer: 20mm/s
  Perimeters: 45mm/s
  Infill: 60mm/s
  
Retraction:
  Length: 0.8mm (direct drive) or 4mm (Bowden)
  Speed: 35mm/s
  Z-lift: 0.2mm

Flow:
  Start with 100%
  Adjust if gaps at splices
```

## Testing Profile

For initial testing, create a simple 2-color model:

### Option 1: Calibration Cube
- 20mm cube
- Front half: Color A
- Back half: Color B
- ~4 color changes per layer

### Option 2: Vertical Strip
- 10x10x50mm tower
- Alternating 10mm stripes
- ~5 color changes total

### Option 3: Simple Vase
- Small vase mode print
- Spiral with color gradient
- Tests long continuous extrusion

## Verifying G-code Output

After slicing, check the G-code contains expected markers:

```gcode
; Look for tool changes
T0
G1 X100 Y100 E10.5  ; Moves for Color A
...
T1                   ; Tool change marker
G1 X120 Y120 E15.2  ; Moves for Color B
```

Run the post-processor with `--verbose`:

```bash
python3 splice3d_postprocessor.py test.gcode -v
```

Expected output:
```
Parsing G-code...
  Found 15 segments
  Total extrusion: 2500.5 mm
  Colors used: 2
  Layers: 100

Segments:
  1. Color 0: 150.2 mm
  2. Color 1: 80.5 mm
  ...
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| No tool changes found | Single extruder G-code | Enable 2+ extruders |
| Prime tower missing | Disabled in settings | Enable prime tower |
| Segments too short | Many color changes | Increase min segment length |
| Parser errors | Unusual G-code flavor | Check slicer flavor setting |
