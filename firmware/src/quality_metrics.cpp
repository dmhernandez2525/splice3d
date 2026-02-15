#include "quality_metrics.h"
#include "config.h"
namespace {
struct QualityState {
    QualitySnapshot snap;
    uint8_t historyIndex;
};
QualityState qs;
void updateTrend() {
    QualityTrend& t = qs.snap.trend;
    if (t.count == 0) return;
    // Compute moving average over last entries.
    float sum = 0.0f;
    const uint8_t n = t.count < kQualityHistorySize ? t.count : kQualityHistorySize;
    for (uint8_t i = 0; i < n; i++) {
        sum += t.scores[i];
    }
    t.movingAvg = sum / static_cast<float>(n);
    // Simple linear trend: compare first half avg to second half avg.
    if (n < 4) {
        t.trend = 0.0f;
        return;
    }
    const uint8_t half = n / 2;
    float firstSum = 0.0f;
    float secondSum = 0.0f;
    for (uint8_t i = 0; i < half; i++) {
        firstSum += t.scores[i];
    }
    for (uint8_t i = half; i < n; i++) {
        secondSum += t.scores[i];
    }
    const float firstAvg = firstSum / static_cast<float>(half);
    const float secondAvg = secondSum / static_cast<float>(n - half);
    t.trend = secondAvg - firstAvg;
}
}  // namespace
void setupQualityMetrics() {
    qs = {};
    for (uint8_t i = 0; i < kMaxMaterials; i++) {
        qs.snap.perMaterial[i].minQuality = 999.0f;
        qs.snap.perMaterial[i].maxQuality = 0.0f;
    }
    qs.snap.sessionBestQuality = 0.0f;
    qs.snap.sessionWorstQuality = 999.0f;
}
void updateQualityMetrics() {
    // Trend update is done on each record, no periodic work needed.
}
void recordSpliceQuality(uint8_t materialIndex, bool success,
                         float quality, float spliceTimeMs) {
    QualitySnapshot& s = qs.snap;
    s.totalSplices++;
    if (success) {
        s.totalSuccesses++;
    } else {
        s.totalFailures++;
    }
    s.overallSuccessRate = static_cast<float>(s.totalSuccesses)
        / static_cast<float>(s.totalSplices);
    // Running average for overall quality.
    const float n = static_cast<float>(s.totalSplices);
    s.overallAvgQuality =
        ((n - 1.0f) * s.overallAvgQuality + quality) / n;
    // Session best/worst.
    if (quality > s.sessionBestQuality) s.sessionBestQuality = quality;
    if (quality < s.sessionWorstQuality) s.sessionWorstQuality = quality;
    // Per-material stats.
    if (materialIndex < kMaxMaterials) {
        MaterialQuality& m = s.perMaterial[materialIndex];
        m.attempts++;
        if (success) m.successes++;
        const float mn = static_cast<float>(m.attempts);
        m.avgQuality = ((mn - 1.0f) * m.avgQuality + quality) / mn;
        m.avgSpliceTimeMs = ((mn - 1.0f) * m.avgSpliceTimeMs + spliceTimeMs) / mn;
        if (quality < m.minQuality) m.minQuality = quality;
        if (quality > m.maxQuality) m.maxQuality = quality;
    }
    // Trend history (ring buffer).
    QualityTrend& t = s.trend;
    t.scores[qs.historyIndex] = quality;
    qs.historyIndex = (qs.historyIndex + 1) % kQualityHistorySize;
    if (t.count < kQualityHistorySize) t.count++;
    updateTrend();
    // Log.
    Serial.print(F("QUALITY mat="));
    Serial.print(materialIndex);
    Serial.print(F(" q="));
    Serial.print(quality, 2);
    Serial.print(F(" rate="));
    Serial.print(s.overallSuccessRate * 100.0f, 1);
    Serial.println('%');
}
QualitySnapshot getQualitySnapshot() { return qs.snap; }
MaterialQuality getMaterialQuality(uint8_t materialIndex) {
    if (materialIndex >= kMaxMaterials) return {};
    return qs.snap.perMaterial[materialIndex];
}
QualityTrend getQualityTrend() { return qs.snap.trend; }
float getSuccessRate() { return qs.snap.overallSuccessRate; }
float getAverageQuality() { return qs.snap.overallAvgQuality; }
void resetQualityMetrics() { setupQualityMetrics(); }
