/**
 * Splice3D Serial Command Handler
 * 
 * Parses commands from USB serial and dispatches to state machine.
 * 
 * Protocol:
 *   RECIPE <json>     - Load a splice recipe
 *   START             - Begin splicing
 *   PAUSE             - Pause operation
 *   RESUME            - Resume from pause
 *   ABORT             - Emergency stop
 *   STATUS            - Query current state
 *   TEMP              - Query temperature
 *   TEMP <value>      - Set target temperature
 *   ENCODER <args>    - Encoder status, calibration, and tuning
 */

#ifndef SERIAL_HANDLER_H
#define SERIAL_HANDLER_H

#include <Arduino.h>

class SerialHandler {
public:
    SerialHandler();
    
    /**
     * Process any available serial input.
     * Call in main loop when Serial.available().
     */
    void processInput();

private:
    // Input buffer
    char _buffer[256];
    uint8_t _bufferIndex;
    
    // Process a complete line
    void processLine(const char* line);
    
    // Command handlers
    void handleRecipe(const char* args);
    void handleStart();
    void handlePause();
    void handleResume();
    void handleAbort();
    void handleStatus();
    void handleTemp(const char* args);
    void handleEncoder(const char* args);
    void handleHelp();
};

#endif // SERIAL_HANDLER_H
