/**
 * Splice3D Cutting System (F2.4).
 *
 * Manages servo/stepper blade, wear tracking, quality detection,
 * maintenance alerts, and EEPROM statistics.
 */

#ifndef CUTTING_SYSTEM_H
#define CUTTING_SYSTEM_H

#include <Arduino.h>

enum class CutResult : uint8_t {
    SUCCESS = 0,
    INCOMPLETE = 1,
    BLADE_WORN = 2,
    TIMEOUT = 3,
    ABORTED = 4,
};

struct CutStatistics {
    uint32_t totalCuts;
    uint32_t successfulCuts;
    uint32_t failedCuts;
    uint32_t lastMaintenanceCut;
    uint16_t averageForce;
    bool maintenanceDue;
};

struct CutConfig {
    uint8_t openAngle;
    uint8_t closedAngle;
    uint16_t travelMs;
    float preCutRetractMm;
    float verifyAdvanceMm;
    uint32_t maintenanceInterval;
    uint16_t maxForceThreshold;
};

void setupCuttingSystem();
void updateCuttingSystem();

CutResult executeCut();
CutResult executeCutForMaterial(uint8_t materialIndex);
bool isCutInProgress();

void triggerManualCut();
bool isManualCutPending();

CutStatistics getCutStatistics();
CutConfig getCutConfig();

void setCutAngles(uint8_t openAngle, uint8_t closedAngle);
void setCutTravelMs(uint16_t travelMs);
void setMaintenanceInterval(uint32_t interval);

bool saveCutStatistics();
bool loadCutStatistics();
void resetCutStatistics();
void acknowledgeMaintenanceAlert();

#endif  // CUTTING_SYSTEM_H
