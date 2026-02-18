#include "thermal_optimizer.h"
#include "config.h"
namespace {
struct ThermalOptState {
    PreheatEntry queue[kMaxPreheatQueue];
    uint8_t queueCount;
    ThermalState state;
    uint16_t lastSpliceTempC;
    uint16_t totalPreheats;
    uint16_t successfulPreheats;
    uint16_t heatReuses;
    uint32_t totalSavedMs;
    uint16_t totalSavedDegrees;
    uint16_t cyclesAvoided;
    float preheatErrorSum;
    uint16_t preheatErrorCount;
};
ThermalOptState to;
}  // namespace
void setupThermalOptimizer() {
    to = {};
    to.state = ThermalState::IDLE;
    Serial.println(F("THERM_OPT_INIT"));
}
void updateThermalOptimizer() {
    if (to.state != ThermalState::PREHEATING) return;
    uint32_t now = millis();
    for (uint8_t i = 0; i < to.queueCount; i++) {
        PreheatEntry& e = to.queue[i];
        if (!e.active || e.completed) continue;
        if (!e.started && now >= e.scheduledTimeMs) {
            e.started = true;
            to.totalPreheats++;
            Serial.print(F("THERM_PREHEAT_START idx="));
            Serial.print(i);
            Serial.print(F(" target="));
            Serial.println(e.targetTempC);
        }
    }
}
uint8_t schedulePreheat(MaterialType material, uint16_t targetTempC,
                        uint32_t leadTimeMs) {
    if (to.queueCount >= kMaxPreheatQueue) return 255;
    PreheatEntry& e = to.queue[to.queueCount];
    e.material = material;
    e.targetTempC = targetTempC;
    e.scheduledTimeMs = millis() + leadTimeMs;
    e.started = false;
    e.completed = false;
    e.active = true;
    to.queueCount++;
    if (to.state == ThermalState::IDLE) {
        to.state = ThermalState::PREHEATING;
    }
    Serial.print(F("THERM_SCHEDULE idx="));
    Serial.print(to.queueCount - 1);
    Serial.print(F(" mat="));
    Serial.print(static_cast<uint8_t>(material));
    Serial.print(F(" temp="));
    Serial.print(targetTempC);
    Serial.print(F(" lead="));
    Serial.println(leadTimeMs);
    return to.queueCount - 1;
}
HeatReuseRecord checkHeatReuse(uint16_t currentTempC,
                                uint16_t targetTempC) {
    HeatReuseRecord rec = {};
    rec.currentTempC = currentTempC;
    rec.targetTempC = targetTempC;
    if (currentTempC == 0) return rec;
    int16_t delta = static_cast<int16_t>(targetTempC)
                  - static_cast<int16_t>(currentTempC);
    if (delta < 0) delta = -delta;
    if (static_cast<uint16_t>(delta) <= kHeatReuseThresholdC) {
        rec.reused = true;
        rec.savedDegrees = currentTempC;
        // Estimate saved time: ~100ms per degree.
        rec.savedTimeMs = static_cast<uint32_t>(currentTempC) * 100;
        to.heatReuses++;
        to.totalSavedDegrees += rec.savedDegrees;
        to.totalSavedMs += rec.savedTimeMs;
        to.cyclesAvoided++;
        to.state = ThermalState::REUSING_HEAT;
        Serial.print(F("THERM_REUSE saved_deg="));
        Serial.print(rec.savedDegrees);
        Serial.print(F(" saved_ms="));
        Serial.println(rec.savedTimeMs);
    }
    return rec;
}
bool cancelPreheat(uint8_t index) {
    if (index >= to.queueCount) return false;
    if (!to.queue[index].active) return false;
    to.queue[index].active = false;
    Serial.print(F("THERM_CANCEL idx="));
    Serial.println(index);
    return true;
}
void clearPreheatQueue() {
    for (uint8_t i = 0; i < to.queueCount; i++) {
        to.queue[i] = {};
    }
    to.queueCount = 0;
    to.state = ThermalState::IDLE;
    Serial.println(F("THERM_CLEAR"));
}
void onSpliceComplete(uint16_t finalTempC) {
    to.lastSpliceTempC = finalTempC;
    // Mark oldest active entry as completed.
    for (uint8_t i = 0; i < to.queueCount; i++) {
        PreheatEntry& e = to.queue[i];
        if (e.active && e.started && !e.completed) {
            e.completed = true;
            to.successfulPreheats++;
            float error = static_cast<float>(finalTempC)
                        - static_cast<float>(e.targetTempC);
            if (error < 0) error = -error;
            to.preheatErrorSum += error;
            to.preheatErrorCount++;
            break;
        }
    }
    to.state = ThermalState::COOLING;
    Serial.print(F("THERM_SPLICE_DONE temp="));
    Serial.println(finalTempC);
}
ThermalState getThermalState() { return to.state; }
uint8_t getPreheatQueueSize() { return to.queueCount; }
PreheatEntry getPreheatEntry(uint8_t index) {
    if (index >= to.queueCount) return {};
    return to.queue[index];
}
uint16_t getLastSpliceTempC() { return to.lastSpliceTempC; }
ThermalOptimizerStats getThermalStats() {
    ThermalOptimizerStats stats = {};
    stats.totalPreheats = to.totalPreheats;
    stats.successfulPreheats = to.successfulPreheats;
    stats.heatReuses = to.heatReuses;
    stats.totalSavedMs = to.totalSavedMs;
    stats.totalSavedDegrees = to.totalSavedDegrees;
    stats.thermalCyclesAvoided = to.cyclesAvoided;
    if (to.preheatErrorCount > 0) {
        stats.avgPreheatAccuracyC =
            to.preheatErrorSum / static_cast<float>(to.preheatErrorCount);
    }
    return stats;
}
void serializeThermalStats() {
    ThermalOptimizerStats stats = getThermalStats();
    Serial.print(F("THERM_STATS preheats="));
    Serial.print(stats.totalPreheats);
    Serial.print(F(" reuses="));
    Serial.print(stats.heatReuses);
    Serial.print(F(" saved_ms="));
    Serial.print(stats.totalSavedMs);
    Serial.print(F(" saved_deg="));
    Serial.print(stats.totalSavedDegrees);
    Serial.print(F(" avoided="));
    Serial.println(stats.thermalCyclesAvoided);
}
