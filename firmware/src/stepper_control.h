/**
 * Splice3D Stepper Control
 * 
 * Controls extruder motors and output winder using AccelStepper.
 */

#ifndef STEPPER_CONTROL_H
#define STEPPER_CONTROL_H

#include <Arduino.h>

/**
 * Initialize all stepper motors.
 */
void setupSteppers();

/**
 * Run stepper updates (call every loop iteration).
 */
void runSteppers();

/**
 * Feed filament from input A or B.
 * @param input 0 for A, 1 for B
 * @param lengthMm Length in mm to feed
 */
void feedFilament(uint8_t input, float lengthMm);

/**
 * Check if a stepper has completed its move.
 * @param input 0 for A, 1 for B
 * @return true if idle
 */
bool isStepperIdle(uint8_t input);

/**
 * Wind filament onto output spool.
 * @param lengthMm Length to wind
 */
void windOutput(float lengthMm);

/**
 * Check if winder has completed.
 */
bool isWinderIdle();

/**
 * Stop all stepper motors immediately.
 */
void stopAllSteppers();

/**
 * Position filaments for welding.
 */
void positionForWeld();

/**
 * Compress filaments together for weld.
 * @param distanceMm Compression distance
 */
void compressWeld(float distanceMm);

/**
 * Activate the cutter mechanism.
 */
void activateCutter();

/**
 * Deactivate the cutter mechanism.
 */
void deactivateCutter();

#endif // STEPPER_CONTROL_H
