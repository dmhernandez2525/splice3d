# Splice3D Feature Roadmap

> A phased approach to building a comprehensive multi-color filament splicer ecosystem.

## Project Vision

Splice3D enables multi-color 3D printing on any single-extruder printer by pre-splicing filament segments before printing. The ultimate goal is a fully automated system capable of handling prints with 4000+ color changes (like the Starry Night Vase benchmark).

---

## Phase 1: Core Splicer Features

**Status:** In Progress
**Target:** v0.2.0
**Timeline:** Q1 2026

### 1.1 Recipe Generation Engine

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Multi-slicer G-code parsing | High | Done | Parse OrcaSlicer, PrusaSlicer, Cura |
| T-command extraction | High | Done | Extract tool changes (T0, T1, etc.) |
| M600 color change support | High | Done | Support manual color change commands |
| Extrusion length calculation | High | Done | Calculate filament per segment |
| Segment merging | Medium | Done | Merge short segments below threshold |
| Recipe validation | Medium | Done | Pre-flight checks before splicing |
| Material profile support | Medium | Done | Per-material splice parameters |

### 1.2 G-code Modification

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Tool change stripping | High | Done | Remove T commands from output |
| Pause injection | High | Done | Add spool load pause at start |
| Purge optimization | Medium | Planned | Minimize purge tower waste |
| Transition tower removal | Medium | Planned | Remove if using pre-spliced filament |
| Prime tower optimization | Low | Backlog | Reduce prime tower size |

### 1.3 CLI Tools

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| splice3d main CLI | High | Done | Primary postprocessor command |
| splice3d-analyze | High | Done | G-code statistics and validation |
| splice3d-simulate | Medium | Done | Test splice cycles without hardware |
| Interactive mode | Low | Backlog | Guided recipe creation |

---

## Phase 2: Hardware Integration

**Status:** Planned
**Target:** v0.3.0
**Timeline:** Q2 2026

### 2.1 Serial Communication

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| USB serial protocol | High | Partial | Send commands to splicer |
| Recipe upload | High | Planned | Transfer splice recipe to device |
| Status monitoring | High | Planned | Real-time splice progress |
| Error handling | High | Planned | Recovery from splice failures |
| Batch processing | Medium | Backlog | Queue multiple prints |

### 2.2 Real-time Monitoring

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Temperature monitoring | High | Planned | Live heater temperature |
| Splice progress | High | Planned | Segment X of Y status |
| Error notifications | High | Planned | Alert on failures |
| Timing statistics | Medium | Planned | Splice cycle timing |
| Quality metrics | Medium | Backlog | Track success rate |

### 2.3 Position Tracking

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Encoder wheel support | High | Planned | Measure filament length |
| Drift compensation | High | Planned | Correct for slippage |
| Dimple encoding | Medium | Research | Embed position in filament |
| Dimple reader | Medium | Research | Read position marks |

---

## Phase 3: Advanced Features

**Status:** Research
**Target:** v0.4.0
**Timeline:** Q3-Q4 2026

### 3.1 Multi-Material Profiles

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Material database | High | Partial | Common filament parameters |
| PLA profiles | High | Done | PLA splice settings |
| PETG profiles | High | Done | PETG splice settings |
| ABS profiles | Medium | Done | ABS splice settings |
| TPU profiles | Medium | Backlog | Flexible filament support |
| Custom profiles | Medium | Planned | User-defined materials |
| Cross-material splicing | Low | Research | Splice different materials |

### 3.2 Optimization Algorithms

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Segment batching | High | Backlog | Optimize segment order |
| Thermal optimization | Medium | Backlog | Minimize heating cycles |
| Waste reduction | Medium | Planned | Minimize purge/transition |
| Speed optimization | Medium | Backlog | Reduce total splice time |
| Parallel splicer support | Low | Research | Multiple splicers |

### 3.3 Slicer Integration

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| OrcaSlicer plugin | High | Planned | Native integration |
| PrusaSlicer plugin | High | Planned | Native integration |
| Cura plugin | Medium | Backlog | Native integration |
| Bambu Studio support | Medium | Research | Parse proprietary G-code |

---

## Phase 4: GUI/Web Interface

**Status:** Research
**Target:** v1.0.0
**Timeline:** 2027

### 4.1 Desktop GUI

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Recipe editor | High | Planned | Visual recipe creation |
| G-code preview | High | Planned | Visualize color changes |
| Material manager | Medium | Planned | Manage filament profiles |
| Device connection | Medium | Planned | Connect to splicer |
| Queue management | Medium | Backlog | Manage print queue |

### 4.2 Web Dashboard

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Remote monitoring | High | Research | Monitor from browser |
| Recipe upload | High | Research | Upload via web |
| Status display | High | Research | Live splicer status |
| History/analytics | Medium | Research | Past splice statistics |
| Multi-device support | Low | Research | Manage multiple splicers |

### 4.3 ESP32 Integration

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Wi-Fi connectivity | High | Research | Wireless control |
| Web server | High | Research | Embedded web interface |
| OTA updates | Medium | Research | Firmware updates over Wi-Fi |
| Mobile notifications | Medium | Research | Push notifications |

---

## Competitive Analysis

### Mosaic Palette (Mosaic Manufacturing)

**Product:** Palette 3 Pro ($799)

| Feature | Palette 3 | Splice3D |
|---------|-----------|----------|
| Input colors | 8 | 2 (v1), 4+ planned |
| Print-time splicing | Yes | No (pre-splicing) |
| Waste percentage | ~30-40% | ~5-10% (target) |
| Printer compatibility | Any | Any |
| Open source | No | Yes |
| Price | $799 | ~$200 (DIY) |

**Palette Strengths:**
- Mature product with polished software
- Real-time splicing with printer sync
- Canvas slicer integration
- Commercial support

**Palette Weaknesses:**
- High purge waste (transition tower)
- Complex calibration
- Closed ecosystem
- Expensive consumables (ping system)

**Splice3D Opportunity:**
- Pre-splicing eliminates printer sync complexity
- Target 80%+ waste reduction vs Palette
- Open source community development
- Lower cost DIY build

---

### Prusa MMU (Prusa Research)

**Product:** Multi Material Upgrade 3 ($349)

| Feature | MMU3 | Splice3D |
|---------|------|----------|
| Input colors | 5 | 2 (v1), 4+ planned |
| Printer compatibility | Prusa only | Any |
| Mechanism | Real-time swap | Pre-spliced |
| Reliability | Improved in v3 | TBD |
| Waste | Medium | Low (target) |

**MMU3 Strengths:**
- Integrated with Prusa ecosystem
- Active development and support
- Large user community
- Good reliability (v3)

**MMU3 Weaknesses:**
- Prusa printers only
- Still has purge waste
- Complex mechanism (jam-prone)
- Real-time swaps slow prints

**Splice3D Opportunity:**
- Works with any single-extruder printer
- Eliminate real-time complexity
- Focus on reliability through simplicity

---

### BigBrain3D (3DChameleon)

**Product:** 3DChameleon ($199)

| Feature | 3DChameleon | Splice3D |
|---------|-------------|----------|
| Input colors | 4 | 2 (v1), 4+ planned |
| Mechanism | Y-splitter | Pre-spliced |
| Waste | High (long purge) | Low (target) |
| Price | $199 | ~$200 (DIY) |
| Open source | No | Yes |

**3DChameleon Strengths:**
- Affordable entry point
- Simple mechanism
- Works with many printers

**3DChameleon Weaknesses:**
- Very high purge waste
- Slow color changes
- Limited to 4 colors
- Requires purge bucket

**Splice3D Opportunity:**
- Similar price point with better waste reduction
- Open source allows customization
- Pre-spliced approach is fundamentally more efficient

---

### ERCF (Enraged Rabbit Carrot Feeder)

**Product:** Open Source MMU

| Feature | ERCF | Splice3D |
|---------|------|----------|
| Input colors | 9+ | 2 (v1), 4+ planned |
| Open source | Yes | Yes |
| Mechanism | Real-time swap | Pre-spliced |
| Community | Active | Starting |
| Complexity | High | Medium |

**ERCF Strengths:**
- Open source with active community
- High color count
- Works with Klipper
- Highly customizable

**ERCF Weaknesses:**
- Complex build
- Requires Klipper
- Real-time reliability challenges
- Steep learning curve

**Splice3D Opportunity:**
- Simpler mechanism (fewer failure points)
- Works with any firmware
- Pre-splicing is inherently more reliable
- Appeal to non-Klipper users

---

## Market Positioning

```
                    Low Waste
                        ^
                        |
           Splice3D ----+---- (Future ideal)
            (Target)    |
                        |
    +-------------------+-------------------+
    |                   |                   |
    Low Cost            |            High Cost
    |                   |                   |
    +-------------------+-------------------+
                        |
        3DChameleon ----+---- Palette 3
                        |
            ERCF -------+---- MMU3
                        |
                    High Waste
```

**Splice3D Target Market:**
- Makers who want multi-color without high waste
- Users of non-Prusa printers
- DIY builders who want open source
- Print farms optimizing material costs
- Complex multi-color prints (1000+ changes)

---

## Technical Differentiation

### Pre-Splicing vs Real-Time Splicing

| Aspect | Real-Time (Palette/MMU) | Pre-Spliced (Splice3D) |
|--------|-------------------------|------------------------|
| Printer sync | Required | Not needed |
| Failure recovery | Complex | Easier |
| Purge waste | 30-50% typical | 5-10% target |
| Print speed | Slowed by changes | Normal speed |
| Complexity | High (timing critical) | Lower |
| Offline operation | No | Yes |

### Key Innovation: Dimple Encoding

Splice3D's planned dimple encoding system provides:
- Sub-millimeter position tracking
- Drift compensation during printing
- No foreign materials (unlike ink marks)
- Works at print speeds

---

## Success Metrics

### Phase 1 (Core)
- [ ] Parse 95% of OrcaSlicer G-code files
- [ ] Generate valid recipes for 2-color prints
- [ ] Pass 50+ unit tests
- [ ] Documentation for all CLI tools

### Phase 2 (Hardware)
- [ ] Successful hardware prototype build
- [ ] 100+ splices without failure
- [ ] Complete Starry Night Vase benchmark
- [ ] Splice strength >20N

### Phase 3 (Advanced)
- [ ] Support 4+ input colors
- [ ] Cross-material splicing (PLA-PETG)
- [ ] Waste <10% on complex prints
- [ ] Slicer plugin for OrcaSlicer

### Phase 4 (GUI)
- [ ] Web dashboard with live monitoring
- [ ] Recipe editor with preview
- [ ] 100+ active users
- [ ] Community-contributed material profiles

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to help with:
- Hardware testing and calibration data
- Material profile contributions
- Slicer plugin development
- Documentation and tutorials
- Translation to other languages
