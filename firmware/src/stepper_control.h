/**
 * Splice3D advanced motor control.
 *
 * Provides high-level motion, diagnostics, and runtime tuning for
 * feed motors A/B and output winder.
 */

#ifndef STEPPER_CONTROL_H
#define STEPPER_CONTROL_H

#include <Arduino.h>

enum class MotorAxis : uint8_t {
    FEED_A = 0,
    FEED_B = 1,
    WINDER = 2,
    CUTTER = 3,
};

struct MotionProfile {
    float maxSpeedStepsPerSec;
    float accelerationStepsPerSec2;
    float jerkLimitStepsPerSec2;
};

struct MotorPosition {
    int64_t absoluteSteps;
    float absoluteMm;
};

struct MotorDiagnostics {
    bool stallDetected;
    bool overTempWarning;
    bool synchronizedMoveActive;
    int32_t missedStepEstimate;
    int64_t commandedSteps;
    int64_t observedSteps;
};

// Core lifecycle.
void setupSteppers();
void runSteppers();
void emergencyStopAll();

// Runtime motion profile and electrical tuning.
bool configureMotionProfile(MotorAxis axis, const MotionProfile& profile);
void setGlobalMicrostepping(uint16_t microstep);
void setGlobalMotorCurrents(uint16_t runCurrentMa, uint16_t holdCurrentMa);
void setBacklashCompensation(MotorAxis axis, float backlashMm);

// Motion commands.
void moveRelative(MotorAxis axis, float distanceMm);
void moveAbsolute(MotorAxis axis, float absolutePositionMm);
bool startSynchronizedMove(float feedAMm, float feedBMm, float winderMm);
bool isSynchronizedMoveActive();
bool isMotorIdle(MotorAxis axis);

// Sensorless homing.
bool performSensorlessHome(MotorAxis axis, float travelLimitMm, float seekSpeedMmS);

// Position and diagnostics.
MotorPosition getMotorPosition(MotorAxis axis);
MotorDiagnostics getMotorDiagnostics(MotorAxis axis);
void resetMotorPosition(MotorAxis axis);

// Legacy compatibility wrappers used by the state machine.
void feedFilament(uint8_t input, float lengthMm);
bool isStepperIdle(uint8_t input);
void windOutput(float lengthMm);
bool isWinderIdle();
void stopAllSteppers();
void positionForWeld();
void compressWeld(float distanceMm);
void activateCutter();
void deactivateCutter();

#endif  // STEPPER_CONTROL_H
