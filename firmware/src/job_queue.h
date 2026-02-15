/**
 * Splice3D Job Queue (F4.3).
 *
 * Manages a queue of splice recipes with priority ordering,
 * pause/resume per job, progress tracking, and completion callbacks.
 */

#ifndef JOB_QUEUE_H
#define JOB_QUEUE_H

#include <Arduino.h>

constexpr uint8_t kMaxQueuedJobs = 8;

enum class JobStatus : uint8_t {
    PENDING = 0,
    RUNNING,
    PAUSED,
    COMPLETE,
    FAILED,
    CANCELLED,
};

struct JobEntry {
    uint16_t jobId;
    uint16_t segmentCount;
    uint16_t currentSegment;
    uint8_t materialIndex;
    uint8_t priority;
    JobStatus status;
    uint32_t startTimeMs;
    uint32_t elapsedMs;
    float progressPercent;
};

struct QueueStats {
    uint16_t totalQueued;
    uint16_t totalCompleted;
    uint16_t totalFailed;
    uint16_t totalCancelled;
    float avgJobTimeMs;
};

void setupJobQueue();
void updateJobQueue();

// Queue management.
int16_t enqueueJob(uint16_t segmentCount, uint8_t materialIndex, uint8_t priority);
bool cancelJob(uint16_t jobId);
bool pauseCurrentJob();
bool resumeCurrentJob();
void clearQueue();

// Query.
uint8_t getQueueLength();
JobEntry getJobEntry(uint8_t queueIndex);
JobEntry getCurrentJob();
bool isQueueEmpty();
bool isJobRunning();
QueueStats getQueueStats();

// Advance to next job (called when current job finishes).
void advanceQueue();

#endif  // JOB_QUEUE_H
