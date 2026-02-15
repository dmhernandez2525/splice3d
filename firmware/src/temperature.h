/**
 * Splice3D Temperature Control
 * 
 * PID-based temperature control for the weld heater.
 */

#ifndef TEMPERATURE_H
#define TEMPERATURE_H

#include <Arduino.h>

enum class MaterialProfile : uint8_t {
    PLA = 0,
    PETG = 1,
    ABS = 2,
};

enum class HeatingStage : uint8_t {
    OFF = 0,
    PREHEAT = 1,
    SOAK = 2,
    READY = 3,
    FAULT = 4,
};

struct TemperatureProfile {
    MaterialProfile material;
    float spliceTargetC;
    float minMotionC;
    float rampRateCPerSec;
    uint16_t soakTimeMs;
};

struct TemperatureTelemetry {
    float currentC;
    float targetC;
    float effectiveSetpointC;
    float predictedTimeSec;
    float pidOutputPwm;
    bool pidAutoTuneActive;
    bool thermalFault;
    HeatingStage stage;
};

/**
 * Initialize temperature control.
 */
void setupTemperature();

/**
 * Update temperature control loop.
 * Call every loop iteration.
 */
void updateTemperature();

/**
 * Set target temperature.
 * @param tempC Target in Celsius
 */
void setTargetTemperature(float tempC);

/**
 * Select material profile and update default targets.
 */
void setMaterialProfile(MaterialProfile profile);
MaterialProfile getMaterialProfile();
TemperatureProfile getActiveTemperatureProfile();

/**
 * Get current temperature.
 * @return Current temp in Celsius
 */
float getCurrentTemperature();

/**
 * Get target temperature.
 */
float getTargetTemperature();

/**
 * Set heater power directly (0-255).
 * Also disables PID control.
 */
void setHeaterPower(uint8_t power);

/**
 * Enable/disable cooling fan.
 */
void setCoolingFan(bool on);

/**
 * Check if temperature is at target (within hysteresis).
 */
bool isTemperatureReached();

/**
 * Motion safety helpers.
 */
bool isColdExtrusionBlocked();
bool hasThermalFault();

/**
 * Fan control with PWM support.
 */
void setCoolingFanPwm(uint8_t pwm);

/**
 * PID and diagnostics helpers.
 */
void setPidTunings(float kp, float ki, float kd);
void startPidAutoTune();
bool isPidAutoTuneActive();
void updatePidAutoTune();
float predictTimeToTargetSeconds();
HeatingStage getHeatingStage();
TemperatureTelemetry getTemperatureTelemetry();

#endif // TEMPERATURE_H
