#include "encoder_system.h"
#include "config.h"
#include "stepper_control.h"
#include <EEPROM.h>
#include <math.h>
#include <string.h>
namespace {
constexpr uint8_t kSlipWindowSize = 16;
constexpr uint32_t kCalibrationSignature = 0x53334445UL;
constexpr int kCalibrationAddress = 0;
struct PersistentCalibration {
    uint32_t signature;
    float ticksPerMm;
    uint32_t calibrationRuns;
    uint32_t checksum;
};
struct EncoderIsrState {
    int64_t tickCount;
    uint8_t lastEncodedState;
    uint32_t lastEdgeUs;
    uint32_t lastStepUs;
    uint32_t lastValidEdgeUs;
    float instantaneousTickRate;
    uint32_t validTransitions;
    uint32_t invalidTransitions;
};
struct RuntimeState {
    EncoderTelemetry telemetry;
    EncoderHealth health;
    float ticksPerMm;
    bool closedLoopEnabled;
    bool calibrationActive;
    float calibrationKnownLengthMm;
    int64_t calibrationStartTicks;
    float slipWindow[kSlipWindowSize];
    uint8_t slipWindowIndex;
    uint8_t slipWindowCount;
    uint32_t logIntervalMs;
    uint32_t lastLogMs;
    uint32_t lastCorrectionMs;
};
volatile EncoderIsrState isrState = {0, 0, 0, 0, 0, 0.0f, 0, 0};
RuntimeState state = {
    {0, 0.0f, 0.0f, 0.0f, 0.0f, false},
    {0, 0, 1.0f, false, false, 0, 0},
    ENCODER_DEFAULT_TICKS_PER_MM,
    true,
    false,
    0.0f,
    0,
    {0.0f},
    0,
    0,
    ENCODER_LOG_INTERVAL_MS,
    0,
    0,
};
uint32_t floatBits(float value) {
    union {
        float f;
        uint32_t u;
    } conv = {value};
    return conv.u;
}
uint32_t computeChecksum(const PersistentCalibration& calibration) {
    return calibration.signature ^ floatBits(calibration.ticksPerMm) ^ calibration.calibrationRuns ^ 0xA55AA55AUL;
}
int8_t decodeQuadratureDelta(uint8_t previous, uint8_t current) {
    static const int8_t transitions[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
    return transitions[(previous << 2) | current];
}
float expectedFilamentPositionMm() {
    const float feedA = fabsf(getMotorPosition(MotorAxis::FEED_A).absoluteMm);
    const float feedB = fabsf(getMotorPosition(MotorAxis::FEED_B).absoluteMm);
    const float winder = fabsf(getMotorPosition(MotorAxis::WINDER).absoluteMm);
    return max(feedA, max(feedB, winder));
}
float averageSlipWindow() {
    if (state.slipWindowCount == 0) {
        return 0.0f;
    }
    float total = 0.0f;
    for (uint8_t index = 0; index < state.slipWindowCount; ++index) {
        total += state.slipWindow[index];
    }
    return total / static_cast<float>(state.slipWindowCount);
}
void pushSlipSample(float errorMm) {
    state.slipWindow[state.slipWindowIndex] = fabsf(errorMm);
    state.slipWindowIndex = static_cast<uint8_t>((state.slipWindowIndex + 1) % kSlipWindowSize);
    if (state.slipWindowCount < kSlipWindowSize) {
        state.slipWindowCount++;
    }
}
void applyClosedLoopCorrection(uint32_t nowMs) {
    if (!state.closedLoopEnabled || nowMs - state.lastCorrectionMs < ENCODER_CORRECTION_INTERVAL_MS) {
        return;
    }
    if (fabsf(state.telemetry.slipErrorMm) < ENCODER_CORRECTION_DEADBAND_MM) {
        return;
    }
    MotorAxis axis = MotorAxis::WINDER;
    bool active = false;
    if (!isMotorIdle(MotorAxis::FEED_A)) {
        axis = MotorAxis::FEED_A;
        active = true;
    } else if (!isMotorIdle(MotorAxis::FEED_B)) {
        axis = MotorAxis::FEED_B;
        active = true;
    } else if (!isMotorIdle(MotorAxis::WINDER)) {
        axis = MotorAxis::WINDER;
        active = true;
    }
    if (!active) {
        return;
    }
    float correctionMm = state.telemetry.slipErrorMm * ENCODER_CORRECTION_GAIN;
    correctionMm = constrain(correctionMm, -ENCODER_CORRECTION_MAX_MM, ENCODER_CORRECTION_MAX_MM);
    moveRelative(axis, correctionMm);
    state.lastCorrectionMs = nowMs;
    state.health.correctionEvents++;
}
void updateHealth(uint32_t nowUs, uint32_t lastValidUs) {
    const uint32_t total = state.health.validTransitions + state.health.invalidTransitions;
    if (total == 0) {
        state.health.signalQuality = 1.0f;
        state.health.degraded = false;
    } else {
        state.health.signalQuality = static_cast<float>(state.health.validTransitions) / static_cast<float>(total);
        const float invalidRatio = static_cast<float>(state.health.invalidTransitions) / static_cast<float>(total);
        state.health.degraded = invalidRatio > ENCODER_INVALID_RATIO_WARN;
    }
    const bool motionActive = !isMotorIdle(MotorAxis::FEED_A) || !isMotorIdle(MotorAxis::FEED_B) ||
                              !isMotorIdle(MotorAxis::WINDER);
    state.health.failed = motionActive && (nowUs - lastValidUs) > (ENCODER_HEALTH_STALE_MS * 1000UL);
}
void logTelemetry(uint32_t nowMs) {
    if (state.logIntervalMs == 0 || nowMs - state.lastLogMs < state.logIntervalMs) {
        return;
    }
    state.lastLogMs = nowMs;
    Serial.print(F("ENCODER ticks="));
    Serial.print(state.telemetry.ticks);
    Serial.print(F(" pos_mm="));
    Serial.print(state.telemetry.positionMm, 3);
    Serial.print(F(" vel_mm_s="));
    Serial.print(state.telemetry.velocityMmPerSec, 3);
    Serial.print(F(" slip_mm="));
    Serial.print(state.telemetry.averageSlipErrorMm, 3);
    Serial.print(F(" quality="));
    Serial.print(state.health.signalQuality, 3);
    Serial.print(F(" failed="));
    Serial.println(state.health.failed ? F("1") : F("0"));
}
void handleEncoderEdge() {
    const uint32_t nowUs = micros();
    if (isrState.lastEdgeUs != 0 && (nowUs - isrState.lastEdgeUs) < ENCODER_DEBOUNCE_US) {
        isrState.invalidTransitions++;
        return;
    }
    const uint8_t current = (digitalRead(ENCODER_CHANNEL_A_PIN) ? 0x02 : 0x00) |
                            (digitalRead(ENCODER_CHANNEL_B_PIN) ? 0x01 : 0x00);
    const int8_t delta = decodeQuadratureDelta(isrState.lastEncodedState, current);
    isrState.lastEncodedState = current;
    isrState.lastEdgeUs = nowUs;
    if (delta == 0) {
        isrState.invalidTransitions++;
        return;
    }
    isrState.tickCount += delta;
    isrState.validTransitions++;
    isrState.lastValidEdgeUs = nowUs;
    if (isrState.lastStepUs != 0) {
        const uint32_t deltaUs = nowUs - isrState.lastStepUs;
        if (deltaUs > 0) {
            isrState.instantaneousTickRate = (1000000.0f * static_cast<float>(delta)) / static_cast<float>(deltaUs);
        }
    }
    isrState.lastStepUs = nowUs;
}
void encoderChannelAIsr() { handleEncoderEdge(); }
void encoderChannelBIsr() { handleEncoderEdge(); }
}  // namespace
void setupEncoderSystem() {
    pinMode(ENCODER_CHANNEL_A_PIN, INPUT_PULLUP);
    pinMode(ENCODER_CHANNEL_B_PIN, INPUT_PULLUP);
    noInterrupts();
    isrState.lastEncodedState = (digitalRead(ENCODER_CHANNEL_A_PIN) ? 0x02 : 0x00) |
                                (digitalRead(ENCODER_CHANNEL_B_PIN) ? 0x01 : 0x00);
    isrState.lastValidEdgeUs = micros();
    interrupts();
    loadEncoderCalibration();
    attachInterrupt(digitalPinToInterrupt(ENCODER_CHANNEL_A_PIN), encoderChannelAIsr, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENCODER_CHANNEL_B_PIN), encoderChannelBIsr, CHANGE);
}
void updateEncoderSystem() {
    EncoderIsrState snapshot;
    noInterrupts();
    snapshot.tickCount = isrState.tickCount;
    snapshot.lastEncodedState = isrState.lastEncodedState;
    snapshot.lastEdgeUs = isrState.lastEdgeUs;
    snapshot.lastStepUs = isrState.lastStepUs;
    snapshot.lastValidEdgeUs = isrState.lastValidEdgeUs;
    snapshot.instantaneousTickRate = isrState.instantaneousTickRate;
    snapshot.validTransitions = isrState.validTransitions;
    snapshot.invalidTransitions = isrState.invalidTransitions;
    interrupts();
    state.telemetry.ticks = snapshot.tickCount;
    state.telemetry.positionMm = snapshot.tickCount / state.ticksPerMm;
    const float instantVelocity = snapshot.instantaneousTickRate / state.ticksPerMm;
    state.telemetry.velocityMmPerSec = (0.8f * state.telemetry.velocityMmPerSec) + (0.2f * instantVelocity);
    state.telemetry.slipErrorMm = expectedFilamentPositionMm() - state.telemetry.positionMm;
    pushSlipSample(state.telemetry.slipErrorMm);
    state.telemetry.averageSlipErrorMm = averageSlipWindow();
    state.telemetry.slipDetected = state.telemetry.averageSlipErrorMm > ENCODER_SLIP_THRESHOLD_MM;
    state.health.validTransitions = snapshot.validTransitions;
    state.health.invalidTransitions = snapshot.invalidTransitions;
    updateHealth(micros(), snapshot.lastValidEdgeUs);
    applyClosedLoopCorrection(millis());
    logTelemetry(millis());
}
EncoderTelemetry getEncoderTelemetry() { return state.telemetry; }
EncoderHealth getEncoderHealth() { return state.health; }
bool beginEncoderCalibration(float knownLengthMm) {
    if (knownLengthMm <= 0.0f) {
        return false;
    }
    state.calibrationActive = true;
    state.calibrationKnownLengthMm = knownLengthMm;
    state.calibrationStartTicks = state.telemetry.ticks;
    return true;
}
bool completeEncoderCalibration() {
    if (!state.calibrationActive || state.calibrationKnownLengthMm <= 0.0f) {
        return false;
    }
    const int64_t tickDelta = llabs(state.telemetry.ticks - state.calibrationStartTicks);
    const float measuredTicksPerMm = static_cast<float>(tickDelta) / state.calibrationKnownLengthMm;
    state.calibrationActive = false;
    if (!setEncoderTicksPerMm(measuredTicksPerMm)) {
        return false;
    }
    state.health.calibrationRuns++;
    return saveEncoderCalibration();
}
bool isEncoderCalibrationActive() { return state.calibrationActive; }
bool saveEncoderCalibration() {
    PersistentCalibration calibration = {kCalibrationSignature, state.ticksPerMm, state.health.calibrationRuns, 0};
    calibration.checksum = computeChecksum(calibration);
    EEPROM.put(kCalibrationAddress, calibration);
    return true;
}
bool loadEncoderCalibration() {
    PersistentCalibration calibration = {0, ENCODER_DEFAULT_TICKS_PER_MM, 0, 0};
    EEPROM.get(kCalibrationAddress, calibration);
    if (calibration.signature != kCalibrationSignature || computeChecksum(calibration) != calibration.checksum ||
        !setEncoderTicksPerMm(calibration.ticksPerMm)) {
        state.ticksPerMm = ENCODER_DEFAULT_TICKS_PER_MM;
        return false;
    }
    state.health.calibrationRuns = calibration.calibrationRuns;
    return true;
}
void resetEncoderCounters() {
    noInterrupts();
    isrState.tickCount = 0;
    isrState.validTransitions = 0;
    isrState.invalidTransitions = 0;
    interrupts();
    state.telemetry = {0, 0.0f, 0.0f, 0.0f, 0.0f, false};
    state.slipWindowIndex = 0;
    state.slipWindowCount = 0;
    memset(state.slipWindow, 0, sizeof(state.slipWindow));
}
bool setEncoderTicksPerMm(float ticksPerMm) {
    if (ticksPerMm < ENCODER_MIN_TICKS_PER_MM || ticksPerMm > ENCODER_MAX_TICKS_PER_MM) {
        return false;
    }
    state.ticksPerMm = ticksPerMm;
    return true;
}
float getEncoderTicksPerMm() { return state.ticksPerMm; }
void setEncoderLogIntervalMs(uint32_t intervalMs) { state.logIntervalMs = intervalMs; }
uint32_t getEncoderLogIntervalMs() { return state.logIntervalMs; }
void setEncoderClosedLoopEnabled(bool enabled) { state.closedLoopEnabled = enabled; }
bool isEncoderClosedLoopEnabled() { return state.closedLoopEnabled; }
