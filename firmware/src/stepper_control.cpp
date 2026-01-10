/**
 * Splice3D Stepper Control Implementation
 */

#include "stepper_control.h"
#include "config.h"
#include <AccelStepper.h>
#include <Servo.h>

// Stepper instances
AccelStepper stepperA(AccelStepper::DRIVER, STEPPER_A_STEP_PIN, STEPPER_A_DIR_PIN);
AccelStepper stepperB(AccelStepper::DRIVER, STEPPER_B_STEP_PIN, STEPPER_B_DIR_PIN);
AccelStepper stepperWinder(AccelStepper::DRIVER, STEPPER_WINDER_STEP_PIN, STEPPER_WINDER_DIR_PIN);

// Cutter servo (if using servo-based cutter)
#if CUTTER_IS_SERVO
Servo cutterServo;
#else
AccelStepper stepperCutter(AccelStepper::DRIVER, STEPPER_CUTTER_STEP_PIN, STEPPER_CUTTER_DIR_PIN);
#endif

void setupSteppers() {
    // Enable pins
    pinMode(STEPPER_A_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_B_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_WINDER_ENABLE_PIN, OUTPUT);
    
    // Enable steppers (active LOW on most boards)
    digitalWrite(STEPPER_A_ENABLE_PIN, LOW);
    digitalWrite(STEPPER_B_ENABLE_PIN, LOW);
    digitalWrite(STEPPER_WINDER_ENABLE_PIN, LOW);
    
    // Configure stepper A
    stepperA.setMaxSpeed(MAX_SPEED_EXTRUDER);
    stepperA.setAcceleration(ACCELERATION);
    
    // Configure stepper B
    stepperB.setMaxSpeed(MAX_SPEED_EXTRUDER);
    stepperB.setAcceleration(ACCELERATION);
    
    // Configure winder
    stepperWinder.setMaxSpeed(MAX_SPEED_WINDER);
    stepperWinder.setAcceleration(ACCELERATION);
    
    // Configure cutter
    #if CUTTER_IS_SERVO
    cutterServo.attach(CUTTER_SERVO_PIN);
    cutterServo.write(0);  // Home position
    #else
    pinMode(STEPPER_CUTTER_ENABLE_PIN, OUTPUT);
    digitalWrite(STEPPER_CUTTER_ENABLE_PIN, LOW);
    stepperCutter.setMaxSpeed(MAX_SPEED_EXTRUDER);
    stepperCutter.setAcceleration(ACCELERATION);
    #endif
    
    DEBUG_PRINTLN(F("Steppers initialized"));
}

void runSteppers() {
    stepperA.run();
    stepperB.run();
    stepperWinder.run();
    
    #if !CUTTER_IS_SERVO
    stepperCutter.run();
    #endif
}

void feedFilament(uint8_t input, float lengthMm) {
    long steps;
    
    if (input == 0) {
        steps = (long)(lengthMm * STEPS_PER_MM_EXTRUDER_A);
        stepperA.move(steps);
        DEBUG_PRINT(F("Feed A: "));
    } else {
        steps = (long)(lengthMm * STEPS_PER_MM_EXTRUDER_B);
        stepperB.move(steps);
        DEBUG_PRINT(F("Feed B: "));
    }
    
    DEBUG_PRINT(steps);
    DEBUG_PRINTLN(F(" steps"));
}

bool isStepperIdle(uint8_t input) {
    if (input == 0) {
        return stepperA.distanceToGo() == 0;
    } else {
        return stepperB.distanceToGo() == 0;
    }
}

void windOutput(float lengthMm) {
    long steps = (long)(lengthMm * STEPS_PER_MM_WINDER);
    stepperWinder.move(steps);
    
    DEBUG_PRINT(F("Wind: "));
    DEBUG_PRINT(steps);
    DEBUG_PRINTLN(F(" steps"));
}

bool isWinderIdle() {
    return stepperWinder.distanceToGo() == 0;
}

void stopAllSteppers() {
    stepperA.stop();
    stepperB.stop();
    stepperWinder.stop();
    
    #if !CUTTER_IS_SERVO
    stepperCutter.stop();
    #endif
    
    // Set current position as target to prevent drift
    stepperA.setCurrentPosition(stepperA.currentPosition());
    stepperB.setCurrentPosition(stepperB.currentPosition());
    stepperWinder.setCurrentPosition(stepperWinder.currentPosition());
    
    DEBUG_PRINTLN(F("All steppers stopped"));
}

void positionForWeld() {
    // Small retract then advance to align filament ends
    // This depends on your mechanical setup
    
    // Example: retract 5mm, pause, advance 7mm to push into weld zone
    // Actual values need calibration
    
    // For now, just a small advance to push into heat zone
    stepperA.move((long)(2.0 * STEPS_PER_MM_EXTRUDER_A));
    stepperB.move((long)(2.0 * STEPS_PER_MM_EXTRUDER_B));
}

void compressWeld(float distanceMm) {
    // Push both filaments together
    long stepsA = (long)(distanceMm * STEPS_PER_MM_EXTRUDER_A);
    long stepsB = (long)(distanceMm * STEPS_PER_MM_EXTRUDER_B);
    
    stepperA.move(stepsA);
    stepperB.move(-stepsB);  // Opposite direction to compress
}

void activateCutter() {
    #if CUTTER_IS_SERVO
    cutterServo.write(90);  // Cut position
    #else
    // Move stepper to cut position
    stepperCutter.move(200);  // Adjust for your mechanism
    #endif
    
    DEBUG_PRINTLN(F("Cutter activated"));
}

void deactivateCutter() {
    #if CUTTER_IS_SERVO
    cutterServo.write(0);  // Home position
    #else
    stepperCutter.move(-200);  // Return
    #endif
    
    DEBUG_PRINTLN(F("Cutter deactivated"));
}
