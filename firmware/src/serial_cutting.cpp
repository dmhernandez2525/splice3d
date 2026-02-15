#include "serial_handler.h"
#include "cutting_system.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

void SerialHandler::handleCutter(const char* args) {
    if (!args || strlen(args) == 0 || strcmp(args, "STATUS") == 0) {
        const CutStatistics s = getCutStatistics();
        const CutConfig c = getCutConfig();
        Serial.print(F("CUTTER TOTAL="));
        Serial.print(s.totalCuts);
        Serial.print(F(" OK="));
        Serial.print(s.successfulCuts);
        Serial.print(F(" FAIL="));
        Serial.print(s.failedCuts);
        Serial.print(F(" AVG_FORCE="));
        Serial.print(s.averageForce);
        Serial.print(F(" MAINT="));
        Serial.print(s.maintenanceDue ? 1 : 0);
        Serial.print(F(" OPEN="));
        Serial.print(c.openAngle);
        Serial.print(F(" CLOSED="));
        Serial.println(c.closedAngle);
        return;
    }
    char buffer[64];
    strncpy(buffer, args, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    char* token = strtok(buffer, " ");
    if (!token) { Serial.println(F("ERROR CUTTER_ARGS")); return; }
    for (char* p = token; *p; ++p) *p = static_cast<char>(toupper(*p));
    if (strcmp(token, "CUT") == 0) {
        triggerManualCut();
        Serial.println(F("OK CUTTER_CUT_QUEUED"));
        return;
    }
    if (strcmp(token, "ANGLES") == 0) {
        char* openStr = strtok(nullptr, " ");
        char* closedStr = strtok(nullptr, " ");
        if (!openStr || !closedStr) { Serial.println(F("ERROR ANGLES open closed")); return; }
        setCutAngles(static_cast<uint8_t>(atoi(openStr)), static_cast<uint8_t>(atoi(closedStr)));
        Serial.println(F("OK CUTTER_ANGLES"));
        return;
    }
    if (strcmp(token, "TRAVEL") == 0) {
        char* msStr = strtok(nullptr, " ");
        if (!msStr) { Serial.println(F("ERROR TRAVEL ms")); return; }
        setCutTravelMs(static_cast<uint16_t>(atoi(msStr)));
        Serial.println(F("OK CUTTER_TRAVEL"));
        return;
    }
    if (strcmp(token, "MAINT_ACK") == 0) {
        acknowledgeMaintenanceAlert();
        return;
    }
    if (strcmp(token, "SAVE") == 0) {
        Serial.println(saveCutStatistics() ? F("OK CUTTER_SAVED") : F("ERROR CUTTER_SAVE"));
        return;
    }
    if (strcmp(token, "RESET") == 0) {
        resetCutStatistics();
        Serial.println(F("OK CUTTER_RESET"));
        return;
    }
    if (strcmp(token, "MAINT_INTERVAL") == 0) {
        char* valStr = strtok(nullptr, " ");
        if (!valStr) { Serial.println(F("ERROR MAINT_INTERVAL val")); return; }
        setMaintenanceInterval(static_cast<uint32_t>(atol(valStr)));
        Serial.println(F("OK CUTTER_MAINT_INTERVAL"));
        return;
    }
    Serial.print(F("ERROR CUTTER_SUBCMD "));
    Serial.println(token);
}
