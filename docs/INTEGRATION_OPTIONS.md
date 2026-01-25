# Integration Options

> Comparison of ways to integrate Splice3D with slicing workflow.

## Recommended Path

| Phase | Integration | Why |
|-------|-------------|-----|
| **V1** | Post-processor script | Simple, works now |
| **V2** | OrcaSlicer plugin | Best UX for end users |
| **V3+** | Web dashboard | For print farm / service |

---

## Option 1: Post-Processor Script (Current)

**How it works:**
```bash
python splice3d_postprocessor.py model.gcode
```

**Pros:**
- ✅ Already built and working
- ✅ Works with any slicer
- ✅ Easy to modify and debug
- ✅ Can be integrated into slicer as post-processing script

**Cons:**
- ❌ Extra manual step
- ❌ No preview in slicer
- ❌ Separate tool to learn

**OrcaSlicer Integration:**
1. Go to Printer Settings → Custom G-code
2. Add post-processing script:
   ```
   /path/to/python /path/to/splice3d_postprocessor.py
   ```
3. Runs automatically after slicing

---

## Option 2: Slicer Plugin (Recommended for V2)

**Target:** OrcaSlicer / PrusaSlicer / BambuStudio

**How it would work:**
- "Export for Splice3D" button in slicer
- Preview color segments in 3D viewer
- Direct USB communication with machine
- Real-time progress during splicing

**Technical Approach:**

### Option 2A: Python Extension
PrusaSlicer and OrcaSlicer support post-processing via scripts.
We could create a more integrated script that:
- Shows GUI for options
- Previews splice positions
- Uploads directly to machine

### Option 2B: Native C++ Plugin
More complex, but fully integrated:
- Menu item in slicer
- Custom preview mode
- Built-in settings panel

**Requirements for C++ Plugin:**
- OrcaSlicer source code
- C++17 compiler
- wxWidgets (GUI framework)
- Significant development effort

**Recommended:** Start with Python post-processor integration, consider C++ plugin for V3+.

---

## Option 3: Web Dashboard (Print Farm Phase)

**When it makes sense:**
- Running multiple Splice3D machines
- Taking orders from customers
- Remote monitoring needed
- Queue management across machines

**Stack (if we build it):**
```
Frontend: React + Tailwind v4 + shadcn/ui
Backend: Node.js or Python FastAPI
Realtime: WebSockets for machine status
Database: PostgreSQL for orders/history
Monorepo: TurboRepo for organization
```

**Features:**
- Order queue management
- Multi-machine dashboard
- Filament inventory tracking
- Analytics on success/failure rates
- Customer order portal (if service)

**NOT needed for:**
- Personal use
- Single machine
- Hobbyist projects

---

## Option 4: OctoPrint/Moonraker Plugin

**For users already running:**
- OctoPrint (Raspberry Pi)
- Moonraker/Mainsail/Fluidd (Klipper)

**How it would work:**
1. Upload multi-color G-code to OctoPrint
2. Plugin intercepts, calls post-processor
3. Sends recipe to Splice3D machine
4. Waits for splice completion
5. Starts print with modified G-code

**Advantages:**
- Familiar interface for users
- Existing plugin ecosystems
- Remote access built-in

---

## Decision Matrix

| Use Case | Best Option |
|----------|-------------|
| Just testing | Post-processor script |
| Personal use | Post-processor + OctoPrint |
| Power user | Slicer plugin |
| Print farm | Web dashboard |
| Commercial service | Web dashboard + customer portal |

---

## Option 5: Home Assistant Integration ✅

**Status:** Implemented

**How it works:**
1. MQTT bridge service connects Splice3D to Home Assistant
2. Custom component provides sensors, buttons, and automations
3. Control and monitor from HA dashboard, voice assistants, or mobile app

**Features:**
- Real-time status (state, progress, temperature)
- Remote control buttons (start, pause, abort)
- Error notifications via HA notify services
- Alexa/Google integration for voice commands
- Daily statistics tracking

**Setup:**
```bash
# Install and run the MQTT bridge
pip install -e .
splice3d-mqtt-bridge --port /dev/ttyUSB0 --mqtt-host localhost
```

**MQTT Topics:**
| Topic | Description |
|-------|-------------|
| `home/splice3d/status/state` | Current state |
| `home/splice3d/status/progress/percent` | Progress 0-100 |
| `home/splice3d/command/start` | Start command |
| `home/splice3d/command/abort` | Abort command |

**Home Assistant Entities:**
- `sensor.splice3d_state` - Machine state
- `sensor.splice3d_progress` - Progress percentage
- `button.splice3d_start` - Start button
- `binary_sensor.splice3d_error` - Error status

---

## Implementation Priority

1. **Now:** Post-processor script ✅
2. **Now:** Home Assistant MQTT integration ✅
3. **V1.1:** OrcaSlicer post-processing integration
4. **V2:** OctoPrint/Moonraker plugin
5. **V2.5:** Python GUI for standalone use
6. **V3+:** Slicer C++ plugin (if demand)
7. **V4+:** Web dashboard (if print farm)
