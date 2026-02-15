/**
 * Splice3D Waste Reduction (F6.3).
 *
 * Tracks filament waste per splice including purge waste, transition
 * waste, and failed splice waste. Provides waste analytics and
 * reduction recommendations based on historical data.
 */

#ifndef WASTE_TRACKER_H
#define WASTE_TRACKER_H

#include <Arduino.h>
#include "material_database.h"

constexpr uint8_t kMaxWasteRecords = 32;

enum class WasteCategory : uint8_t {
    PURGE = 0,
    TRANSITION,
    FAILED_SPLICE,
    TIP_SHAPING,
    CATEGORY_COUNT,
};

struct WasteRecord {
    uint16_t spliceId;
    MaterialType material;
    WasteCategory category;
    float wasteMm;
    float wasteGrams;
    uint32_t timestampMs;
    bool active;
};

struct WasteAnalytics {
    float totalWasteMm;
    float totalWasteGrams;
    float avgWastePerSpliceMm;
    float purgeWasteMm;
    float transitionWasteMm;
    float failedWasteMm;
    float tipShapingWasteMm;
    uint16_t totalRecords;
    uint16_t failedSplices;
    float wasteReductionPct;
};

struct WasteRecommendation {
    WasteCategory worstCategory;
    float worstCategoryMm;
    float potentialSavingMm;
    bool hasRecommendation;
};

void setupWasteTracker();
void updateWasteTracker();

// Record waste from a splice. Returns index or 255.
uint8_t recordWaste(uint16_t spliceId, MaterialType material,
                    WasteCategory category, float wasteMm,
                    float wasteGrams);

// Get waste analytics.
WasteAnalytics getWasteAnalytics();

// Get reduction recommendation.
WasteRecommendation getWasteRecommendation();

// Query APIs.
uint8_t getWasteRecordCount();
WasteRecord getWasteRecord(uint8_t index);
float getTotalWasteMm();
float getTotalWasteGrams();
float getWasteByCategory(WasteCategory category);
float getWasteByMaterial(MaterialType material);

// Set baseline for waste reduction tracking.
void setWasteBaseline(float baselineMmPerSplice);

// Clear all records.
void clearWasteRecords();

// Serialize to serial.
void serializeWasteAnalytics();

#endif  // WASTE_TRACKER_H
