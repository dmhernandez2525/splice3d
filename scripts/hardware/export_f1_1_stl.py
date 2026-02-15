#!/usr/bin/env python3
"""Export F1.1 OpenSCAD files to STL when OpenSCAD is available."""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from postprocessor.mechanical_validation import load_mechanical_layout

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def export_stl_files() -> int:
    """Export all STL files described in the mechanical layout manifest."""
    openscad_bin = shutil.which("openscad")
    if openscad_bin is None:
        logger.error("OpenSCAD is not installed. Install openscad to export STL files.")
        return 2

    manifest_path = PROJECT_ROOT / "hardware" / "f1_1" / "spec" / "mechanical_layout.json"
    layout = load_mechanical_layout(manifest_path)

    for part in layout.printable_parts:
        source_path = PROJECT_ROOT / part.source_scad
        stl_path = PROJECT_ROOT / part.output_stl
        stl_path.parent.mkdir(parents=True, exist_ok=True)

        if not source_path.exists():
            logger.error("Missing source CAD file for %s: %s", part.name, source_path)
            return 1

        command = [openscad_bin, "-o", str(stl_path), str(source_path)]
        logger.info("Exporting %s", part.name)

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error("OpenSCAD export failed for %s", part.name)
            logger.error("stderr: %s", result.stderr.strip())
            return result.returncode

        if not stl_path.exists() or stl_path.stat().st_size <= 84:
            logger.error("Generated STL is missing or empty: %s", stl_path)
            return 1

    logger.info("STL export completed successfully")
    return 0


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(export_stl_files())
