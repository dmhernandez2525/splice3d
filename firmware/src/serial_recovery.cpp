#include "serial_handler.h"
#include "error_handler.h"
#include "error_recovery.h"
void SerialHandler::handleRecover(const char* args) {
    if (!args || args[0] == '\0') {
        // No subcommand: show recovery status.
        const RecoveryPhase phase = getRecoveryPhase();
        const char* labels[] = {
            "IDLE", "ASSESSING", "COOLDOWN_WAIT", "RETRYING",
            "AWAITING_USER", "RESOLVED", "UNRECOVERABLE",
        };
        Serial.print(F("RECOVER phase="));
        Serial.print(labels[static_cast<uint8_t>(phase)]);
        Serial.print(F(" active="));
        Serial.println(isRecoveryActive() ? F("true") : F("false"));
        return;
    }
    char sub[32];
    const char* rest = nullptr;
    const char* sp = strchr(args, ' ');
    if (sp) {
        const size_t len = sp - args;
        if (len >= sizeof(sub)) return;
        memcpy(sub, args, len);
        sub[len] = '\0';
        rest = sp + 1;
    } else {
        strncpy(sub, args, sizeof(sub) - 1);
        sub[sizeof(sub) - 1] = '\0';
    }
    if (strcmp(sub, "BEGIN") == 0) {
        if (beginRecovery()) {
            Serial.println(F("OK recovery started"));
        } else {
            Serial.println(F("ERR no active error or recovery in progress"));
        }
    } else if (strcmp(sub, "CONFIRM") == 0) {
        if (confirmUserRecovery()) {
            Serial.println(F("OK user recovery confirmed"));
        } else {
            Serial.println(F("ERR not awaiting user confirmation"));
        }
    } else if (strcmp(sub, "ABORT") == 0) {
        abortRecovery();
        Serial.println(F("OK recovery aborted"));
    } else if (strcmp(sub, "STATS") == 0) {
        const RecoveryStatistics s = getRecoveryStatistics();
        Serial.print(F("RECOVER_STATS errors="));
        Serial.print(s.totalErrors);
        Serial.print(F(" auto="));
        Serial.print(s.autoRecovered);
        Serial.print(F(" user="));
        Serial.print(s.userRecovered);
        Serial.print(F(" unrecov="));
        Serial.print(s.unrecoverable);
        Serial.print(F(" retries="));
        Serial.print(s.totalRetries);
        Serial.print(F(" aborted="));
        Serial.print(s.abortedJobs);
        Serial.print(F(" avgMs="));
        Serial.println(s.averageRecoveryMs, 1);
    } else if (strcmp(sub, "RESET_STATS") == 0) {
        resetRecoveryStatistics();
        Serial.println(F("OK recovery stats reset"));
    } else if (strcmp(sub, "CONFIG") == 0) {
        if (rest) {
            // RECOVER CONFIG <maxRetries> <cooldownMs> <cooldownC>
            uint8_t maxR = 0;
            uint32_t cdMs = 0;
            float cdC = 0.0f;
            if (sscanf(rest, "%hhu %lu %f", &maxR, &cdMs, &cdC) == 3) {
                RecoveryConfig cfg = getRecoveryConfig();
                cfg.maxRetries = maxR;
                cfg.cooldownTimeoutMs = cdMs;
                cfg.cooldownTargetC = cdC;
                setRecoveryConfig(cfg);
                Serial.println(F("OK recovery config updated"));
            } else {
                Serial.println(F("ERR usage: RECOVER CONFIG <retries> <cdMs> <cdC>"));
            }
        } else {
            const RecoveryConfig c = getRecoveryConfig();
            Serial.print(F("RECOVER_CONFIG retries="));
            Serial.print(c.maxRetries);
            Serial.print(F(" cdMs="));
            Serial.print(c.cooldownTimeoutMs);
            Serial.print(F(" cdC="));
            Serial.println(c.cooldownTargetC, 1);
        }
    } else {
        Serial.println(F("ERR unknown RECOVER subcommand"));
    }
}
