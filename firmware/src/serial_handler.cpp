/**
 * Splice3D Serial Command Handler Implementation
 */

#include "serial_handler.h"
#include "config.h"
#include "state_machine.h"
#include "temperature.h"
#include "encoder_system.h"
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

// Reference to global state machine (declared in main.cpp)
extern StateMachine stateMachine;

SerialHandler::SerialHandler() 
    : _bufferIndex(0) {
    memset(_buffer, 0, sizeof(_buffer));
}

void SerialHandler::processInput() {
    while (Serial.available()) {
        char c = Serial.read();
        
        // Handle newline - process complete line
        if (c == '\n' || c == '\r') {
            if (_bufferIndex > 0) {
                _buffer[_bufferIndex] = '\0';
                processLine(_buffer);
                _bufferIndex = 0;
            }
        }
        // Handle backspace
        else if (c == '\b' && _bufferIndex > 0) {
            _bufferIndex--;
        }
        // Add to buffer
        else if (_bufferIndex < sizeof(_buffer) - 1) {
            _buffer[_bufferIndex++] = c;
        }
    }
}

void SerialHandler::processLine(const char* line) {
    // Skip empty lines
    if (strlen(line) == 0) {
        return;
    }
    
    DEBUG_PRINT(F("CMD: "));
    DEBUG_PRINTLN(line);
    
    // Parse command and arguments
    char cmd[32];
    const char* args = nullptr;
    
    // Find first space to separate command from args
    const char* space = strchr(line, ' ');
    if (space) {
        size_t cmdLen = space - line;
        if (cmdLen >= sizeof(cmd)) cmdLen = sizeof(cmd) - 1;
        strncpy(cmd, line, cmdLen);
        cmd[cmdLen] = '\0';
        args = space + 1;
    } else {
        strncpy(cmd, line, sizeof(cmd) - 1);
        cmd[sizeof(cmd) - 1] = '\0';
    }
    
    // Convert command to uppercase for comparison
    for (char* p = cmd; *p; p++) {
        *p = toupper(*p);
    }
    
    // Dispatch to handlers
    if (strcmp(cmd, "RECIPE") == 0) {
        handleRecipe(args);
    }
    else if (strcmp(cmd, "START") == 0) {
        handleStart();
    }
    else if (strcmp(cmd, "PAUSE") == 0) {
        handlePause();
    }
    else if (strcmp(cmd, "RESUME") == 0) {
        handleResume();
    }
    else if (strcmp(cmd, "ABORT") == 0) {
        handleAbort();
    }
    else if (strcmp(cmd, "STATUS") == 0) {
        handleStatus();
    }
    else if (strcmp(cmd, "TEMP") == 0) {
        handleTemp(args);
    }
    else if (strcmp(cmd, "ENCODER") == 0) {
        handleEncoder(args);
    }
    else if (strcmp(cmd, "HELP") == 0 || strcmp(cmd, "?") == 0) {
        handleHelp();
    }
    else {
        Serial.print(F("ERROR Unknown command: "));
        Serial.println(cmd);
    }
}

void SerialHandler::handleRecipe(const char* args) {
    if (!args || strlen(args) == 0) {
        Serial.println(F("ERROR Missing recipe data"));
        return;
    }
    
    // Simple JSON parsing for our specific format
    // Expected: {"segments":[{"color":0,"length_mm":123.45},...],"total_length_mm":999.99}
    
    SpliceSegment segments[MAX_SEGMENTS];
    uint16_t segmentCount = 0;
    
    // Find segments array
    const char* segStart = strstr(args, "\"segments\"");
    if (!segStart) {
        Serial.println(F("ERROR Invalid recipe format"));
        return;
    }
    
    // Find array start
    const char* arrStart = strchr(segStart, '[');
    if (!arrStart) {
        Serial.println(F("ERROR No segments array"));
        return;
    }
    
    // Parse segments
    const char* ptr = arrStart + 1;
    while (*ptr && segmentCount < MAX_SEGMENTS) {
        // Find next object
        const char* objStart = strchr(ptr, '{');
        if (!objStart) break;
        
        const char* objEnd = strchr(objStart, '}');
        if (!objEnd) break;
        
        // Parse color
        const char* colorPtr = strstr(objStart, "\"color\"");
        if (colorPtr && colorPtr < objEnd) {
            colorPtr = strchr(colorPtr, ':');
            if (colorPtr) {
                segments[segmentCount].colorIndex = atoi(colorPtr + 1);
            }
        }
        
        // Parse length
        const char* lengthPtr = strstr(objStart, "\"length_mm\"");
        if (lengthPtr && lengthPtr < objEnd) {
            lengthPtr = strchr(lengthPtr, ':');
            if (lengthPtr) {
                segments[segmentCount].lengthMm = atof(lengthPtr + 1);
            }
        }
        
        segmentCount++;
        ptr = objEnd + 1;
        
        // Check for end of array
        if (*ptr == ']') break;
    }
    
    if (segmentCount == 0) {
        Serial.println(F("ERROR No segments parsed"));
        return;
    }
    
    // Load into state machine
    if (stateMachine.loadRecipe(segments, segmentCount)) {
        Serial.print(F("OK RECIPE_LOADED "));
        Serial.print(segmentCount);
        Serial.println(F(" segments"));
    } else {
        Serial.println(F("ERROR Failed to load recipe"));
    }
}

void SerialHandler::handleStart() {
    if (stateMachine.start()) {
        // Response is handled in state machine
    } else {
        Serial.println(F("ERROR Cannot start"));
    }
}

void SerialHandler::handlePause() {
    stateMachine.pause();
}

void SerialHandler::handleResume() {
    stateMachine.resume();
}

void SerialHandler::handleAbort() {
    stateMachine.abort();
}

void SerialHandler::handleStatus() {
    Serial.print(F("STATUS "));
    Serial.print(stateMachine.getStateString());
    
    if (stateMachine.isBusy()) {
        uint16_t current, total;
        stateMachine.getProgress(current, total);
        Serial.print(F(" PROGRESS "));
        Serial.print(current);
        Serial.print(F("/"));
        Serial.print(total);
    }
    
    Serial.print(F(" TEMP "));
    Serial.print(getCurrentTemperature());
    Serial.print(F("/"));
    Serial.print(getTargetTemperature());

    const EncoderTelemetry telemetry = getEncoderTelemetry();
    Serial.print(F(" ENC_MM "));
    Serial.print(telemetry.positionMm, 2);
    Serial.print(F(" ENC_SLIP "));
    Serial.print(telemetry.slipDetected ? 1 : 0);
    
    Serial.println();
}

void SerialHandler::handleTemp(const char* args) {
    if (args && strlen(args) > 0) {
        // Set temperature
        float temp = atof(args);
        if (temp >= 0 && temp <= MAX_TEMP) {
            setTargetTemperature(temp);
            Serial.print(F("OK TEMP_SET "));
            Serial.println(temp);
        } else {
            Serial.println(F("ERROR Invalid temperature"));
        }
    } else {
        // Query temperature
        Serial.print(F("TEMP "));
        Serial.print(getCurrentTemperature());
        Serial.print(F("/"));
        Serial.println(getTargetTemperature());
    }
}

void SerialHandler::handleHelp() {
    Serial.println(F("Splice3D Commands:"));
    Serial.println(F("  RECIPE <json>  - Load splice recipe"));
    Serial.println(F("  START          - Begin splicing"));
    Serial.println(F("  PAUSE          - Pause operation"));
    Serial.println(F("  RESUME         - Resume from pause"));
    Serial.println(F("  ABORT          - Emergency stop"));
    Serial.println(F("  STATUS         - Query state"));
    Serial.println(F("  TEMP [value]   - Get/set temperature"));
    Serial.println(F("  ENCODER ...    - Encoder status/calibration"));
    Serial.println(F("  HELP           - Show this help"));
}
