# ESP32 Wi-Fi Module (V3 Feature)

> Documentation for future wireless control capability.

## Purpose

Add Wi-Fi connectivity for:
- Wireless recipe upload
- Remote monitoring
- Web-based control interface
- OctoPrint/Moonraker integration

## Hardware

### Recommended Module

**ESP32-WROOM-32** or **ESP32-S3**

| Spec | Value |
|------|-------|
| Processor | Dual-core 240MHz |
| RAM | 520KB |
| Flash | 4-8MB |
| Wi-Fi | 802.11 b/g/n |
| GPIO | 34 |
| Price | $4-8 |

### Wiring to SKR Mini E3

The ESP32 communicates with the SKR via serial (UART):

```
SKR Mini E3 v2          ESP32
─────────────          ──────
TX (PA9)  ──────────── RX (GPIO3)
RX (PA10) ──────────── TX (GPIO1)
GND       ──────────── GND
5V        ──────────── VIN (or 3.3V pin)

Note: Use level shifter if ESP32 is 3.3V only
```

### Alternative: Replace SKR with ESP32

For future versions, ESP32 could run everything:
- Stepper control via TMC2209 UART
- Temperature control
- Wi-Fi built-in
- No separate controller needed

---

## Firmware Architecture

### Two-Processor Design (V3)

```
┌─────────────────────┐     ┌─────────────────────┐
│   SKR Mini E3 v2    │     │      ESP32          │
│                     │     │                     │
│  - Stepper control  │◄───►│  - Wi-Fi stack     │
│  - Temperature PID  │UART │  - Web server      │
│  - Splice cycle     │     │  - Recipe storage  │
│  - Real-time tasks  │     │  - File system     │
│                     │     │                     │
└─────────────────────┘     └─────────────────────┘
        │                           │
        │                           │
    Motors, heater            Wi-Fi network
```

### Communication Protocol

ESP32 sends commands to SKR:

```json
{"cmd": "load_recipe", "data": {"segments": [...]}}
{"cmd": "start"}
{"cmd": "status"}
{"cmd": "abort"}
```

SKR responds:

```json
{"status": "ok", "state": "WELDING", "segment": 42, "temp": 210.5}
{"error": "THERMAL_RUNAWAY"}
```

---

## Web Interface (Planned)

### Features

1. **Dashboard**
   - Current status
   - Temperature graph
   - Progress bar
   - Error log

2. **Recipe Upload**
   - Drag-and-drop JSON
   - Preview segments
   - Start button

3. **Settings**
   - Wi-Fi configuration
   - Material profiles
   - Calibration values

4. **History**
   - Past splice jobs
   - Success/failure stats
   - Filament usage

### Tech Stack

```
ESP32 Web Stack:
- ESPAsyncWebServer: HTTP server
- LittleFS: File system for HTML/CSS/JS
- ArduinoJSON: Data serialization
- WebSockets: Real-time updates
```

### UI Framework (for development)

Build web files on PC, then upload to ESP32:

```bash
# Development
cd esp32/web
npm install
npm run build  # Outputs to /dist

# Upload to ESP32
pio run -t uploadfs
```

---

## mDNS Discovery

```cpp
// ESP32 advertises as splice3d.local
MDNS.begin("splice3d");
MDNS.addService("http", "tcp", 80);

// Access via: http://splice3d.local
```

---

## OctoPrint Integration

### MQTT Bridge

ESP32 can publish status to MQTT broker:

```cpp
mqttClient.publish("splice3d/status", statusJSON);
```

OctoPrint plugin subscribes and displays status.

### REST API

ESP32 exposes REST endpoints:

```
GET  /api/status     - Current state
POST /api/recipe     - Upload recipe
POST /api/start      - Start splicing
POST /api/abort      - Emergency stop
```

---

## Implementation Timeline

| Phase | Feature | Priority |
|-------|---------|----------|
| V3.0 | Basic ESP32-to-SKR serial | High |
| V3.1 | Web interface (status only) | High |
| V3.2 | Recipe upload via web | Medium |
| V3.3 | mDNS discovery | Medium |
| V3.4 | MQTT integration | Low |
| V3.5 | OctoPrint plugin | Low |

---

## Pin Assignments (ESP32)

```cpp
// esp32_config.h

// UART to SKR
#define SKR_TX_PIN 1
#define SKR_RX_PIN 3
#define SKR_BAUD 115200

// Status LED
#define STATUS_LED_PIN 2

// Optional: Direct TMC control (future)
#define TMC_UART_PIN 16
```

---

## Security Considerations

1. **Wi-Fi credentials** - Store encrypted in ESP32 flash
2. **Web interface** - Consider authentication
3. **OTA updates** - Password-protected firmware updates
4. **HTTPS** - Optional for local network

---

## Getting Started (Future)

```bash
# Clone ESP32 firmware (when ready)
cd esp32
pio run -t upload

# Connect to Splice3D Wi-Fi AP
# Configure your home Wi-Fi
# Access http://splice3d.local
```
