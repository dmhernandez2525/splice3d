#include "splice_execution.h"
#include "config.h"
#include "stepper_control.h"
#include "temperature.h"
#include "cutting_system.h"
#include "filament_feed.h"
#include "encoder_system.h"
namespace {
constexpr SpliceProfile kProfiles[] = {
    {210.0f, 2.0f, 2000, 5000, 50.0f, 1.0f, 20.0f},   // PLA
    {235.0f, 2.5f, 3000, 6000, 60.0f, 1.0f, 18.0f},   // PETG
    {250.0f, 3.0f, 4000, 8000, 70.0f, 1.0f, 15.0f},   // ABS
};
constexpr uint8_t kProfileCount = sizeof(kProfiles) / sizeof(kProfiles[0]);
struct SpliceState {
    SplicePhase phase;
    SpliceProfile profile;
    SpliceStatistics stats;
    uint32_t phaseStartMs;
    uint32_t spliceStartMs;
    float qualityScore;
    bool passed;
    bool active;
    bool complete;
    uint8_t materialIndex;
};
SpliceState st = {
    SplicePhase::IDLE,
    kProfiles[0],
    {0, 0, 0, 0.0f, 0.0f},
    0, 0, 0.0f,
    false, false, false, 0,
};
void enterPhase(SplicePhase phase) {
    st.phase = phase;
    st.phaseStartMs = millis();
}
void finishSplice(bool success, float quality) {
    st.passed = success;
    st.qualityScore = quality;
    st.active = false;
    st.complete = true;
    st.stats.totalAttempts++;
    if (success) {
        st.stats.successes++;
    } else {
        st.stats.failures++;
    }
    const float elapsed = static_cast<float>(millis() - st.spliceStartMs);
    const float total = static_cast<float>(st.stats.totalAttempts);
    st.stats.averageSpliceTimeMs =
        ((total - 1.0f) * st.stats.averageSpliceTimeMs + elapsed) / total;
    st.stats.averageQualityScore =
        ((total - 1.0f) * st.stats.averageQualityScore + quality) / total;
    enterPhase(success ? SplicePhase::COMPLETE : SplicePhase::FAILED);
    setHeaterPower(0);
    setCoolingFan(false);
    Serial.print(success ? F("SPLICE_OK") : F("SPLICE_FAIL"));
    Serial.print(F(" time="));
    Serial.print(static_cast<uint32_t>(elapsed));
    Serial.print(F(" quality="));
    Serial.println(quality, 2);
}
uint32_t estimateRemainingMs() {
    const uint32_t elapsed = millis() - st.phaseStartMs;
    switch (st.phase) {
        case SplicePhase::HEATING: {
            const float eta = predictTimeToTargetSeconds();
            return static_cast<uint32_t>(eta * 1000.0f) + st.profile.holdTimeMs + st.profile.coolTimeMs;
        }
        case SplicePhase::HOLDING:
            return (elapsed < st.profile.holdTimeMs ? st.profile.holdTimeMs - elapsed : 0) + st.profile.coolTimeMs;
        case SplicePhase::COOLING:
            return elapsed < st.profile.coolTimeMs ? st.profile.coolTimeMs - elapsed : 0;
        default:
            return 0;
    }
}
}  // namespace
void setupSpliceExecution() {}
void updateSpliceExecution() {
    if (!st.active) return;
    const uint32_t elapsed = millis() - st.phaseStartMs;
    switch (st.phase) {
        case SplicePhase::RETRACT_A:
            if (isMotorIdle(MotorAxis::FEED_A)) {
                moveRelative(MotorAxis::FEED_B, st.profile.compressionMm + 2.0f);
                enterPhase(SplicePhase::ADVANCE_B);
            }
            if (elapsed > 5000UL) { finishSplice(false, 0.0f); }
            break;
        case SplicePhase::ADVANCE_B:
            if (isMotorIdle(MotorAxis::FEED_B)) {
                setTargetTemperature(st.profile.temperatureC);
                enterPhase(SplicePhase::HEATING);
            }
            if (elapsed > 5000UL) { finishSplice(false, 0.0f); }
            break;
        case SplicePhase::HEATING:
            if (isTemperatureReached()) {
                startSynchronizedMove(st.profile.compressionMm, -st.profile.compressionMm, 0.0f);
                enterPhase(SplicePhase::COMPRESSING);
            }
            if (elapsed > HEATER_TIMEOUT_MS) { finishSplice(false, 0.0f); }
            break;
        case SplicePhase::COMPRESSING:
            if (!isSynchronizedMoveActive()) {
                enterPhase(SplicePhase::HOLDING);
            }
            if (elapsed > 3000UL) { enterPhase(SplicePhase::HOLDING); }
            break;
        case SplicePhase::HOLDING:
            if (elapsed >= st.profile.holdTimeMs) {
                setHeaterPower(0);
                setCoolingFan(true);
                enterPhase(SplicePhase::COOLING);
            }
            break;
        case SplicePhase::COOLING: {
            const float current = getCurrentTemperature();
            const bool tempOk = current <= st.profile.coolTargetC;
            const bool timeOk = elapsed >= st.profile.coolTimeMs;
            if (tempOk || timeOk) {
                setCoolingFan(false);
                if (st.profile.pullTestMm > 0.0f) {
                    moveRelative(MotorAxis::FEED_A, -st.profile.pullTestMm);
                    enterPhase(SplicePhase::VERIFYING);
                } else {
                    finishSplice(true, 1.0f);
                }
            }
            break;
        }
        case SplicePhase::VERIFYING:
            if (isMotorIdle(MotorAxis::FEED_A)) {
                const EncoderTelemetry enc = getEncoderTelemetry();
                const float slipMm = fabsf(enc.slipErrorMm);
                const float quality = slipMm < 0.5f ? 1.0f : (slipMm < 1.0f ? 0.8f : 0.5f);
                const bool success = quality >= 0.5f;
                finishSplice(success, quality);
            }
            if (elapsed > 3000UL) { finishSplice(false, 0.0f); }
            break;
        case SplicePhase::IDLE:
        case SplicePhase::COMPLETE:
        case SplicePhase::FAILED:
            break;
    }
}
bool startSplice(uint8_t materialIndex) {
    if (st.active) return false;
    if (materialIndex >= kProfileCount) materialIndex = 0;
    st.materialIndex = materialIndex;
    st.profile = kProfiles[materialIndex];
    st.active = true;
    st.complete = false;
    st.qualityScore = 0.0f;
    st.passed = false;
    st.spliceStartMs = millis();
    moveRelative(MotorAxis::FEED_A, -2.0f);
    enterPhase(SplicePhase::RETRACT_A);
    return true;
}
void abortSplice() {
    if (!st.active) return;
    emergencyStopAll();
    setHeaterPower(0);
    setCoolingFan(true);
    finishSplice(false, 0.0f);
}
bool isSpliceActive() { return st.active; }
bool isSpliceComplete() { return st.complete; }
SplicePhase getSplicePhase() { return st.phase; }
SpliceTelemetry getSpliceTelemetry() {
    return {
        st.phase, getCurrentTemperature(),
        st.profile.compressionMm,
        millis() - st.spliceStartMs,
        estimateRemainingMs(),
        st.qualityScore, st.passed,
    };
}
SpliceStatistics getSpliceStatistics() { return st.stats; }
void resetSpliceStatistics() { st.stats = {0, 0, 0, 0.0f, 0.0f}; }
