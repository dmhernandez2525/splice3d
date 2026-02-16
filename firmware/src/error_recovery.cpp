#include "error_recovery.h"
#include "config.h"
#include "temperature.h"
#include "stepper_control.h"
#include "cutting_system.h"
#include "splice_execution.h"
namespace {
constexpr uint8_t kDefaultMaxRetries = 3;
constexpr uint32_t kDefaultCooldownTimeoutMs = 60000UL;
constexpr float kDefaultCooldownTargetC = 60.0f;
constexpr uint32_t kDefaultAssessmentDelayMs = 500UL;
constexpr uint32_t kDefaultRetryDelayMs = 1000UL;
constexpr uint8_t kAttemptHistorySize = 8;
struct RecoveryState {
    RecoveryPhase phase;
    RecoveryConfig cfg;
    RecoveryStatistics stats;
    RecoveryAttempt current;
    RecoveryAttempt history[kAttemptHistorySize];
    uint8_t historyCount;
    uint32_t phaseStartMs;
    uint32_t lastUpdateMs;
    bool active;
};
RecoveryState st;
void enterPhase(RecoveryPhase phase) {
    st.phase = phase;
    st.phaseStartMs = millis();
    st.current.phase = phase;
}
void finishAttempt(bool success) {
    st.current.succeeded = success;
    st.current.durationMs = millis() - st.current.startMs;
    // Store in history ring.
    if (st.historyCount < kAttemptHistorySize) {
        st.history[st.historyCount] = st.current;
        st.historyCount++;
    }
    // Update statistics.
    if (success) {
        if (st.current.action == RecoveryAction::MANUAL_REQUIRED) {
            st.stats.userRecovered++;
        } else {
            st.stats.autoRecovered++;
        }
    } else {
        st.stats.unrecoverable++;
    }
    // Running average of recovery time.
    const uint32_t total = st.stats.autoRecovered + st.stats.userRecovered;
    if (total > 0) {
        const float t = static_cast<float>(total);
        st.stats.averageRecoveryMs =
            ((t - 1.0f) * st.stats.averageRecoveryMs +
             static_cast<float>(st.current.durationMs)) / t;
    }
    st.active = false;
    enterPhase(success ? RecoveryPhase::RESOLVED : RecoveryPhase::UNRECOVERABLE);
    if (success) {
        Serial.print(F("RECOVERY_OK"));
    } else {
        Serial.print(F("RECOVERY_FAIL"));
    }
    Serial.print(F(" code="));
    Serial.print(static_cast<uint8_t>(st.current.errorCode));
    Serial.print(F(" retries="));
    Serial.print(st.current.retryNumber);
    Serial.print(F(" ms="));
    Serial.println(st.current.durationMs);
}
void handleAssessing() {
    const uint32_t elapsed = millis() - st.phaseStartMs;
    if (elapsed < st.cfg.assessmentDelayMs) return;
    const RecoveryAction action = errorHandler.getRecoveryAction();
    st.current.action = action;
    switch (action) {
        case RecoveryAction::RETRY_ONCE:
            enterPhase(RecoveryPhase::RETRYING);
            break;
        case RecoveryAction::RETRY_AFTER_COOL:
            setHeaterPower(0);
            setCoolingFan(true);
            enterPhase(RecoveryPhase::COOLDOWN_WAIT);
            break;
        case RecoveryAction::MANUAL_REQUIRED:
            Serial.println(F("RECOVERY AWAITING_USER"));
            enterPhase(RecoveryPhase::AWAITING_USER);
            break;
        case RecoveryAction::ABORT:
            st.stats.abortedJobs++;
            finishAttempt(false);
            break;
        case RecoveryAction::RESET:
            st.stats.abortedJobs++;
            finishAttempt(false);
            break;
        default:
            finishAttempt(false);
            break;
    }
}
void handleCooldownWait() {
    const uint32_t elapsed = millis() - st.phaseStartMs;
    const float temp = getCurrentTemperature();
    if (temp <= st.cfg.cooldownTargetC) {
        setCoolingFan(false);
        enterPhase(RecoveryPhase::RETRYING);
        return;
    }
    if (elapsed > st.cfg.cooldownTimeoutMs) {
        setCoolingFan(false);
        Serial.println(F("RECOVERY cooldown timeout"));
        finishAttempt(false);
    }
}
void handleRetrying() {
    const uint32_t elapsed = millis() - st.phaseStartMs;
    if (elapsed < st.cfg.retryDelayMs) return;
    st.current.retryNumber++;
    st.stats.totalRetries++;
    if (st.current.retryNumber > st.cfg.maxRetries) {
        Serial.println(F("RECOVERY retries exhausted"));
        finishAttempt(false);
        return;
    }
    // Attempt the retry through the error handler.
    const bool ok = errorHandler.attemptRecovery();
    if (ok) {
        finishAttempt(true);
    } else {
        // Error handler could not recover; try again or give up.
        if (st.current.retryNumber >= st.cfg.maxRetries) {
            finishAttempt(false);
        } else {
            enterPhase(RecoveryPhase::ASSESSING);
        }
    }
}
}  // namespace
void setupErrorRecovery() {
    st = {};
    st.phase = RecoveryPhase::IDLE;
    st.cfg.maxRetries = kDefaultMaxRetries;
    st.cfg.cooldownTimeoutMs = kDefaultCooldownTimeoutMs;
    st.cfg.cooldownTargetC = kDefaultCooldownTargetC;
    st.cfg.assessmentDelayMs = kDefaultAssessmentDelayMs;
    st.cfg.retryDelayMs = kDefaultRetryDelayMs;
}
void updateErrorRecovery() {
    if (!st.active) return;
    switch (st.phase) {
        case RecoveryPhase::ASSESSING:
            handleAssessing();
            break;
        case RecoveryPhase::COOLDOWN_WAIT:
            handleCooldownWait();
            break;
        case RecoveryPhase::RETRYING:
            handleRetrying();
            break;
        case RecoveryPhase::AWAITING_USER:
            // Waiting for confirmUserRecovery() call.
            break;
        case RecoveryPhase::IDLE:
        case RecoveryPhase::RESOLVED:
        case RecoveryPhase::UNRECOVERABLE:
            break;
    }
}
bool beginRecovery() {
    if (st.active) return false;
    if (!errorHandler.hasError()) return false;
    st.active = true;
    st.current = {};
    st.current.errorCode = errorHandler.getErrorCode();
    st.current.startMs = millis();
    st.current.retryNumber = 0;
    st.stats.totalErrors++;
    Serial.print(F("RECOVERY BEGIN code="));
    Serial.println(static_cast<uint8_t>(st.current.errorCode));
    enterPhase(RecoveryPhase::ASSESSING);
    return true;
}
bool confirmUserRecovery() {
    if (st.phase != RecoveryPhase::AWAITING_USER) return false;
    errorHandler.clearError();
    finishAttempt(true);
    return true;
}
void abortRecovery() {
    if (!st.active) return;
    if (isSpliceActive()) abortSplice();
    setHeaterPower(0);
    setCoolingFan(false);
    errorHandler.clearError();
    st.active = false;
    st.stats.abortedJobs++;
    enterPhase(RecoveryPhase::IDLE);
    Serial.println(F("RECOVERY ABORTED"));
}
RecoveryPhase getRecoveryPhase() { return st.phase; }
RecoveryStatistics getRecoveryStatistics() { return st.stats; }
void resetRecoveryStatistics() { st.stats = {}; }
RecoveryAttempt getLastAttempt() {
    if (st.historyCount == 0) return {};
    return st.history[st.historyCount - 1];
}
bool isRecoveryActive() { return st.active; }
void setRecoveryConfig(const RecoveryConfig& cfg) { st.cfg = cfg; }
RecoveryConfig getRecoveryConfig() { return st.cfg; }
