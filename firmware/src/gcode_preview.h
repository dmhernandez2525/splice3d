/**
 * Splice3D G-Code Visualization And Color Preview (F8.2).
 *
 * G-code visualization with layer-by-layer color assignments and filament usage stats.
 */

#ifndef GCODE_PREVIEW_H
#define GCODE_PREVIEW_H

#include <Arduino.h>

constexpr uint16_t kMaxPreviewLayers = 512;
constexpr uint8_t kMaxColorZones = 64;
enum class GcodeViewMode : uint8_t {
    LAYER_BY_LAYER = 0,
    COLOR_MAP = 1,
    SPLICE_POINTS = 2,
    USAGE_CHART = 3,
};

struct GcodePreviewStats {
    uint32_t totalLayers;
    uint32_t totalColorZones;
    uint32_t totalSplicePoints;
    uint32_t filamentUsedMm;
    bool previewReady;
};

void setupGcodePreview();
void updateGcodePreview();
GcodePreviewStats getGcodePreviewStats();
void serializeGcodePreviewStats();

#endif  // GCODE_PREVIEW_H
