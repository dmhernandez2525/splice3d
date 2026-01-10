# Splice3D Future Roadmap

> From MVP to fully automated print manufacturing.

## Current Status

**Phase 1: Core Splicer** ✅ Software Complete
- [x] G-code parser (OrcaSlicer)
- [x] Recipe generation
- [x] Firmware state machine
- [ ] Hardware prototype (pending)

---

## Near-Term Phases

### Phase 2: Position Tracking (Drift Compensation)

**Problem**: Printer gear slippage causes color drift over long prints.

**Solution**: Mechanical dimple encoding + database sync

```
Filament surface:
══╝══╝╝══╝══╝╝╝════
  ↑  ↑ ↑ ↑  ↑ ↑ ↑
  Position data (dimples 0.1-0.2mm deep)
```

**Tasks:**
- [ ] Design dimple encoder (pins + solenoids)
- [ ] Build dimple reader (LED + photodiode)
- [ ] Implement position database
- [ ] Add drift compensation algorithm
- [ ] Test at printing speeds (50-150mm/sec)

**Why dimples over ink/barcode:**
- No color impact
- No foreign materials
- Rotation immune
- Essentially free

---

### Phase 3: Reusable Crimp System

**Problem**: NFC chips at every color change = expensive ($0.10-0.50 each × 4000 changes = $400-2000/print)

**Solution**: Reusable NFC crimps ejected before hotend and returned to vault

```
[Vault] → [Crimp on] → [Print] → [Eject] → [Return] → [Vault]
                                     ↓
                              Return conveyor
```

**Tasks:**
- [ ] Design crimp hardware (hinged clamp + NFC)
- [ ] Build ejector mechanism (spring pin or cam)
- [ ] Implement NFC read/write
- [ ] Build return conveyor system
- [ ] Track crimp health (cycle count, signal strength)

**Economics:**
- 200 crimps × $3 = $600 initial
- 10,000+ cycles per crimp
- Break-even after ~1 day of operation

---

### Phase 4: Dry Vault

**Problem**: Moisture causes bubbles, weak splices, random failures.

**Solution**: Sealed climate-controlled chamber

```
┌─────────────────────────────┐
│  SEALED DRY VAULT (<10% RH) │
│  [Input Spools]             │
│  [Cutting Station]          │
│  [Dimple Encoder]           │
│  [Splicing Station]         │
│  [Crimp Applicator]         │
│  [Output Queue Spool]       │
│  [Dehumidifier][Temp Ctrl]  │
└─────────────────────────────┘
```

**Tasks:**
- [ ] Design sealed chamber
- [ ] Add active dehumidification
- [ ] Temperature control
- [ ] IoT monitoring (humidity, temp, spool levels)
- [ ] Auto-order low filament

---

## Long-Term Phases

### Phase 5: Automated Print Farm

**Vision**: 100+ print queue running unattended

```
[Bed Stack] → [Printer] → [Success Bin] → Fulfillment
                  ↓
            [Failure Bin] → Re-queue
```

**Features:**
- Pez-style bed dispenser (100 beds stacked)
- Spaghetti/adhesion failure detection
- Automatic re-queuing of failed prints
- Order management integration
- 95%+ success rate notification

**Tasks:**
- [ ] Bed eject/load mechanism
- [ ] Print quality monitoring (camera)
- [ ] Queue management software
- [ ] Order API integration
- [ ] Failure analytics dashboard

---

### Phase 6: Vertical Integration

**Ultimate vision**: Pellets → Prints → Shipping

```
[Raw Pellets] → [Color Mixing] → [Extrusion] → [Splicing] → [Printing] → [Fulfillment]
```

**Features:**
- Custom color creation on-demand
- Variable diameter extrusion
- Specialty material blending
- Full lights-out manufacturing

---

## Ultimate Test Case

**Starry Night Vase** - The perfect benchmark:

| Metric | Current (H2C) | With Splice3D |
|--------|---------------|---------------|
| Tool changes | 4,068 | 0 (pre-spliced) |
| Filament used | 90m | ~95m |
| Purge waste | 187m (67%!) | ~5m (5%) |
| AMS wear | Heavy | None |

[MakerWorld Link](https://makerworld.com/en/models/2129520-starry-night-vase)

---

## Tech Debt / Future Improvements

- [ ] Multi-slicer support (Cura, Prusa)
- [ ] Wi-Fi/web interface (ESP32)
- [ ] OctoPrint/Moonraker plugins
- [ ] Mobile app notifications
- [ ] Material database (temps, speeds per filament)
- [ ] Splice quality inspection (camera)
