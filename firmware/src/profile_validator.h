/**
 * Splice3D Profile Validation (F5.4).
 *
 * Automated validation of material profiles against safety limits
 * including temperature range, time bounds, and force limits.
 * Includes a profile testing sequence for verifying splice
 * parameters before production use.
 */

#ifndef PROFILE_VALIDATOR_H
#define PROFILE_VALIDATOR_H

#include <Arduino.h>
#include "material_database.h"

constexpr uint8_t kMaxValidationErrors = 8;

enum class ValidationSeverity : uint8_t {
    INFO = 0,
    WARNING,
    ERROR,
    CRITICAL,
};

enum class ValidationCode : uint8_t {
    OK = 0,
    TEMP_TOO_LOW,
    TEMP_TOO_HIGH,
    HOLD_TIME_TOO_SHORT,
    HOLD_TIME_TOO_LONG,
    COMPRESSION_OUT_OF_RANGE,
    COOL_TIME_TOO_SHORT,
    COOL_TIME_TOO_LONG,
    PULL_FORCE_TOO_LOW,
    PULL_FORCE_TOO_HIGH,
    NAME_EMPTY,
    BRAND_EMPTY,
};

struct ValidationError {
    ValidationCode code;
    ValidationSeverity severity;
    float actual;
    float limit;
};

struct ValidationResult {
    ValidationError errors[kMaxValidationErrors];
    uint8_t errorCount;
    bool passed;
};

struct SafetyLimits {
    uint16_t minTempC;
    uint16_t maxTempC;
    uint16_t minHoldTimeMs;
    uint16_t maxHoldTimeMs;
    float minCompressionMm;
    float maxCompressionMm;
    uint16_t minCoolTimeMs;
    uint16_t maxCoolTimeMs;
    float minPullForceN;
    float maxPullForceN;
};

enum class TestPhase : uint8_t {
    IDLE = 0,
    HEATING,
    HOLDING,
    COMPRESSING,
    COOLING,
    PULL_TEST,
    COMPLETE,
    FAILED,
};

struct TestSequenceState {
    TestPhase phase;
    uint32_t phaseStartMs;
    uint8_t profileIndex;
    bool active;
    bool passed;
};

void setupProfileValidator();
void updateProfileValidator();

// Validate a profile against safety limits.
ValidationResult validateProfile(const MaterialProfile& profile);
ValidationResult validateProfileByIndex(uint8_t index);

// Get current safety limits.
SafetyLimits getSafetyLimits();

// Override safety limits (for testing).
void setSafetyLimits(const SafetyLimits& limits);
void resetSafetyLimits();

// Profile test sequence.
bool startTestSequence(uint8_t profileIndex);
void abortTestSequence();
TestSequenceState getTestSequenceState();
bool isTestRunning();

// Serialize validation result.
void serializeValidationResult(const ValidationResult& result);

#endif  // PROFILE_VALIDATOR_H
