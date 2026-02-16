/**
 * Splice3D Manufacturing Readiness Validation And Certification (F10.4).
 *
 * Self-test sequences, calibration verification, uptime tracking, failure rate monitoring.
 */

#ifndef MFG_READY_H
#define MFG_READY_H

#include <Arduino.h>

constexpr uint8_t kMaxTestSteps = 16;
enum class TestCategory : uint8_t {
    MECHANICAL = 0,
    THERMAL = 1,
    ELECTRICAL = 2,
    CALIBRATION = 3,
    COMMUNICATION = 4,
    SAFETY = 5,
};

struct MfgReadyStats {
    uint32_t totalTestRuns;
    float passRate;
    uint32_t avgTestDurationMs;
    uint16_t lastCertDate;
    bool certValid;
    float failureRate;
};

void setupMfgReady();
void updateMfgReady();
MfgReadyStats getMfgReadyStats();
void serializeMfgReadyStats();

#endif  // MFG_READY_H
