#include "queue_manager.h"
#include "config.h"

namespace {

struct State {
    QueueManagerStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupQueueManager() {
    st = {};
    st.initialized = true;
    Serial.println(F("QUEUE_MANAGER_INIT"));
}

void updateQueueManager() {
    if (!st.initialized) return;
}

QueueManagerStats getQueueManagerStats() {
    return st.stats;
}

void serializeQueueManagerStats() {
    QueueManagerStats s = st.stats;
    Serial.print(F("QUEUE_MANAGER_STATS"));
    Serial.print(F(" totalQueued="));
    Serial.print(s.totalQueued);
    Serial.print(F(" totalCompleted="));
    Serial.print(s.totalCompleted ? F("Y") : F("N"));
    Serial.print(F(" totalFailed="));
    Serial.print(s.totalFailed);
    Serial.print(F(" avgWaitMinutes="));
    Serial.print(s.avgWaitMinutes);
    Serial.print(F(" currentJobId="));
    Serial.print(s.currentJobId);
    Serial.print(F(" queueState="));
    Serial.print(s.queueState);
    Serial.println();
}
