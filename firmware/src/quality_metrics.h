/**
 * Splice3D Quality Metrics System (F4.2).
 *
 * Tracks splice quality scores, success/failure rates, material-specific
 * statistics, and generates quality trend data for host analytics.
 */

#ifndef QUALITY_METRICS_H
#define QUALITY_METRICS_H

#include <Arduino.h>

constexpr uint8_t kMaxMaterials = 4;
constexpr uint8_t kQualityHistorySize = 32;

struct MaterialQuality {
    uint32_t attempts;
    uint32_t successes;
    float avgQuality;
    float avgSpliceTimeMs;
    float minQuality;
    float maxQuality;
};

struct QualityTrend {
    float scores[kQualityHistorySize];
    uint8_t count;
    float movingAvg;
    float trend;
};

struct QualitySnapshot {
    uint32_t totalSplices;
    uint32_t totalSuccesses;
    uint32_t totalFailures;
    float overallSuccessRate;
    float overallAvgQuality;
    float sessionBestQuality;
    float sessionWorstQuality;
    MaterialQuality perMaterial[kMaxMaterials];
    QualityTrend trend;
};

void setupQualityMetrics();
void updateQualityMetrics();

// Record a completed splice.
void recordSpliceQuality(uint8_t materialIndex, bool success,
                         float quality, float spliceTimeMs);

// Query.
QualitySnapshot getQualitySnapshot();
MaterialQuality getMaterialQuality(uint8_t materialIndex);
QualityTrend getQualityTrend();
float getSuccessRate();
float getAverageQuality();

// Reset.
void resetQualityMetrics();

#endif  // QUALITY_METRICS_H
