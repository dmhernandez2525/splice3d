/**
 * Error Handler Implementation for Splice3D Firmware
 */

#include "error_handler.h"
#include "config.h"

// Global instance
ErrorHandler errorHandler;

ErrorHandler::ErrorHandler() 
    : _currentError(ErrorCode::NONE)
    , _retryCount(0)
    , _shutdownComplete(false) 
{
    _errorMessage[0] = '\0';
}

void ErrorHandler::reportError(ErrorCode code, const char* message) {
    _currentError = code;
    strncpy(_errorMessage, message, sizeof(_errorMessage) - 1);
    _errorMessage[sizeof(_errorMessage) - 1] = '\0';
    
    // Send error to serial
    Serial.print("ERROR ");
    Serial.print(static_cast<uint8_t>(code));
    Serial.print(": ");
    Serial.println(message);
    
    // Critical errors trigger immediate shutdown
    if (code == ErrorCode::THERMAL_RUNAWAY || 
        code == ErrorCode::TEMP_TOO_HIGH ||
        code == ErrorCode::EMERGENCY_STOP) {
        emergencyShutdown();
    }
    
    notifyUser();
}

void ErrorHandler::clearError() {
    _currentError = ErrorCode::NONE;
    _errorMessage[0] = '\0';
    _retryCount = 0;
    Serial.println("OK Error cleared");
}

RecoveryAction ErrorHandler::getRecoveryAction() const {
    switch (_currentError) {
        case ErrorCode::NONE:
            return RecoveryAction::NONE;
            
        // Temperature errors
        case ErrorCode::THERMAL_RUNAWAY:
        case ErrorCode::TEMP_TOO_HIGH:
            return RecoveryAction::RETRY_AFTER_COOL;
            
        case ErrorCode::TEMP_SENSOR_FAIL:
            return RecoveryAction::MANUAL_REQUIRED;
            
        // Motor errors - can retry once
        case ErrorCode::MOTOR_STALL_A:
        case ErrorCode::MOTOR_STALL_B:
        case ErrorCode::MOTOR_STALL_WINDER:
            return _retryCount < 2 ? RecoveryAction::RETRY_ONCE : RecoveryAction::MANUAL_REQUIRED;
            
        // Filament errors
        case ErrorCode::FILAMENT_JAM:
            return RecoveryAction::MANUAL_REQUIRED;
            
        case ErrorCode::FILAMENT_OUT_A:
        case ErrorCode::FILAMENT_OUT_B:
            return RecoveryAction::MANUAL_REQUIRED;
            
        // Cutter errors
        case ErrorCode::CUTTER_FAIL:
            return RecoveryAction::RETRY_ONCE;
            
        // Recipe errors
        case ErrorCode::RECIPE_INVALID:
        case ErrorCode::RECIPE_TOO_LARGE:
            return RecoveryAction::ABORT;
            
        // Communication
        case ErrorCode::SERIAL_TIMEOUT:
            return RecoveryAction::RETRY_ONCE;
            
        // Emergency
        case ErrorCode::EMERGENCY_STOP:
            return RecoveryAction::RESET;
            
        default:
            return RecoveryAction::ABORT;
    }
}

bool ErrorHandler::isRecoverable() const {
    RecoveryAction action = getRecoveryAction();
    return action == RecoveryAction::RETRY_ONCE || 
           action == RecoveryAction::RETRY_AFTER_COOL;
}

bool ErrorHandler::attemptRecovery() {
    if (!isRecoverable()) {
        return false;
    }
    
    RecoveryAction action = getRecoveryAction();
    _retryCount++;
    
    switch (action) {
        case RecoveryAction::RETRY_ONCE:
            Serial.println("INFO Retrying operation...");
            clearError();
            return true;
            
        case RecoveryAction::RETRY_AFTER_COOL:
            Serial.println("INFO Cooling down before retry...");
            // Caller should wait for cool-down, then call clearError()
            return true;
            
        default:
            return false;
    }
}

void ErrorHandler::emergencyShutdown() {
    if (_shutdownComplete) return;
    
    Serial.println("!!! EMERGENCY SHUTDOWN !!!");
    
    disableHeaters();
    disableMotors();
    
    _shutdownComplete = true;
    Serial.println("INFO All outputs disabled");
}

void ErrorHandler::disableHeaters() {
    #ifdef HEATER_PIN
    pinMode(HEATER_PIN, OUTPUT);
    digitalWrite(HEATER_PIN, LOW);
    #endif
    
    #ifdef COOLING_FAN_PIN
    // Turn cooling fan ON during emergency
    pinMode(COOLING_FAN_PIN, OUTPUT);
    digitalWrite(COOLING_FAN_PIN, HIGH);
    #endif
}

void ErrorHandler::disableMotors() {
    // Disable all stepper drivers
    #ifdef STEPPER_A_ENABLE_PIN
    pinMode(STEPPER_A_ENABLE_PIN, OUTPUT);
    digitalWrite(STEPPER_A_ENABLE_PIN, HIGH);  // HIGH = disabled for most drivers
    #endif
    
    #ifdef STEPPER_B_ENABLE_PIN
    pinMode(STEPPER_B_ENABLE_PIN, OUTPUT);
    digitalWrite(STEPPER_B_ENABLE_PIN, HIGH);
    #endif
    
    #ifdef STEPPER_WINDER_ENABLE_PIN
    pinMode(STEPPER_WINDER_ENABLE_PIN, OUTPUT);
    digitalWrite(STEPPER_WINDER_ENABLE_PIN, HIGH);
    #endif
}

void ErrorHandler::notifyUser() {
    // Beep if beeper available
    #ifdef BEEPER_PIN
    pinMode(BEEPER_PIN, OUTPUT);
    for (int i = 0; i < 3; i++) {
        digitalWrite(BEEPER_PIN, HIGH);
        delay(100);
        digitalWrite(BEEPER_PIN, LOW);
        delay(100);
    }
    #endif
}
