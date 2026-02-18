#include "cross_material.h"
#include "config.h"
namespace {
struct CompatState {
    CompatEntry entries[kMaxCompatEntries];
    uint8_t count;
};
CompatState cs;
int8_t findEntry(MaterialType a, MaterialType b) {
    for (uint8_t i = 0; i < cs.count; i++) {
        if (!cs.entries[i].active) continue;
        bool match = (cs.entries[i].typeA == a && cs.entries[i].typeB == b)
                  || (cs.entries[i].typeA == b && cs.entries[i].typeB == a);
        if (match) return static_cast<int8_t>(i);
    }
    return -1;
}
void addEntry(MaterialType a, MaterialType b, CompatLevel level,
              uint8_t score, bool hasOvr, const CompatOverride& ovr) {
    if (cs.count >= kMaxCompatEntries) return;
    CompatEntry& e = cs.entries[cs.count];
    e.typeA = a;
    e.typeB = b;
    e.level = level;
    e.score = score;
    e.hasOverrides = hasOvr;
    if (hasOvr) e.overrides = ovr;
    e.active = true;
    cs.count++;
}
void addSimple(MaterialType a, MaterialType b,
               CompatLevel level, uint8_t score) {
    CompatOverride ovr = {};
    addEntry(a, b, level, score, false, ovr);
}
void addWithOvr(MaterialType a, MaterialType b,
                CompatLevel level, uint8_t score,
                uint16_t temp, uint16_t hold,
                float comp, uint16_t cool) {
    CompatOverride ovr = {};
    ovr.spliceTemp = temp;
    ovr.holdTimeMs = hold;
    ovr.compressionMm = comp;
    ovr.coolTimeMs = cool;
    addEntry(a, b, level, score, true, ovr);
}
}  // namespace
void setupCrossMaterial() {
    cs = {};
    loadDefaultCompatMatrix();
    Serial.print(F("COMPAT_INIT entries="));
    Serial.println(cs.count);
}
void updateCrossMaterial() {
    // Compatibility matrix is passive; nothing to poll.
}
CompatEntry getCompatibility(MaterialType a, MaterialType b) {
    int8_t idx = findEntry(a, b);
    if (idx < 0) {
        // Same-type splicing is always excellent.
        if (a == b) {
            CompatEntry e = {};
            e.typeA = a;
            e.typeB = b;
            e.level = CompatLevel::EXCELLENT;
            e.score = 100;
            e.active = true;
            return e;
        }
        return {};
    }
    return cs.entries[idx];
}
CompatLevel getCompatLevel(MaterialType a, MaterialType b) {
    return getCompatibility(a, b).level;
}
uint8_t getCompatScore(MaterialType a, MaterialType b) {
    return getCompatibility(a, b).score;
}
bool canSplice(MaterialType a, MaterialType b) {
    return getCompatLevel(a, b) > CompatLevel::INCOMPATIBLE;
}
CompatOverride getSpliceOverrides(MaterialType a, MaterialType b) {
    int8_t idx = findEntry(a, b);
    if (idx >= 0 && cs.entries[idx].hasOverrides) {
        return cs.entries[idx].overrides;
    }
    // Fallback: no overrides available.
    CompatOverride fallback = {};
    return fallback;
}
uint8_t setCompatibility(MaterialType a, MaterialType b,
                         CompatLevel level, uint8_t score) {
    int8_t idx = findEntry(a, b);
    if (idx >= 0) {
        cs.entries[idx].level = level;
        cs.entries[idx].score = score;
        Serial.print(F("COMPAT_UPDATE idx="));
        Serial.println(idx);
        return static_cast<uint8_t>(idx);
    }
    if (cs.count >= kMaxCompatEntries) return 255;
    CompatOverride ovr = {};
    addEntry(a, b, level, score, false, ovr);
    Serial.print(F("COMPAT_ADD idx="));
    Serial.println(cs.count - 1);
    return cs.count - 1;
}
uint8_t setCompatibilityWithOverrides(MaterialType a, MaterialType b,
                                      CompatLevel level, uint8_t score,
                                      const CompatOverride& overrides) {
    int8_t idx = findEntry(a, b);
    if (idx >= 0) {
        cs.entries[idx].level = level;
        cs.entries[idx].score = score;
        cs.entries[idx].overrides = overrides;
        cs.entries[idx].hasOverrides = true;
        return static_cast<uint8_t>(idx);
    }
    if (cs.count >= kMaxCompatEntries) return 255;
    addEntry(a, b, level, score, true, overrides);
    return cs.count - 1;
}
void serializeCompatMatrix() {
    Serial.print(F("COMPAT_LIST count="));
    Serial.println(cs.count);
    for (uint8_t i = 0; i < cs.count; i++) {
        if (!cs.entries[i].active) continue;
        const CompatEntry& e = cs.entries[i];
        Serial.print(F("COMPAT idx="));
        Serial.print(i);
        Serial.print(F(" a="));
        Serial.print(static_cast<uint8_t>(e.typeA));
        Serial.print(F(" b="));
        Serial.print(static_cast<uint8_t>(e.typeB));
        Serial.print(F(" level="));
        Serial.print(static_cast<uint8_t>(e.level));
        Serial.print(F(" score="));
        Serial.println(e.score);
    }
    Serial.println(F("COMPAT_LIST_END"));
}
CompatMatrixStats getCompatMatrixStats() {
    CompatMatrixStats stats = {};
    stats.totalEntries = cs.count;
    for (uint8_t i = 0; i < cs.count; i++) {
        if (!cs.entries[i].active) continue;
        stats.activeEntries++;
        if (cs.entries[i].level == CompatLevel::INCOMPATIBLE) {
            stats.incompatiblePairs++;
        }
        if (cs.entries[i].level == CompatLevel::EXCELLENT) {
            stats.excellentPairs++;
        }
    }
    return stats;
}
void loadDefaultCompatMatrix() {
    // PLA + PETG: fair, needs higher temp and longer hold.
    addWithOvr(MaterialType::PLA, MaterialType::PETG,
               CompatLevel::FAIR, 55, 230, 4500, 2.5f, 6000);
    // PLA + ABS: poor compatibility.
    addWithOvr(MaterialType::PLA, MaterialType::ABS,
               CompatLevel::POOR, 25, 240, 5000, 3.0f, 7000);
    // PLA + TPU: fair, flexible bond.
    addWithOvr(MaterialType::PLA, MaterialType::TPU,
               CompatLevel::FAIR, 50, 218, 4000, 1.8f, 6000);
    // PETG + ABS: good, similar temps.
    addWithOvr(MaterialType::PETG, MaterialType::ABS,
               CompatLevel::GOOD, 70, 245, 4500, 2.8f, 7000);
    // PETG + TPU: poor.
    addWithOvr(MaterialType::PETG, MaterialType::TPU,
               CompatLevel::POOR, 30, 232, 5000, 2.0f, 7000);
    // ABS + TPU: incompatible.
    addSimple(MaterialType::ABS, MaterialType::TPU,
              CompatLevel::INCOMPATIBLE, 0);
}
