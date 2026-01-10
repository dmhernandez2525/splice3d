# Starry Night Vase Analysis

> Understanding the benchmark print for Splice3D validation.

## Model Overview

**Source**: [MakerWorld - Starry Night Vase](https://makerworld.com/en/models/2129520-starry-night-vase)

| Metric | Value |
|--------|-------|
| Tool changes | ~4,068 |
| Colors | 7 |
| Sizes | Small (100mm), Medium (150mm), Large (250mm) |

## Color Palette (Bambu Matte PLA)

| Tool | Color | Code |
|------|-------|------|
| T0 | Matte Charcoal | 11101 |
| T1 | Matte Dark Blue | 11602 |
| T2 | Matte Marine Blue | 11600 |
| T3 | Matte Sky Blue | 11603 |
| T4 | Matte Ice Blue | 11601 |
| T5 | Matte Apple Green | 11502 |
| T6 | Matte Lemon Yellow | 11400 |

## Current Multi-Color Printing Stats

From the MakerWorld listing:

| Printer | Filament Used | Purge Waste | Waste % | Time |
|---------|---------------|-------------|---------|------|
| H2C 7-nozzle | ~90m | ~187m | 67% | Fast |
| H2C 5-nozzle | ~186m | ~320m | 63% | Slower |
| Standard AMS | ~90m | ~800m+ | 90%+ | Very slow |

## Expected Splice3D Performance

### With Pre-Splicing

| Metric | Traditional | Splice3D | Improvement |
|--------|-------------|----------|-----------|
| Purge waste | 187m | ~40m | **79% less waste** |
| Tool changes | 4,068 | 0 | No mechanical wear |
| AMS cycles | 4,068 | 0 | No PTFE wear |
| Real-time sync | Required | Not needed | Simpler |

### Calculation

With Splice3D, waste comes only from splice buffers:
- ~4,000 splices × 10mm buffer = 40m
- vs. 187m+ with traditional purge towers

### Segment Analysis (Estimated)

Based on typical multi-color vases:

```
Segment length distribution:
  Very short (<5mm):    ~10%  - May need merging
  Short (5-20mm):       ~25%  - Prime tower artifacts
  Medium (20-100mm):    ~40%  - Main artwork
  Long (100-500mm):     ~20%  - Large single-color regions
  Very long (500mm+):   ~5%   - Background areas
```

## Challenges for Splice3D

### 1. Segment Count
4,000+ segments = 4,000+ splices
- Each splice takes ~30-60 seconds
- Total splice time: ~33-66 hours for spool prep
- Can run unattended overnight

### 2. Seven Colors
V1 Splice3D supports 2 colors.
Options:
- **V1**: Build 2-color version first (simpler art)
- **V2**: Add selector mechanism for 7 inputs
- **Alternative**: Run 3-4 passes, manually swap input spools

### 3. Very Short Segments
Some segments may be <5mm (single pixel of art).
Solution: Merge small segments (already implemented in recipe generator)

### 4. Precision Requirements
Color alignment must be accurate across all 4,000 transitions.
- Dimple encoding will help track position
- Start with 2-color test to validate drift before full benchmark

## Recommended Test Progression

### Stage 1: Basic Validation
- 2 colors (black + white)
- Simple geometric pattern
- ~50 tool changes
- Validate splice strength

### Stage 2: Complexity Test  
- 2 colors
- Gradient pattern
- ~500 tool changes
- Validate position tracking

### Stage 3: Multi-Color Prep
- Add selector mechanism for 4+ colors
- Test color switching reliability

### Stage 4: Starry Night Attempt
- All 7 colors
- Full 4,000+ changes
- Medium size (150mm) first

## G-code Analysis To-Do

When you have actual Starry Night G-code:

```bash
# Analyze with post-processor
python3 splice3d_postprocessor.py starry_night_medium.gcode -v

# Expected output:
#   Segments: ~4,000
#   Colors: 7
#   Total length: ~90,000mm (90m)
#   Shortest segment: ?mm
#   Longest segment: ?mm
#   Average segment: ~22mm
```

## Success Criteria

✅ **Print matches original colors** within acceptable tolerance
✅ **No visible splice artifacts** on exterior surface
✅ **All 4,000 splices hold** through entire print
✅ **Position accuracy** maintained (no color drift)
✅ **Time competitive** with traditional methods
