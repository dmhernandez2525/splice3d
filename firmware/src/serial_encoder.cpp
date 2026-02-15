/**
 * Splice3D serial encoder command handling.
 */

#include "serial_handler.h"
#include "encoder_system.h"

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

namespace {
void printEncoderStatus() {
    const EncoderTelemetry telemetry = getEncoderTelemetry();
    const EncoderHealth health = getEncoderHealth();
    Serial.print(F("ENCODER STATUS TICKS "));
    Serial.print(telemetry.ticks);
    Serial.print(F(" POS_MM "));
    Serial.print(telemetry.positionMm, 3);
    Serial.print(F(" VEL_MM_S "));
    Serial.print(telemetry.velocityMmPerSec, 3);
    Serial.print(F(" SLIP "));
    Serial.print(telemetry.slipDetected ? 1 : 0);
    Serial.print(F(" ERR_MM "));
    Serial.print(telemetry.averageSlipErrorMm, 3);
    Serial.print(F(" QUALITY "));
    Serial.print(health.signalQuality, 3);
    Serial.print(F(" FAILED "));
    Serial.print(health.failed ? 1 : 0);
    Serial.print(F(" TICKS_PER_MM "));
    Serial.print(getEncoderTicksPerMm(), 4);
    Serial.print(F(" CLOSED_LOOP "));
    Serial.println(isEncoderClosedLoopEnabled() ? 1 : 0);
}

void uppercaseInPlace(char* value) {
    for (char* cursor = value; *cursor; ++cursor) {
        *cursor = static_cast<char>(toupper(*cursor));
    }
}
}  // namespace

void SerialHandler::handleEncoder(const char* args) {
    if (!args || strlen(args) == 0) {
        printEncoderStatus();
        return;
    }

    char buffer[96];
    strncpy(buffer, args, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    char* token = strtok(buffer, " ");
    if (!token) {
        Serial.println(F("ERROR ENCODER_ARGS"));
        return;
    }
    uppercaseInPlace(token);

    if (strcmp(token, "STATUS") == 0) {
        printEncoderStatus();
        return;
    }
    if (strcmp(token, "CAL_START") == 0) {
        const char* lengthToken = strtok(nullptr, " ");
        const float lengthMm = lengthToken ? atof(lengthToken) : 0.0f;
        Serial.println(beginEncoderCalibration(lengthMm) ? F("OK ENCODER_CAL_START") : F("ERROR ENCODER_CAL_START"));
        return;
    }
    if (strcmp(token, "CAL_COMPLETE") == 0) {
        Serial.println(completeEncoderCalibration() ? F("OK ENCODER_CAL_COMPLETE") : F("ERROR ENCODER_CAL_COMPLETE"));
        return;
    }
    if (strcmp(token, "TICKS_PER_MM") == 0) {
        const char* valueToken = strtok(nullptr, " ");
        const float ticksPerMm = valueToken ? atof(valueToken) : 0.0f;
        Serial.println(setEncoderTicksPerMm(ticksPerMm) ? F("OK ENCODER_TICKS_SET") : F("ERROR ENCODER_TICKS_SET"));
        return;
    }
    if (strcmp(token, "LOG_INTERVAL") == 0) {
        const char* intervalToken = strtok(nullptr, " ");
        const uint32_t intervalMs = intervalToken ? static_cast<uint32_t>(atol(intervalToken)) : 0UL;
        setEncoderLogIntervalMs(intervalMs);
        Serial.println(F("OK ENCODER_LOG_INTERVAL"));
        return;
    }
    if (strcmp(token, "CLOSED_LOOP") == 0) {
        char* modeToken = strtok(nullptr, " ");
        if (!modeToken) {
            Serial.println(F("ERROR ENCODER_LOOP_ARG"));
            return;
        }
        uppercaseInPlace(modeToken);
        const bool enabled = strcmp(modeToken, "ON") == 0 || strcmp(modeToken, "1") == 0;
        setEncoderClosedLoopEnabled(enabled);
        Serial.println(enabled ? F("OK ENCODER_LOOP_ON") : F("OK ENCODER_LOOP_OFF"));
        return;
    }
    if (strcmp(token, "SAVE") == 0) {
        Serial.println(saveEncoderCalibration() ? F("OK ENCODER_SAVED") : F("ERROR ENCODER_SAVE"));
        return;
    }
    if (strcmp(token, "RESET_COUNTERS") == 0) {
        resetEncoderCounters();
        Serial.println(F("OK ENCODER_COUNTERS_RESET"));
        return;
    }

    Serial.print(F("ERROR ENCODER_SUBCOMMAND "));
    Serial.println(token);
}
