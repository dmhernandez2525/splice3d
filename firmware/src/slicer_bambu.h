/**
 * Splice3D Bambu Studio G-Code Parsing Support (F7.4).
 *
 * Bambu Studio G-code parser with proprietary extensions and AMS metadata.
 */

#ifndef SLICER_BAMBU_H
#define SLICER_BAMBU_H

#include <Arduino.h>

constexpr uint8_t kAmsSlotsPerUnit = 4;
constexpr uint8_t kMaxAmsUnits = 4;

struct SlicerBambuStats {
    uint16_t parsedLines;
    bool amsUnitsDetected;
    uint16_t filamentChanges;
    uint16_t flushVolumeMl;
    uint16_t platesProcessed;
};

void setupSlicerBambu();
void updateSlicerBambu();
SlicerBambuStats getSlicerBambuStats();
void serializeSlicerBambuStats();

#endif  // SLICER_BAMBU_H
