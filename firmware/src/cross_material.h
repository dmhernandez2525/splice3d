/**
 * Splice3D Cross-Material Splicing (F5.2).
 *
 * Material compatibility matrix defining which material pairs can
 * be spliced, with temperature/time overrides for cross-material
 * joints and compatibility scoring.
 */

#ifndef CROSS_MATERIAL_H
#define CROSS_MATERIAL_H

#include <Arduino.h>
#include "material_database.h"

constexpr uint8_t kMaxCompatEntries = 16;

enum class CompatLevel : uint8_t {
    INCOMPATIBLE = 0,
    POOR,
    FAIR,
    GOOD,
    EXCELLENT,
};

struct CompatOverride {
    uint16_t spliceTemp;
    uint16_t holdTimeMs;
    float compressionMm;
    uint16_t coolTimeMs;
};

struct CompatEntry {
    MaterialType typeA;
    MaterialType typeB;
    CompatLevel level;
    uint8_t score;              // 0-100
    CompatOverride overrides;
    bool hasOverrides;
    bool active;
};

struct CompatMatrixStats {
    uint8_t totalEntries;
    uint8_t activeEntries;
    uint8_t incompatiblePairs;
    uint8_t excellentPairs;
};

void setupCrossMaterial();
void updateCrossMaterial();

// Query compatibility between two material types.
CompatEntry getCompatibility(MaterialType a, MaterialType b);
CompatLevel getCompatLevel(MaterialType a, MaterialType b);
uint8_t getCompatScore(MaterialType a, MaterialType b);

// Check if a pair can be spliced (level > INCOMPATIBLE).
bool canSplice(MaterialType a, MaterialType b);

// Get overrides for a cross-material splice. Falls back to
// material A defaults when no override is defined.
CompatOverride getSpliceOverrides(MaterialType a, MaterialType b);

// Add or update a compatibility entry. Returns index or 255.
uint8_t setCompatibility(MaterialType a, MaterialType b,
                         CompatLevel level, uint8_t score);
uint8_t setCompatibilityWithOverrides(MaterialType a, MaterialType b,
                                      CompatLevel level, uint8_t score,
                                      const CompatOverride& overrides);

// Serialize to serial.
void serializeCompatMatrix();

// Statistics.
CompatMatrixStats getCompatMatrixStats();

// Load built-in compatibility matrix.
void loadDefaultCompatMatrix();

#endif  // CROSS_MATERIAL_H
