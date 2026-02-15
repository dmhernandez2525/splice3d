#include "stepper_control.h"
#include "config.h"
#include "tmc_config.h"
#include <AccelStepper.h>
#include <Servo.h>
#include <stdlib.h>
namespace {
constexpr uint8_t kAxisCount = 3;
constexpr int32_t kPositionNormalizeThreshold = 100000000;
constexpr uint32_t kSensorlessHomeTimeoutMs = 12000;
constexpr uint8_t kDefaultStallThreshold = 8;
AccelStepper stepperA(AccelStepper::DRIVER, STEPPER_A_STEP_PIN, STEPPER_A_DIR_PIN);
AccelStepper stepperB(AccelStepper::DRIVER, STEPPER_B_STEP_PIN, STEPPER_B_DIR_PIN);
AccelStepper stepperWinder(AccelStepper::DRIVER, STEPPER_WINDER_STEP_PIN, STEPPER_WINDER_DIR_PIN);
#if CUTTER_IS_SERVO
Servo cutterServo;
#else
AccelStepper stepperCutter(AccelStepper::DRIVER, STEPPER_CUTTER_STEP_PIN, STEPPER_CUTTER_DIR_PIN);
#endif
struct MotorControlState {
    MotionProfile profiles[kAxisCount];
    float backlashCompensationMm[kAxisCount];
    int8_t lastDirection[kAxisCount];
    int64_t positionOffsetSteps[kAxisCount];
    int64_t commandedAbsoluteSteps[kAxisCount];
    MotorDiagnostics diagnostics[kAxisCount];
    bool synchronizedMoveActive;
    uint16_t globalMicrostep;
    uint16_t runCurrentMa;
    uint16_t holdCurrentMa;
};
MotorControlState state = {
    {},
    {0.0f, 0.0f, 0.0f},
    {0, 0, 0},
    {0, 0, 0},
    {0, 0, 0},
    {},
    false,
    16,
    MOTOR_CURRENT_MA,
    MOTOR_CURRENT_MA / 2,
};
void setDriversEnabled(bool enabled) {
    const uint8_t pinState = enabled ? LOW : HIGH;
    digitalWrite(STEPPER_A_ENABLE_PIN, pinState);
    digitalWrite(STEPPER_B_ENABLE_PIN, pinState);
    digitalWrite(STEPPER_WINDER_ENABLE_PIN, pinState);
#if !CUTTER_IS_SERVO
    digitalWrite(STEPPER_CUTTER_ENABLE_PIN, pinState);
#endif
}
uint8_t axisIndex(MotorAxis axis) { return axis == MotorAxis::FEED_B ? 1 : (axis == MotorAxis::WINDER ? 2 : 0); }
char axisToTmcLabel(MotorAxis axis) { return axis == MotorAxis::FEED_B ? 'Y' : (axis == MotorAxis::WINDER ? 'Z' : (axis == MotorAxis::CUTTER ? 'E' : 'X')); }
AccelStepper* axisStepper(MotorAxis axis) {
    switch (axis) {
        case MotorAxis::FEED_A: return &stepperA;
        case MotorAxis::FEED_B: return &stepperB;
        case MotorAxis::WINDER: return &stepperWinder;
#if !CUTTER_IS_SERVO
        case MotorAxis::CUTTER: return &stepperCutter;
#else
        case MotorAxis::CUTTER: return nullptr;
#endif
    }
    return nullptr;
}
float microstepScale() { return static_cast<float>(state.globalMicrostep) / 16.0f; }
float stepsPerMm(MotorAxis axis) { const float scale = microstepScale(); return (axis == MotorAxis::FEED_B ? STEPS_PER_MM_EXTRUDER_B : (axis == MotorAxis::WINDER ? STEPS_PER_MM_WINDER : STEPS_PER_MM_EXTRUDER_A)) * scale; }
long mmToSteps(MotorAxis axis, float distanceMm) { return static_cast<long>(distanceMm * stepsPerMm(axis)); }
void applyProfile(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) return;
    AccelStepper* stepper = axisStepper(axis);
    const MotionProfile& profile = state.profiles[axisIndex(axis)];
    stepper->setMaxSpeed(profile.maxSpeedStepsPerSec);
    const float jerkLimitedAccel = profile.jerkLimitStepsPerSec2 > 0.0f
                                       ? min(profile.accelerationStepsPerSec2, profile.jerkLimitStepsPerSec2)
                                       : profile.accelerationStepsPerSec2;
    stepper->setAcceleration(jerkLimitedAccel);
}
void normalizeStepperPositionIfNeeded(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) return;
    AccelStepper* stepper = axisStepper(axis);
    if (stepper->distanceToGo() != 0) return;
    const long current = stepper->currentPosition();
    if (labs(current) <= kPositionNormalizeThreshold) return;
    const uint8_t idx = axisIndex(axis);
    state.positionOffsetSteps[idx] += static_cast<int64_t>(current);
    stepper->setCurrentPosition(0);
}
bool axisIdle(MotorAxis axis) {
    AccelStepper* stepper = axisStepper(axis);
    return stepper == nullptr || stepper->distanceToGo() == 0;
}
void updateAxisDiagnostics(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) return;
    const uint8_t idx = axisIndex(axis);
    const int64_t observed = state.positionOffsetSteps[idx] + static_cast<int64_t>(axisStepper(axis)->currentPosition());
    state.diagnostics[idx].observedSteps = observed;
    state.diagnostics[idx].commandedSteps = state.commandedAbsoluteSteps[idx];
    state.diagnostics[idx].missedStepEstimate = static_cast<int32_t>(llabs(state.commandedAbsoluteSteps[idx] - observed));
    state.diagnostics[idx].synchronizedMoveActive = state.synchronizedMoveActive;
#ifdef TMC_UART_ENABLED
    state.diagnostics[idx].stallDetected = isStalled(axisToTmcLabel(axis));
    state.diagnostics[idx].overTempWarning = getDriverTempStatus(axisToTmcLabel(axis)) != 0;
#else
    state.diagnostics[idx].stallDetected = false;
    state.diagnostics[idx].overTempWarning = false;
#endif
}
void queueRelativeMove(MotorAxis axis, long requestedSteps) {
    if (requestedSteps == 0 || axis == MotorAxis::CUTTER) return;
    setDriversEnabled(true);
    const uint8_t idx = axisIndex(axis);
    AccelStepper* stepper = axisStepper(axis);
    const int8_t direction = requestedSteps > 0 ? 1 : -1;
    if (state.lastDirection[idx] != 0 && direction != state.lastDirection[idx] && state.backlashCompensationMm[idx] > 0.0f) {
        const long backlashSteps = mmToSteps(axis, state.backlashCompensationMm[idx]) * direction;
        stepper->move(backlashSteps);
        state.commandedAbsoluteSteps[idx] += backlashSteps;
    }
    stepper->move(requestedSteps);
    state.commandedAbsoluteSteps[idx] += requestedSteps;
    state.lastDirection[idx] = direction;
}
}  // namespace
void setupSteppers() {
    pinMode(STEPPER_A_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_B_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_WINDER_ENABLE_PIN, OUTPUT);
#if !CUTTER_IS_SERVO
    pinMode(STEPPER_CUTTER_ENABLE_PIN, OUTPUT);
#endif
    setDriversEnabled(true);
    state.profiles[0] = {MAX_SPEED_EXTRUDER, ACCELERATION, ACCELERATION};
    state.profiles[1] = {MAX_SPEED_EXTRUDER, ACCELERATION, ACCELERATION};
    state.profiles[2] = {MAX_SPEED_WINDER, ACCELERATION, ACCELERATION};
    applyProfile(MotorAxis::FEED_A);
    applyProfile(MotorAxis::FEED_B);
    applyProfile(MotorAxis::WINDER);
#if CUTTER_IS_SERVO
    cutterServo.attach(CUTTER_SERVO_PIN);
    cutterServo.write(0);
#else
    stepperCutter.setMaxSpeed(MAX_SPEED_EXTRUDER);
    stepperCutter.setAcceleration(ACCELERATION);
#endif
    setGlobalMotorCurrents(state.runCurrentMa, state.holdCurrentMa);
    setGlobalMicrostepping(16);
}
void runSteppers() {
    stepperA.run();
    stepperB.run();
    stepperWinder.run();
#if !CUTTER_IS_SERVO
    stepperCutter.run();
#endif
    normalizeStepperPositionIfNeeded(MotorAxis::FEED_A);
    normalizeStepperPositionIfNeeded(MotorAxis::FEED_B);
    normalizeStepperPositionIfNeeded(MotorAxis::WINDER);
    if (state.synchronizedMoveActive && axisIdle(MotorAxis::FEED_A) && axisIdle(MotorAxis::FEED_B) && axisIdle(MotorAxis::WINDER)) {
        state.synchronizedMoveActive = false;
#ifdef TMC_UART_ENABLED
        setMotorCurrent('X', state.holdCurrentMa);
        setMotorCurrent('Y', state.holdCurrentMa);
        setMotorCurrent('Z', state.holdCurrentMa);
#endif
    }
    updateAxisDiagnostics(MotorAxis::FEED_A);
    updateAxisDiagnostics(MotorAxis::FEED_B);
    updateAxisDiagnostics(MotorAxis::WINDER);
}
void emergencyStopAll() {
    stepperA.stop();
    stepperB.stop();
    stepperWinder.stop();
#if !CUTTER_IS_SERVO
    stepperCutter.stop();
#endif
    stepperA.setCurrentPosition(stepperA.currentPosition());
    stepperB.setCurrentPosition(stepperB.currentPosition());
    stepperWinder.setCurrentPosition(stepperWinder.currentPosition());
    state.synchronizedMoveActive = false;
    setDriversEnabled(false);
}
bool configureMotionProfile(MotorAxis axis, const MotionProfile& profile) {
    if (axis == MotorAxis::CUTTER) return false;
    state.profiles[axisIndex(axis)] = profile;
    applyProfile(axis);
    return true;
}
void setGlobalMicrostepping(uint16_t microstep) {
    if (microstep != 8 && microstep != 16 && microstep != 32) return;
    state.globalMicrostep = microstep;
#ifdef TMC_UART_ENABLED
    setAllMotorMicrosteps(state.globalMicrostep);
#endif
}
void setGlobalMotorCurrents(uint16_t runCurrent, uint16_t holdCurrent) {
    state.runCurrentMa = runCurrent;
    state.holdCurrentMa = holdCurrent;
#ifdef TMC_UART_ENABLED
    setMotorCurrent('X', state.runCurrentMa);
    setMotorCurrent('Y', state.runCurrentMa);
    setMotorCurrent('Z', state.runCurrentMa);
#endif
}
void setBacklashCompensation(MotorAxis axis, float backlashMm) {
    if (axis == MotorAxis::CUTTER) return;
    state.backlashCompensationMm[axisIndex(axis)] = max(0.0f, backlashMm);
}
void moveRelative(MotorAxis axis, float distanceMm) { queueRelativeMove(axis, mmToSteps(axis, distanceMm)); }
void moveAbsolute(MotorAxis axis, float absolutePositionMm) {
    if (axis == MotorAxis::CUTTER) return;
    const uint8_t idx = axisIndex(axis);
    const int64_t currentAbsolute = state.positionOffsetSteps[idx] + static_cast<int64_t>(axisStepper(axis)->currentPosition());
    const int64_t targetAbsolute = static_cast<int64_t>(absolutePositionMm * stepsPerMm(axis));
    const int64_t delta = targetAbsolute - currentAbsolute;
    queueRelativeMove(axis, static_cast<long>(delta));
}
bool startSynchronizedMove(float feedAMm, float feedBMm, float winderMm) {
    moveRelative(MotorAxis::FEED_A, feedAMm);
    moveRelative(MotorAxis::FEED_B, feedBMm);
    moveRelative(MotorAxis::WINDER, winderMm);
    state.synchronizedMoveActive = true;
#ifdef TMC_UART_ENABLED
    setMotorCurrent('X', state.runCurrentMa);
    setMotorCurrent('Y', state.runCurrentMa);
    setMotorCurrent('Z', state.runCurrentMa);
#endif
    return true;
}
bool isSynchronizedMoveActive() { return state.synchronizedMoveActive; }
bool isMotorIdle(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) {
        return true;
    }
    return axisIdle(axis);
}
bool performSensorlessHome(MotorAxis axis, float travelLimitMm, float seekSpeedMmS) {
#ifdef TMC_UART_ENABLED
    if (axis == MotorAxis::CUTTER) return false;
    const long homingSteps = llabs(mmToSteps(axis, travelLimitMm));
    AccelStepper* stepper = axisStepper(axis);
    stepper->setMaxSpeed(max(100.0f, seekSpeedMmS * stepsPerMm(axis)));
    stepper->move(-homingSteps);
    enableStallDetection(axisToTmcLabel(axis), kDefaultStallThreshold);
    const unsigned long deadline = millis() + kSensorlessHomeTimeoutMs;
    while (millis() < deadline) {
        runSteppers();
        if (isStalled(axisToTmcLabel(axis))) {
            stepper->stop();
            stepper->setCurrentPosition(0);
            const uint8_t idx = axisIndex(axis);
            state.positionOffsetSteps[idx] = 0;
            state.commandedAbsoluteSteps[idx] = 0;
            state.diagnostics[idx].stallDetected = false;
            return true;
        }
        if (stepper->distanceToGo() == 0) break;
    }
#endif
    return false;
}
MotorPosition getMotorPosition(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) return {0, 0.0f};
    const uint8_t idx = axisIndex(axis);
    const int64_t absolute = state.positionOffsetSteps[idx] + static_cast<int64_t>(axisStepper(axis)->currentPosition());
    return {absolute, static_cast<float>(absolute) / stepsPerMm(axis)};
}
MotorDiagnostics getMotorDiagnostics(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) return {false, false, false, 0, 0, 0};
    return state.diagnostics[axisIndex(axis)];
}
void resetMotorPosition(MotorAxis axis) {
    if (axis == MotorAxis::CUTTER) return;
    const uint8_t idx = axisIndex(axis);
    axisStepper(axis)->setCurrentPosition(0);
    state.positionOffsetSteps[idx] = 0;
    state.commandedAbsoluteSteps[idx] = 0;
}
void activateCutter() {
#if CUTTER_IS_SERVO
    cutterServo.write(90);
#else
    stepperCutter.move(CUTTER_STEPPER_TRAVEL_STEPS);
#endif
}
void deactivateCutter() {
#if CUTTER_IS_SERVO
    cutterServo.write(0);
#else
    stepperCutter.move(-CUTTER_STEPPER_TRAVEL_STEPS);
#endif
}
