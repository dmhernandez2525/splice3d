/**
 * Error Handler for Splice3D Firmware
 * 
 * Handles error conditions and provides recovery options.
 */

#ifndef ERROR_HANDLER_H
#define ERROR_HANDLER_H

#include <Arduino.h>

// Error codes
enum class ErrorCode : uint8_t {
    NONE = 0,
    
    // Temperature errors
    THERMAL_RUNAWAY = 10,      // Heater not responding
    TEMP_SENSOR_FAIL = 11,     // Thermistor disconnected
    TEMP_TOO_HIGH = 12,        // Exceeded MAX_TEMP
    
    // Motor errors
    MOTOR_STALL_A = 20,        // Extruder A not moving
    MOTOR_STALL_B = 21,        // Extruder B not moving
    MOTOR_STALL_WINDER = 22,   // Winder not moving
    
    // Filament errors
    FILAMENT_JAM = 30,         // Filament stuck
    FILAMENT_OUT_A = 31,       // Spool A empty
    FILAMENT_OUT_B = 32,       // Spool B empty
    
    // Cutter errors
    CUTTER_FAIL = 40,          // Cutter didn't actuate
    
    // Recipe errors
    RECIPE_INVALID = 50,       // Malformed recipe
    RECIPE_TOO_LARGE = 51,     // Recipe exceeds memory
    
    // Communication errors
    SERIAL_TIMEOUT = 60,       // Lost connection
    
    // General
    EMERGENCY_STOP = 99        // User triggered E-stop
};

// Recovery actions
enum class RecoveryAction : uint8_t {
    NONE = 0,
    RETRY_ONCE,       // Retry the failed operation once
    RETRY_AFTER_COOL, // Cool down, then retry
    MANUAL_REQUIRED,  // User intervention needed
    ABORT,            // Abort current job
    RESET             // Full system reset required
};

/**
 * Error handler class for managing errors and recovery.
 */
class ErrorHandler {
public:
    ErrorHandler();
    
    /**
     * Report an error.
     * @param code Error code
     * @param message Human-readable message
     */
    void reportError(ErrorCode code, const char* message);
    
    /**
     * Clear the current error.
     */
    void clearError();
    
    /**
     * Check if there's an active error.
     */
    bool hasError() const { return _currentError != ErrorCode::NONE; }
    
    /**
     * Get current error code.
     */
    ErrorCode getErrorCode() const { return _currentError; }
    
    /**
     * Get recommended recovery action.
     */
    RecoveryAction getRecoveryAction() const;
    
    /**
     * Get error message.
     */
    const char* getErrorMessage() const { return _errorMessage; }
    
    /**
     * Check if error is recoverable.
     */
    bool isRecoverable() const;
    
    /**
     * Attempt automatic recovery.
     * @return true if recovery succeeded
     */
    bool attemptRecovery();
    
    /**
     * Get retry count for current error.
     */
    uint8_t getRetryCount() const { return _retryCount; }
    
    /**
     * Emergency shutdown - disable all outputs.
     */
    void emergencyShutdown();

private:
    ErrorCode _currentError;
    char _errorMessage[64];
    uint8_t _retryCount;
    bool _shutdownComplete;
    
    void disableHeaters();
    void disableMotors();
    void notifyUser();
};

// Global error handler instance
extern ErrorHandler errorHandler;

// Convenience macros
#define REPORT_ERROR(code, msg) errorHandler.reportError(ErrorCode::code, msg)
#define CHECK_ERROR() errorHandler.hasError()
#define CLEAR_ERROR() errorHandler.clearError()
#define EMERGENCY_STOP() errorHandler.emergencyShutdown()

#endif // ERROR_HANDLER_H
