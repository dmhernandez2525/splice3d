# Phase 2: Software & Slicer Integration

## Overview

Build the G-code analysis software, desktop control application, and slicer integrations.

**Goal:** Full software pipeline from slicer to spliced filament

---

## Milestones

### M1: G-code Parser (Week 1)

- [ ] Multi-color G-code parser
  - Support PrusaSlicer format
  - Support OrcaSlicer/BambuStudio format
  - Support Cura format
- [ ] Tool change extraction
  - T0, T1, T2, etc. command parsing
  - M600 color change parsing
  - Wipe tower detection
- [ ] Extrusion tracking
  - Absolute E value parsing
  - Relative E value handling
  - Retraction detection
- [ ] Position calculation
  - Filament length between tool changes
  - Account for retractions
  - Handle print resume scenarios

**Supported G-code Commands:**
```
T0, T1, T2, ... Tn    # Tool changes
M600                  # Manual color change
G1 E{value}           # Extrusion
G92 E0                # E reset
```

**Acceptance Criteria:**
- Parses PrusaSlicer multi-color G-code
- Parses OrcaSlicer AMS G-code
- Correctly calculates filament lengths ±1mm

### M2: Splice Planner Algorithm (Week 1-2)

- [ ] Splice position calculator
  - Account for transition length (hotend-specific)
  - Add splice overlap amount
  - Handle minimum segment lengths
- [ ] Waste optimizer
  - Minimize transition waste
  - Purge-to-infill opportunities
  - Sparse purge tower detection
- [ ] Error handling
  - Too-short segments warning
  - Incompatible material pairs
  - Position overflow detection

**Splice Plan Format:**
```json
{
  "version": "1.0",
  "printer_profile": "bambu_x1c",
  "total_length_mm": 15234.5,
  "splices": [
    {
      "position_mm": 0,
      "color": "Color1",
      "material": "PLA",
      "to_color": null
    },
    {
      "position_mm": 1523.4,
      "color": "Color1",
      "material": "PLA",
      "to_color": "Color2",
      "splice_temp": 220
    },
    ...
  ]
}
```

**Acceptance Criteria:**
- Generates valid splice plan from G-code
- Handles edge cases (single color, no changes)
- Optimizes waste where possible

### M3: CLI Analyzer Tool (Week 2)

- [ ] Python CLI application
  - Click-based interface
  - Input G-code file
  - Output splice plan (JSON/CSV)
  - Verbose mode for debugging
- [ ] Printer profiles
  - Transition length per printer
  - Default material temperatures
  - Hotend configuration
- [ ] Validation and preview
  - Dry-run mode
  - Estimated splice count
  - Filament usage summary

**CLI Usage:**
```bash
# Basic usage
splice3d analyze model.gcode -o splice_plan.json

# With printer profile
splice3d analyze model.gcode --profile bambu_x1c

# Dry run
splice3d analyze model.gcode --dry-run

# Verbose output
splice3d analyze model.gcode -v
```

**Acceptance Criteria:**
- CLI installs via pip
- Processes typical G-code in <5 seconds
- Output validates against schema

### M4: Desktop Control Application (Week 3-4)

- [ ] Electron/Tauri application framework
- [ ] Device connection
  - Serial/USB detection
  - Connection status
  - Auto-reconnect
- [ ] Splice job management
  - Load splice plan
  - Start/pause/stop controls
  - Progress visualization
- [ ] Real-time monitoring
  - Position tracking display
  - Temperature graph
  - Splice status (current/total)
- [ ] Manual controls
  - Jog filament forward/backward
  - Heat/cool commands
  - Test splice button

**UI Features:**
| Screen | Features |
|--------|----------|
| Home | Device status, quick actions |
| Job | Load file, preview, start splice |
| Monitor | Real-time position, temp, progress |
| Settings | Profiles, calibration, preferences |
| History | Past splice jobs, statistics |

**Acceptance Criteria:**
- Connects to Splice3D hardware reliably
- Displays real-time splice progress
- Manual controls work as expected

### M5: Material Profile System (Week 4)

- [ ] Built-in material profiles
  - PLA (multiple brands)
  - PETG (multiple brands)
  - ABS
  - ASA
  - TPU/TPE
- [ ] Profile parameters
  - Splice temperature
  - Heat time
  - Cool time
  - Compression force
- [ ] Cross-material compatibility
  - PLA↔PETG settings
  - Incompatible pairs warnings
- [ ] Custom profile creation
  - Import/export profiles
  - Community profile sharing

**Material Profile Format:**
```yaml
name: "Generic PLA"
type: "PLA"
splice:
  temperature: 220
  heat_time_ms: 1500
  cool_time_ms: 2000
  compression_mm: 0.5
compatible_with:
  - PLA
  - PLA+
incompatible_with:
  - ABS
  - ASA
```

**Acceptance Criteria:**
- Profiles for 5+ common materials
- Cross-material splice settings
- Custom profiles save/load

### M6: Slicer Plugin - PrusaSlicer (Week 5)

- [ ] Post-processing script
  - Python-based processor
  - Extracts tool changes
  - Generates splice file
- [ ] Profile integration
  - Custom printer profile
  - Multi-material wizard
  - Splice3D-specific settings
- [ ] Documentation
  - Installation guide
  - Configuration guide
  - Troubleshooting

**PrusaSlicer Integration:**
```bash
# Post-processing script path
/path/to/splice3d_postprocess.py [input_file]

# Outputs:
# - Modified G-code (optional header)
# - splice_plan.json alongside G-code
```

**Acceptance Criteria:**
- Post-processor works with PrusaSlicer
- Generates valid splice plan
- Documentation complete

### M7: Slicer Plugin - OrcaSlicer (Week 5-6)

- [ ] OrcaSlicer post-processor
  - Handle Bambu-style G-code
  - AMS filament mapping
  - Support flush volumes
- [ ] Bambu printer profiles
  - X1 Carbon
  - P1P/P1S
  - A1/A1 Mini
- [ ] Creality printer profiles
  - K1/K1 Max
  - Ender 3 V3

**Acceptance Criteria:**
- Works with OrcaSlicer for Bambu printers
- Handles AMS-style color changes
- Profiles for popular printers

### M8: Testing & Documentation (Week 6)

- [ ] End-to-end testing
  - Test print suite (2-8 colors)
  - Different printers (Bambu, Creality, Prusa)
  - Various materials
- [ ] Performance testing
  - Large file parsing speed
  - Long splice job stability
  - Memory usage profiling
- [ ] Documentation
  - User guide
  - API reference
  - Video tutorials
  - FAQ/troubleshooting

**Test Matrix:**
| Printer | Colors | Materials | Result |
|---------|--------|-----------|--------|
| Bambu X1C | 4 | PLA | Pass |
| Bambu P1S | 2 | PETG | Pass |
| Creality K1 | 3 | PLA | Pass |
| Prusa MK4 | 5 | Mixed | Pass |

**Acceptance Criteria:**
- All test prints complete successfully
- Documentation covers all features
- Known issues documented

---

## Technical Requirements

### G-code Parser Performance

| Metric | Target |
|--------|--------|
| Parse time (100MB file) | <10 seconds |
| Memory usage | <500MB |
| Supported file size | Up to 1GB |

### Control App Requirements

| Platform | Support |
|----------|---------|
| Windows | 10/11 64-bit |
| macOS | 12+ (Intel/Apple Silicon) |
| Linux | Ubuntu 22.04+ |

### Slicer Compatibility

| Slicer | Version |
|--------|---------|
| PrusaSlicer | 2.7+ |
| OrcaSlicer | 2.0+ |
| BambuStudio | 1.9+ |
| Cura | 5.0+ (stretch goal) |

---

## Definition of Done

- [ ] All milestones complete
- [ ] G-code parser handles all major slicers
- [ ] Splice planner generates accurate plans
- [ ] Desktop app connects and controls hardware
- [ ] Material profiles for common filaments
- [ ] PrusaSlicer and OrcaSlicer plugins working
- [ ] 95%+ successful test prints
- [ ] Documentation complete
- [ ] 80%+ test coverage
