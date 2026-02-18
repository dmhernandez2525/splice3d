/**
 * Splice3D Firmware Configuration
 * 
 * Pin mappings for BTT SKR Mini E3 v2.0
 * MCU: STM32F103RCT6 (32-bit, 256KB flash, 48KB RAM)
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================================
// VERSION
// ============================================================
#define FIRMWARE_VERSION "0.1.0"

// ============================================================
// BOARD IDENTIFICATION
// ============================================================
#define BOARD_SKR_MINI_E3_V2

// ============================================================
// SERIAL COMMUNICATION
// ============================================================
#define SERIAL_BAUD 115200
#define SERIAL_BUFFER_SIZE 512  // More RAM = bigger buffer

// ============================================================
// PIN MAPPINGS - BTT SKR Mini E3 v2.0
// Reference: https://github.com/bigtreetech/BIGTREETECH-SKR-mini-E3
// ============================================================

// Input Extruder A (uses X stepper driver)
#define STEPPER_A_STEP_PIN     PB13  // X_STEP
#define STEPPER_A_DIR_PIN      PB12  // X_DIR
#define STEPPER_A_ENABLE_PIN   PB14  // X_ENABLE

// Input Extruder B (uses Y stepper driver)
#define STEPPER_B_STEP_PIN     PB10  // Y_STEP
#define STEPPER_B_DIR_PIN      PB2   // Y_DIR
#define STEPPER_B_ENABLE_PIN   PB11  // Y_ENABLE

// Output Winder (uses Z stepper driver)
#define STEPPER_WINDER_STEP_PIN    PB0   // Z_STEP
#define STEPPER_WINDER_DIR_PIN     PC5   // Z_DIR
#define STEPPER_WINDER_ENABLE_PIN  PB1   // Z_ENABLE

// Cutter Servo (uses E stepper for servo or stepper cutter)
#define CUTTER_SERVO_PIN       PB3   // E_STEP (PWM capable)
#define CUTTER_IS_SERVO        true  // Set to false for stepper cutter

// Alternative: Stepper-based cutter (if CUTTER_IS_SERVO = false)
#define STEPPER_CUTTER_STEP_PIN    PB3   // E_STEP
#define STEPPER_CUTTER_DIR_PIN     PB4   // E_DIR
#define STEPPER_CUTTER_ENABLE_PIN  PD1   // E_ENABLE

// ============================================================
// HEATER (Weld Chamber) - Uses hotend circuit
// ============================================================
#define HEATER_PIN             PC8   // HE0 (Hotend heater)
#define THERMISTOR_PIN         PA0   // TH0 (Hotend thermistor)
#define COOLING_FAN_PIN        PC6   // FAN0 (Part cooling)

// Thermistor settings (100K NTC, common in 3D printers)
#define THERMISTOR_NOMINAL_R   100000  // Resistance at 25°C
#define THERMISTOR_NOMINAL_T   25      // Temp at nominal resistance
#define THERMISTOR_B_COEFF     3950    // Beta coefficient
#define THERMISTOR_SERIES_R    4700    // Series resistor value

// ============================================================
// FILAMENT SENSORS - Uses endstop inputs
// ============================================================
#define FILAMENT_SENSOR_A_PIN  PC0   // X_STOP
#define FILAMENT_SENSOR_B_PIN  PC1   // Y_STOP
#define FILAMENT_SENSOR_OUT_PIN PC2  // Z_STOP

// ============================================================
// QUADRATURE ENCODER (F2.2)
// ============================================================
#define ENCODER_CHANNEL_A_PIN  PA1
#define ENCODER_CHANNEL_B_PIN  PA2
#define ENCODER_DEFAULT_TICKS_PER_MM 120.0f
#define ENCODER_MIN_TICKS_PER_MM 10.0f
#define ENCODER_MAX_TICKS_PER_MM 2000.0f
#define ENCODER_DEBOUNCE_US    70UL
#define ENCODER_SLIP_THRESHOLD_MM 2.0f
#define ENCODER_CORRECTION_GAIN 0.25f
#define ENCODER_CORRECTION_MAX_MM 0.35f
#define ENCODER_CORRECTION_DEADBAND_MM 0.20f
#define ENCODER_CORRECTION_INTERVAL_MS 120UL
#define ENCODER_LOG_INTERVAL_MS 1000UL
#define ENCODER_HEALTH_STALE_MS 1500UL
#define ENCODER_INVALID_RATIO_WARN 0.05f

// ============================================================
// LCD DISPLAY - SKR Mini E3 uses EXP1 connector
// Note: Stock Ender 3 LCD is directly compatible
// ============================================================
#define LCD_ENABLED            true

// For CR10 Stock Display (directly compatible)
#define LCD_RS_PIN             PB15  // EXP1_7
#define LCD_EN_PIN             PB8   // EXP1_5
#define LCD_D4_PIN             PB9   // EXP1_6
#define LCD_D5_PIN             PA10  // EXP1_8
#define LCD_D6_PIN             PA9   // EXP1_10
#define LCD_D7_PIN             PB5   // EXP1_9

// Encoder
#define BTN_EN1                PA15  // EXP1_3
#define BTN_EN2                PA8   // EXP1_1
#define BTN_ENC                PD6   // EXP1_2

// Beeper
#define BEEPER_PIN             PB5   // EXP1_9

// ============================================================
// NEOPIXEL (Optional - if you want status LEDs)
// ============================================================
#define NEOPIXEL_PIN           PA13  // Optional RGB LED

// ============================================================
// STEPPER CALIBRATION
// ============================================================
// Steps per mm of filament - calibrate with your extruder gears!
// Default assumes 16 microsteps, standard extruder gearing
#define STEPS_PER_MM_EXTRUDER_A  93.0
#define STEPS_PER_MM_EXTRUDER_B  93.0
#define STEPS_PER_MM_WINDER      50.0   // Depends on spool diameter

// TMC2209 UART (SKR Mini E3 has onboard TMC2209)
#define TMC_UART_ENABLED       true
#define X_SERIAL_RX_PIN        PC11
#define X_SERIAL_TX_PIN        PC10
#define Y_SERIAL_RX_PIN        PC11
#define Y_SERIAL_TX_PIN        PC10
#define Z_SERIAL_RX_PIN        PC11
#define Z_SERIAL_TX_PIN        PC10
#define E_SERIAL_RX_PIN        PC11
#define E_SERIAL_TX_PIN        PC10

// Motor currents (milliamps) - TMC2209 can be configured via UART
#define MOTOR_CURRENT_MA       800

// Max speeds (steps/sec) - can be higher with 32-bit
#define MAX_SPEED_EXTRUDER     5000
#define MAX_SPEED_WINDER       8000
#define ACCELERATION           2000

// ============================================================
// WELD PARAMETERS
// ============================================================
#define WELD_TEMP_PLA          210     // °C
#define WELD_TEMP_PETG         235     // °C
#define WELD_TEMP_ABS          250     // °C
#define WELD_HOLD_TIME_MS      3000    // Hold at temp (ms)
#define WELD_COMPRESSION_MM    2.0     // Push distance during weld
#define WELD_POSITION_ADVANCE_MM 2.0   // Positioning distance before weld
#define COOLING_TIME_MS        5000    // Cooling fan time (ms)
#define COOLING_TEMP_TARGET    50      // °C to reach before continuing

// Cutter travel for stepper-based cutter configuration
#define CUTTER_STEPPER_TRAVEL_STEPS 200

// ============================================================
// SAFETY
// ============================================================
#define MAX_TEMP               280     // Emergency shutoff temp
#define TEMP_HYSTERESIS        3       // °C
#define HEATER_TIMEOUT_MS      120000  // 2 min max heat time
#define THERMAL_RUNAWAY_PERIOD_MS 40000UL // Must heat THERMAL_RUNAWAY_MIN_RISE_C in this window
#define THERMAL_RUNAWAY_MIN_RISE_C 10.0f  // Minimum rise required in the window
#define THERMAL_RUNAWAY_CHECK_INTERVAL_MS 5000UL
#define THERMISTOR_DISCONNECT_LOW_C -10.0f
#define THERMISTOR_DISCONNECT_HIGH_C 350.0f
#define COLD_EXTRUSION_MIN_C   170.0f // Block motor motion below this temp
#define TEMP_LOG_INTERVAL_MS   1000UL // 1Hz serial log
#define PID_WATCHDOG_MS        2000UL // PID loop must run within this interval
#define PREHEAT_RAMP_RATE_C_PER_SEC 2.0f
#define SOAK_HOLD_MS           3000UL // Hold at target before declaring READY

// ============================================================
// FILAMENT PROPERTIES
// ============================================================
#define FILAMENT_DIAMETER      1.75    // mm

// ============================================================
// DEBUG
// ============================================================
#define DEBUG_ENABLED          true
#define DEBUG_SERIAL           Serial  // USB CDC serial

#if DEBUG_ENABLED
  #define DEBUG_PRINT(x)    DEBUG_SERIAL.print(x)
  #define DEBUG_PRINTLN(x)  DEBUG_SERIAL.println(x)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
#endif

#endif // CONFIG_H
