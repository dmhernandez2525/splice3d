#include "serial_handler.h"
#include "temperature.h"
#include "config.h"

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

void SerialHandler::handleTemp(const char* args) {
    if (!args || strlen(args) == 0) {
        const TemperatureTelemetry t = getTemperatureTelemetry();
        Serial.print(F("TEMP C="));
        Serial.print(t.currentC, 1);
        Serial.print(F(" T="));
        Serial.print(t.targetC, 1);
        Serial.print(F(" EFF="));
        Serial.print(t.effectiveSetpointC, 1);
        Serial.print(F(" PWM="));
        Serial.print(t.pidOutputPwm, 0);
        Serial.print(F(" STAGE="));
        Serial.print(static_cast<uint8_t>(t.stage));
        Serial.print(F(" FAULT="));
        Serial.print(t.thermalFault ? 1 : 0);
        Serial.print(F(" ETA="));
        Serial.println(t.predictedTimeSec, 1);
        return;
    }

    char buffer[96];
    strncpy(buffer, args, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    char* token = strtok(buffer, " ");
    if (!token) {
        Serial.println(F("ERROR TEMP_ARGS"));
        return;
    }

    for (char* p = token; *p; ++p) {
        *p = static_cast<char>(toupper(*p));
    }

    if (strcmp(token, "MATERIAL") == 0) {
        char* matToken = strtok(nullptr, " ");
        if (!matToken) { Serial.println(F("ERROR TEMP_MATERIAL_ARG")); return; }
        for (char* p = matToken; *p; ++p) *p = static_cast<char>(toupper(*p));
        if (strcmp(matToken, "PLA") == 0) { setMaterialProfile(MaterialProfile::PLA); }
        else if (strcmp(matToken, "PETG") == 0) { setMaterialProfile(MaterialProfile::PETG); }
        else if (strcmp(matToken, "ABS") == 0) { setMaterialProfile(MaterialProfile::ABS); }
        else { Serial.println(F("ERROR UNKNOWN_MATERIAL")); return; }
        Serial.print(F("OK MATERIAL "));
        Serial.println(matToken);
        return;
    }
    if (strcmp(token, "PID") == 0) {
        char* kpStr = strtok(nullptr, " ");
        char* kiStr = strtok(nullptr, " ");
        char* kdStr = strtok(nullptr, " ");
        if (!kpStr || !kiStr || !kdStr) {
            Serial.println(F("ERROR PID_ARGS Kp Ki Kd"));
            return;
        }
        setPidTunings(atof(kpStr), atof(kiStr), atof(kdStr));
        Serial.println(F("OK PID_SET"));
        return;
    }
    if (strcmp(token, "AUTOTUNE") == 0) {
        startPidAutoTune();
        return;
    }
    if (strcmp(token, "FAN") == 0) {
        char* valStr = strtok(nullptr, " ");
        if (!valStr) { Serial.println(F("ERROR FAN_ARG")); return; }
        const int pwm = atoi(valStr);
        setCoolingFanPwm(static_cast<uint8_t>(constrain(pwm, 0, 255)));
        Serial.print(F("OK FAN_PWM "));
        Serial.println(pwm);
        return;
    }
    if (strcmp(token, "HEATER") == 0) {
        char* valStr = strtok(nullptr, " ");
        if (!valStr) { Serial.println(F("ERROR HEATER_ARG")); return; }
        const int pwr = atoi(valStr);
        setHeaterPower(static_cast<uint8_t>(constrain(pwr, 0, 255)));
        Serial.print(F("OK HEATER_PWM "));
        Serial.println(pwr);
        return;
    }

    const float temp = atof(token);
    if (temp >= 0.0f && temp <= static_cast<float>(MAX_TEMP)) {
        setTargetTemperature(temp);
        Serial.print(F("OK TEMP_SET "));
        Serial.println(temp, 1);
    } else {
        Serial.println(F("ERROR TEMP_RANGE"));
    }
}
