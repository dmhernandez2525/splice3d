/**
 * Splice3D State Machine Implementation
 */

#include "state_machine.h"
#include "config.h"
#include "stepper_control.h"
#include "temperature.h"

StateMachine::StateMachine() 
    : _state(State::IDLE)
    , _pausedState(State::IDLE)
    , _isPaused(false)
    , _segmentCount(0)
    , _currentSegment(0)
    , _stateStartTime(0)
    , _heaterTimeout(0) {
    memset(_segments, 0, sizeof(_segments));
    memset(_errorMessage, 0, sizeof(_errorMessage));
    _feedStarted = false;
    _cutStarted = false;
    _positionStarted = false;
    _heatingStarted = false;
    _weldStarted = false;
    _coolingStarted = false;
    _spoolingStarted = false;
    _completionReported = false;
}

void StateMachine::init() {
    _state = State::IDLE;
    _isPaused = false;
    _segmentCount = 0;
    _currentSegment = 0;
    DEBUG_PRINTLN(F("State machine initialized"));
}

void StateMachine::update() {
    // Don't update if paused
    if (_isPaused) {
        return;
    }
    
    // Call appropriate state handler
    switch (_state) {
        case State::IDLE:         handleIdle(); break;
        case State::LOADING:      handleLoading(); break;
        case State::READY:        handleReady(); break;
        case State::FEEDING_A:    handleFeedingA(); break;
        case State::FEEDING_B:    handleFeedingB(); break;
        case State::CUTTING:      handleCutting(); break;
        case State::POSITIONING:  handlePositioning(); break;
        case State::HEATING:      handleHeating(); break;
        case State::WELDING:      handleWelding(); break;
        case State::COOLING:      handleCooling(); break;
        case State::SPOOLING:     handleSpooling(); break;
        case State::NEXT_SEGMENT: handleNextSegment(); break;
        case State::COMPLETE:     handleComplete(); break;
        case State::ERROR:        handleErrorState(); break;
    }
}

const char* StateMachine::getStateString() const {
    switch (_state) {
        case State::IDLE:         return "IDLE";
        case State::LOADING:      return "LOADING";
        case State::READY:        return "READY";
        case State::FEEDING_A:    return "FEEDING_A";
        case State::FEEDING_B:    return "FEEDING_B";
        case State::CUTTING:      return "CUTTING";
        case State::POSITIONING:  return "POSITIONING";
        case State::HEATING:      return "HEATING";
        case State::WELDING:      return "WELDING";
        case State::COOLING:      return "COOLING";
        case State::SPOOLING:     return "SPOOLING";
        case State::NEXT_SEGMENT: return "NEXT_SEGMENT";
        case State::COMPLETE:     return "COMPLETE";
        case State::ERROR:        return "ERROR";
        default:                  return "UNKNOWN";
    }
}

bool StateMachine::loadRecipe(SpliceSegment* segments, uint16_t count) {
    if (_state != State::IDLE && _state != State::COMPLETE) {
        DEBUG_PRINTLN(F("Cannot load recipe - machine busy"));
        return false;
    }
    
    if (count > MAX_SEGMENTS) {
        DEBUG_PRINTLN(F("Recipe too large"));
        return false;
    }
    
    // Copy segments
    memcpy(_segments, segments, count * sizeof(SpliceSegment));
    _segmentCount = count;
    _currentSegment = 0;
    
    transitionTo(State::READY);
    
    DEBUG_PRINT(F("Recipe loaded: "));
    DEBUG_PRINT(count);
    DEBUG_PRINTLN(F(" segments"));
    
    return true;
}

bool StateMachine::start() {
    if (_state != State::READY) {
        DEBUG_PRINTLN(F("Cannot start - not ready"));
        return false;
    }
    
    if (_segmentCount == 0) {
        DEBUG_PRINTLN(F("Cannot start - no segments"));
        return false;
    }
    
    _currentSegment = 0;
    
    // Start with first segment
    SpliceSegment& seg = _segments[_currentSegment];
    if (seg.colorIndex == 0) {
        transitionTo(State::FEEDING_A);
    } else {
        transitionTo(State::FEEDING_B);
    }
    
    Serial.println(F("OK STARTED"));
    return true;
}

void StateMachine::pause() {
    if (_state == State::IDLE || _state == State::COMPLETE || _state == State::ERROR) {
        return;
    }
    
    _pausedState = _state;
    _isPaused = true;
    
    // Stop motors
    stopAllSteppers();
    
    // Turn off heater (safety)
    setHeaterPower(0);
    
    Serial.println(F("OK PAUSED"));
}

void StateMachine::resume() {
    if (!_isPaused) {
        return;
    }

    _isPaused = false;
    _state = _pausedState;

    // Restore heater if we were in a heating/welding state
    if (_state == State::HEATING || _state == State::WELDING) {
        setTargetTemperature(WELD_TEMP_PLA);
        _heatingStarted = false;  // Force re-init of heating handler
    }

    Serial.println(F("OK RESUMED"));
}

void StateMachine::abort() {
    // Stop everything
    stopAllSteppers();
    setHeaterPower(0);
    setCoolingFan(true);  // Turn on cooling for safety
    
    _isPaused = false;
    transitionTo(State::IDLE);
    
    Serial.println(F("OK ABORTED"));
}

void StateMachine::getProgress(uint16_t& current, uint16_t& total) const {
    current = _currentSegment + 1;
    total = _segmentCount;
}

bool StateMachine::isBusy() const {
    return _state != State::IDLE && 
           _state != State::READY && 
           _state != State::COMPLETE && 
           _state != State::ERROR;
}

void StateMachine::transitionTo(State newState) {
    DEBUG_PRINT(F("State: "));
    DEBUG_PRINT(getStateString());
    DEBUG_PRINT(F(" -> "));

    // Reset all handler flags on every state transition
    _feedStarted = false;
    _cutStarted = false;
    _positionStarted = false;
    _heatingStarted = false;
    _weldStarted = false;
    _coolingStarted = false;
    _spoolingStarted = false;
    _completionReported = false;

    _state = newState;
    _stateStartTime = millis();

    DEBUG_PRINTLN(getStateString());
}

void StateMachine::handleError(const char* message) {
    strncpy(_errorMessage, message, sizeof(_errorMessage) - 1);
    stopAllSteppers();
    setHeaterPower(0);
    setCoolingFan(true);
    transitionTo(State::ERROR);
    
    Serial.print(F("ERROR "));
    Serial.println(message);
}

// ============================================================
// State Handlers
// ============================================================

void StateMachine::handleIdle() {
    // Nothing to do, waiting for recipe
}

void StateMachine::handleLoading() {
    // Recipe loading is handled by serial handler
    // This state is transitory
}

void StateMachine::handleReady() {
    // Waiting for START command
}

void StateMachine::handleFeedingA() {
    if (!_feedStarted) {
        SpliceSegment& seg = _segments[_currentSegment];
        feedFilament(0, seg.lengthMm);
        _feedStarted = true;
        DEBUG_PRINT(F("Feeding A: "));
        DEBUG_PRINT(seg.lengthMm);
        DEBUG_PRINTLN(F(" mm"));
    }

    // Check for motor timeout
    if (millis() - _stateStartTime > 30000UL) {
        handleError("FEED_A_TIMEOUT");
        return;
    }

    if (isStepperIdle(0)) {
        transitionTo(State::CUTTING);
    }
}

void StateMachine::handleFeedingB() {
    if (!_feedStarted) {
        SpliceSegment& seg = _segments[_currentSegment];
        feedFilament(1, seg.lengthMm);
        _feedStarted = true;
        DEBUG_PRINT(F("Feeding B: "));
        DEBUG_PRINT(seg.lengthMm);
        DEBUG_PRINTLN(F(" mm"));
    }

    // Check for motor timeout
    if (millis() - _stateStartTime > 30000UL) {
        handleError("FEED_B_TIMEOUT");
        return;
    }

    if (isStepperIdle(1)) {
        _feedStarted = false;
        transitionTo(State::CUTTING);
    }
}

void StateMachine::handleCutting() {
    // _cutStarted is now _cutStarted member
    
    if (!_cutStarted) {
        activateCutter();
        _cutStarted = true;
    }
    
    // Wait for cut to complete (servo movement time)
    if (millis() - _stateStartTime > 500) {
        deactivateCutter();
        _cutStarted = false;
        transitionTo(State::POSITIONING);
    }
}

void StateMachine::handlePositioning() {
    // _positionStarted is now _positionStarted member
    
    if (!_positionStarted) {
        // Move cut end into weld position
        // This might involve a small retract then advance
        positionForWeld();
        _positionStarted = true;
    }
    
    // Wait for positioning complete
    if (millis() - _stateStartTime > 1000) {
        _positionStarted = false;
        transitionTo(State::HEATING);
    }
}

void StateMachine::handleHeating() {
    // _heatingStarted is now _heatingStarted member
    
    if (!_heatingStarted) {
        // Set target temperature using active material profile
        const TemperatureProfile profile = getActiveTemperatureProfile();
        setTargetTemperature(profile.spliceTargetC);
        _heatingStarted = true;
    }

    // Check for timeout (rollover-safe elapsed time pattern)
    if (millis() - _stateStartTime > HEATER_TIMEOUT_MS) {
        handleError("HEATER_TIMEOUT");
        return;
    }

    // Check if temperature reached
    if (isTemperatureReached()) {
        transitionTo(State::WELDING);
    }
}

void StateMachine::handleWelding() {
    // _weldStarted is now _weldStarted member
    
    if (!_weldStarted) {
        // Compress filaments together
        compressWeld(WELD_COMPRESSION_MM);
        _weldStarted = true;
    }
    
    // Hold at temperature for weld time
    if (millis() - _stateStartTime >= WELD_HOLD_TIME_MS) {
        _weldStarted = false;
        transitionTo(State::COOLING);
    }
}

void StateMachine::handleCooling() {
    // _coolingStarted is now _coolingStarted member
    
    if (!_coolingStarted) {
        // Turn off heater, turn on fan
        setHeaterPower(0);
        setCoolingFan(true);
        _coolingStarted = true;
    }
    
    // Wait for cooling (either time-based or temp-based)
    float currentTemp = getCurrentTemperature();
    bool tempReached = currentTemp <= COOLING_TEMP_TARGET;
    bool timeElapsed = millis() - _stateStartTime >= COOLING_TIME_MS;
    
    if (tempReached || timeElapsed) {
        setCoolingFan(false);
        _coolingStarted = false;
        transitionTo(State::SPOOLING);
    }
}

void StateMachine::handleSpooling() {
    // _spoolingStarted is now _spoolingStarted member
    
    if (!_spoolingStarted) {
        // Wind the welded segment onto output spool
        SpliceSegment& seg = _segments[_currentSegment];
        windOutput(seg.lengthMm);
        _spoolingStarted = true;
    }
    
    // Check if spooling complete
    if (isWinderIdle()) {
        _spoolingStarted = false;
        transitionTo(State::NEXT_SEGMENT);
    }
}

void StateMachine::handleNextSegment() {
    _currentSegment++;
    
    // Report progress
    Serial.print(F("PROGRESS "));
    Serial.print(_currentSegment);
    Serial.print(F("/"));
    Serial.println(_segmentCount);
    
    // Check if done
    if (_currentSegment >= _segmentCount) {
        transitionTo(State::COMPLETE);
        return;
    }
    
    // Start next segment
    SpliceSegment& seg = _segments[_currentSegment];
    if (seg.colorIndex == 0) {
        transitionTo(State::FEEDING_A);
    } else {
        transitionTo(State::FEEDING_B);
    }
}

void StateMachine::handleComplete() {
    // _completionReported is now _completionReported member
    
    if (!_completionReported) {
        Serial.println(F("DONE"));
        _completionReported = true;
    }
    
    // Reset for next recipe
    // State stays COMPLETE until new recipe loaded or reset
}

void StateMachine::handleErrorState() {
    // Error state - waiting for ABORT command
    // Keep cooling fan on for safety
    setCoolingFan(true);
}
