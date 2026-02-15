/**
 * TMC2209 UART Driver Configuration for Splice3D
 * 
 * Configures the onboard TMC2209 drivers on SKR Mini E3 v2 for:
 * - StealthChop (silent operation)
 * - Programmable motor current
 * - Stall detection (sensorless homing capability)
 */

#ifndef TMC_CONFIG_H
#define TMC_CONFIG_H

#include <Arduino.h>
#include "config.h"

#ifdef TMC_UART_ENABLED

// TMCStepper library for UART communication
// Add to platformio.ini: lib_deps = teemuatlut/TMCStepper@^0.7.3

#include <TMCStepper.h>

// Driver addresses (SKR Mini E3 v2 uses shared UART with different addresses)
#define TMC_X_ADDR 0b00  // X driver address
#define TMC_Y_ADDR 0b01  // Y driver address
#define TMC_Z_ADDR 0b10  // Z driver address
#define TMC_E_ADDR 0b11  // E driver address

// UART pins (shared TX/RX on SKR Mini E3 v2)
#define TMC_UART_RX PC11
#define TMC_UART_TX PC10

// R_SENSE value for current calculation (typically 0.11 ohm for TMC2209)
#define R_SENSE 0.11f

// Create software serial for TMC communication
// Note: On STM32, we may use HardwareSerial instead
#define SERIAL_PORT Serial2  // Adjust based on your board

// Driver instances
extern TMC2209Stepper tmc_x;
extern TMC2209Stepper tmc_y;
extern TMC2209Stepper tmc_z;
extern TMC2209Stepper tmc_e;

/**
 * Initialize all TMC2209 drivers via UART.
 */
void initTMCDrivers();

/**
 * Configure a single driver with standard settings.
 * @param driver TMC2209 driver instance
 * @param current_mA RMS current in milliamps
 * @param stealthchop Enable StealthChop mode
 */
void configureTMCDriver(TMC2209Stepper& driver, uint16_t current_mA, bool stealthchop = true);

/**
 * Set motor current for a specific axis.
 * @param axis 'X', 'Y', 'Z', or 'E'
 * @param current_mA RMS current in milliamps
 */
void setMotorCurrent(char axis, uint16_t current_mA);

/**
 * Set motor microstepping for a specific axis.
 * @param axis 'X', 'Y', 'Z', or 'E'
 * @param microsteps 8, 16, or 32 recommended
 */
void setMotorMicrosteps(char axis, uint16_t microsteps);

/**
 * Set motor microstepping on all axes.
 * @param microsteps 8, 16, or 32 recommended
 */
void setAllMotorMicrosteps(uint16_t microsteps);

/**
 * Enable/disable StealthChop for a specific axis.
 * @param axis 'X', 'Y', 'Z', or 'E'
 * @param enable true for StealthChop (silent), false for SpreadCycle (more torque)
 */
void setStealthChop(char axis, bool enable);

/**
 * Read driver status and report any errors.
 * @return true if all drivers are healthy
 */
bool checkDriverStatus();

/**
 * Get current driver temperature (if supported).
 * @param axis 'X', 'Y', 'Z', or 'E'
 * @return Temperature warning level (0=OK, 1=Warning, 2=Shutdown)
 */
uint8_t getDriverTempStatus(char axis);

/**
 * Enable stall detection for sensorless operation.
 * @param axis 'X', 'Y', 'Z', or 'E'
 * @param threshold Stall threshold (0-255, lower = more sensitive)
 */
void enableStallDetection(char axis, uint8_t threshold);

/**
 * Check if motor has stalled.
 * @param axis 'X', 'Y', 'Z', or 'E'
 * @return true if stall detected
 */
bool isStalled(char axis);

#endif // TMC_UART_ENABLED

#endif // TMC_CONFIG_H
