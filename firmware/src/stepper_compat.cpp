#include "stepper_control.h"
#include "config.h"

void feedFilament(uint8_t input, float lengthMm) {
    moveRelative(input == 0 ? MotorAxis::FEED_A : MotorAxis::FEED_B, lengthMm);
}

bool isStepperIdle(uint8_t input) {
    return isMotorIdle(input == 0 ? MotorAxis::FEED_A : MotorAxis::FEED_B);
}

void windOutput(float lengthMm) { moveRelative(MotorAxis::WINDER, lengthMm); }

bool isWinderIdle() { return isMotorIdle(MotorAxis::WINDER); }

void stopAllSteppers() { emergencyStopAll(); }

void positionForWeld() {
    startSynchronizedMove(WELD_POSITION_ADVANCE_MM, WELD_POSITION_ADVANCE_MM, 0.0f);
}

void compressWeld(float distanceMm) { startSynchronizedMove(distanceMm, -distanceMm, 0.0f); }
