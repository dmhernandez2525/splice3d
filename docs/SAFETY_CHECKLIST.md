# Safety Checklist

> Pre-power-on verification steps for Splice3D.

## Before First Power-On

Complete ALL items before applying power.

### Electrical Safety

- [ ] **PSU voltage set correctly** (115V or 230V switch)
- [ ] **All connections secure** - No loose wires
- [ ] **No exposed conductors** - All terminals covered
- [ ] **Correct polarity** - V+ and V- to correct terminals
- [ ] **Grounding connected** - PSU earth to mains ground
- [ ] **Wire gauge adequate** - 18AWG for heater, 22AWG for signals
- [ ] **No shorts** - Multimeter check between V+ and GND

### Stepper Motors

- [ ] **Connectors fully seated** - 4-pin JST pushed in
- [ ] **Driver heatsinks attached** - TMC2209s can overheat
- [ ] **Motors secured** - Won't move during operation
- [ ] **No binding** - Shafts rotate freely by hand

### Heater

- [ ] **Heater cartridge secure** - Set screw tightened
- [ ] **Thermistor in place** - Thermal paste applied
- [ ] **Thermistor wires separated** - Not touching heater wires
- [ ] **Heat block insulated** - Silicone sock or cotton insulation
- [ ] **PTFE away from heater** - Min 5mm clearance from heat block

### Cutter

- [ ] **Blade guard in place** - Fingers protected
- [ ] **Servo range tested** - Manually moved through range
- [ ] **No binding** - Cuts cleanly without jamming
- [ ] **Blade sharp** - Replace if dull

### Firmware

- [ ] **Correct board selected** - platformio.ini matches your board
- [ ] **Pin mappings verified** - config.h matches your wiring
- [ ] **Safety limits set** - MAX_TEMP appropriate for material

---

## First Power-On Procedure

### Step 1: Visual Check (Power Off)

1. Triple-check all connections
2. Look for any obvious problems
3. Ensure work area is clear

### Step 2: USB Only (No 24V)

1. Connect USB cable only
2. Board should power from USB
3. Check status LEDs light up
4. Connect serial monitor (115200 baud)
5. Verify boot message appears

### Step 3: 24V Power

1. Turn on PSU
2. Listen for any unusual sounds
3. Feel for heat (nothing should be hot yet)
4. Check serial for error messages

### Step 4: Temperature Test

```
TEMP 50
```

1. Set low temperature (50°C)
2. Watch thermistor reading increase
3. Should reach 50°C in ~30 seconds
4. Turn off: `TEMP 0`

### Step 5: Motor Test

```
FEED A 10
FEED B 10
WIND 10
```

1. Test each motor individually
2. Verify correct direction
3. If wrong direction, swap A+/A- or B+/B- wires

### Step 6: Cutter Test

```
CUT
```

1. Verify servo moves
2. Blade should cut cleanly
3. Servo returns to home position

---

## Operating Safety

### During Operation

- [ ] **Never leave unattended** during first few runs
- [ ] **Keep hands clear** of moving parts
- [ ] **Don't touch heater** - can reach 250°C
- [ ] **Keep flammables away** - No paper, plastic near heater
- [ ] **Ensure ventilation** - Especially for ABS/ASA

### Emergency Stop

If anything goes wrong:

1. **Turn off PSU** (main power switch)
2. Or send: `ABORT`
3. Or unplug USB (triggers emergency stop in firmware)

### After Power-Off

1. Let heater cool naturally (fan will run)
2. Don't touch heat block for 5 minutes
3. Secure any loose filament

---

## Periodic Maintenance

### Weekly

- [ ] Clean PTFE tube (check for debris)
- [ ] Verify thermistor secure
- [ ] Check for loose connections
- [ ] Inspect cutter blade sharpness

### Monthly

- [ ] Lubricate spool bearings
- [ ] Check stepper motor temperatures (shouldn't exceed 60°C)
- [ ] Verify steps/mm calibration
- [ ] Replace PTFE if discolored

### After Failures

- [ ] Inspect for filament jams
- [ ] Check splice chamber for debris
- [ ] Verify heater still works
- [ ] Run full test cycle before production use

---

## Warning Signs

Stop immediately if you observe:

| Symptom | Possible Cause | Action |
|---------|---------------|--------|
| Smoke | Short circuit, burnt insulation | Power off immediately |
| Burning smell | Overheated motor, heater fault | Power off, investigate |
| Sparks | Short circuit | Power off immediately |
| Motor not moving but hot | Stall, driver issue | Power off, check wiring |
| Temperature runaway | PID issue, thermistor fault | Power off, check sensor |
| Unusual sounds | Binding, loose parts | Stop, investigate |
