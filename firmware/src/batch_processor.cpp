#include "batch_processor.h"
#include "config.h"
namespace {
struct BatchState {
    BatchSession session;
    BatchEntry history[kMaxBatchHistory];
    uint8_t historyCount;
    uint8_t historyIndex;
};
BatchState bs;
void updateThroughput() {
    if (!bs.session.active) return;
    bs.session.totalTimeMs = millis() - bs.session.startTimeMs;
    if (bs.session.totalTimeMs > 0 && bs.session.completedJobs > 0) {
        const float hours = static_cast<float>(bs.session.totalTimeMs) / 3600000.0f;
        bs.session.throughputJobsPerHour =
            static_cast<float>(bs.session.completedJobs) / hours;
    }
}
}  // namespace
void setupBatchProcessor() {
    bs = {};
}
void updateBatchProcessor() {
    if (bs.session.active) {
        updateThroughput();
    }
}
void startBatchSession(BatchMode mode) {
    if (bs.session.active) return;
    bs.session = {};
    bs.session.mode = mode;
    bs.session.active = true;
    bs.session.startTimeMs = millis();
    Serial.print(F("BATCH_START mode="));
    Serial.println(static_cast<uint8_t>(mode));
}
void stopBatchSession() {
    if (!bs.session.active) return;
    bs.session.active = false;
    bs.session.totalTimeMs = millis() - bs.session.startTimeMs;
    updateThroughput();
    Serial.print(F("BATCH_STOP jobs="));
    Serial.print(bs.session.completedJobs);
    Serial.print(F("/"));
    Serial.print(bs.session.totalJobs);
    Serial.print(F(" throughput="));
    Serial.print(bs.session.throughputJobsPerHour, 1);
    Serial.println(F("/hr"));
}
bool isBatchSessionActive() { return bs.session.active; }
BatchSession getBatchSession() { return bs.session; }
void recordBatchJob(uint16_t jobId, uint8_t materialIndex,
                    uint16_t segmentCount, uint32_t durationMs,
                    float quality, bool success) {
    // Store in history ring buffer.
    BatchEntry& entry = bs.history[bs.historyIndex];
    entry.jobId = jobId;
    entry.materialIndex = materialIndex;
    entry.segmentCount = segmentCount;
    entry.durationMs = durationMs;
    entry.quality = quality;
    entry.success = success;
    bs.historyIndex = (bs.historyIndex + 1) % kMaxBatchHistory;
    if (bs.historyCount < kMaxBatchHistory) bs.historyCount++;
    // Update session stats.
    if (bs.session.active) {
        bs.session.totalJobs++;
        if (success) {
            bs.session.completedJobs++;
        } else {
            bs.session.failedJobs++;
        }
        const float n = static_cast<float>(bs.session.totalJobs);
        bs.session.avgQuality =
            ((n - 1.0f) * bs.session.avgQuality + quality) / n;
        updateThroughput();
    }
}
uint8_t getBatchHistoryCount() { return bs.historyCount; }
BatchEntry getBatchHistoryEntry(uint8_t index) {
    if (index >= bs.historyCount) return {};
    return bs.history[index];
}
void clearBatchHistory() {
    bs.historyCount = 0;
    bs.historyIndex = 0;
}
float getBatchThroughput() { return bs.session.throughputJobsPerHour; }
float getBatchAvgQuality() { return bs.session.avgQuality; }
