/**
 * Splice3D Error Recovery Engine (F3.4).
 *
 * Manages automatic and user-guided recovery sequences for errors
 * reported by the ErrorHandler. Tracks recovery state, cooldown
 * periods, retry budgets, and recovery statistics.
 */

#ifndef ERROR_RECOVERY_H
#define ERROR_RECOVERY_H

#include <Arduino.h>
#include "error_handler.h"

enum class RecoveryPhase : uint8_t {
    IDLE = 0,
    ASSESSING,
    COOLDOWN_WAIT,
    RETRYING,
    AWAITING_USER,
    RESOLVED,
    UNRECOVERABLE,
};

struct RecoveryAttempt {
    ErrorCode errorCode;
    RecoveryAction action;
    RecoveryPhase phase;
    uint8_t retryNumber;
    uint32_t startMs;
    uint32_t durationMs;
    bool succeeded;
};

struct RecoveryStatistics {
    uint32_t totalErrors;
    uint32_t autoRecovered;
    uint32_t userRecovered;
    uint32_t unrecoverable;
    uint32_t totalRetries;
    uint32_t abortedJobs;
    float averageRecoveryMs;
};

struct RecoveryConfig {
    uint8_t maxRetries;
    uint32_t cooldownTimeoutMs;
    float cooldownTargetC;
    uint32_t assessmentDelayMs;
    uint32_t retryDelayMs;
};

void setupErrorRecovery();
void updateErrorRecovery();

// Trigger recovery for current error.
bool beginRecovery();

// User acknowledges manual intervention is complete.
bool confirmUserRecovery();

// Force abort of recovery and clear error.
void abortRecovery();

// Query state.
RecoveryPhase getRecoveryPhase();
RecoveryStatistics getRecoveryStatistics();
void resetRecoveryStatistics();
RecoveryAttempt getLastAttempt();
bool isRecoveryActive();

// Configuration.
void setRecoveryConfig(const RecoveryConfig& cfg);
RecoveryConfig getRecoveryConfig();

#endif  // ERROR_RECOVERY_H
