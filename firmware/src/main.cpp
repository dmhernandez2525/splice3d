/**
 * Splice3D Firmware - Main Entry Point
 * 
 * Controls the filament splicing machine using an Ender 3 board.
 * Receives splice recipes via USB serial and executes weld cycles.
 */

#include <Arduino.h>
#include <AccelStepper.h>
#include "config.h"
#include "state_machine.h"
#include "serial_handler.h"
#include "stepper_control.h"
#include "temperature.h"
#include "encoder_system.h"
#include "cutting_system.h"
#include "filament_feed.h"
#include "splice_execution.h"
#include "position_tracking.h"
#include "error_recovery.h"
#include "telemetry_stream.h"
#include "quality_metrics.h"
#include "job_queue.h"
#include "batch_processor.h"
#include "material_database.h"

// Global state machine instance
StateMachine stateMachine;
SerialHandler serialHandler;

void setup() {
    // Initialize serial communication
    Serial.begin(SERIAL_BAUD);
    while (!Serial && millis() < 3000) {
        ; // Wait for serial port (USB) with 3s timeout
    }
    
    Serial.println(F("Splice3D Firmware v" FIRMWARE_VERSION));
    Serial.println(F("Initializing..."));
    
    // Initialize subsystems
    setupSteppers();
    setupTemperature();
    setupEncoderSystem();
    setupCuttingSystem();
    setupFilamentFeed();
    setupSpliceExecution();
    setupPositionTracking();
    setupErrorRecovery();
    setupTelemetryStream();
    setupQualityMetrics();
    setupJobQueue();
    setupBatchProcessor();
    setupMaterialDatabase();

    // Initialize state machine
    stateMachine.init();
    
    // Ready
    Serial.println(F("OK READY"));
}

void loop() {
    // Handle incoming serial commands
    if (Serial.available()) {
        serialHandler.processInput();
    }
    
    // Run state machine update
    stateMachine.update();
    
    // Update temperature control (PID loop)
    updateTemperature();
    
    // Update stepper positions (non-blocking)
    runSteppers();

    // Update encoder subsystem
    updateEncoderSystem();

    // Update cutting system
    updateCuttingSystem();

    // Update filament feed
    updateFilamentFeed();

    // Update splice execution
    updateSpliceExecution();

    // Update position tracking
    updatePositionTracking();

    // Update error recovery engine
    updateErrorRecovery();

    // Update telemetry stream
    updateTelemetryStream();

    // Update quality metrics
    updateQualityMetrics();

    // Update job queue
    updateJobQueue();

    // Update batch processor
    updateBatchProcessor();

    // Update material database
    updateMaterialDatabase();
}
