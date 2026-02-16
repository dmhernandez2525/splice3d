/**
 * Splice3D Prusaslicer G-Code Parsing Plugin (F7.2).
 *
 * PrusaSlicer G-code parser with multi-material config and MMU tool mappings.
 */

#ifndef SLICER_PRUSA_H
#define SLICER_PRUSA_H

#include <Arduino.h>

struct SlicerPrusaStats {
    uint16_t parsedLines;
    uint16_t toolChangesFound;
    bool mmuDetected;
    uint32_t errorsEncountered;
    bool parseComplete;
};

void setupSlicerPrusa();
void updateSlicerPrusa();
SlicerPrusaStats getSlicerPrusaStats();
void serializeSlicerPrusaStats();

#endif  // SLICER_PRUSA_H
