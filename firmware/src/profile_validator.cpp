#include "profile_validator.h"
#include "config.h"
namespace {
struct ValidatorState {
    SafetyLimits limits;
    TestSequenceState testSeq;
};
ValidatorState vs;
SafetyLimits defaultLimits() {
    SafetyLimits lim = {};
    lim.minTempC = 150;
    lim.maxTempC = 280;
    lim.minHoldTimeMs = 500;
    lim.maxHoldTimeMs = 15000;
    lim.minCompressionMm = 0.5f;
    lim.maxCompressionMm = 5.0f;
    lim.minCoolTimeMs = 1000;
    lim.maxCoolTimeMs = 30000;
    lim.minPullForceN = 1.0f;
    lim.maxPullForceN = 20.0f;
    return lim;
}
void addError(ValidationResult& r, ValidationCode code,
              ValidationSeverity sev, float actual, float limit) {
    if (r.errorCount >= kMaxValidationErrors) return;
    ValidationError& e = r.errors[r.errorCount];
    e.code = code;
    e.severity = sev;
    e.actual = actual;
    e.limit = limit;
    r.errorCount++;
    if (sev >= ValidationSeverity::ERROR) r.passed = false;
}
void advanceTestPhase() {
    TestSequenceState& ts = vs.testSeq;
    switch (ts.phase) {
    case TestPhase::HEATING:
        ts.phase = TestPhase::HOLDING;
        ts.phaseStartMs = millis();
        Serial.println(F("TEST_PHASE HOLDING"));
        break;
    case TestPhase::HOLDING:
        ts.phase = TestPhase::COMPRESSING;
        ts.phaseStartMs = millis();
        Serial.println(F("TEST_PHASE COMPRESSING"));
        break;
    case TestPhase::COMPRESSING:
        ts.phase = TestPhase::COOLING;
        ts.phaseStartMs = millis();
        Serial.println(F("TEST_PHASE COOLING"));
        break;
    case TestPhase::COOLING:
        ts.phase = TestPhase::PULL_TEST;
        ts.phaseStartMs = millis();
        Serial.println(F("TEST_PHASE PULL_TEST"));
        break;
    case TestPhase::PULL_TEST:
        ts.phase = TestPhase::COMPLETE;
        ts.passed = true;
        ts.active = false;
        Serial.println(F("TEST_COMPLETE PASSED"));
        break;
    default:
        break;
    }
}
}  // namespace
void setupProfileValidator() {
    vs = {};
    vs.limits = defaultLimits();
    Serial.println(F("PROFVAL_INIT"));
}
void updateProfileValidator() {
    if (!vs.testSeq.active) return;
    // Simulate phase progression based on elapsed time.
    uint32_t elapsed = millis() - vs.testSeq.phaseStartMs;
    // Each phase simulates 500ms of activity.
    if (elapsed >= 500) {
        advanceTestPhase();
    }
}
ValidationResult validateProfile(const MaterialProfile& profile) {
    ValidationResult r = {};
    r.passed = true;
    const SafetyLimits& lim = vs.limits;
    // Temperature checks.
    if (profile.spliceTemp < lim.minTempC) {
        addError(r, ValidationCode::TEMP_TOO_LOW,
                 ValidationSeverity::ERROR,
                 static_cast<float>(profile.spliceTemp),
                 static_cast<float>(lim.minTempC));
    }
    if (profile.spliceTemp > lim.maxTempC) {
        addError(r, ValidationCode::TEMP_TOO_HIGH,
                 ValidationSeverity::CRITICAL,
                 static_cast<float>(profile.spliceTemp),
                 static_cast<float>(lim.maxTempC));
    }
    // Hold time checks.
    if (profile.holdTimeMs < lim.minHoldTimeMs) {
        addError(r, ValidationCode::HOLD_TIME_TOO_SHORT,
                 ValidationSeverity::WARNING,
                 static_cast<float>(profile.holdTimeMs),
                 static_cast<float>(lim.minHoldTimeMs));
    }
    if (profile.holdTimeMs > lim.maxHoldTimeMs) {
        addError(r, ValidationCode::HOLD_TIME_TOO_LONG,
                 ValidationSeverity::ERROR,
                 static_cast<float>(profile.holdTimeMs),
                 static_cast<float>(lim.maxHoldTimeMs));
    }
    // Compression checks.
    if (profile.compressionMm < lim.minCompressionMm) {
        addError(r, ValidationCode::COMPRESSION_OUT_OF_RANGE,
                 ValidationSeverity::WARNING,
                 profile.compressionMm, lim.minCompressionMm);
    }
    if (profile.compressionMm > lim.maxCompressionMm) {
        addError(r, ValidationCode::COMPRESSION_OUT_OF_RANGE,
                 ValidationSeverity::ERROR,
                 profile.compressionMm, lim.maxCompressionMm);
    }
    // Cooling time checks.
    if (profile.coolTimeMs < lim.minCoolTimeMs) {
        addError(r, ValidationCode::COOL_TIME_TOO_SHORT,
                 ValidationSeverity::WARNING,
                 static_cast<float>(profile.coolTimeMs),
                 static_cast<float>(lim.minCoolTimeMs));
    }
    if (profile.coolTimeMs > lim.maxCoolTimeMs) {
        addError(r, ValidationCode::COOL_TIME_TOO_LONG,
                 ValidationSeverity::ERROR,
                 static_cast<float>(profile.coolTimeMs),
                 static_cast<float>(lim.maxCoolTimeMs));
    }
    // Pull force checks.
    if (profile.pullTestForceN < lim.minPullForceN) {
        addError(r, ValidationCode::PULL_FORCE_TOO_LOW,
                 ValidationSeverity::WARNING,
                 profile.pullTestForceN, lim.minPullForceN);
    }
    if (profile.pullTestForceN > lim.maxPullForceN) {
        addError(r, ValidationCode::PULL_FORCE_TOO_HIGH,
                 ValidationSeverity::ERROR,
                 profile.pullTestForceN, lim.maxPullForceN);
    }
    // Name/brand checks.
    if (profile.name[0] == '\0') {
        addError(r, ValidationCode::NAME_EMPTY,
                 ValidationSeverity::ERROR, 0.0f, 0.0f);
    }
    if (profile.brand[0] == '\0') {
        addError(r, ValidationCode::BRAND_EMPTY,
                 ValidationSeverity::WARNING, 0.0f, 0.0f);
    }
    return r;
}
ValidationResult validateProfileByIndex(uint8_t index) {
    MaterialProfile p = getMaterialProfile(index);
    return validateProfile(p);
}
SafetyLimits getSafetyLimits() { return vs.limits; }
void setSafetyLimits(const SafetyLimits& limits) {
    vs.limits = limits;
    Serial.println(F("PROFVAL_LIMITS_SET"));
}
void resetSafetyLimits() {
    vs.limits = defaultLimits();
    Serial.println(F("PROFVAL_LIMITS_RESET"));
}
bool startTestSequence(uint8_t profileIndex) {
    if (vs.testSeq.active) return false;
    // Validate first.
    MaterialProfile p = getMaterialProfile(profileIndex);
    ValidationResult vr = validateProfile(p);
    if (!vr.passed) {
        Serial.println(F("TEST_REJECTED VALIDATION_FAILED"));
        return false;
    }
    vs.testSeq = {};
    vs.testSeq.profileIndex = profileIndex;
    vs.testSeq.phase = TestPhase::HEATING;
    vs.testSeq.phaseStartMs = millis();
    vs.testSeq.active = true;
    Serial.print(F("TEST_START idx="));
    Serial.println(profileIndex);
    Serial.println(F("TEST_PHASE HEATING"));
    return true;
}
void abortTestSequence() {
    if (!vs.testSeq.active) return;
    vs.testSeq.phase = TestPhase::FAILED;
    vs.testSeq.active = false;
    vs.testSeq.passed = false;
    Serial.println(F("TEST_ABORTED"));
}
TestSequenceState getTestSequenceState() { return vs.testSeq; }
bool isTestRunning() { return vs.testSeq.active; }
void serializeValidationResult(const ValidationResult& result) {
    Serial.print(F("PROFVAL_RESULT passed="));
    Serial.print(result.passed ? F("YES") : F("NO"));
    Serial.print(F(" errors="));
    Serial.println(result.errorCount);
    for (uint8_t i = 0; i < result.errorCount; i++) {
        const ValidationError& e = result.errors[i];
        Serial.print(F("  PROFVAL_ERR code="));
        Serial.print(static_cast<uint8_t>(e.code));
        Serial.print(F(" sev="));
        Serial.print(static_cast<uint8_t>(e.severity));
        Serial.print(F(" actual="));
        Serial.print(e.actual, 1);
        Serial.print(F(" limit="));
        Serial.println(e.limit, 1);
    }
}
