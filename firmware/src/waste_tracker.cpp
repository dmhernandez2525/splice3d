#include "waste_tracker.h"
#include "config.h"
namespace {
struct WasteState {
    WasteRecord records[kMaxWasteRecords];
    uint8_t count;
    uint8_t ringIndex;
    float categoryTotals[static_cast<uint8_t>(WasteCategory::CATEGORY_COUNT)];
    float totalMm;
    float totalGrams;
    uint16_t failedCount;
    float baselineMmPerSplice;
};
WasteState ws;
}  // namespace
void setupWasteTracker() {
    ws = {};
    ws.baselineMmPerSplice = 25.0f;  // Default baseline.
    Serial.println(F("WASTE_INIT"));
}
void updateWasteTracker() {
    // Waste tracking is passive; recording happens on demand.
}
uint8_t recordWaste(uint16_t spliceId, MaterialType material,
                    WasteCategory category, float wasteMm,
                    float wasteGrams) {
    WasteRecord& r = ws.records[ws.ringIndex];
    r.spliceId = spliceId;
    r.material = material;
    r.category = category;
    r.wasteMm = wasteMm;
    r.wasteGrams = wasteGrams;
    r.timestampMs = millis();
    r.active = true;
    uint8_t idx = ws.ringIndex;
    ws.ringIndex = (ws.ringIndex + 1) % kMaxWasteRecords;
    if (ws.count < kMaxWasteRecords) ws.count++;
    // Update running totals.
    ws.totalMm += wasteMm;
    ws.totalGrams += wasteGrams;
    uint8_t catIdx = static_cast<uint8_t>(category);
    if (catIdx < static_cast<uint8_t>(WasteCategory::CATEGORY_COUNT)) {
        ws.categoryTotals[catIdx] += wasteMm;
    }
    if (category == WasteCategory::FAILED_SPLICE) {
        ws.failedCount++;
    }
    Serial.print(F("WASTE_REC id="));
    Serial.print(spliceId);
    Serial.print(F(" cat="));
    Serial.print(catIdx);
    Serial.print(F(" mm="));
    Serial.print(wasteMm, 1);
    Serial.print(F(" g="));
    Serial.println(wasteGrams, 2);
    return idx;
}
WasteAnalytics getWasteAnalytics() {
    WasteAnalytics a = {};
    a.totalWasteMm = ws.totalMm;
    a.totalWasteGrams = ws.totalGrams;
    a.totalRecords = ws.count;
    a.failedSplices = ws.failedCount;
    a.purgeWasteMm = ws.categoryTotals[
        static_cast<uint8_t>(WasteCategory::PURGE)];
    a.transitionWasteMm = ws.categoryTotals[
        static_cast<uint8_t>(WasteCategory::TRANSITION)];
    a.failedWasteMm = ws.categoryTotals[
        static_cast<uint8_t>(WasteCategory::FAILED_SPLICE)];
    a.tipShapingWasteMm = ws.categoryTotals[
        static_cast<uint8_t>(WasteCategory::TIP_SHAPING)];
    if (ws.count > 0) {
        a.avgWastePerSpliceMm = ws.totalMm / static_cast<float>(ws.count);
        if (ws.baselineMmPerSplice > 0) {
            float saved = ws.baselineMmPerSplice - a.avgWastePerSpliceMm;
            a.wasteReductionPct =
                (saved / ws.baselineMmPerSplice) * 100.0f;
        }
    }
    return a;
}
WasteRecommendation getWasteRecommendation() {
    WasteRecommendation rec = {};
    float maxWaste = 0;
    uint8_t worstIdx = 0;
    for (uint8_t i = 0;
         i < static_cast<uint8_t>(WasteCategory::CATEGORY_COUNT);
         i++) {
        if (ws.categoryTotals[i] > maxWaste) {
            maxWaste = ws.categoryTotals[i];
            worstIdx = i;
        }
    }
    if (maxWaste > 0) {
        rec.hasRecommendation = true;
        rec.worstCategory = static_cast<WasteCategory>(worstIdx);
        rec.worstCategoryMm = maxWaste;
        // Estimate 20% potential saving on worst category.
        rec.potentialSavingMm = maxWaste * 0.2f;
    }
    return rec;
}
uint8_t getWasteRecordCount() { return ws.count; }
WasteRecord getWasteRecord(uint8_t index) {
    if (index >= ws.count) return {};
    return ws.records[index];
}
float getTotalWasteMm() { return ws.totalMm; }
float getTotalWasteGrams() { return ws.totalGrams; }
float getWasteByCategory(WasteCategory category) {
    uint8_t idx = static_cast<uint8_t>(category);
    if (idx >= static_cast<uint8_t>(WasteCategory::CATEGORY_COUNT)) {
        return 0;
    }
    return ws.categoryTotals[idx];
}
float getWasteByMaterial(MaterialType material) {
    float total = 0;
    for (uint8_t i = 0; i < ws.count; i++) {
        if (ws.records[i].active && ws.records[i].material == material) {
            total += ws.records[i].wasteMm;
        }
    }
    return total;
}
void setWasteBaseline(float baselineMmPerSplice) {
    ws.baselineMmPerSplice = baselineMmPerSplice;
    Serial.print(F("WASTE_BASELINE mm="));
    Serial.println(baselineMmPerSplice, 1);
}
void clearWasteRecords() {
    float baseline = ws.baselineMmPerSplice;
    ws = {};
    ws.baselineMmPerSplice = baseline;
    Serial.println(F("WASTE_CLEAR"));
}
void serializeWasteAnalytics() {
    WasteAnalytics a = getWasteAnalytics();
    Serial.print(F("WASTE_STATS total_mm="));
    Serial.print(a.totalWasteMm, 1);
    Serial.print(F(" total_g="));
    Serial.print(a.totalWasteGrams, 2);
    Serial.print(F(" avg_mm="));
    Serial.print(a.avgWastePerSpliceMm, 1);
    Serial.print(F(" purge="));
    Serial.print(a.purgeWasteMm, 1);
    Serial.print(F(" trans="));
    Serial.print(a.transitionWasteMm, 1);
    Serial.print(F(" failed="));
    Serial.print(a.failedWasteMm, 1);
    Serial.print(F(" reduction="));
    Serial.print(a.wasteReductionPct, 1);
    Serial.println(F("%"));
}
