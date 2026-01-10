/**
 * Splice3D Temperature Control
 * 
 * PID-based temperature control for the weld heater.
 */

#ifndef TEMPERATURE_H
#define TEMPERATURE_H

#include <Arduino.h>

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

#endif // TEMPERATURE_H
