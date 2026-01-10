# Video Tutorial Outline

> Script and outline for future Splice3D build video.

## Video Series Plan

### Video 1: Introduction & Overview (5-8 min)

**Intro (1 min)**
- What is Splice3D?
- Show example multi-color print (Starry Night Vase)
- "Print this on ANY single-extruder printer"

**How It Works (2 min)**
- Diagram: G-code → Post-processor → Splice machine → Pre-spliced spool
- Show the splice cycle animation
- Before/after: multi-extruder vs single extruder

**What You'll Need (2 min)**
- Parts overview (point to BOM.md)
- Donor Ender 3 parts
- Additional purchases (~$200)
- Tools required

**Series Overview (1 min)**
- Video 2: Build
- Video 3: Wiring
- Video 4: Firmware
- Video 5: First splice

---

### Video 2: Hardware Build (15-20 min)

**Frame Assembly (5 min)**
- Cut 2020 extrusion (or reuse Ender frame)
- Attach brackets
- Mount to work surface

**Extruder Installation (4 min)**
- Mount input extruders (A and B)
- Mount output winder
- Align filament paths

**Splice Chamber Build (5 min)**
- Modify hotend for weld chamber
- Install 2mm ID PTFE tube
- Attach heater and thermistor
- Mount cooling fan

**Cutter Assembly (3 min)**
- Mount servo
- Attach blade to servo horn
- Adjust blade position
- Install blade guard

**Spool Holders (2 min)**
- Assemble with bearings
- Mount to frame
- Thread filament path test

---

### Video 3: Wiring (10-15 min)

**Safety First (1 min)**
- Disconnect PSU before wiring
- Use correct wire gauges
- Double-check polarity

**Board Overview (2 min)**
- SKR Mini E3 v2 layout
- Label each connector

**Stepper Motor Wiring (3 min)**
- X driver → Extruder A
- Y driver → Extruder B  
- Z driver → Winder
- Check motor direction

**Heater & Thermistor (2 min)**
- HE0 connection
- TH0 connection
- Use thermal compound

**Servo & Sensors (2 min)**
- Servo signal to E_STEP
- Filament sensors to endstops

**Power (2 min)**
- PSU to SKR board
- Grounding

**Cable Management (2 min)**
- Wire clips
- Label connections
- Strain relief

---

### Video 4: Firmware & Software (10-12 min)

**Flash Firmware (3 min)**
- Install PlatformIO
- Build firmware
- Upload to board
- Verify boot message

**Configure Settings (3 min)**
- config.h walkthrough
- Pin mappings
- Safety limits

**Install Post-Processor (2 min)**
- Clone repository
- Install Python dependencies
- Run test

**OrcaSlicer Setup (3 min)**
- Create Splice3D printer profile
- Configure virtual extruders
- Export settings

---

### Video 5: First Splice (10-15 min)

**Safety Checklist (2 min)**
- Walk through SAFETY_CHECKLIST.md
- Power-on procedure

**Calibration (5 min)**
- Steps/mm calibration
- Temperature calibration
- Cutter adjustment

**First Splice Test (3 min)**
- Load filament
- Run 2-segment recipe
- Inspect splice quality

**First Print (4 min)**
- Simple 2-color cube
- Process G-code
- Load spliced spool
- Start print
- Show result!

---

## B-Roll Shots Needed

- [ ] Splice cycle close-up (slow-mo if possible)
- [ ] Filament feeding into extruder
- [ ] Weld chamber heating up
- [ ] Cutter in action
- [ ] Spliced filament close-up
- [ ] Successful multi-color print
- [ ] LCD displaying status
- [ ] Spool winding onto holder

---

## Graphics Needed

- [ ] System diagram (G-code flow)
- [ ] Splice cycle state machine
- [ ] Temperature graph during splice
- [ ] BOM overview graphic
- [ ] Wiring diagram
- [ ] Before/after comparison

---

## Equipment

- Camera (1080p minimum, 4K preferred)
- Macro lens for close-ups
- Tripod
- Good lighting (softbox)
- Microphone (lavalier or shotgun)
- Screen recording software
- Video editing software

---

## Notes for Recording

1. **Show failures too** - Helps viewers troubleshoot
2. **Explain the "why"** - Not just what, but reasoning
3. **Include timestamps** - In video description
4. **Reference docs** - Point to GitHub docs for details
5. **Call to action** - Subscribe, contribute, etc.
