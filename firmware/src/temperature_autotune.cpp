#include "temperature.h"
#include "config.h"

namespace {
struct AutoTuneState {
    bool active;
    float outputHigh;
    float outputLow;
    float peakHigh;
    float peakLow;
    uint8_t cycleCount;
    uint8_t targetCycles;
    uint32_t lastToggleMs;
    bool heatingPhase;
    float computedKp;
    float computedKi;
    float computedKd;
};
AutoTuneState atState = {false, 200.0f, 0.0f, 0.0f, 999.0f, 0, 5, 0, true, 0, 0, 0};
}  // namespace

void startPidAutoTune() {
    atState.active = true;
    atState.cycleCount = 0;
    atState.peakHigh = 0.0f;
    atState.peakLow = 999.0f;
    atState.heatingPhase = true;
    atState.lastToggleMs = millis();
    setHeaterPower(static_cast<uint8_t>(atState.outputHigh));
    Serial.println(F("OK PID_AUTOTUNE_START"));
}

bool isPidAutoTuneActive() { return atState.active; }

void updatePidAutoTune() {
    if (!atState.active) return;
    const float current = getCurrentTemperature();
    const float target = getTargetTemperature();
    if (target <= 0.0f) { atState.active = false; return; }
    if (current > atState.peakHigh) atState.peakHigh = current;
    if (current < atState.peakLow) atState.peakLow = current;
    if (atState.heatingPhase && current > target + 2.0f) {
        atState.heatingPhase = false;
        setHeaterPower(static_cast<uint8_t>(atState.outputLow));
        atState.cycleCount++;
        const uint32_t period = millis() - atState.lastToggleMs;
        atState.lastToggleMs = millis();
        if (atState.cycleCount >= atState.targetCycles) {
            const float amplitude = (atState.peakHigh - atState.peakLow) / 2.0f;
            const float ku = (4.0f * (atState.outputHigh - atState.outputLow)) / (3.14159f * amplitude);
            const float tu = static_cast<float>(period) / 1000.0f;
            atState.computedKp = 0.6f * ku;
            atState.computedKi = 1.2f * ku / tu;
            atState.computedKd = 0.075f * ku * tu;
            setPidTunings(atState.computedKp, atState.computedKi, atState.computedKd);
            atState.active = false;
            Serial.print(F("PID_AUTOTUNE_DONE Kp="));
            Serial.print(atState.computedKp, 3);
            Serial.print(F(" Ki="));
            Serial.print(atState.computedKi, 3);
            Serial.print(F(" Kd="));
            Serial.println(atState.computedKd, 3);
            return;
        }
        atState.peakHigh = 0.0f;
        atState.peakLow = 999.0f;
    } else if (!atState.heatingPhase && current < target - 2.0f) {
        atState.heatingPhase = true;
        setHeaterPower(static_cast<uint8_t>(atState.outputHigh));
        atState.lastToggleMs = millis();
    }
}
