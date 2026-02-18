#include "serial_handler.h"
#include "telemetry_stream.h"
void SerialHandler::handleStream(const char* args) {
    if (!args || args[0] == '\0') {
        const StreamConfig cfg = getStreamConfig();
        const char* modes[] = {"OFF", "SUMMARY", "VERBOSE"};
        Serial.print(F("STREAM mode="));
        Serial.print(modes[static_cast<uint8_t>(cfg.mode)]);
        Serial.print(F(" interval="));
        Serial.print(cfg.intervalMs);
        Serial.print(F(" heartbeat="));
        Serial.println(isHeartbeatEnabled() ? F("on") : F("off"));
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
    if (strcmp(sub, "OFF") == 0) {
        setStreamMode(StreamMode::OFF);
        Serial.println(F("OK stream off"));
    } else if (strcmp(sub, "SUMMARY") == 0) {
        setStreamMode(StreamMode::SUMMARY);
        Serial.println(F("OK stream summary"));
    } else if (strcmp(sub, "VERBOSE") == 0) {
        setStreamMode(StreamMode::VERBOSE);
        Serial.println(F("OK stream verbose"));
    } else if (strcmp(sub, "INTERVAL") == 0 && rest) {
        const uint32_t ms = strtoul(rest, nullptr, 10);
        setStreamInterval(ms);
        Serial.print(F("OK interval="));
        Serial.println(ms);
    } else if (strcmp(sub, "HEARTBEAT") == 0) {
        if (rest && strcmp(rest, "OFF") == 0) {
            enableHeartbeat(false);
            Serial.println(F("OK heartbeat off"));
        } else {
            enableHeartbeat(true);
            Serial.println(F("OK heartbeat on"));
        }
    } else if (strcmp(sub, "REPORT") == 0) {
        emitStatusReport();
    } else {
        Serial.println(F("ERR unknown STREAM subcommand"));
    }
}
