#include "cutting_system.h"
#include "config.h"
#include "stepper_control.h"
#include <EEPROM.h>
namespace {
constexpr uint32_t kStatSignature = 0x43555453UL;  // "CUTS"
struct PersistentCutStats {
    uint32_t signature;
    uint32_t totalCuts;
    uint32_t successfulCuts;
    uint32_t failedCuts;
    uint32_t lastMaintenanceCut;
    uint32_t checksum;
};
uint32_t computeStatsChecksum(const PersistentCutStats& s) {
    return s.signature ^ s.totalCuts ^ s.successfulCuts ^ s.failedCuts ^ s.lastMaintenanceCut ^ 0xB44DB44DUL;
}
enum class CutPhase : uint8_t {
    IDLE = 0,
    RETRACTING,
    CLOSING,
    HOLDING,
    OPENING,
    VERIFYING,
    DONE,
};
struct CutState {
    CutConfig config;
    CutStatistics stats;
    CutPhase phase;
    uint32_t phaseStartMs;
    bool cutInProgress;
    bool manualCutPending;
    CutResult lastResult;
    uint16_t lastForceReading;
    uint32_t forceAccum;
    uint32_t forceCount;
};
CutState st = {
    {CUTTER_SERVO_OPEN_ANGLE, CUTTER_SERVO_CLOSED_ANGLE,
     static_cast<uint16_t>(CUTTER_SERVO_TRAVEL_MS),
     CUTTER_PRE_CUT_RETRACT_MM, CUTTER_VERIFY_ADVANCE_MM,
     CUTTER_MAINTENANCE_INTERVAL, CUTTER_MAX_FORCE_THRESHOLD},
    {0, 0, 0, 0, 0, false},
    CutPhase::IDLE, 0, false, false,
    CutResult::SUCCESS, 0, 0, 0,
};
void enterPhase(CutPhase phase) {
    st.phase = phase;
    st.phaseStartMs = millis();
}
void finishCut(CutResult result) {
    st.lastResult = result;
    st.cutInProgress = false;
    st.stats.totalCuts++;
    if (result == CutResult::SUCCESS) {
        st.stats.successfulCuts++;
    } else {
        st.stats.failedCuts++;
    }
    if (st.forceCount > 0) {
        st.stats.averageForce = static_cast<uint16_t>(st.forceAccum / st.forceCount);
    }
    const uint32_t cutsSinceMaint = st.stats.totalCuts - st.stats.lastMaintenanceCut;
    st.stats.maintenanceDue = cutsSinceMaint >= st.config.maintenanceInterval;
    if (st.stats.maintenanceDue) {
        Serial.print(F("CUTTER_MAINT cuts_since="));
        Serial.println(cutsSinceMaint);
    }
    enterPhase(CutPhase::DONE);
}
uint16_t readServoForce() {
#if CUTTER_IS_SERVO
    return static_cast<uint16_t>(analogRead(THERMISTOR_PIN));
#else
    return 0;
#endif
}
}  // namespace
void setupCuttingSystem() {
    loadCutStatistics();
}
void updateCuttingSystem() {
    if (!st.cutInProgress && st.manualCutPending) {
        st.manualCutPending = false;
        executeCut();
        return;
    }
    if (!st.cutInProgress) return;
    const uint32_t elapsed = millis() - st.phaseStartMs;
    switch (st.phase) {
        case CutPhase::RETRACTING:
            if (isMotorIdle(MotorAxis::FEED_A) && isMotorIdle(MotorAxis::FEED_B)) {
                activateCutter();
                enterPhase(CutPhase::CLOSING);
            }
            if (elapsed > 5000UL) { finishCut(CutResult::TIMEOUT); }
            break;
        case CutPhase::CLOSING:
            if (elapsed >= st.config.travelMs) {
                st.lastForceReading = readServoForce();
                st.forceAccum += st.lastForceReading;
                st.forceCount++;
                enterPhase(CutPhase::HOLDING);
            }
            break;
        case CutPhase::HOLDING:
            if (elapsed >= 200UL) {
                deactivateCutter();
                enterPhase(CutPhase::OPENING);
            }
            break;
        case CutPhase::OPENING:
            if (elapsed >= st.config.travelMs) {
                if (st.config.verifyAdvanceMm > 0.0f) {
                    moveRelative(MotorAxis::FEED_A, st.config.verifyAdvanceMm);
                    enterPhase(CutPhase::VERIFYING);
                } else {
                    CutResult result = CutResult::SUCCESS;
                    if (st.lastForceReading > st.config.maxForceThreshold) {
                        result = CutResult::BLADE_WORN;
                    }
                    finishCut(result);
                }
            }
            break;
        case CutPhase::VERIFYING:
            if (isMotorIdle(MotorAxis::FEED_A)) {
                CutResult result = CutResult::SUCCESS;
                if (st.lastForceReading > st.config.maxForceThreshold) {
                    result = CutResult::BLADE_WORN;
                }
                finishCut(result);
            }
            if (elapsed > 3000UL) { finishCut(CutResult::TIMEOUT); }
            break;
        case CutPhase::IDLE:
        case CutPhase::DONE:
            break;
    }
}
CutResult executeCut() {
    if (st.cutInProgress) return CutResult::ABORTED;
    st.cutInProgress = true;
    st.forceAccum = 0;
    st.forceCount = 0;
    st.lastForceReading = 0;
    if (st.config.preCutRetractMm > 0.0f) {
        moveRelative(MotorAxis::FEED_A, -st.config.preCutRetractMm);
        moveRelative(MotorAxis::FEED_B, -st.config.preCutRetractMm);
        enterPhase(CutPhase::RETRACTING);
    } else {
        activateCutter();
        enterPhase(CutPhase::CLOSING);
    }
    return CutResult::SUCCESS;
}
CutResult executeCutForMaterial(uint8_t materialIndex) {
    (void)materialIndex;
    return executeCut();
}
bool isCutInProgress() { return st.cutInProgress; }
void triggerManualCut() { st.manualCutPending = true; }
bool isManualCutPending() { return st.manualCutPending; }
CutStatistics getCutStatistics() { return st.stats; }
CutConfig getCutConfig() { return st.config; }
void setCutAngles(uint8_t openAngle, uint8_t closedAngle) {
    st.config.openAngle = openAngle;
    st.config.closedAngle = closedAngle;
}
void setCutTravelMs(uint16_t travelMs) { st.config.travelMs = travelMs; }
void setMaintenanceInterval(uint32_t interval) { st.config.maintenanceInterval = interval; }
bool saveCutStatistics() {
    PersistentCutStats ps = {
        kStatSignature,
        st.stats.totalCuts, st.stats.successfulCuts,
        st.stats.failedCuts, st.stats.lastMaintenanceCut, 0,
    };
    ps.checksum = computeStatsChecksum(ps);
    EEPROM.put(CUTTER_EEPROM_ADDRESS, ps);
    return true;
}
bool loadCutStatistics() {
    PersistentCutStats ps = {};
    EEPROM.get(CUTTER_EEPROM_ADDRESS, ps);
    if (ps.signature != kStatSignature) return false;
    if (computeStatsChecksum(ps) != ps.checksum) return false;
    st.stats.totalCuts = ps.totalCuts;
    st.stats.successfulCuts = ps.successfulCuts;
    st.stats.failedCuts = ps.failedCuts;
    st.stats.lastMaintenanceCut = ps.lastMaintenanceCut;
    const uint32_t since = st.stats.totalCuts - st.stats.lastMaintenanceCut;
    st.stats.maintenanceDue = since >= st.config.maintenanceInterval;
    return true;
}
void resetCutStatistics() {
    st.stats = {0, 0, 0, 0, 0, false};
    saveCutStatistics();
}
void acknowledgeMaintenanceAlert() {
    st.stats.lastMaintenanceCut = st.stats.totalCuts;
    st.stats.maintenanceDue = false;
    saveCutStatistics();
    Serial.println(F("OK CUTTER_MAINT_ACK"));
}
