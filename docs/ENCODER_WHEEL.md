# Encoder Wheel Design (V2 Feature)

> Documentation for dimple/encoder-based position tracking.

## Purpose

Track exact filament position to detect and compensate for:
- Extruder gear slippage
- Stretch in filament
- Accumulated drift over long prints

## V1 vs V2 Tracking

| Version | Method | Accuracy |
|---------|--------|----------|
| V1 | Stepper counting only | ±2% per 1000mm |
| V2 | Encoder wheel | ±0.1% per 1000mm |
| V3 | Dimple encoding | 0.1mm precision |

## Encoder Wheel Design

### Simple Approach: Optical Encoder

```
           ┌─────────────────┐
           │  FILAMENT PATH  │
           │       │         │
           │   ┌───┴───┐     │
           │   │ENCODER│     │
           │   │ WHEEL │     │
           │   │  ───  │     │
           │   └───────┘     │
           │       │         │
           │    SENSOR       │
           └─────────────────┘

Components:
- Encoder wheel with slots (3D printed)
- IR LED + phototransistor pair
- Quadrature encoding for direction
```

### Bill of Materials (Encoder)

| Part | Qty | Est. Price |
|------|-----|------------|
| Optical encoder module | 1 | $3-5 |
| 608 Bearing | 2 | $1 |
| Spring (for tension) | 1 | $1 |
| Printed wheel | 1 | $0 |

### Encoder Wheel Specs

```
Wheel Parameters:
- Diameter: 40mm
- Slots: 100 per revolution
- Slot width: 0.5mm
- Resolution: 40mm × π / 100 = 1.26mm per pulse

With quadrature (4x):
- Resolution: 0.31mm per pulse
```

### Firmware Integration

```cpp
// Encoder interrupt handler
volatile long encoderCount = 0;

void encoderISR() {
    // Read direction from quadrature
    if (digitalRead(ENCODER_B)) {
        encoderCount++;
    } else {
        encoderCount--;
    }
}

// Calculate actual filament length
float getActualLength() {
    return encoderCount * MM_PER_PULSE;
}

// Drift compensation
float calculateDrift() {
    float expected = stepperPosition * MM_PER_STEP;
    float actual = getActualLength();
    return actual - expected;
}
```

---

## Advanced: Dimple Encoding (V3)

### Concept

Create physical dimples in the filament at splice points. A mechanical sensor detects these dimples for absolute positioning.

```
Filament cross-section with dimple:

  Normal:        Dimpled:
    ○              ◠
  (1.75mm)      (1.65mm at dimple)
```

### Dimple Parameters

- Dimple depth: ~0.1mm (reduces OD from 1.75 to 1.65)
- Dimple width: 2mm along filament
- Spacing: One dimple per splice point

### Detection

```
Mechanical sensor (spring-loaded stylus):

    ┌───────┐
    │STYLUS │
    │  ───  │ ← Spring tension
    │   │   │
    │   ▼   │
    ═══════════ ← Filament
    ___∪_______  ← Dimple causes stylus to dip
        ↑
     ENCODER reads depth
```

### Creating Dimples

Option 1: **After splice** - Press tool into warm filament
Option 2: **During splice** - Mold slightly smaller at junction

### Firmware Logic

```cpp
// Detect dimple (depth below threshold)
bool detectDimple() {
    float depth = readDimpleSensor();  // 0-1mm
    return depth > DIMPLE_THRESHOLD;   // e.g., 0.05mm
}

// Count dimples = count splices
void dimpleISR() {
    if (detectDimple() && !lastDimpleState) {
        dimpleCount++;
        // We've passed splice #dimpleCount
        // Compare to expected position
    }
    lastDimpleState = detectDimple();
}
```

---

## Implementation Priority

1. **V1 (Now):** Stepper counting only
2. **V2:** Add optical encoder wheel for drift monitoring
3. **V3:** Add dimple encoding for absolute position

## Pin Assignments (Future)

```cpp
// config.h additions for V2

// Encoder pins (use interrupt-capable pins)
#define ENCODER_A_PIN PA0    // Interrupt
#define ENCODER_B_PIN PA1    // Quadrature direction

// Dimple sensor (V3)
#define DIMPLE_SENSOR_PIN PA2  // Analog for depth reading
```

## Testing Encoder Accuracy

1. Mark filament at 1000mm
2. Feed 1000mm by stepper
3. Read encoder count
4. Calculate: `actual = count × MM_PER_PULSE`
5. Drift = actual - 1000mm
6. Log drift for different materials
