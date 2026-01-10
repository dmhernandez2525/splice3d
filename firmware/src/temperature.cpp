/**
 * Splice3D Temperature Control Implementation
 * 
 * Uses PID control for heater, reads NTC thermistor.
 */

#include "temperature.h"
#include "config.h"
#include <PID_v1.h>

// PID variables
double pidInput = 0;    // Current temp
double pidOutput = 0;   // Heater PWM
double pidSetpoint = 0; // Target temp

// PID tuning - these will need adjustment for your setup
double Kp = 20.0;
double Ki = 1.0;
double Kd = 5.0;

PID heaterPID(&pidInput, &pidOutput, &pidSetpoint, Kp, Ki, Kd, DIRECT);

// State
bool pidEnabled = false;
float currentTemp = 0;
float targetTemp = 0;
unsigned long lastTempRead = 0;

void setupTemperature() {
    // Heater output
    pinMode(HEATER_PIN, OUTPUT);
    digitalWrite(HEATER_PIN, LOW);
    
    // Cooling fan
    pinMode(COOLING_FAN_PIN, OUTPUT);
    digitalWrite(COOLING_FAN_PIN, LOW);
    
    // Thermistor input
    pinMode(THERMISTOR_PIN, INPUT);
    
    // Configure PID
    heaterPID.SetMode(MANUAL);
    heaterPID.SetOutputLimits(0, 255);
    heaterPID.SetSampleTime(100);  // 100ms sample time
    
    DEBUG_PRINTLN(F("Temperature control initialized"));
}

/**
 * Read temperature from NTC thermistor using Steinhart-Hart equation.
 */
float readThermistor() {
    // Average multiple readings for stability
    float average = 0;
    for (int i = 0; i < 5; i++) {
        average += analogRead(THERMISTOR_PIN);
        delay(1);
    }
    average /= 5;
    
    // Convert to resistance
    // Using voltage divider formula: R_thermistor = R_series * (1023/reading - 1)
    float resistance = THERMISTOR_SERIES_R / (1023.0 / average - 1.0);
    
    // Steinhart-Hart equation (simplified B parameter equation)
    float steinhart;
    steinhart = resistance / THERMISTOR_NOMINAL_R;     // (R/Ro)
    steinhart = log(steinhart);                        // ln(R/Ro)
    steinhart /= THERMISTOR_B_COEFF;                   // 1/B * ln(R/Ro)
    steinhart += 1.0 / (THERMISTOR_NOMINAL_T + 273.15); // + (1/To)
    steinhart = 1.0 / steinhart;                       // Invert
    steinhart -= 273.15;                               // Convert Kelvin to Celsius
    
    return steinhart;
}

void updateTemperature() {
    // Read temperature periodically (not every loop)
    if (millis() - lastTempRead >= 100) {
        currentTemp = readThermistor();
        lastTempRead = millis();
        
        // Safety check
        if (currentTemp > MAX_TEMP) {
            // Emergency shutoff
            setHeaterPower(0);
            pidEnabled = false;
            DEBUG_PRINTLN(F("SAFETY: Max temp exceeded!"));
            return;
        }
    }
    
    // Run PID if enabled
    if (pidEnabled) {
        pidInput = currentTemp;
        heaterPID.Compute();
        analogWrite(HEATER_PIN, (int)pidOutput);
    }
}

void setTargetTemperature(float tempC) {
    if (tempC > MAX_TEMP) {
        tempC = MAX_TEMP;
    }
    
    targetTemp = tempC;
    pidSetpoint = tempC;
    
    if (tempC > 0) {
        pidEnabled = true;
        heaterPID.SetMode(AUTOMATIC);
    } else {
        pidEnabled = false;
        heaterPID.SetMode(MANUAL);
        analogWrite(HEATER_PIN, 0);
    }
    
    DEBUG_PRINT(F("Target temp: "));
    DEBUG_PRINT(tempC);
    DEBUG_PRINTLN(F("C"));
}

float getCurrentTemperature() {
    return currentTemp;
}

float getTargetTemperature() {
    return targetTemp;
}

void setHeaterPower(uint8_t power) {
    // Disable PID when setting power directly
    pidEnabled = false;
    heaterPID.SetMode(MANUAL);
    
    analogWrite(HEATER_PIN, power);
    
    DEBUG_PRINT(F("Heater power: "));
    DEBUG_PRINTLN(power);
}

void setCoolingFan(bool on) {
    digitalWrite(COOLING_FAN_PIN, on ? HIGH : LOW);
    
    DEBUG_PRINT(F("Cooling fan: "));
    DEBUG_PRINTLN(on ? F("ON") : F("OFF"));
}

bool isTemperatureReached() {
    return currentTemp >= targetTemp - TEMP_HYSTERESIS;
}
