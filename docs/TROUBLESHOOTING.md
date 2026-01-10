# Troubleshooting Guide

> Common issues and solutions for Splice3D.

## Post-Processor Issues

### "No segments found"

**Cause**: G-code doesn't contain tool changes.

**Solutions**:
1. Verify OrcaSlicer is set up with 2+ extruders
2. Check G-code contains `T0`, `T1`, or `M600` commands
3. Try `--verbose` flag to see parsing details

```bash
python3 splice3d_postprocessor.py input.gcode -v
```

---

### "Single color detected"

**Cause**: Only one tool used in the print.

**Solutions**:
1. Assign different colors to different parts in slicer
2. Add color changes at specific layers
3. Verify multi-color model is imported correctly

---

### Very short segments

**Cause**: Many rapid color changes (common in artwork prints).

**Solution**: Increase minimum segment length:

```bash
python3 splice3d_postprocessor.py input.gcode --min-segment 10
```

Note: Merged segments may slightly affect color accuracy.

---

## Firmware Issues

### Motor not moving

**Symptoms**: No motion when feeding/winding.

**Causes & Solutions**:

| Cause | Check | Fix |
|-------|-------|-----|
| Wrong pins | Verify config.h | Update pin definitions |
| Enable inverted | TMC2209 settings | Change enable polarity |
| Power off | PSU status | Verify 24V supply |
| Wiring loose | Connectors | Reseat all cables |

**Debug command**:
```
FEED A 10
```
Should extrude 10mm from input A.

---

### Heater not heating

**Symptoms**: Temperature stays at ambient.

**Causes & Solutions**:

| Cause | Check | Fix |
|-------|-------|-----|
| PWM pin wrong | config.h HEATER_PIN | Use PC8 for SKR Mini E3 |
| Thermistor disconnected | Read -10 or 999 | Check TH0 connector |
| MOSFET failure | Measure voltage | Replace board |

**Thermal runaway**:
If temp doesn't increase by 10°C in 40 seconds → emergency shutdown.

---

### Cutter not activating

**Symptoms**: Servo doesn't move.

**Causes & Solutions**:

1. **Wrong pin**: Verify PB3 (E_STEP)
2. **Power**: Servo needs 5V, check BEC
3. **Signal**: Use oscilloscope to verify PWM

**Test command**:
```
CUT
```

---

## Serial Communication Issues

### CLI can't connect

**Symptoms**: "Could not open port"

**Solutions**:
1. Check USB cable (some are charge-only)
2. Verify correct port: `ls /dev/tty*`
3. On Mac: `ls /dev/cu.usbmodem*`
4. Permissions: `sudo chmod 666 /dev/ttyACM0`

---

### Commands not responding

**Symptoms**: Sent command, no reply.

**Causes**:
1. Wrong baud rate (should be 115200)
2. Firmware crashed
3. Serial buffer overflow

**Solutions**:
- Reset board
- Reduce recipe JSON size
- Add delays between commands

---

## Splice Quality Issues

### Weak splices (break easily)

| Cause | Fix |
|-------|-----|
| Temp too low | +10°C |
| Hold time short | +1 second |
| Poor alignment | Check PTFE guide |
| Filament degraded | Use fresh stock |

---

### Fat splices (>1.85mm)

| Cause | Fix |
|-------|-----|
| Temp too high | -10°C |
| Over-compression | -0.5mm compression |
| PTFE worn | Replace tube |
| Material pooling | Improve heat break |

---

### Kinked splices

| Cause | Fix |
|-------|-----|
| Misalignment | Center filaments |
| Uneven tension | Adjust extruder grip |
| Cooling too fast | Slow fan speed |

---

## Position Drift

**Symptom**: Colors shift from expected position over long prints.

**Causes**:
1. Extruder gear slippage
2. Stepper step loss
3. Measurement errors

**V1 workaround**:
- Start with shorter prints
- Validate on simple patterns first
- Document drift for compensation

**V2 solution**:
- Dimple encoding (tracks actual position)
- Drift compensation algorithm

---

## Emergency Recovery

### Lost power mid-splice

1. Let heater cool naturally (don't force)
2. Once cool, manually extract filament
3. Clear any jams
4. Resume from last completed segment

### Filament stuck in weld chamber

1. Heat to splice temperature
2. Push filament through from input side
3. If stuck: disassemble hotend, clean PTFE
4. Prevent: maintain tube, don't exceed temps

---

## Getting Help

1. Check this guide
2. Review firmware serial output: `monitor 115200`
3. Run diagnostic: `STATUS`
4. File issue on GitHub with:
   - G-code sample
   - Recipe JSON
   - Serial log output
