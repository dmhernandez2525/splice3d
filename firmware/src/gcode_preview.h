/**
 * Splice3D G-Code Visualization And Color Preview (F8.2).
 *
 * G-code visualization with layer-by-layer color assignments and filament usage stats.
 */

#ifndef GCODE_PREVIEW_H
#define GCODE_PREVIEW_H

#include <Arduino.h>

struct GcodePreviewStats {
    uint32_t totalLayers;
    uint32_t totalColorZones;
    uint32_t totalSplicePoints;
    uint16_t filamentUsedMm;
    bool previewReady;
};

void setupGcodePreview();
void updateGcodePreview();
GcodePreviewStats getGcodePreviewStats();
void serializeGcodePreviewStats();

#endif  // GCODE_PREVIEW_H
