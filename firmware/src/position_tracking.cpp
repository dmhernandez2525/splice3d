#include "position_tracking.h"
#include "config.h"
#include "encoder_system.h"
#include "stepper_control.h"
namespace {
constexpr uint32_t kDefaultTrackingIntervalMs = 200UL;
constexpr float kDefaultMinorDriftMm = 0.5f;
constexpr float kDefaultModerateDriftMm = 1.5f;
constexpr float kDefaultSevereDriftMm = 3.0f;
struct TrackingConfig {
    float minorDriftMm;
    float moderateDriftMm;
    float severeDriftMm;
    uint32_t intervalMs;
};
struct TrackingState {
    PositionJobStats job;
    Waypoint waypoints[kMaxWaypoints];
    DriftEvent driftEvents[kMaxDriftEvents];
    TrackingConfig cfg;
    float lastEncoderMm;
    float lastDriftMm;
    float cumulativeDrift;
    uint32_t lastUpdateMs;
    uint16_t correctionCount;
};
TrackingState st;
float computeDrift() {
    const EncoderTelemetry enc = getEncoderTelemetry();
    const MotorPosition mA = getMotorPosition(MotorAxis::FEED_A);
    const MotorPosition mB = getMotorPosition(MotorAxis::FEED_B);
    const float activeMotorMm = (fabsf(mA.absoluteMm) > fabsf(mB.absoluteMm))
        ? mA.absoluteMm : mB.absoluteMm;
    return enc.positionMm - activeMotorMm;
}
DriftSeverity classifyDrift(float absDrift) {
    if (absDrift >= st.cfg.severeDriftMm) return DriftSeverity::SEVERE;
    if (absDrift >= st.cfg.moderateDriftMm) return DriftSeverity::MODERATE;
    return DriftSeverity::MINOR;
}
void recordDriftEvent(float expected, float actual, float error) {
    if (st.job.driftEventCount >= kMaxDriftEvents) return;
    DriftEvent& ev = st.driftEvents[st.job.driftEventCount];
    ev.timestampMs = millis() - st.job.startTimeMs;
    ev.expectedMm = expected;
    ev.actualMm = actual;
    ev.errorMm = error;
    ev.severity = classifyDrift(fabsf(error));
    st.job.driftEventCount++;
    if (ev.severity == DriftSeverity::SEVERE) {
        Serial.print(F("POS_DRIFT SEVERE err="));
        Serial.println(error, 2);
    }
}
}  // namespace
void setupPositionTracking() {
    st = {};
    st.cfg.minorDriftMm = kDefaultMinorDriftMm;
    st.cfg.moderateDriftMm = kDefaultModerateDriftMm;
    st.cfg.severeDriftMm = kDefaultSevereDriftMm;
    st.cfg.intervalMs = kDefaultTrackingIntervalMs;
}
void updatePositionTracking() {
    if (!st.job.active) return;
    const uint32_t now = millis();
    if (now - st.lastUpdateMs < st.cfg.intervalMs) return;
    st.lastUpdateMs = now;
    const EncoderTelemetry enc = getEncoderTelemetry();
    const float drift = computeDrift();
    const float absDrift = fabsf(drift);
    // Update cumulative drift (absolute changes).
    const float driftDelta = fabsf(drift - st.lastDriftMm);
    st.cumulativeDrift += driftDelta;
    st.lastDriftMm = drift;
    // Track peak velocity.
    if (enc.velocityMmPerSec > st.job.peakVelocityMmPerSec) {
        st.job.peakVelocityMmPerSec = enc.velocityMmPerSec;
    }
    // Track max instantaneous drift.
    if (absDrift > st.job.maxDriftMm) {
        st.job.maxDriftMm = absDrift;
    }
    // Update total distance traveled.
    const float moved = fabsf(enc.positionMm - st.lastEncoderMm);
    st.job.totalDistanceMm += moved;
    st.lastEncoderMm = enc.positionMm;
    // Update cumulative drift stat.
    st.job.cumulativeDriftMm = st.cumulativeDrift;
    // Track corrections from encoder system.
    const EncoderHealth health = getEncoderHealth();
    if (health.correctionEvents > st.correctionCount) {
        st.job.correctionCount += (health.correctionEvents - st.correctionCount);
        st.correctionCount = health.correctionEvents;
    }
    // Record drift events when threshold exceeded.
    if (absDrift >= st.cfg.minorDriftMm) {
        const MotorPosition mA = getMotorPosition(MotorAxis::FEED_A);
        recordDriftEvent(mA.absoluteMm, enc.positionMm, drift);
    }
}
void startPositionJob() {
    if (st.job.active) return;
    const EncoderTelemetry enc = getEncoderTelemetry();
    const EncoderHealth health = getEncoderHealth();
    st.job = {};
    st.job.active = true;
    st.job.startTimeMs = millis();
    st.job.startPositionMm = enc.positionMm;
    st.lastEncoderMm = enc.positionMm;
    st.lastDriftMm = 0.0f;
    st.cumulativeDrift = 0.0f;
    st.correctionCount = health.correctionEvents;
    st.lastUpdateMs = millis();
    Serial.println(F("POS_JOB START"));
}
void stopPositionJob() {
    if (!st.job.active) return;
    st.job.active = false;
    Serial.print(F("POS_JOB STOP dist="));
    Serial.print(st.job.totalDistanceMm, 1);
    Serial.print(F(" maxDrift="));
    Serial.print(st.job.maxDriftMm, 2);
    Serial.print(F(" driftEvents="));
    Serial.println(st.job.driftEventCount);
}
bool isPositionJobActive() { return st.job.active; }
PositionSnapshot getPositionSnapshot() {
    const EncoderTelemetry enc = getEncoderTelemetry();
    const MotorPosition mA = getMotorPosition(MotorAxis::FEED_A);
    const MotorPosition mB = getMotorPosition(MotorAxis::FEED_B);
    const float drift = computeDrift();
    return {
        enc.positionMm,
        mA.absoluteMm,
        mB.absoluteMm,
        drift,
        st.cumulativeDrift,
        enc.velocityMmPerSec,
        st.job.active ? (millis() - st.job.startTimeMs) : 0,
    };
}
PositionJobStats getPositionJobStats() { return st.job; }
bool addWaypoint() {
    if (st.job.waypointCount >= kMaxWaypoints) return false;
    const EncoderTelemetry enc = getEncoderTelemetry();
    const MotorPosition mA = getMotorPosition(MotorAxis::FEED_A);
    Waypoint& wp = st.waypoints[st.job.waypointCount];
    wp.timestampMs = millis() - st.job.startTimeMs;
    wp.positionMm = enc.positionMm;
    wp.motorPositionMm = mA.absoluteMm;
    wp.driftMm = enc.positionMm - mA.absoluteMm;
    st.job.waypointCount++;
    return true;
}
uint8_t getWaypointCount() { return st.job.waypointCount; }
Waypoint getWaypoint(uint8_t index) {
    if (index >= st.job.waypointCount) return {};
    return st.waypoints[index];
}
void clearWaypoints() {
    st.job.waypointCount = 0;
}
uint8_t getDriftEventCount() { return st.job.driftEventCount; }
DriftEvent getDriftEvent(uint8_t index) {
    if (index >= st.job.driftEventCount) return {};
    return st.driftEvents[index];
}
void clearDriftEvents() {
    st.job.driftEventCount = 0;
}
void setDriftThresholds(float minorMm, float moderateMm, float severeMm) {
    st.cfg.minorDriftMm = minorMm;
    st.cfg.moderateDriftMm = moderateMm;
    st.cfg.severeDriftMm = severeMm;
}
void setTrackingIntervalMs(uint32_t intervalMs) {
    if (intervalMs < 50) intervalMs = 50;
    st.cfg.intervalMs = intervalMs;
}
