/**
 * Splice3D Splice Execution Engine (F3.2).
 *
 * Orchestrates the complete splice sequence: retract, advance, heat,
 * compress, hold, cool, and verify.
 */

#ifndef SPLICE_EXECUTION_H
#define SPLICE_EXECUTION_H

#include <Arduino.h>

enum class SplicePhase : uint8_t {
    IDLE = 0,
    RETRACT_A,
    ADVANCE_B,
    HEATING,
    COMPRESSING,
    HOLDING,
    COOLING,
    VERIFYING,
    COMPLETE,
    FAILED,
};

struct SpliceProfile {
    float temperatureC;
    float compressionMm;
    uint32_t holdTimeMs;
    uint32_t coolTimeMs;
    float coolTargetC;
    float pullTestMm;
    float minPullForce;
};

struct SpliceTelemetry {
    SplicePhase phase;
    float temperatureC;
    float compressionMm;
    uint32_t elapsedMs;
    uint32_t estimatedRemainingMs;
    float qualityScore;
    bool passed;
};

struct SpliceStatistics {
    uint32_t totalAttempts;
    uint32_t successes;
    uint32_t failures;
    float averageSpliceTimeMs;
    float averageQualityScore;
};

void setupSpliceExecution();
void updateSpliceExecution();

bool startSplice(uint8_t materialIndex);
void abortSplice();
bool isSpliceActive();
bool isSpliceComplete();

SpliceTelemetry getSpliceTelemetry();
SpliceStatistics getSpliceStatistics();
SplicePhase getSplicePhase();

void resetSpliceStatistics();

#endif  // SPLICE_EXECUTION_H
