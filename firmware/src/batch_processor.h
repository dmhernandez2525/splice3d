/**
 * Splice3D Batch Processor (F4.4).
 *
 * Manages batch operations: multi-spool sequential processing,
 * job history persistence, and aggregate batch statistics.
 */

#ifndef BATCH_PROCESSOR_H
#define BATCH_PROCESSOR_H

#include <Arduino.h>

constexpr uint8_t kMaxBatchHistory = 16;

enum class BatchMode : uint8_t {
    SINGLE = 0,
    SEQUENTIAL,
    ROUND_ROBIN,
};

struct BatchEntry {
    uint16_t jobId;
    uint8_t materialIndex;
    uint16_t segmentCount;
    uint32_t durationMs;
    float quality;
    bool success;
};

struct BatchSession {
    uint32_t startTimeMs;
    uint32_t totalTimeMs;
    uint16_t totalJobs;
    uint16_t completedJobs;
    uint16_t failedJobs;
    float avgQuality;
    float throughputJobsPerHour;
    BatchMode mode;
    bool active;
};

void setupBatchProcessor();
void updateBatchProcessor();

// Session management.
void startBatchSession(BatchMode mode);
void stopBatchSession();
bool isBatchSessionActive();
BatchSession getBatchSession();

// Record completed job into batch history.
void recordBatchJob(uint16_t jobId, uint8_t materialIndex,
                    uint16_t segmentCount, uint32_t durationMs,
                    float quality, bool success);

// History.
uint8_t getBatchHistoryCount();
BatchEntry getBatchHistoryEntry(uint8_t index);
void clearBatchHistory();

// Batch statistics.
float getBatchThroughput();
float getBatchAvgQuality();

#endif  // BATCH_PROCESSOR_H
