/**
 * Splice3D Print Job Queue Management Interface (F8.4).
 *
 * Queue management with drag-and-drop reordering, estimated completion times, job priorities.
 */

#ifndef QUEUE_MANAGER_H
#define QUEUE_MANAGER_H

#include <Arduino.h>

constexpr uint8_t kMaxQueueSize = 32;
constexpr uint8_t kPriorityLevels = 4;
enum class QueueManagerState : uint8_t {
    EMPTY = 0,
    RUNNING = 1,
    PAUSED = 2,
    COMPLETED = 3,
    ERROR = 4,
};

struct QueueManagerStats {
    uint32_t totalQueued;
    uint32_t totalCompleted;
    uint32_t totalFailed;
    uint16_t avgWaitMinutes;
    uint16_t currentJobId;
    uint16_t queueState;
};

void setupQueueManager();
void updateQueueManager();
QueueManagerStats getQueueManagerStats();
void serializeQueueManagerStats();

#endif  // QUEUE_MANAGER_H
