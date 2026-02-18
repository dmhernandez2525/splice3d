/**
 * Splice3D Position Tracking (F3.3).
 *
 * Provides job-level filament position tracking, drift event logging,
 * waypoint management, and motor-vs-encoder position reconciliation.
 */

#ifndef POSITION_TRACKING_H
#define POSITION_TRACKING_H

#include <Arduino.h>

constexpr uint8_t kMaxWaypoints = 32;
constexpr uint8_t kMaxDriftEvents = 16;

enum class DriftSeverity : uint8_t {
    MINOR = 0,
    MODERATE,
    SEVERE,
};

struct Waypoint {
    uint32_t timestampMs;
    float positionMm;
    float motorPositionMm;
    float driftMm;
};

struct DriftEvent {
    uint32_t timestampMs;
    float expectedMm;
    float actualMm;
    float errorMm;
    DriftSeverity severity;
};

struct PositionSnapshot {
    float encoderMm;
    float motorAMm;
    float motorBMm;
    float driftMm;
    float cumulativeDriftMm;
    float velocityMmPerSec;
    uint32_t elapsedMs;
};

struct PositionJobStats {
    uint32_t startTimeMs;
    float startPositionMm;
    float totalDistanceMm;
    float peakVelocityMmPerSec;
    float maxDriftMm;
    float cumulativeDriftMm;
    uint16_t driftEventCount;
    uint16_t waypointCount;
    uint16_t correctionCount;
    bool active;
};

void setupPositionTracking();
void updatePositionTracking();

// Job management.
void startPositionJob();
void stopPositionJob();
bool isPositionJobActive();

// Snapshot and statistics.
PositionSnapshot getPositionSnapshot();
PositionJobStats getPositionJobStats();

// Waypoints.
bool addWaypoint();
uint8_t getWaypointCount();
Waypoint getWaypoint(uint8_t index);
void clearWaypoints();

// Drift events.
uint8_t getDriftEventCount();
DriftEvent getDriftEvent(uint8_t index);
void clearDriftEvents();

// Configuration.
void setDriftThresholds(float minorMm, float moderateMm, float severeMm);
void setTrackingIntervalMs(uint32_t intervalMs);

#endif  // POSITION_TRACKING_H
