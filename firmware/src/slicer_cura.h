/**
 * Splice3D Cura G-Code Parsing Plugin (F7.3).
 *
 * Cura G-code parser with T-command patterns, start/end block handling, marketplace support.
 */

#ifndef SLICER_CURA_H
#define SLICER_CURA_H

#include <Arduino.h>

enum class CuraExtruderMode : uint8_t {
    SINGLE = 0,
    DUAL = 1,
    MULTI = 2,
};

enum class CuraBlockType : uint8_t {
    START_GCODE = 0,
    PRINT_BODY = 1,
    END_GCODE = 2,
    TOOL_CHANGE = 3,
    PRIME_TOWER = 4,
};

struct SlicerCuraStats {
    uint16_t parsedLines;
    uint16_t toolChangesFound;
    uint16_t blocksIdentified;
    uint32_t errorsEncountered;
    bool pluginLoaded;
};

void setupSlicerCura();
void updateSlicerCura();
SlicerCuraStats getSlicerCuraStats();
void serializeSlicerCuraStats();

#endif  // SLICER_CURA_H
