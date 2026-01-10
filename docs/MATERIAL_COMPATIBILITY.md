# Material Compatibility Matrix

> Which filaments can be spliced together.

## Compatibility Rules

**General Rule:** Only splice materials from the same family.

Splicing works by melting the ends together. Materials must:
1. Have similar melting temperatures
2. Bond chemically when molten
3. Cool to similar hardness

## Compatibility Matrix

✅ = Compatible | ⚠️ = Possible (test first) | ❌ = Incompatible

### PLA Family

|  | PLA | PLA+ | PLA Matte | PLA Silk | PLA Wood |
|--|-----|------|-----------|----------|----------|
| **PLA** | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **PLA+** | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **PLA Matte** | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **PLA Silk** | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **PLA Wood** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ |

**Notes:**
- PLA Wood may need lower temp (200°C) to avoid burning fibers
- Silk PLA may need slightly higher temp (220°C)

### PETG Family

|  | PETG | PETG+ | PETG-CF |
|--|------|-------|---------|
| **PETG** | ✅ | ✅ | ⚠️ |
| **PETG+** | ✅ | ✅ | ⚠️ |
| **PETG-CF** | ⚠️ | ⚠️ | ✅ |

**Notes:**
- Carbon fiber variants may wear the splice chamber
- Higher temps needed (235-245°C)

### ABS/ASA Family

|  | ABS | ASA | ABS+ |
|--|-----|-----|------|
| **ABS** | ✅ | ✅ | ✅ |
| **ASA** | ✅ | ✅ | ✅ |
| **ABS+** | ✅ | ✅ | ✅ |

**Notes:**
- Requires good ventilation (fumes)
- Highest temp needed (250°C)
- ABS and ASA are chemically similar

### Cross-Family (NOT Recommended)

|  | PLA | PETG | ABS | TPU |
|--|-----|------|-----|-----|
| **PLA** | ✅ | ❌ | ❌ | ❌ |
| **PETG** | ❌ | ✅ | ❌ | ❌ |
| **ABS** | ❌ | ❌ | ✅ | ❌ |
| **TPU** | ❌ | ❌ | ❌ | ⚠️ |

**Why cross-family fails:**
- Different melting points
- No chemical bond between different polymers
- Splice will be weak or fail completely

## Splice Parameters by Material

| Material | Temp (°C) | Heat Time (ms) | Compression (mm) | Cooling (ms) |
|----------|-----------|----------------|------------------|--------------|
| PLA | 210 | 3000 | 2.0 | 5000 |
| PLA Matte | 215 | 3200 | 2.0 | 5000 |
| PLA Silk | 220 | 3500 | 2.0 | 5500 |
| PLA Wood | 200 | 2500 | 1.8 | 4000 |
| PETG | 235 | 3500 | 2.5 | 6000 |
| ABS | 250 | 4000 | 2.5 | 7000 |
| ASA | 255 | 4000 | 2.5 | 7000 |

## Brand-Specific Notes

### Bambu Lab
- Matte PLA: Works great at 215°C
- PLA-CF: Not recommended (carbon fiber)

### Polymaker
- PolyTerra: Lower temp (205°C)
- PolyMax: Standard PLA settings

### Overture
- Standard PLA: Works at default settings
- PETG: May need +5°C

### Hatchbox
- PLA: Standard settings
- Good consistency

## Testing New Materials

Before committing to a large print:

1. **Test splice strength:**
   - Create 2-segment recipe (A → B)
   - Bend splice 90° - should not break
   - Pull test: should hold ~2kg

2. **Test diameter:**
   - Measure splice point with calipers
   - Should be 1.75mm ± 0.05mm
   - >1.85mm may jam in Bowden

3. **Test print:**
   - Small 2-color calibration cube
   - Check color transitions
   - Verify no gaps at splices
