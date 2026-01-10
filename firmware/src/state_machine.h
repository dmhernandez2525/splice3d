/**
 * Splice3D State Machine
 * 
 * Manages the splice cycle through various states:
 * IDLE -> LOADING -> READY -> FEEDING -> CUTTING -> POSITIONING -> 
 * HEATING -> WELDING -> COOLING -> SPOOLING -> (repeat or COMPLETE)
 */

#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include <Arduino.h>

// Maximum number of segments in a recipe
#define MAX_SEGMENTS 500

// Splice segment structure
struct SpliceSegment {
    uint8_t colorIndex;     // 0 or 1 for two-color
    float lengthMm;         // Length in mm
};

// State machine states
enum class State {
    IDLE,           // Waiting for recipe
    LOADING,        // Parsing recipe from serial
    READY,          // Recipe loaded, waiting for START
    FEEDING_A,      // Feeding filament A
    FEEDING_B,      // Feeding filament B
    CUTTING,        // Cutting filament
    POSITIONING,    // Moving cut end to weld position
    HEATING,        // Heating weld chamber
    WELDING,        // Compressing filaments together
    COOLING,        // Cooling weld joint
    SPOOLING,       // Winding onto output spool
    NEXT_SEGMENT,   // Moving to next segment
    COMPLETE,       // Recipe finished
    ERROR           // Error state
};

class StateMachine {
public:
    StateMachine();
    
    /**
     * Initialize the state machine.
     * Call once in setup().
     */
    void init();
    
    /**
     * Update the state machine.
     * Call every loop iteration.
     */
    void update();
    
    /**
     * Get current state.
     */
    State getState() const { return _state; }
    
    /**
     * Get state as string for display/debug.
     */
    const char* getStateString() const;
    
    /**
     * Load a recipe (called by serial handler).
     * @param segments Array of segments
     * @param count Number of segments
     * @return true if loaded successfully
     */
    bool loadRecipe(SpliceSegment* segments, uint16_t count);
    
    /**
     * Start splicing the loaded recipe.
     * @return true if started
     */
    bool start();
    
    /**
     * Pause current operation.
     */
    void pause();
    
    /**
     * Resume from pause.
     */
    void resume();
    
    /**
     * Abort current operation and reset.
     */
    void abort();
    
    /**
     * Get current progress (segment index / total).
     */
    void getProgress(uint16_t& current, uint16_t& total) const;
    
    /**
     * Check if machine is busy.
     */
    bool isBusy() const;

private:
    State _state;
    State _pausedState;  // State to return to after pause
    bool _isPaused;
    
    // Recipe data
    SpliceSegment _segments[MAX_SEGMENTS];
    uint16_t _segmentCount;
    uint16_t _currentSegment;
    
    // Timing
    unsigned long _stateStartTime;
    unsigned long _heaterTimeout;
    
    // Error tracking
    char _errorMessage[64];
    
    // State transition helpers
    void transitionTo(State newState);
    void handleError(const char* message);
    
    // State handlers
    void handleIdle();
    void handleLoading();
    void handleReady();
    void handleFeedingA();
    void handleFeedingB();
    void handleCutting();
    void handlePositioning();
    void handleHeating();
    void handleWelding();
    void handleCooling();
    void handleSpooling();
    void handleNextSegment();
    void handleComplete();
    void handleErrorState();
};

#endif // STATE_MACHINE_H
