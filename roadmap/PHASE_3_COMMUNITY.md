# Phase 3: Community & Kit Ecosystem

## Overview

Build the Splice3D community following the Voron model: open-source everything, certified kit vendors, solid documentation, and serial number culture.

**Goal:** Active maker community with quality kit vendors

---

## Milestones

### M1: Documentation Excellence (Week 1)

- [ ] Full assembly guide:
  - Step-by-step with photos
  - Video accompaniment
  - Troubleshooting sections
  - Tool requirements
- [ ] Calibration guide
- [ ] Material compatibility guide
- [ ] FAQ and common issues
- [ ] Multi-language support (EN, DE, ES)
- [ ] Printable quick-start card

**Documentation Structure:**
```
docs/
├── assembly/
│   ├── GETTING_STARTED.md
│   ├── HARDWARE_ASSEMBLY.md
│   ├── ELECTRONICS_WIRING.md
│   ├── FIRMWARE_FLASH.md
│   └── images/
├── calibration/
│   ├── ENCODER_CALIBRATION.md
│   ├── SPLICE_TUNING.md
│   └── MATERIAL_PROFILES.md
├── troubleshooting/
│   ├── COMMON_ISSUES.md
│   └── ERROR_CODES.md
└── reference/
    ├── BOM.md
    └── SPECIFICATIONS.md
```

**Acceptance Criteria:**
- Assembly completable by beginner
- Photos for every major step
- Video tutorials published

### M2: Open Source Release (Week 1-2)

- [ ] CAD files (STEP, STL)
- [ ] PCB files (KiCad/EasyEDA)
- [ ] Firmware source code
- [ ] Software source code
- [ ] License selection:
  - Hardware: CERN OHL-S
  - Software: MIT/Apache 2.0
- [ ] Contributing guidelines
- [ ] Code of conduct
- [ ] Issue templates

**Repository Structure:**
| Repo | Contents |
|------|----------|
| splice3d-hardware | CAD, PCB, BOM |
| splice3d-firmware | ESP32 code |
| splice3d-software | Desktop app, analyzer |
| splice3d-docs | Documentation site |

**Acceptance Criteria:**
- All files publicly available
- Licenses clearly stated
- Build instructions complete

### M3: Discord Community (Week 2)

- [ ] Discord server setup
- [ ] Channel organization:
  - #announcements
  - #general-chat
  - #build-help
  - #showcase
  - #troubleshooting
  - #firmware-dev
  - #software-dev
- [ ] Role system (Builder, Contributor, Vendor)
- [ ] Bot for serial number registration
- [ ] Moderation team
- [ ] Community guidelines

**Acceptance Criteria:**
- Server active and moderated
- Help channels responsive
- Community engaged

### M4: Serial Number Culture (Week 2-3)

- [ ] Serial number registration system
- [ ] Verification process:
  - Build photos required
  - Working splice video
  - Registration form
- [ ] Serial number database
- [ ] Builder profile pages
- [ ] Serial number badges
- [ ] Build gallery/showcase
- [ ] Statistics dashboard

**Serial Number Format:**
```
S3D-[YEAR]-[SEQ]-[VARIANT]
Example: S3D-2026-0001-KIT
```

**Variants:**
| Code | Description |
|------|-------------|
| DIY | Self-sourced build |
| KIT | Certified kit build |
| MOD | Modified design |

**Acceptance Criteria:**
- Registration process smooth
- Verification timely (<48h)
- Showcase displays nicely

### M5: Kit Vendor Program (Week 3-4)

- [ ] Vendor application process
- [ ] Kit certification requirements:
  - Complete BOM compliance
  - Quality standards
  - Support commitment
  - Pricing guidelines
- [ ] Vendor agreement
- [ ] Quality audit process
- [ ] Vendor listing page
- [ ] Kit reviews/ratings
- [ ] Vendor support forum

**Certification Requirements:**
| Requirement | Standard |
|-------------|----------|
| BOM compliance | 100% spec parts |
| Print quality | PETG, 0.2mm, 4 perimeters |
| Electronics | Tested before ship |
| Documentation | Vendor-specific additions |
| Support | 30-day response SLA |

**Acceptance Criteria:**
- Application process clear
- Certification standards defined
- Vendors listed and reviewed

### M6: Print Farm Testing (Week 4)

- [ ] Beta tester program
- [ ] Long-run reliability testing
- [ ] Diverse filament testing:
  - Multiple PLA brands
  - PETG variations
  - ABS/ASA
  - TPU
  - Specialty filaments
- [ ] Bug tracking and resolution
- [ ] Community feedback integration
- [ ] Performance benchmarks

**Testing Matrix:**
| Filament | Brands Tested | Status |
|----------|---------------|--------|
| PLA | 10+ | Required |
| PETG | 5+ | Required |
| ABS | 3+ | Required |
| TPU | 2+ | Stretch |

**Acceptance Criteria:**
- 100+ hours testing completed
- Major bugs resolved
- Community feedback addressed

### M7: Community Contributions (Week 4-5)

- [ ] Mod showcase system
- [ ] Community mods repository
- [ ] Contribution guidelines
- [ ] Pull request workflow
- [ ] Mod certification (tested/untested)
- [ ] Credit and attribution system
- [ ] Community challenges/competitions

**Popular Mod Categories:**
| Category | Examples |
|----------|----------|
| Enclosure | Temperature control |
| Lighting | Status LEDs |
| Capacity | 8+ spool holders |
| Integration | Printer-specific mounts |

**Acceptance Criteria:**
- Mods can be submitted
- Credit given properly
- Quality mods highlighted

### M8: Educational Content (Week 5)

- [ ] YouTube channel setup
- [ ] Build tutorial series
- [ ] Calibration walkthrough
- [ ] Advanced tips videos
- [ ] Troubleshooting guides
- [ ] Guest creator program
- [ ] Live build streams

**Video Content:**
| Series | Videos |
|--------|--------|
| Build Guide | 5-7 parts |
| Calibration | 3 parts |
| Tips & Tricks | Ongoing |
| Troubleshooting | As needed |

**Acceptance Criteria:**
- Videos professional quality
- Content comprehensive
- Engagement growing

---

## Technical Requirements

### Documentation Platform

| Option | Best For |
|--------|----------|
| GitBook | Beautiful docs |
| Docusaurus | Developer-focused |
| MkDocs | Simple, fast |

### Serial Number System

```python
# Registration API
POST /api/serial/register
{
  "builder_name": "string",
  "build_photos": ["url"],
  "splice_video": "url",
  "kit_vendor": "optional"
}
```

### Community Metrics

| Metric | Target (Year 1) |
|--------|-----------------|
| Registered builds | 500+ |
| Discord members | 2,000+ |
| Kit vendors | 5-10 |
| GitHub stars | 1,000+ |

---

## Kit Pricing Guidelines

| Kit Type | MSRP Range |
|----------|------------|
| DIY (4-color) | $99-149 |
| DIY (8-color) | $149-199 |
| Pre-assembled | $249-349 |
| Print + electronics | $79-99 |

---

## Definition of Done

- [ ] All milestones complete
- [ ] Documentation complete
- [ ] Open source release complete
- [ ] Discord active and moderated
- [ ] Serial number system running
- [ ] Kit vendors certified
- [ ] Beta testing complete
- [ ] Community contributions flowing
- [ ] Educational content published
- [ ] 500+ community members
