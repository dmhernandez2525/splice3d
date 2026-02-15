#include "filament_feed.h"
#include "config.h"
#include "stepper_control.h"
#include "encoder_system.h"
#include "temperature.h"
namespace {
struct FeedState {
    FeedMode mode;
    FeedConfig config;
    FeedStatistics stats;
    uint8_t activeInput;
    float targetLengthMm;
    float fedSoFarMm;
    float startEncoderMm;
    uint32_t feedStartMs;
    uint32_t lastJamCheckMs;
    float lastJamCheckPosMm;
    bool jamDetected;
    bool runoutA;
    bool runoutB;
    bool complete;
};
FeedState st = {
    FeedMode::IDLE,
    {20.0f, 5.0f, 15.0f, 0.5f, 2.0f, 30.0f, 500},
    {0.0f, 0.0f, 0.0f, 0, 0, 0},
    0, 0.0f, 0.0f, 0.0f,
    0, 0, 0.0f,
    false, false, false, false,
};
MotorAxis inputAxis(uint8_t input) {
    return input == 0 ? MotorAxis::FEED_A : MotorAxis::FEED_B;
}
void checkRunout() {
    st.runoutA = digitalRead(FILAMENT_SENSOR_A_PIN) == LOW;
    st.runoutB = digitalRead(FILAMENT_SENSOR_B_PIN) == LOW;
    if (st.mode == FeedMode::FEED_A && st.runoutA) {
        st.stats.runoutEvents++;
        abortFeed();
        Serial.println(F("FEED_RUNOUT A"));
    }
    if (st.mode == FeedMode::FEED_B && st.runoutB) {
        st.stats.runoutEvents++;
        abortFeed();
        Serial.println(F("FEED_RUNOUT B"));
    }
}
void checkJam(uint32_t nowMs) {
    if (st.mode == FeedMode::IDLE || st.mode == FeedMode::DRY_RUN) return;
    if (nowMs - st.lastJamCheckMs < st.config.jamDetectionWindowMs) return;
    st.lastJamCheckMs = nowMs;
    const EncoderTelemetry enc = getEncoderTelemetry();
    const float posDelta = fabsf(enc.positionMm - st.lastJamCheckPosMm);
    st.lastJamCheckPosMm = enc.positionMm;
    const float elapsed = static_cast<float>(st.config.jamDetectionWindowMs) / 1000.0f;
    const float velocity = posDelta / elapsed;
    if (velocity < st.config.jamThresholdMmS && st.fedSoFarMm > 1.0f) {
        st.jamDetected = true;
        st.stats.jamCount++;
        abortFeed();
        Serial.println(F("FEED_JAM"));
    }
}
void updateFeedProgress() {
    const EncoderTelemetry enc = getEncoderTelemetry();
    st.fedSoFarMm = fabsf(enc.positionMm - st.startEncoderMm);
    const MotorAxis axis = inputAxis(st.activeInput);
    if (isMotorIdle(axis)) {
        st.complete = true;
        st.mode = FeedMode::IDLE;
        if (st.activeInput == 0) {
            st.stats.totalFedMmA += st.fedSoFarMm;
        } else {
            st.stats.totalFedMmB += st.fedSoFarMm;
        }
        const float elapsed = static_cast<float>(millis() - st.feedStartMs) / 1000.0f;
        if (elapsed > 0.0f) {
            st.stats.averageFeedRate = st.fedSoFarMm / elapsed;
        }
        Serial.print(F("FEED_DONE fed="));
        Serial.print(st.fedSoFarMm, 2);
        Serial.println(F(" mm"));
    }
}
}  // namespace
void setupFilamentFeed() {
    pinMode(FILAMENT_SENSOR_A_PIN, INPUT_PULLUP);
    pinMode(FILAMENT_SENSOR_B_PIN, INPUT_PULLUP);
}
void updateFilamentFeed() {
    if (st.mode == FeedMode::IDLE) return;
    const uint32_t nowMs = millis();
    checkRunout();
    if (st.mode != FeedMode::DRY_RUN) {
        checkJam(nowMs);
    }
    updateFeedProgress();
}
bool startFeed(uint8_t input, float lengthMm) {
    if (st.mode != FeedMode::IDLE) return false;
    if (lengthMm <= 0.0f) return false;
    if (isColdExtrusionBlocked()) {
        Serial.println(F("ERROR COLD_EXTRUSION_BLOCK"));
        return false;
    }
    st.activeInput = input;
    st.targetLengthMm = lengthMm;
    st.fedSoFarMm = 0.0f;
    st.startEncoderMm = getEncoderTelemetry().positionMm;
    st.feedStartMs = millis();
    st.lastJamCheckMs = millis();
    st.lastJamCheckPosMm = st.startEncoderMm;
    st.jamDetected = false;
    st.complete = false;
    st.mode = input == 0 ? FeedMode::FEED_A : FeedMode::FEED_B;
    moveRelative(inputAxis(input), lengthMm);
    return true;
}
bool startRetract(uint8_t input, float lengthMm) {
    if (st.mode != FeedMode::IDLE) return false;
    if (lengthMm <= 0.0f) return false;
    st.activeInput = input;
    st.targetLengthMm = lengthMm;
    st.fedSoFarMm = 0.0f;
    st.startEncoderMm = getEncoderTelemetry().positionMm;
    st.feedStartMs = millis();
    st.lastJamCheckMs = millis();
    st.lastJamCheckPosMm = st.startEncoderMm;
    st.jamDetected = false;
    st.complete = false;
    st.mode = input == 0 ? FeedMode::RETRACT_A : FeedMode::RETRACT_B;
    moveRelative(inputAxis(input), -lengthMm);
    return true;
}
bool startDryRunFeed(uint8_t input, float lengthMm) {
    if (st.mode != FeedMode::IDLE) return false;
    if (lengthMm <= 0.0f) return false;
    st.activeInput = input;
    st.targetLengthMm = lengthMm;
    st.fedSoFarMm = 0.0f;
    st.startEncoderMm = getEncoderTelemetry().positionMm;
    st.feedStartMs = millis();
    st.lastJamCheckMs = millis();
    st.lastJamCheckPosMm = st.startEncoderMm;
    st.jamDetected = false;
    st.complete = false;
    st.mode = FeedMode::DRY_RUN;
    moveRelative(inputAxis(input), lengthMm);
    return true;
}
void abortFeed() {
    emergencyStopAll();
    st.mode = FeedMode::IDLE;
    st.complete = false;
}
bool isFeedActive() { return st.mode != FeedMode::IDLE; }
bool isFeedComplete() { return st.complete; }
FeedMode getFeedMode() { return st.mode; }
FeedStatistics getFeedStatistics() { return st.stats; }
FeedConfig getFeedConfig() { return st.config; }
bool isFilamentRunout(uint8_t input) { return input == 0 ? st.runoutA : st.runoutB; }
bool isJamDetected() { return st.jamDetected; }
void setFeedSpeeds(float fastMmS, float slowMmS, float retractMmS) {
    st.config.fastSpeedMmS = fastMmS;
    st.config.slowSpeedMmS = slowMmS;
    st.config.retractSpeedMmS = retractMmS;
}
void setJamThreshold(float thresholdMmS) { st.config.jamThresholdMmS = thresholdMmS; }
void resetFeedStatistics() { st.stats = {0.0f, 0.0f, 0.0f, 0, 0, 0}; }
