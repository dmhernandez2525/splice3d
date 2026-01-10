# Splice3D Calibration Guide

Tuning your Splice3D machine for accurate filament lengths and reliable welds.

## 1. Steps Per MM Calibration

### Input Extruders (A and B)

1. Load filament through extruder (not into weld chamber)
2. Mark filament 120mm from extruder entrance
3. Send command: `FEED A 100` (or use CLI)
4. Measure actual distance extruded
5. Calculate:
   ```
   new_steps = current_steps × (100 / actual_distance)
   ```
6. Update `STEPS_PER_MM_EXTRUDER_A` in `config.h`
7. Repeat for Extruder B

### Output Winder

1. Mark output filament at a reference point
2. Wind 100mm
3. Measure actual length wound
4. Adjust `STEPS_PER_MM_WINDER`

**Note:** Winder steps/mm varies with spool fill level. Start with empty spool for calibration.

## 2. Temperature Calibration

### PID Tuning

Default PID values may not match your setup. To tune:

1. Set temperature: `TEMP 200`
2. Watch temperature response via serial
3. If oscillating: Reduce Kp
4. If slow to reach: Increase Ki
5. If overshooting: Increase Kd

Edit values in `temperature.cpp`:
```cpp
double Kp = 20.0;  // Proportional
double Ki = 1.0;   // Integral
double Kd = 5.0;   // Derivative
```

### Thermistor Verification

1. Set target to room temp reading
2. Use external thermometer to verify
3. Adjust `THERMISTOR_B_COEFF` if readings are off

## 3. Weld Quality Testing

### Basic Weld Test

1. Create a short recipe (2 segments, 50mm each)
2. Run splice cycle
3. Inspect weld joint:
   - Should be smooth, not bulging
   - Diameter should be 1.75mm ± 0.1mm
   - Should bend without breaking

### Weld Parameter Tuning

If welds are weak:
- Increase `WELD_TEMP_*` by 5-10°C
- Increase `WELD_HOLD_TIME_MS`
- Increase `WELD_COMPRESSION_MM`

If welds are blobby/oversized:
- Decrease temperature
- Decrease hold time
- Check PTFE tube is constraining properly

## 4. Cutter Calibration

### Servo Cutter

1. Power on with `CUTTER_SERVO_PIN` connected
2. Adjust `cutterServo.write(0)` home position
3. Adjust `cutterServo.write(90)` cut position
4. Ensure full cut without over-travel

### Stepper Cutter

1. Manually position cutter at home
2. Test cut motion
3. Adjust steps in `activateCutter()` / `deactivateCutter()`

## 5. Full Cycle Test

1. Create test recipe:
   ```json
   {
     "segments": [
       {"color": 0, "length_mm": 200},
       {"color": 1, "length_mm": 200},
       {"color": 0, "length_mm": 200}
     ]
   }
   ```

2. Run full cycle
3. Measure output:
   - Total length should be ~600mm
   - Welds at 200mm and 400mm marks

4. Feed through Bowden tube test:
   - Should pass through without jamming
   - If jamming, check weld diameter

## 6. Print Test

### Simple Test Object

Use a simple two-color calibration cube:
- 20mm cube
- Alternating layers or vertical split
- Minimal color changes

### What to Look For

✅ **Good:**
- Color changes at expected positions
- No gaps at transitions
- Continuous extrusion

❌ **Bad:**
- Colors shifted from expected position → Length calibration
- Gaps or under-extrusion at welds → Weld quality
- Jams during print → Weld diameter too large

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Color change early | Extruding more than calculated | Reduce steps/mm |
| Color change late | Extruding less than calculated | Increase steps/mm |
| Weak welds | Low temp or short hold | Increase temp/time |
| Fat welds | Over-compression | Reduce compression distance |
| Jams at weld | Weld diameter >1.8mm | Fix PTFE constraint |
