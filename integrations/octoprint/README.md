# Splice3D OctoPrint Plugin

> OctoPrint plugin skeleton for future development.

## Overview

This directory will contain an OctoPrint plugin that:
1. Intercepts multi-color G-code uploads
2. Calls the Splice3D post-processor
3. Communicates with the Splice3D machine
4. Waits for splicing to complete
5. Starts the print with modified G-code

## Status

**Not yet implemented** - See docs/INTEGRATION_OPTIONS.md for roadmap.

## Planned Features

- [ ] Auto-detect multi-tool G-code
- [ ] Call post-processor automatically
- [ ] Serial communication with Splice3D
- [ ] Progress display in OctoPrint UI
- [ ] Settings panel for configuration
- [ ] Queue management

## Installation (Future)

```bash
pip install octoprint-splice3d
# or
pip install /path/to/splice3d/integrations/octoprint
```

## Development

```bash
# Install in development mode
pip install -e .

# Run OctoPrint with plugin
octoprint serve
```

## Plugin Structure (Planned)

```
octoprint_splice3d/
├── __init__.py          # Plugin entry point
├── static/
│   ├── js/
│   │   └── splice3d.js  # Frontend JS
│   └── css/
│       └── splice3d.css # Styles
├── templates/
│   └── splice3d.jinja2  # Settings template
└── api.py               # REST API endpoints
```

## API Endpoints (Planned)

```
GET  /api/plugin/splice3d/status     # Get Splice3D machine status
POST /api/plugin/splice3d/process    # Process G-code file
POST /api/plugin/splice3d/start      # Start splicing
POST /api/plugin/splice3d/abort      # Abort current operation
GET  /api/plugin/splice3d/settings   # Get settings
POST /api/plugin/splice3d/settings   # Update settings
```
