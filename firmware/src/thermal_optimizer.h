/**
 * Splice3D Thermal Optimization (F6.2).
 *
 * Predictive thermal management for splice operations. Schedules
 * pre-heating based on upcoming splices, reuses residual heat
 * between consecutive same-material splices, and minimizes total
 * thermal cycles to reduce energy use and wear.
 */

#ifndef THERMAL_OPTIMIZER_H
#define THERMAL_OPTIMIZER_H

#include <Arduino.h>
#include "material_database.h"

constexpr uint8_t kMaxPreheatQueue = 8;
constexpr uint16_t kHeatReuseThresholdC = 15;
constexpr uint32_t kPreheatLeadTimeMs = 5000;

enum class ThermalState : uint8_t {
    IDLE = 0,
    PREHEATING,
    AT_TEMP,
    COOLING,
    REUSING_HEAT,
};

struct PreheatEntry {
    MaterialType material;
    uint16_t targetTempC;
    uint32_t scheduledTimeMs;
    bool started;
    bool completed;
    bool active;
};

struct HeatReuseRecord {
    uint16_t currentTempC;
    uint16_t targetTempC;
    uint16_t savedDegrees;
    uint32_t savedTimeMs;
    bool reused;
};

struct ThermalOptimizerStats {
    uint16_t totalPreheats;
    uint16_t successfulPreheats;
    uint16_t heatReuses;
    uint32_t totalSavedMs;
    uint16_t totalSavedDegrees;
    uint16_t thermalCyclesAvoided;
    float avgPreheatAccuracyC;
};

void setupThermalOptimizer();
void updateThermalOptimizer();

// Schedule a preheat for an upcoming splice. Returns index or 255.
uint8_t schedulePreheat(MaterialType material, uint16_t targetTempC,
                        uint32_t leadTimeMs);

// Check if preheating can be skipped due to residual heat.
HeatReuseRecord checkHeatReuse(uint16_t currentTempC,
                                uint16_t targetTempC);

// Cancel a scheduled preheat.
bool cancelPreheat(uint8_t index);

// Clear the preheat queue.
void clearPreheatQueue();

// Mark current splice complete (updates thermal state).
void onSpliceComplete(uint16_t finalTempC);

// Query APIs.
ThermalState getThermalState();
uint8_t getPreheatQueueSize();
PreheatEntry getPreheatEntry(uint8_t index);
uint16_t getLastSpliceTempC();

// Statistics.
ThermalOptimizerStats getThermalStats();
void serializeThermalStats();

#endif  // THERMAL_OPTIMIZER_H
