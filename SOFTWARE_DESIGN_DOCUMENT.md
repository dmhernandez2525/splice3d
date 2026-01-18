# Software Design Document - Splice3D

## 1. Overview

### Project Purpose and Goals

Splice3D is an open-source system that enables multi-color 3D printing on any single-extruder FDM printer by pre-splicing filament segments into a continuous spool before printing. Unlike traditional multi-material systems (AMS, Palette, MMU) that swap filaments during printing, Splice3D creates a pre-joined filament spool with color transitions precisely calculated to align with extrusion points in the print.

**Primary Goals:**
- Enable multi-color printing on any single-extruder printer
- Drastically reduce filament waste (from ~67% to ~5% purge waste)
- Eliminate real-time tool changes and associated mechanical wear
- Support prints with thousands of color changes (target: Starry Night Vase with 4000+ transitions)

### Target Users

1. **Makers and Hobbyists**: Users with basic single-extruder printers wanting multi-color capability
2. **Print Farms**: High-volume operations seeking reduced waste and faster turnaround
3. **DIY Enthusiasts**: Users who enjoy building custom hardware from donor parts (e.g., Ender 3)

### Key Features

- G-code parsing for OrcaSlicer, PrusaSlicer, and BambuStudio formats
- Automatic filament segment length extraction from multi-tool G-code
- JSON recipe generation for the splicing machine
- G-code modification for single-extruder printing
- Firmware simulator for testing without hardware
- CLI and GUI interfaces for post-processing
- Comprehensive filament profile database with splice parameters

---

## 2. Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SPLICE3D SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐        │
│   │   SLICER    │    │  POST-PROCESSOR  │    │   SPLICE MACHINE    │        │
│   │ (OrcaSlicer)│───>│     (Python)     │───>│    (Firmware/C++)   │        │
│   └─────────────┘    └──────────────────┘    └─────────────────────┘        │
│         │                    │                        │                      │
│   Multi-tool           ┌─────┴─────┐           ┌──────┴──────┐              │
│   G-code               │           │           │             │              │
│                   Recipe.json  Modified.gcode  │  Pre-spliced │              │
│                        │           │           │    Spool     │              │
│                        v           v           └──────┬───────┘              │
│                   ┌────────────────┐                  │                      │
│                   │ SPLICE MACHINE │                  v                      │
│                   │   (Hardware)   │           ┌─────────────┐              │
│                   └────────────────┘           │   PRINTER   │              │
│                                                │ (Any FDM)   │              │
│                                                └─────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

| Component | Technology | Purpose |
|-----------|------------|---------|
| Post-Processor | Python 3.9+ | Parse G-code, generate recipes, modify files |
| CLI Tools | Python (argparse) | Command-line interface for all operations |
| GUI | Python (tkinter) | Graphical interface for post-processing |
| Simulator | Python | Test firmware logic without hardware |
| Firmware | C++ (PlatformIO) | Control physical splicing hardware |
| Hardware | BTT SKR Mini E3 | Stepper control, heater, servo actuation |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SLICING PHASE                                                            │
│     ┌──────────┐         ┌──────────────┐                                   │
│     │  Model   │ ──────> │  OrcaSlicer  │ ──────> Multi-tool G-code         │
│     │ (STL/3MF)│         │(Virtual MMU) │         (T0, T1, ... commands)    │
│     └──────────┘         └──────────────┘                                   │
│                                                                              │
│  2. POST-PROCESSING PHASE                                                    │
│     ┌────────────────┐                                                       │
│     │ GCodeParser    │ ──> Segments[] (color, length, line numbers)         │
│     └────────────────┘                                                       │
│              │                                                               │
│              v                                                               │
│     ┌────────────────┐                                                       │
│     │ RecipeGenerator│ ──> splice_recipe.json                               │
│     └────────────────┘                                                       │
│              │                                                               │
│              v                                                               │
│     ┌────────────────┐                                                       │
│     │ GCodeModifier  │ ──> modified_print.gcode (tool changes removed)      │
│     └────────────────┘                                                       │
│                                                                              │
│  3. SPLICING PHASE                                                           │
│     ┌────────────────┐         ┌────────────────┐                           │
│     │ Recipe JSON    │ ──────> │ Splice Machine │ ──────> Pre-spliced Spool │
│     └────────────────┘         │ (via USB CLI)  │                           │
│                                └────────────────┘                           │
│                                                                              │
│  4. PRINTING PHASE                                                           │
│     ┌────────────────┐         ┌────────────────┐                           │
│     │ Modified G-code│ ──────> │  Any Printer   │ ──────> Finished Print    │
│     │ + Spliced Spool│         │(single extruder)│                          │
│     └────────────────┘         └────────────────┘                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Design

### 3.1 Post-Processor Package (`postprocessor/`)

#### `gcode_parser.py` - G-code Parsing

**Purpose**: Parse multi-tool G-code files and extract filament segment information.

**Responsibilities**:
- Detect tool change commands (T0, T1, etc.) and M600 color changes
- Track extrusion amounts in both absolute (M82) and relative (M83) modes
- Handle G92 E reset commands
- Extract layer information from slicer comments
- Support OrcaSlicer, PrusaSlicer, and BambuStudio formats

**Key Classes**:
```python
@dataclass
class Segment:
    color_index: int      # Tool number (0, 1, 2, ...)
    length_mm: float      # Extrusion length in mm
    start_line: int       # Starting line in G-code
    end_line: int         # Ending line in G-code
    layer_start: int      # Starting layer
    layer_end: int        # Ending layer

@dataclass
class ParseResult:
    segments: list[Segment]
    total_length_mm: float
    color_count: int
    layer_count: int
    errors: list[str]
    warnings: list[str]

class GCodeParser:
    def parse_file(filepath: str) -> ParseResult
    def parse_lines(lines: list[str]) -> ParseResult
```

#### `recipe_generator.py` - Recipe Generation

**Purpose**: Convert parsed segments into machine-readable JSON recipes.

**Responsibilities**:
- Merge small segments (configurable minimum length)
- Add transition lengths for color purging
- Map tool indices to color names
- Calculate total filament requirements
- Generate metadata for traceability

**Key Classes**:
```python
@dataclass
class SpliceRecipe:
    version: str
    total_length_mm: float
    segment_count: int
    color_count: int
    segments: list[dict]   # [{color, length_mm}, ...]
    colors: dict[str, str] # {"0": "white", "1": "black"}
    metadata: dict

class RecipeGenerator:
    def generate(parse_result: ParseResult, source_file: str) -> SpliceRecipe
    def to_json(recipe: SpliceRecipe, pretty: bool) -> str
    def save_recipe(recipe: SpliceRecipe, filepath: str)
```

#### `gcode_modifier.py` - G-code Modification

**Purpose**: Prepare G-code for single-extruder printing with pre-spliced filament.

**Responsibilities**:
- Remove tool change commands (Tn) with comments
- Add header identifying modified file
- Optionally add M0 pause at start for spool loading
- Preserve all geometry and print settings

**Key Classes**:
```python
class GCodeModifier:
    def modify_file(input_path: str, output_path: str) -> dict
    def modify_lines(lines: list[str]) -> tuple[list[str], dict]
```

#### `recipe_validator.py` - Recipe Validation

**Purpose**: Validate recipes before sending to hardware to prevent failures.

**Responsibilities**:
- Check segment lengths against hardware limits
- Verify segment count within firmware memory limits
- Validate color count (max 8)
- Warn about potential issues (short segments, long splice times)

**Key Classes**:
```python
@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]

class RecipeValidator:
    MIN_SEGMENT_LENGTH_MM = 3.0
    MAX_SEGMENT_LENGTH_MM = 50000.0
    MAX_SEGMENTS = 10000
    MAX_COLORS = 8

    def validate(recipe: dict) -> ValidationResult
    def validate_file(filepath: str) -> ValidationResult
```

#### `filament_profiles.py` - Material Database

**Purpose**: Store splice parameters for different filament materials and brands.

**Responsibilities**:
- Define temperature, timing, and compression settings per material
- Track material compatibility for cross-material splicing
- Provide lookup functions for profiles

**Key Classes**:
```python
@dataclass
class FilamentProfile:
    name: str
    material: str          # PLA, PETG, ABS, etc.
    brand: str             # Optional brand name
    splice_temp: int       # Celsius
    heat_time_ms: int
    cooling_time_ms: int
    compression_mm: float
    compatible_with: list[str]

PROFILES = {
    "pla": FilamentProfile(...),
    "petg": FilamentProfile(...),
    "abs": FilamentProfile(...),
    # ... more profiles
}
```

#### `splice3d_postprocessor.py` - Main Entry Point

**Purpose**: Orchestrate the complete post-processing workflow.

**Responsibilities**:
- Parse command-line arguments
- Coordinate parser, generator, and modifier
- Provide user feedback and progress
- Output files to specified locations

### 3.2 CLI Package (`cli/`)

#### `splice3d_cli.py` - USB Communication

**Purpose**: Send recipes to the splice machine and monitor progress.

**Responsibilities**:
- Serial port discovery and connection
- Recipe transmission (JSON over serial)
- Command execution (STATUS, START, PAUSE, ABORT)
- Real-time progress monitoring
- Interactive mode for debugging

**Key Classes**:
```python
class Splice3DCli:
    def connect() -> bool
    def disconnect()
    def send_command(command: str) -> list[str]
    def send_recipe(recipe_path: str) -> bool
    def start_splicing() -> bool
    def get_status() -> str
    def monitor(interval: float)
```

#### `simulator.py` - Firmware Simulator

**Purpose**: Test firmware logic and estimate splice times without hardware.

**Responsibilities**:
- Implement firmware state machine in Python
- Simulate timing for each operation
- Calculate total splice time and filament usage
- Provide visual feedback of splice cycle

**Key Classes**:
```python
class State(Enum):
    IDLE, LOADING, READY, FEEDING_A, FEEDING_B,
    CUTTING, POSITIONING, HEATING, WELDING,
    COOLING, SPOOLING, NEXT_SEGMENT, COMPLETE, ERROR

@dataclass
class SimConfig:
    feed_rate_mm_s: float = 50.0
    weld_temp_c: float = 210.0
    heat_rate_c_s: float = 5.0
    # ... more parameters

class FirmwareSimulator:
    def load_recipe(recipe_path: str) -> bool
    def run() -> bool
```

#### `analyze_gcode.py` - G-code Analysis

**Purpose**: Analyze multi-color G-code and provide statistics.

**Responsibilities**:
- Calculate segment length distribution
- Estimate splice time and waste reduction
- Warn about potential issues
- Export analysis as JSON

**Key Classes**:
```python
@dataclass
class SegmentStats:
    count: int
    total_mm: float
    min_mm: float
    max_mm: float
    avg_mm: float
    # Distribution buckets
    very_short: int  # <5mm
    short: int       # 5-20mm
    medium: int      # 20-100mm
    long: int        # 100-500mm
    very_long: int   # >500mm

@dataclass
class AnalysisResult:
    segment_stats: SegmentStats
    color_count: int
    color_distribution: dict
    estimated_splice_time_hours: float
    estimated_waste_reduction_percent: float
    warnings: list
```

#### `gui.py` - Graphical Interface

**Purpose**: Provide a user-friendly GUI for the post-processor.

**Responsibilities**:
- File selection dialogs
- Parameter configuration
- Process execution
- Output log display

### 3.3 Firmware (`firmware/src/`)

#### `state_machine.h/.cpp` - Core State Machine

**Purpose**: Manage the splice cycle through sequential states.

**State Flow**:
```
IDLE -> LOADING -> READY -> FEEDING_A/B -> CUTTING -> POSITIONING
                                              |
                                              v
COMPLETE <-- NEXT_SEGMENT <-- SPOOLING <-- COOLING <-- WELDING <-- HEATING
```

**Key Structures**:
```cpp
struct SpliceSegment {
    uint8_t colorIndex;
    float lengthMm;
};

enum class State {
    IDLE, LOADING, READY, FEEDING_A, FEEDING_B,
    CUTTING, POSITIONING, HEATING, WELDING,
    COOLING, SPOOLING, NEXT_SEGMENT, COMPLETE, ERROR
};

class StateMachine {
    void init();
    void update();
    bool loadRecipe(SpliceSegment* segments, uint16_t count);
    bool start();
    void pause();
    void resume();
    void abort();
};
```

#### `config.h` - Hardware Configuration

**Purpose**: Define pin mappings and calibration constants.

**Key Definitions**:
- Pin mappings for BTT SKR Mini E3 v2.0
- Stepper motor configuration (steps/mm, current, speed)
- Temperature settings (weld temps for PLA/PETG/ABS)
- Safety limits (max temp, thermal runaway detection)
- TMC2209 UART configuration

#### `serial_handler.h/.cpp` - Communication Protocol

**Purpose**: Handle USB serial communication with host PC.

**Supported Commands**:
- `RECIPE {json}` - Load splice recipe
- `START` - Begin splicing
- `PAUSE` - Pause operation
- `RESUME` - Resume from pause
- `ABORT` - Stop and reset
- `STATUS` - Query current state

#### `stepper_control.h/.cpp` - Motor Control

**Purpose**: Control NEMA17 stepper motors for filament movement.

**Responsibilities**:
- Feed filament A (input extruder)
- Feed filament B (input extruder)
- Wind onto output spool
- Position filament for cutting/welding

#### `temperature.h/.cpp` - Heater Control

**Purpose**: Manage weld chamber temperature.

**Responsibilities**:
- PID temperature control
- Thermistor reading (100K NTC)
- Thermal runaway protection
- Cooling fan control

#### `error_handler.h/.cpp` - Error Management

**Purpose**: Handle errors and recovery.

**Error Types**:
- Thermal runaway
- Filament runout
- Motor stall
- Communication timeout

---

## 4. Data Structures

### Splice Recipe JSON Format

```json
{
  "version": "1.0",
  "total_length_mm": 95000.0,
  "segment_count": 4068,
  "color_count": 2,
  "segments": [
    {"color": 0, "length_mm": 25.5},
    {"color": 1, "length_mm": 18.3},
    {"color": 0, "length_mm": 42.1}
  ],
  "colors": {
    "0": "white",
    "1": "black"
  },
  "metadata": {
    "source_file": "starry_night_vase.gcode",
    "transition_length_mm": 10.0,
    "original_segments": 4068,
    "merged_segments": 0
  }
}
```

### Firmware Segment Structure

```cpp
struct SpliceSegment {
    uint8_t colorIndex;     // 0-7 (max 8 colors)
    float lengthMm;         // Length in mm (precision to 0.01mm)
};
```

### Parse Result Structure

```python
@dataclass
class ParseResult:
    segments: list[Segment]   # Ordered list of segments
    total_length_mm: float    # Sum of all segment lengths
    color_count: int          # Unique colors used
    layer_count: int          # Total layers in print
    errors: list[str]         # Critical errors
    warnings: list[str]       # Non-critical warnings
```

---

## 5. Interfaces

### CLI Commands

#### Post-Processor
```bash
# Basic usage
splice3d input.gcode --colors white black

# With options
splice3d input.gcode \
  --output /path/to/output \
  --transition 10.0 \
  --min-segment 5.0 \
  --colors white black red blue \
  --no-pause \
  --verbose
```

#### Analysis Tool
```bash
# Analyze G-code
splice3d-analyze model.gcode

# Export to JSON
splice3d-analyze model.gcode --output stats.json
```

#### Simulator
```bash
# Run simulation
splice3d-simulate recipe.json

# With custom parameters
splice3d-simulate recipe.json --speed 100 --temp 210 --feed-rate 50
```

#### Machine CLI
```bash
# List available ports
splice3d-cli --list-ports

# Send recipe and start
splice3d-cli --port /dev/ttyACM0 --recipe recipe.json --start --monitor

# Interactive mode
splice3d-cli --port /dev/ttyACM0

# Single command
splice3d-cli --port /dev/ttyACM0 --command STATUS
```

### Input/Output Formats

#### Input: Multi-Tool G-code
Standard slicer output with tool change commands:
```gcode
; OrcaSlicer multi-tool output
T0
G1 X10 Y10 E5.0 F1200
T1
G1 X20 Y10 E8.0 F1200
M600  ; Alternative color change
```

#### Output: Modified G-code
Tool changes replaced with comments:
```gcode
; Modified by Splice3D Post-Processor
; Load your Splice3D spool before printing.

M0 ; Pause for spool loading
; SPLICE3D: Removed T0
G1 X10 Y10 E5.0 F1200
; SPLICE3D: Removed T1
G1 X20 Y10 E8.0 F1200
```

#### Output: Splice Recipe
JSON format for machine consumption (see Section 4).

### Serial Protocol

**Host -> Machine:**
```
RECIPE {"version":"1.0","segments":[...]}
START
PAUSE
RESUME
ABORT
STATUS
```

**Machine -> Host:**
```
OK RECIPE_LOADED 4068 segments
OK STARTED
OK PAUSED
OK RESUMED
OK ABORTED
STATUS FEEDING_A segment=42/4068 progress=1%
ERROR THERMAL_RUNAWAY
DONE 4068 splices completed
```

---

## 6. Dependencies

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pyserial | >=3.5 | Serial communication with hardware |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=7.0 | Unit testing framework |
| pytest-cov | >=4.0 | Code coverage reporting |
| black | >=23.0 | Code formatting |
| flake8 | >=6.0 | Linting |
| isort | >=5.12 | Import sorting |

### Firmware Dependencies (PlatformIO)

| Library | Purpose |
|---------|---------|
| Arduino | Core framework |
| AccelStepper | Stepper motor control with acceleration |
| TMCStepper | TMC2209 UART configuration |
| LiquidCrystal | LCD display support |
| Servo | Cutter servo control |

### Hardware Requirements

| Component | Specification | Purpose |
|-----------|---------------|---------|
| BTT SKR Mini E3 v2.0 | STM32F103RCT6 | Main controller |
| NEMA17 Motors (x3) | 1.8 deg, 1A | Filament feeding and winding |
| Hotend Heater | 40W, 24V | Weld chamber heating |
| NTC Thermistor | 100K, 3950 | Temperature sensing |
| SG90 Servo | 180 deg | Cutter actuation |
| CR10 Stock LCD | 128x64 | Status display |

---

## 7. Testing Strategy

### Test Types

#### Unit Tests (`postprocessor/tests/`)

**test_parser.py**:
- Simple extrusion parsing
- Tool change detection
- Relative/absolute extrusion modes
- G92 E reset handling
- Layer tracking
- Edge cases (empty input, no extrusion)

**test_recipe.py**:
- Basic recipe generation
- Segment merging
- Transition length addition
- Color name mapping
- JSON serialization
- G-code modifier behavior

#### Integration Tests

- End-to-end post-processing of sample files
- Recipe validation against firmware limits
- CLI command execution

#### Simulator Tests

- State machine transitions
- Timing calculations
- Error handling

### Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| gcode_parser.py | 90% |
| recipe_generator.py | 85% |
| gcode_modifier.py | 85% |
| recipe_validator.py | 80% |
| filament_profiles.py | 70% |

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=postprocessor --cov-report=html

# Specific test file
pytest postprocessor/tests/test_parser.py -v
```

### Sample Test Files (`samples/`)

| File | Purpose |
|------|---------|
| test_multicolor.gcode | Basic 2-color test |
| test_m600_colorchange.gcode | M600-based color changes |
| test_gradient.gcode | Many small segments |
| test_long_segments.gcode | Few long segments |
| test_multicolor_splice_recipe.json | Example output recipe |

---

## 8. Future Considerations

### Planned Improvements

#### Phase 2: Position Tracking (Drift Compensation)
- Mechanical dimple encoding on filament surface
- Dimple reader (LED + photodiode)
- Position database for drift compensation
- Real-time correction at print speeds (50-150mm/sec)

#### Phase 3: Reusable Crimp System
- NFC-enabled reusable crimps
- Crimp ejection before hotend
- Return conveyor system
- Crimp health tracking

#### Phase 4: Dry Vault
- Sealed climate-controlled chamber
- Active dehumidification (<10% RH)
- Temperature control
- IoT monitoring

#### Phase 5: Automated Print Farm
- Bed stack dispenser (100+ beds)
- Failure detection and re-queuing
- Order management integration
- 95%+ success rate target

### Known Limitations

1. **Maximum Segments**: 10,000 segments per recipe (firmware memory limit)
2. **Maximum Colors**: 8 colors per print
3. **Minimum Segment Length**: 3mm (mechanical limitation)
4. **Maximum Segment Length**: 50m (practical spool limit)
5. **Supported Slicers**: OrcaSlicer, PrusaSlicer, BambuStudio (others may work)
6. **Material Compatibility**: Cross-material splicing limited to compatible pairs

### Technical Debt

- [ ] Multi-slicer support (Cura profiles)
- [ ] Wi-Fi/web interface (ESP32 upgrade)
- [ ] OctoPrint/Moonraker plugins
- [ ] Mobile app notifications
- [ ] Splice quality inspection (camera)
- [ ] Automatic firmware updates

### Performance Targets

| Metric | Target |
|--------|--------|
| Splice time | 45 seconds average |
| Waste reduction | 80% vs traditional MMU |
| Splice success rate | 99%+ |
| Maximum transitions | 10,000 per print |
| Feed rate | 50mm/s |

---

## Appendix A: Project Structure

```
splice3d/
├── cli/                         # CLI tools
│   ├── analyze_gcode.py         # G-code analysis
│   ├── gui.py                   # Tkinter GUI
│   ├── simulator.py             # Firmware simulator
│   └── splice3d_cli.py          # USB communication
├── docs/                        # Documentation
│   ├── BOM.md                   # Bill of materials
│   ├── CALIBRATION.md           # Calibration guide
│   ├── MECHANICAL.md            # Build instructions
│   ├── ORCASLICER_SETUP.md      # Slicer configuration
│   ├── ROADMAP.md               # Future plans
│   ├── SPLICE_CORE.md           # Weld mechanism design
│   ├── TROUBLESHOOTING.md       # Common issues
│   ├── VISION.md                # Long-term vision
│   └── WIRING.md                # Wiring diagram
├── firmware/                    # Embedded C++
│   ├── platformio.ini           # PlatformIO config
│   └── src/
│       ├── config.h             # Hardware configuration
│       ├── error_handler.*      # Error management
│       ├── lcd_display.*        # LCD support
│       ├── main.cpp             # Entry point
│       ├── serial_handler.*     # USB communication
│       ├── state_machine.*      # Core state machine
│       ├── stepper_control.*    # Motor control
│       ├── temperature.*        # Heater control
│       └── tmc_config.*         # TMC2209 setup
├── integrations/                # Third-party integrations
│   └── octoprint/               # OctoPrint plugin
├── postprocessor/               # Python package
│   ├── __init__.py
│   ├── filament_profiles.py     # Material database
│   ├── gcode_modifier.py        # G-code modification
│   ├── gcode_parser.py          # G-code parsing
│   ├── recipe_generator.py      # Recipe generation
│   ├── recipe_validator.py      # Recipe validation
│   ├── splice3d_postprocessor.py # Main entry point
│   └── tests/                   # Unit tests
├── samples/                     # Test files
├── scripts/                     # Utility scripts
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE                      # MIT License
├── pyproject.toml               # Python package config
├── README.md
├── setup.py
└── SOFTWARE_DESIGN_DOCUMENT.md  # This document
```

---

## Appendix B: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-17 | Splice3D Team | Initial document |
